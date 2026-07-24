#!/usr/bin/env python3
"""PreToolUse commit gate — the ONE structural slice of delegation-framework.

Reads the PreToolUse hook payload on stdin. If the tool command *runs*
`git commit` (anchored matching — a command that merely mentions the words,
like `echo please run git commit later` or `grep 'git commit' docs/`, does
NOT trigger), and the target repo has **opted in** by having a
`.delegation/` directory at its root, the gate requires a well-formed,
all-PLEASED review artifact at `.delegation/review-artifact.json`. Without
one it emits a JSON `permissionDecision: "deny"`; otherwise it stays silent
and the normal permission flow proceeds.

Scoping (the opt-in marker): plugin hooks are SESSION-GLOBAL — this script
is consulted for tool calls in every repo the session touches. To avoid
walling off repos that never use the framework, the gate enforces only
where `.delegation/` exists at the resolved repo root (the `delegating`
skill / `/delegate` creates it when a loop starts). No marker → silent
allow.

Repo resolution: from the hook's cwd, adjusted minimally when the command
itself says otherwise — a leading `cd <path> &&`/`;` prefix and/or
`git -C <path>` flags are followed (plain paths only). Paths built from
variables or nested quoting are NOT resolved and can make the gate consult
the wrong repo silently — a stated residual (limit 4).

Design choices, stated honestly:

- The script always exits 0 and communicates via hook JSON output. This
  makes the `python || python3` fallback chain in hooks.json safe: a block
  is a successful run that outputs "deny", never a nonzero exit that would
  trigger the fallback interpreter.
- Fail-open on infrastructure problems (unreadable stdin, malformed hook
  payload, unresolvable paths): a broken hook must not brick tool calls.
  Fail-CLOSED on artifact problems in an opted-in repo (missing, malformed,
  not all-PLEASED): that is the gate doing its job.
- FIVE honest limits (see README "Enforcement, honestly"):
  (1) fires only where these hooks are installed and enabled, and only if
      `python`/`python3` is on PATH — otherwise it silently vanishes;
  (2) verifies the artifact exists / is well-formed (including a non-empty
      `deliverable`) / is all-PLEASED — not that the review was rigorous; a
      PLEASED artifact can be fabricated (wall against forgetting, not bad
      faith);
  (3) local working tree only;
  (4) only commits crossing the hooked tool matcher, and only as the
      anchored regex + minimal cd/-C parsing understand them — aliases,
      subprocesses/heredocs (`bash -c "git commit"`), IDE commits bypass
      it, and variable/nested-quoted paths can mis-resolve the repo
      silently;
  (5) OVER-reach: the hook is session-global; it is scoped by the
      `.delegation/` opt-in marker and anchored matching, but exotic
      compound commands can still false-positive. Escape hatches: write
      the artifact, remove `.delegation/`, or disable the hook.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ARTIFACT_REL_PATH = Path(".delegation") / "review-artifact.json"
OPT_IN_MARKER = ".delegation"
VALID_MODES = {"swarm", "deep", "hybrid"}

# A quoted-or-plain token (no shell separators inside a plain token).
_TOKEN = r"(?:\"[^\"]+\"|'[^']+'|[^\s;&|()`\"']+)"

# Anchored `git commit`: the `git` word must sit at a command position —
# start of string/line or right after ; & | ( or a backtick — so prose
# mentions (echo/grep/log messages) never match. Env-var assignment
# prefixes (`GIT_AUTHOR_DATE=... git commit`) are consumed so they can't
# push `git` off the anchor. Global flags that are single tokens
# (`--no-pager`, `-c k=v`) and `-C <path>` are consumed; `-C` paths are
# captured for repo resolution.
GIT_COMMIT_RE = re.compile(
    r"(?m)(?:^|[;&|(`])\s*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*"
    r"git((?:\s+(?:-C\s+" + _TOKEN + r"|-c\s+\S+|--?[A-Za-z][\w=./:-]*))*)"
    r"\s+commit\b"
)

CD_PREFIX_RE = re.compile(r"(?m)(?:^|[;&|(`])\s*cd\s+(" + _TOKEN + r")")
C_FLAG_RE = re.compile(r"-C\s+(" + _TOKEN + r")")


def unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
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


def resolve_target_dir(command: str, match: re.Match, cwd: Path) -> Path:
    """Start from cwd; apply the last `cd <path>` before the git command,
    then any `git -C <path>` flags in order. Minimal by design — variables
    and nested quoting are not resolved (stated residual, limit 4)."""
    base = cwd
    last_cd = None
    for cd in CD_PREFIX_RE.finditer(command):
        if cd.end() <= match.start():
            last_cd = cd
    if last_cd is not None:
        base = base / unquote(last_cd.group(1))
    for flag in C_FLAG_RE.finditer(match.group(1) or ""):
        base = base / unquote(flag.group(1))
    return base


def artifact_problem(artifact_path: Path) -> str | None:
    """Return a human-readable problem string, or None if the artifact passes."""
    if not artifact_path.is_file():
        return f"no review artifact found at {ARTIFACT_REL_PATH.as_posix()}"
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return f"review artifact is not valid JSON ({exc})"
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
                f"review #{i + 1} (lens '{review.get('lens')}') has verdict "
                f"'{review.get('verdict')}' — every verdict must be PLEASED"
            )
        if review.get("blocking"):
            return (
                f"review #{i + 1} (lens '{review.get('lens')}') still lists "
                "blocking findings"
            )
    if data.get("consolidated_blocking"):
        return "review artifact 'consolidated_blocking' is not empty"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
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
        return 0  # not a git commit at a command position — stay out of the way

    cwd = payload.get("cwd")
    start = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    root = find_repo_root(resolve_target_dir(command, match, start))
    if root is None:
        return 0  # not inside a git repo; nothing coherent to gate
    if not (root / OPT_IN_MARKER).is_dir():
        return 0  # repo has not opted in — the gate does not reach it

    problem = artifact_problem(root / ARTIFACT_REL_PATH)
    if problem is not None:
        deny(
            "delegation-framework commit gate (this repo opted in via its "
            f"{OPT_IN_MARKER}/ directory): "
            + problem
            + ". Run the skeptic panel to an all-PLEASED verdict and write "
            "the review artifact (see the skeptical-review skill) before "
            "committing. The manager commits; implementers never do."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
