#!/usr/bin/env python3
"""PreToolUse commit gate — the ONE structural slice of delegation-framework.

Reads the PreToolUse hook payload on stdin. If the tool command *runs* a
commit-creating git subcommand (`commit`, `merge`, `rebase`, `cherry-pick`,
`revert`, `pull`, `am` — all of them write commits; gating only `commit`
left the rest wide open), and the target repo has **opted in** by having a
`.delegation/` directory at its root, the gate requires a well-formed,
all-PLEASED review artifact at `.delegation/review-artifact.json` that is
**bound to the current HEAD**. Without one it emits a JSON
`permissionDecision: "deny"`; otherwise it stays silent and the normal
permission flow proceeds.

Matching is anchored — the `git` word must sit at a command position (start
of line, after `; & | ( ) { }` or a backtick, or after a shell keyword like
`if`/`then`/`do`), so `echo please run git commit later` and
`grep 'git commit' docs/` do not trigger. Anchoring is about command
*position*, not quoting: `echo "step1; git commit -m x"` and a heredoc line
beginning `git commit` DO match, because a `;` inside quotes is still a `;`
to this regex and the regex is multiline. That is deliberate — teaching the
regex to parse quoting and heredocs is writing a shell, and every bug in
that shell fails OPEN. Over-matching is the fail-closed direction and has
three escape hatches (write the artifact, remove `.delegation/`, disable the
hook). Both shapes are pinned by tests.

Scoping (the opt-in marker): plugin hooks are SESSION-GLOBAL — this script
is consulted for tool calls in every repo the session touches. To avoid
walling off repos that never use the framework, the gate enforces only
where `.delegation/` exists at the resolved repo root (the `delegating`
skill / `/delegate` creates it when a loop starts). No marker → silent
allow.

Repo resolution: from the hook's cwd, adjusted when the command itself says
otherwise — EVERY `cd <path>` before the git word is composed in order (a
chain like `cd frontend && ... && cd .. && git commit` lands where the shell
would), then `git -C <path>`, `--work-tree=<path>` and `--git-dir=<path>`
are followed (plain paths only). Paths built from variables or nested
quoting are still NOT resolved (a stated residual, limit 4) — but an
unresolvable or out-of-tree result now FALLS BACK to the hook's own repo
instead of reading as "not gated". "Couldn't resolve" must never be a
silent waiver.

Design choices, stated honestly:

- The script always exits 0 and communicates via hook JSON output. This
  makes the `python || python3` fallback chain in hooks.json safe: a block
  is a successful run that outputs "deny", never a nonzero exit that would
  trigger the fallback interpreter.
- Fail-open on infrastructure problems (unreadable stdin, malformed hook
  payload, an unreadable `.git`): a broken hook must not brick tool calls.
  Fail-CLOSED on artifact problems in an opted-in repo (missing, malformed,
  not all-PLEASED, not bound to the current HEAD): that is the gate doing
  its job.
- Nothing read out of the artifact is echoed into the reason string. Hook
  output is delivered to the model as privileged text, so a cloned repo
  shipping a crafted artifact would otherwise be able to speak directly to
  the agent at the moment it decides how to proceed. Problems are reported
  positionally ("review #2 ..."); the only artifact value ever echoed is a
  `head_sha` already validated as hex, and everything on the reason channel
  goes through `scrub()` (control characters stripped, hard length cap).
- ONE artifact waives ONE commit. The artifact records the HEAD it was
  reviewed against; once that commit is made, HEAD moves and the artifact
  is stale. The "archive it afterwards" step is prose guidance to an LLM,
  and the failure mode this gate exists to wall off is *forgetting* — so
  freshness is checked structurally rather than trusted.
- FIVE honest limits (see README "Enforcement, honestly"):
  (1) fires only where these hooks are installed and enabled, and only if
      `python`/`python3` is on PATH — otherwise it silently vanishes;
  (2) verifies the artifact exists / is well-formed (including a non-empty
      `deliverable`) / is all-PLEASED / is bound to the current HEAD — not
      that the review was rigorous; a PLEASED artifact can be fabricated
      (wall against forgetting, not bad faith);
  (3) local working tree only;
  (4) only commits crossing the hooked tool matcher, and only as the
      anchored regex + cd/-C/--git-dir parsing understand them — aliases,
      subprocesses (`bash -c "git commit"`), IDE commits bypass it, and
      variable/nested-quoted paths still do not resolve (they now fall back
      to the hook's repo rather than waiving);
  (5) OVER-reach: the hook is session-global; it is scoped by the
      `.delegation/` opt-in marker and anchored matching, but compound
      commands, quoted prose containing a command separator, and the
      fail-closed fallback above can still deny something they shouldn't.
      Escape hatches: write the artifact, remove `.delegation/`, or disable
      the hook.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ARTIFACT_REL_PATH = Path(".delegation") / "review-artifact.json"
OPT_IN_MARKER = ".delegation"
VALID_MODES = {"swarm", "deep", "hybrid"}

# Every porcelain subcommand that can write a commit. `commit` alone was the
# old matcher; this framework's own history contains a merge commit.
COMMIT_SUBCOMMANDS = (
    "commit",
    "merge",
    "rebase",
    "cherry-pick",
    "revert",
    "pull",
    "am",
)

# read_head_sha() sentinel: the repo is real but carries no commit yet.
HEAD_UNBORN = "<unborn>"

# Hard cap on any text that reaches the reason channel.
MAX_REASON_ECHO = 60

# A quoted-or-plain token (no shell separators inside a plain token).
_TOKEN = r"(?:\"[^\"]+\"|'[^']+'|[^\s;&|()`\"']+)"

# Anchored commit-creating `git`: the `git` word must sit at a command
# position — start of string/line or right after ; & | ( ) { } or a
# backtick. Shell keywords and `!` that themselves sit at a command
# position are consumed, so `if git commit; then`, `for f in a; do git
# commit; done`, `{ git commit; }` and `! git commit` match (shapes an LLM
# writes by accident, not evasions, and they used to slip past) while the
# same words inside prose (`# then git commit`) do not. Env-var assignment
# prefixes (`GIT_AUTHOR_DATE=... git commit`) are consumed so they can't
# push `git` off the anchor. Global flags that are single tokens
# (`--no-pager`, `-c k=v`) are consumed; `-C`, `--git-dir` and `--work-tree`
# paths are captured for repo resolution (the specific alternatives come
# first so the generic flag pattern cannot swallow them). The trailing
# `(?![-\w])` keeps neighbours like `git merge-base` / `git commit-tree`
# (plumbing that moves no ref) out of the gate.
GIT_COMMIT_RE = re.compile(
    r"(?m)(?:^|[;&|(){}`])\s*(?:!\s*)*"
    r"(?:(?:if|then|else|elif|do|while|until)\s+)*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*"
    r"git("
    r"(?:\s+(?:-C\s+" + _TOKEN + r"|"
    r"--git-dir(?:=|\s+)" + _TOKEN + r"|"
    r"--work-tree(?:=|\s+)" + _TOKEN + r"|"
    r"-c\s+\S+|--?[A-Za-z][\w=./:-]*))*"
    r")"
    r"\s+(?:" + "|".join(COMMIT_SUBCOMMANDS) + r")(?![-\w])"
)

CD_PREFIX_RE = re.compile(
    r"(?m)(?:^|[;&|(){}`])\s*(?:(?:then|else|do)\s+)*cd\s+(" + _TOKEN + r")"
)
C_FLAG_RE = re.compile(r"-C\s+(" + _TOKEN + r")")
GIT_DIR_FLAG_RE = re.compile(r"--git-dir(?:=|\s+)(" + _TOKEN + r")")
WORK_TREE_FLAG_RE = re.compile(r"--work-tree(?:=|\s+)(" + _TOKEN + r")")

_SHA_RE = re.compile(r"\A[0-9a-fA-F]{7,64}\Z")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def scrub(text: object, limit: int = MAX_REASON_ECHO) -> str:
    """Flatten text bound for the reason channel: no control characters, no
    newlines, hard length cap. The reason string is privileged model-facing
    output, so anything that came off disk is treated as hostile."""
    flat = _CONTROL_RE.sub(" ", str(text))
    flat = " ".join(flat.split())
    if len(flat) > limit:
        flat = flat[:limit].rstrip() + "..."
    return flat


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    # Belt and braces: the callers already scrub, and the
                    # fixed text carries no control characters.
                    "permissionDecisionReason": _CONTROL_RE.sub(" ", reason),
                }
            }
        )
    )


def find_repo_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def resolve_target_dir(command: str, match: re.Match, cwd: Path) -> Path | None:
    """Where the git command will actually run, or None if we cannot say.

    Start from cwd and COMPOSE every `cd <path>` that runs before the git
    word, in order — `cd frontend && ... && cd .. && git commit` has to land
    where the shell would, not where the last `cd` alone points. Then follow
    the git path flags: `-C <path>` in order, then `--work-tree` (the tree
    itself) or `--git-dir` (whose parent is the tree). Variables, `~` and
    `cd -` are not resolved; rather than guessing, we return None and let
    main() fall back to the hook's own repo — fail closed, not open."""
    base = cwd
    for cd in CD_PREFIX_RE.finditer(command):
        if cd.end() > match.start():
            break
        target = unquote(cd.group(1))
        if target == "-" or target.startswith(("$", "~")):
            return None  # unresolvable hop; everything after it is a guess
        base = base / target

    flags = match.group(1) or ""
    for flag in C_FLAG_RE.finditer(flags):
        target = unquote(flag.group(1))
        if target.startswith(("$", "~")):
            return None
        base = base / target

    work_tree = [unquote(m.group(1)) for m in WORK_TREE_FLAG_RE.finditer(flags)]
    git_dir = [unquote(m.group(1)) for m in GIT_DIR_FLAG_RE.finditer(flags)]
    if work_tree:
        if work_tree[-1].startswith(("$", "~")):
            return None
        base = base / work_tree[-1]
    elif git_dir:
        if git_dir[-1].startswith(("$", "~")):
            return None
        candidate = base / git_dir[-1]
        # `--git-dir` names the .git directory; the tree we gate is its parent.
        base = candidate.parent if candidate.name == ".git" else candidate
    return base


def resolve_git_dir(root: Path) -> Path | None:
    """The repo's git directory: `<root>/.git`, or what a `.git` *file*
    points at (worktrees and submodules)."""
    dot = root / ".git"
    try:
        if dot.is_dir():
            return dot
        if not dot.is_file():
            return None
        text = dot.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text.startswith("gitdir:"):
        return None
    pointer = text[len("gitdir:") :].strip()
    if not pointer:
        return None
    candidate = Path(pointer)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate if candidate.is_dir() else None


def read_commondir(git_dir: Path) -> Path | None:
    """Linked worktrees keep HEAD locally but refs in the common dir."""
    try:
        text = (git_dir / "commondir").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = git_dir / candidate
    return candidate if candidate.is_dir() else None


def read_packed_ref(git_dir: Path, ref: str) -> str | None:
    try:
        lines = (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if not line or line[0] in "#^":
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == ref and _SHA_RE.match(parts[0]):
            return parts[0].lower()
    return None


def read_head_sha(root: Path) -> str | None:
    """The repo's current HEAD commit, read straight off the filesystem.

    No shell-out: the same code path on Windows and POSIX, no dependency on
    `git` being installed, and nothing that can hang a PreToolUse hook.
    Returns a lowercase SHA, HEAD_UNBORN when the repo has no commit yet, or
    None when HEAD cannot be determined at all — an infrastructure problem,
    which the caller treats as fail-open for the freshness check only."""
    git_dir = resolve_git_dir(root)
    if git_dir is None:
        return None
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not head:
        return None
    if not head.startswith("ref:"):
        return head.lower() if _SHA_RE.match(head) else None

    ref = head[4:].strip()
    parts = ref.split("/")
    if not ref.startswith("refs/") or any(p in ("", ".", "..") for p in parts):
        return None
    bases = [git_dir]
    common = read_commondir(git_dir)
    if common is not None:
        bases.append(common)
    for base in bases:
        try:
            loose = base.joinpath(*parts)
            if loose.is_file():
                value = loose.read_text(encoding="utf-8").strip()
                return value.lower() if _SHA_RE.match(value) else None
        except OSError:
            return None
    for base in bases:
        packed = read_packed_ref(base, ref)
        if packed is not None:
            return packed
    return HEAD_UNBORN  # branch named but never committed to


def freshness_problem(data: dict, root: Path) -> str | None:
    """One artifact waives one commit: it must name the HEAD it was reviewed
    against. Artifacts written before this binding existed carry no
    `head_sha` and fail closed with an explicit message."""
    if "head_sha" not in data:
        return (
            "review artifact has no 'head_sha' — it predates the one-commit "
            "binding and cannot be trusted for this commit"
        )
    recorded = data.get("head_sha")
    current = read_head_sha(root)
    if current is None:
        return None  # cannot read HEAD: infrastructure, so fail open here

    if current == HEAD_UNBORN:
        if recorded in (None, ""):
            return None
        return (
            "review artifact names a commit but this repo has none yet — "
            "'head_sha' must be null in a repo with no commits"
        )
    if not isinstance(recorded, str) or not _SHA_RE.match(recorded):
        return (
            "review artifact 'head_sha' must be the git commit SHA the review "
            "was run against (or null in a repo with no commits)"
        )
    if not current.startswith(recorded.lower()):
        # `recorded` is hex-validated above, so these 12 chars are safe to echo.
        return (
            f"review artifact was written against commit {scrub(recorded[:12])}, "
            f"but HEAD is now {current[:12]} — one artifact waives one commit"
        )
    return None


def artifact_problem(root: Path) -> str | None:
    """Return a human-readable problem string, or None if the artifact passes.

    Every branch reports positionally. Artifact-derived values never reach
    the returned string except a hex-validated SHA prefix — the reason
    channel is model-facing, privileged output, and a repo can be cloned."""
    artifact_path = root / ARTIFACT_REL_PATH
    if not artifact_path.is_file():
        return f"no review artifact found at {ARTIFACT_REL_PATH.as_posix()}"
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return (
            "review artifact is not valid JSON "
            f"(line {exc.lineno}, column {exc.colno})"
        )
    except (OSError, UnicodeDecodeError):
        return "review artifact could not be read as UTF-8 JSON"
    if not isinstance(data, dict):
        return "review artifact must be a JSON object"
    deliverable = data.get("deliverable")
    if not isinstance(deliverable, str) or not deliverable.strip():
        return (
            "review artifact 'deliverable' must be a non-empty string saying "
            "what was reviewed"
        )
    if data.get("mode") not in VALID_MODES:
        return "review artifact 'mode' must be one of: swarm, deep, hybrid"
    reviews = data.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        return "review artifact 'reviews' must be a non-empty array"
    for i, review in enumerate(reviews):
        if not isinstance(review, dict) or not review.get("lens"):
            return f"review #{i + 1} is malformed (needs 'lens' and 'verdict')"
        if review.get("verdict") != "PLEASED":
            return (
                f"review #{i + 1} has a verdict other than PLEASED — every "
                "verdict must be exactly PLEASED"
            )
        if review.get("blocking"):
            return f"review #{i + 1} still lists blocking findings"
    if data.get("consolidated_blocking"):
        return "review artifact 'consolidated_blocking' is not empty"
    return freshness_problem(data, root)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0  # fail-open: infrastructure problem, not a gate decision

    if not isinstance(payload, dict):
        return 0
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return 0
    match = GIT_COMMIT_RE.search(command)
    if match is None:
        return 0  # not a commit-creating git call at a command position

    cwd = payload.get("cwd")
    hook_dir = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    hook_root = find_repo_root(hook_dir)
    target = resolve_target_dir(command, match, hook_dir)
    named_root = find_repo_root(target) if target is not None else None

    # Candidate order: the repo the command names, then — as a FAIL-CLOSED
    # fallback — the hook's own repo. A path we could not resolve, or one
    # that hopped out of the tree, must not read as "not gated"; that is
    # exactly how an ordinary `cd sub && ... && cd .. && git commit` used to
    # walk out of a gated repo and take the gate with it.
    candidates: list[Path] = []
    for candidate in (named_root, hook_root):
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)

    root = None
    for candidate in candidates:
        if (candidate / OPT_IN_MARKER).is_dir():
            root = candidate
            break
    if root is None:
        return 0  # no opted-in repo in reach — the gate does not apply

    problem = artifact_problem(root)
    if problem is not None:
        scope = ""
        if named_root is None or root != named_root:
            scope = (
                f" [gate scoped to {scrub(root.as_posix(), 80)} — the command's "
                "own target could not be resolved to an opted-in repo]"
            )
        deny(
            "delegation-framework commit gate (this repo opted in via its "
            f"{OPT_IN_MARKER}/ directory): "
            + problem
            + ". Run the skeptic panel to an all-PLEASED verdict and write "
            "the review artifact (see the skeptical-review skill) before "
            "committing. The manager commits; implementers never do."
            + scope
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 — a broken gate must never brick a commit
        sys.exit(0)
