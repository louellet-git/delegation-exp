#!/usr/bin/env python3
"""PreToolUse commit gate: the one structural slice of delegation-framework.

Requires Python 3.7 or newer (`from __future__ import annotations`, and the
`subprocess.run(capture_output=True)` used by the sibling reminder hook).

Contract: read the hook payload on stdin. If the tool command runs a git
subcommand that authors a new commit (`commit`, `cherry-pick`, `revert`, `am`)
and the target repo has opted in (an UNCOMMITTED `.delegation/` at its root),
require a well-formed, all-PLEASED `.delegation/review-artifact.json` bound to
the current HEAD; without one, print a JSON `permissionDecision: "deny"`.
Otherwise stay silent (or warn) and let the normal permission flow proceed.

README, "Enforcement, honestly", specifies the behaviour: gated and ungated
subcommands and flags, anchored matching, the marker table, one panel per
commit, and the five numbered limits (limit 1: a Python 3.7+ interpreter must
answer to `python3`, `python` or `py -3`, else the gate silently vanishes).
This docstring keeps the reasons the code depends on.

Scoping: plugin hooks are session-global, so this script sees tool calls in
every repo. It enforces only where `.delegation/` exists at the resolved repo
root; no marker means silent allow, and that silence is load-bearing.

Three marker states are not opt-ins. Each stands the gate down and warns on
EVERY gated command (a hook is a one-shot process, so "once" needs state that
outlives it and hides the only signal that the gate is not enforcing).
- INHERITED (HEAD carries `.delegation/<file>`, or a symlink or submodule of
  that name): it arrived with the repo, so nobody here opted in, and the
  documented escape would delete a shared tracked file for every colleague.
  Read from the HEAD tree, never the index: staging is a local act, so a
  staged marker leaves the gate ON (the deny and an allow both say so).
- UNKNOWN (HEAD's commit or trees unreadable, or HEAD unresolved in a repo
  with refs): the marker check and the artifact check have opposite hazards.
  Past the marker, failing closed stops unreviewed work; AT the marker it
  blocks a colleague who never opted in. They must not share a default.
- ORPHAN (a marker outside any git repo): there is no HEAD to bind an
  artifact to, so nothing can be enforced; silence left an armed-looking
  marker with nothing behind it.
A fresh `git init` (no refs) reads LOCAL. See `marker_provenance`,
`repo_has_history` and MARKER_MODES.

Repo resolution: the hook's cwd, adjusted by every `cd <path>` before the git
word and by `git -C`, `--work-tree` and `--git-dir` (plain paths only).
Variables and nested quoting are not resolved (limit 4), but an unresolvable
or out-of-tree result falls back to the hook's own repo: "couldn't resolve"
must never be a silent waiver.

Exit status is always 0; a deny is a successful run that prints "deny".
hooks.json wires `python3 X || python X || py -3 X || exit 0`. The chain is
safe because every way a link can fail (interpreter absent, script absent,
interpreter too old to compile it) happens before the first statement reads
stdin, and once the script reads stdin it always exits 0, so `||` never fires
on a drained pipe. A nonzero PreToolUse exit would block every Bash call in
the session.

Fail-open on infrastructure problems (unreadable stdin, malformed payload, an
unstattable repo root): a broken hook must not brick tool calls. Fail-CLOSED
on artifact problems in an opted-in repo (see `artifact_problem`).

Nothing read out of the artifact is echoed into the reason string, except a
12-char `head_sha` prefix already validated as hex (`freshness_problem`): hook
output reaches the model as privileged text, so a cloned repo could speak
through it.
See `scrub`, `deny_message`, ARTIFACT_SCHEMA and `check_artifact`.

One artifact waives one commit (`freshness_problem`). The `git reset --soft
HEAD~1` re-arm is a known residual, left open on purpose (README).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zlib
from pathlib import Path

ARTIFACT_REL_PATH = Path(".delegation") / "review-artifact.json"
OPT_IN_MARKER = ".delegation"
VALID_MODES = {"swarm", "deep", "hybrid"}

# The answers `marker_provenance()` can give. Only LOCAL enforces; INHERITED
# and UNKNOWN stand the gate down (module docstring).
MARKER_LOCAL = "local"
MARKER_INHERITED = "inherited"
MARKER_UNKNOWN = "unknown"

# Git subcommands that author a NEW commit. `merge`, `rebase` and `pull` are
# absent on purpose: they replay commits already gated when authored (README).
COMMIT_SUBCOMMANDS = (
    "commit",
    "cherry-pick",
    "revert",
    "am",
)

# Flags that back out of, skip past or simulate an operation: none can produce
# a commit, so a command carrying one is never gated. `--continue` is absent on
# purpose: it writes the commit the conflicted operation stopped short of.
# `--amend` is absent too, at a real cost: it writes a NEW commit from whatever
# is in the index, so `git add unreviewed.py && git commit --amend --no-edit`
# would launder unreviewed work, and telling a message-only amend from a
# content amend means diffing the index against HEAD on every command. The
# price of a typo fix is re-pointing `head_sha` at the new HEAD.
NON_COMMITTING_FLAGS = (
    "abort",
    "skip",
    "quit",
    "dry-run",
)

# read_head_sha() sentinel: the repo is real but carries no commit yet.
HEAD_UNBORN = "<unborn>"

# Hard cap on any text that reaches the reason channel.
MAX_REASON_ECHO = 60

# Fixed tail of the stale-binding problem string. `deny_message` keys its
# "re-point head_sha" hint off it, so message and check cannot drift apart.
HEAD_MISMATCH_MARKER = "one artifact waives one commit"

# A quoted-or-plain token (no shell separators inside a plain token).
_TOKEN = r"(?:\"[^\"]+\"|'[^']+'|[^\s;&|()`\"']+)"

# Anchored commit-creating `git`: the word must sit at a command position
# (start of line, or after ; & | ( ) { } or a backtick). Shell keywords and `!`
# at a command position are consumed, so `if git commit; then`, `{ git commit;
# }` and `! git commit` match (shapes written by accident, not evasions) while
# prose (`# then git commit`) does not. Env-var assignment prefixes are
# consumed so they cannot push `git` off the anchor, and so are single-token
# global flags (`--no-pager`, `-c k=v`); `-C`, `--git-dir` and `--work-tree`
# paths are captured for repo resolution (their alternatives come first so the
# generic flag pattern cannot swallow them). The trailing `(?![-\w])` keeps
# plumbing like `git merge-base` and `git commit-tree` out of the gate.
#
# The final lookahead drops any command carrying a non-committing flag
# (`--abort`, `--skip`, `--quit`, `--dry-run`) wherever it sits on the line. It
# scans to the next separator, treating a quoted run as ONE opaque token, so
# the flag only counts OUTSIDE quotes: `git commit -m "fix --abort handling"`
# stays gated while `git commit -m "wip" --dry-run` passes in either order. The
# two alternatives are disjoint at every position (the character class
# excludes quotes), which keeps the scan linear instead of catastrophically
# backtracking. An unterminated quote matches neither branch, so the command
# stays gated: fail-closed, as everywhere the parser gives up.
_SCAN_TO_SEPARATOR = r"(?:[^\n;&|()`'\"]|\"[^\"\n]*\"|'[^'\n]*')*"

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
    r"(?!" + _SCAN_TO_SEPARATOR
    + r"\s--(?:" + "|".join(NON_COMMITTING_FLAGS) + r")(?![-\w]))"
)

CD_PREFIX_RE = re.compile(
    r"(?m)(?:^|[;&|(){}`])\s*(?:(?:then|else|do)\s+)*cd\s+(" + _TOKEN + r")"
)
C_FLAG_RE = re.compile(r"-C\s+(" + _TOKEN + r")")
GIT_DIR_FLAG_RE = re.compile(r"--git-dir(?:=|\s+)(" + _TOKEN + r")")
WORK_TREE_FLAG_RE = re.compile(r"--work-tree(?:=|\s+)(" + _TOKEN + r")")

_SHA_RE = re.compile(r"\A[0-9a-fA-F]{7,64}\Z")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
# Same class, minus \n. Used ONLY on the fixed deny frame, whose line breaks
# are ours; every value interpolated into it went through `scrub()` first.
_CONTROL_KEEP_NEWLINE_RE = re.compile(r"[\x00-\x09\x0b-\x1f\x7f-\x9f]")

# The minimal passing artifact, printed verbatim in every deny so a blocked
# human can satisfy the gate or recognise that they do not want it. Printing it
# lowers the cost of fabricating an artifact, but a tester fabricated one in
# 172 bytes after reading a single skill file, so withholding it bought nothing
# and cost the honest user the ability to unblock themselves.
ARTIFACT_SCHEMA = (
    '{"deliverable": "<one line: what was reviewed>", '
    '"mode": "swarm|deep|hybrid", '
    '"rounds": 1, '
    '"head_sha": "<git rev-parse HEAD, or null if the repo has no commits '
    'yet>", '
    '"reviews": [{"reviewer": "<id>", "lens": "<lens>", '
    '"verdict": "PLEASED", "blocking": []}], '
    '"consolidated_blocking": []}'
)


def unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def scrub(text: object, limit: int = MAX_REASON_ECHO) -> str:
    """Flatten text bound for the reason channel: no control characters, no
    newlines, hard length cap. The reason string is privileged model-facing
    output, so anything read off disk is treated as hostile."""
    flat = _CONTROL_RE.sub(" ", str(text))
    flat = " ".join(flat.split())
    if len(flat) > limit:
        flat = flat[:limit].rstrip() + "..."
    return flat


def deny(reason: str) -> None:
    """Emit the deny decision, keeping the frame's own line breaks: this last
    pass strips every control character EXCEPT the newline. Interpolated
    values were already scrubbed in `deny_message`, so nothing off disk can
    inject structure into this channel."""
    decision = {
        "permissionDecision": "deny",
        "permissionDecisionReason": _CONTROL_KEEP_NEWLINE_RE.sub(" ", reason),
    }
    if "--copilot" not in sys.argv:  # Copilot CLI reads the top-level shape
        decision = {
            "hookSpecificOutput": {"hookEventName": "PreToolUse", **decision}
        }
    print(json.dumps(decision))


def warn(message: str) -> None:
    """Say something without touching the permission decision.

    Not `permissionDecision: "allow"`, which would auto-approve the command and
    take the choice away from the user's normal permission flow."""
    print(json.dumps({"systemMessage": _CONTROL_RE.sub(" ", message)}))


def path_is_dir(path: Path) -> bool:
    """`Path.is_dir()` that answers False rather than raising on EACCES.

    Used only while LOOKING for the opt-in marker: a directory the OS will not
    let us stat is no evidence of an opt-in, so this fails open. Everything
    AFTER a marker is found fails closed (see `artifact_problem`). Symlinks are
    followed, and the HEAD-tree side agrees on purpose (see MARKER_MODES)."""
    try:
        return path.is_dir()
    except OSError:
        return False


def path_exists(path: Path) -> bool:
    """`Path.exists()` that answers False rather than raising on EACCES."""
    try:
        return path.exists()
    except OSError:
        return False


def find_repo_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        if path_exists(candidate / ".git"):
            return candidate
    return None


def find_orphan_marker(start: Path) -> Path | None:
    """A `.delegation/` marker outside any git repo, or None.

    It looks armed, but with no HEAD to bind an artifact to the gate enforces
    nothing, so main() warns."""
    if start is None or find_repo_root(start) is not None:
        return None
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        if path_is_dir(candidate / OPT_IN_MARKER):
            return candidate
    return None


def resolve_target_dir(command: str, match: re.Match, cwd: Path) -> Path | None:
    """Where the git command will actually run, or None if we cannot say.

    Start from cwd and COMPOSE every `cd <path>` before the git word, in order
    (`cd a && cd .. && git commit` lands where the shell would), then follow
    `-C <path>`, then `--work-tree` (the tree itself) or `--git-dir` (whose
    parent is the tree). Variables, `~` and `cd -` are not resolved: return
    None and let main() fall back to the hook's own repo (fail closed)."""
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
        text = dot.read_text(encoding="utf-8-sig").strip()
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


def is_marker_own_path(rel_path: str) -> bool:
    """True for `.delegation/<file>`: the marker's own files, including the
    live artifact, but NOT anything in a subdirectory of it.

    Used on index paths by `marker_is_staged`; `marker_provenance` applies the
    same rule to HEAD tree entries. Keying on the whole subtree would treat two
    opposite intents alike: a user who armed a repo, gitignored the live
    artifact and committed the `.delegation/history/` audit trail (where the
    manager archives spent artifacts) would silently disarm their own gate."""
    prefix = OPT_IN_MARKER + "/"
    if not rel_path.startswith(prefix):
        return False
    return "/" not in rel_path[len(prefix) :]


def marker_is_staged(root: Path) -> bool:
    """True when one of the marker's own files sits in the git index.

    ADVISORY ONLY: it selects one extra deny sentence telling a user who ran
    `git add .delegation` what they did and how to undo it. Staging is a local
    act, never evidence the marker arrived from elsewhere;
    `marker_provenance()` answers that from the HEAD commit tree. The index
    must not drive the rule:
    `git add .` would disarm the gate, and `index.version=4` and
    `core.splitIndex` are not parsed here, so an index this reader cannot parse
    just omits the sentence.

    Index v2/v3 layout: b"DIRC", 4-byte version, 4-byte entry count, then per
    entry 62 bytes of metadata (plus 2 more when the v3 extended flag 0x4000 is
    set), a NUL-terminated path, and NUL padding to an 8-byte boundary."""
    try:
        git_dir = resolve_git_dir(root)
        if git_dir is None:
            return False
        data = (git_dir / "index").read_bytes()
        if len(data) < 12 or data[:4] != b"DIRC":
            return False
        version = int.from_bytes(data[4:8], "big")
        count = int.from_bytes(data[8:12], "big")
        if version not in (2, 3):
            return False  # v4 paths are prefix-compressed; do not guess
        pos = 12
        for _ in range(count):
            if pos + 62 > len(data):
                return False
            flags = int.from_bytes(data[pos + 60 : pos + 62], "big")
            path_start = pos + 62
            if version >= 3 and flags & 0x4000:
                path_start += 2
            end = data.find(b"\x00", path_start)
            if end == -1:
                return False
            entry = data[path_start:end].decode("utf-8", "replace")
            if is_marker_own_path(entry):
                return True
            record = (end + 1) - pos  # metadata + path + its NUL terminator
            pos += ((record + 7) // 8) * 8
        return False
    except Exception:  # noqa: BLE001 - unreadable index: just no extra line
        return False


def read_commondir(git_dir: Path) -> Path | None:
    """Linked worktrees keep HEAD locally but refs in the common dir."""
    try:
        text = (git_dir / "commondir").read_text(encoding="utf-8-sig").strip()
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
        lines = (git_dir / "packed-refs").read_text(
            encoding="utf-8-sig"
        ).splitlines()
    except OSError:
        return None
    for line in lines:
        if not line or line[0] in "#^":
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == ref and _SHA_RE.match(parts[0]):
            return parts[0].lower()
    return None


def repo_has_history(git_dir: Path) -> bool:
    """Does this repo hold commits even though HEAD does not name one?

    Cheap and narrow on purpose: does ANY ref exist, loose under `refs/` or in
    `packed-refs`, here or in the common dir a linked worktree shares. A fresh
    `git init` has none until its first commit. A repo whose every ref was
    deleted while its objects survive, or whose refs live only in a reftable
    (`git init --ref-format=reftable`, not parsed here), reads "no history".
    Both read the marker LOCAL and keep the gate enforcing: the safe side of
    this question, and the side a fresh `git init` needs."""
    bases = [git_dir]
    common = read_commondir(git_dir)
    if common is not None:
        bases.append(common)
    for base in bases:
        try:
            for path in (base / "refs").rglob("*"):
                if path.is_file():
                    return True
        except OSError:
            pass
        try:
            lines = (base / "packed-refs").read_text(
                encoding="utf-8-sig"
            ).splitlines()
        except OSError:
            continue
        for line in lines:
            if line and line[0] not in "#^":
                return True
    return False


def read_head_sha(root: Path) -> str | None:
    """The repo's current HEAD commit, read straight off the filesystem.

    No shell-out: one code path on Windows and POSIX, no dependency on `git`,
    nothing that can hang a PreToolUse hook. Returns a lowercase SHA,
    HEAD_UNBORN when the repo has no commit yet, or None when HEAD cannot be
    determined (infrastructure: the caller fails open for the freshness check
    only)."""
    git_dir = resolve_git_dir(root)
    if git_dir is None:
        return None
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8-sig").strip()
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
                value = loose.read_text(encoding="utf-8-sig").strip()
                return value.lower() if _SHA_RE.match(value) else None
        except OSError:
            return None
    for base in bases:
        packed = read_packed_ref(base, ref)
        if packed is not None:
            return packed
    return HEAD_UNBORN  # branch named but never committed to


# --------------------------------------------------------------------------
# Reading the HEAD commit tree, without a git binary.
#
# The provenance rule needs a fact only a COMMIT supplies: is the marker part
# of the history the repo arrived with? That takes HEAD (above), a commit
# object and two tree levels. Objects are loose (zlib files under
# objects/xx/yyyy) or packed (an .idx for lookup; an entry may be a delta
# against another). Both are implemented because loose-only leaves a
# one-command bypass: `git gc` (run automatically) packs everything, and a gate
# reading "cannot tell" after it would stand itself down in the repo its owner
# armed. Reads are bounded (object size, delta depth, .idx binary search by
# seeks, not slurping a 200 MB file) because this runs inside a 10-second hook,
# and every failure returns None, which the caller turns into "cannot tell",
# not a guess.
# --------------------------------------------------------------------------

_PACK_TYPES = {1: "commit", 2: "tree", 3: "blob", 4: "tag"}
_OFS_DELTA = 6
_REF_DELTA = 7
_TREE_MODE = b"40000"
_GITLINK_MODE = b"160000"
_SYMLINK_MODE = b"120000"

# The HEAD-tree entry modes that MATERIALISE, on checkout, what the
# working-tree check counts as the marker (`path_is_dir()` follows symlinks).
# The one place that decides it; both checks use it. A tree, a gitlink and a
# symlink each arrive with the repository; a regular file cannot, so a file
# named `.delegation` is not the marker. Reading only trees would gate every
# cloner of a repo whose `.delegation` is a committed symlink.
MARKER_MODES = (_TREE_MODE, _GITLINK_MODE, _SYMLINK_MODE)

# Bounds. A commit is a few hundred bytes and a tree a few kilobytes; the cap
# is generous only so that a legitimately huge root tree still parses.
MAX_OBJECT_BYTES = 32 * 1024 * 1024
MAX_DELTA_DEPTH = 64
_CHUNK = 65536
# How many object directories one repo may reach through alternates. Git and
# `_object_dirs()` follow them transitively, so this cap is what ends a
# circular chain; it is far above any real `--reference` fan-out.
MAX_OBJECT_DIRS = 64


def _object_dirs(git_dir: Path) -> list[Path]:
    """Every object directory this repo can read: its own, the common dir's
    (a linked worktree keeps HEAD locally but objects centrally), and any
    alternates those name (shared clones, submodule stores)."""
    bases = [git_dir]
    common = read_commondir(git_dir)
    if common is not None:
        bases.append(common)
    dirs: list[Path] = []
    for base in bases:
        objects = base / "objects"
        try:
            if objects.is_dir() and objects not in dirs:
                dirs.append(objects)
        except OSError:
            continue
    # Alternates are TRANSITIVE, as in git: `git clone --shared A B; git clone
    # --shared B C` leaves C naming B's objects, whose alternates name A's,
    # where the objects live. Following one level only made every read in C
    # fail and a local marker read UNKNOWN, standing the gate down in ordinary
    # CI and monorepo setups. `dirs` doubles as the visited set and
    # MAX_OBJECT_DIRS ends a circular chain, however the cycle is spelled.
    index = 0
    while index < len(dirs) and len(dirs) < MAX_OBJECT_DIRS:
        objects = dirs[index]
        index += 1
        try:
            text = (objects / "info" / "alternates").read_text(
                encoding="utf-8-sig"
            )
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            candidate = Path(line)
            if not candidate.is_absolute():
                candidate = objects / candidate
            try:
                # Normalised, so a cycle spelled two ways is one entry.
                candidate = candidate.resolve()
            except OSError:
                continue
            if len(dirs) >= MAX_OBJECT_DIRS:
                break
            try:
                if candidate.is_dir() and candidate not in dirs:
                    dirs.append(candidate)
            except OSError:
                continue
    return dirs


def _read_loose_object(objects_dir: Path, sha: str):
    """(kind, payload) for a loose object, or None.

    The object id is VERIFIED against the content hash, not just the header
    length: a well-formed object swapped in would get a confident answer where
    git refuses ("hash mismatch"), forging a verdict either way (hiding a
    committed marker, so the gate blocks a colleague who never opted in, or
    inventing one, so it stands down in an armed repo). A mismatch is "cannot
    tell": None, and the caller reads UNKNOWN."""
    path = objects_dir / sha[:2] / sha[2:]
    try:
        if path.stat().st_size > MAX_OBJECT_BYTES:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    try:
        data = zlib.decompressobj().decompress(raw, MAX_OBJECT_BYTES)
    except zlib.error:
        return None
    nul = data.find(b"\x00")
    if nul == -1:
        return None
    kind, _, size_text = data[:nul].decode("ascii", "replace").partition(" ")
    if kind not in ("commit", "tree", "tag", "blob") or not size_text.isdigit():
        return None
    body = data[nul + 1 :]
    if len(body) != int(size_text):
        return None
    if len(sha) == 40:
        digest = hashlib.sha1(data).hexdigest()
    elif len(sha) == 64:
        digest = hashlib.sha256(data).hexdigest()
    else:
        return None  # an object id width this reader does not hash
    return (kind, body) if digest == sha else None


def _idx_lookup(idx_path: Path, sha: str, oid_len: int):
    """Byte offset of `sha` in the matching packfile, or None.

    Binary search driven by the .idx fanout table, using seeks: a large repo
    can have a .idx of hundreds of megabytes and a PreToolUse hook must not
    read it into memory. Handles idx v2 and v1."""
    try:
        target = bytes.fromhex(sha)
    except ValueError:
        return None
    if len(target) != oid_len:
        return None
    try:
        with idx_path.open("rb") as fh:
            magic = fh.read(8)
            if len(magic) < 8:
                return None
            if magic[:4] == b"\xfftOc":
                if int.from_bytes(magic[4:8], "big") != 2:
                    return None
                version, fanout = 2, 8
            else:
                if oid_len != 20:  # v1 predates any non-SHA-1 object format
                    return None
                version, fanout = 1, 0
            first = target[0]
            if first == 0:
                lo = 0
            else:
                fh.seek(fanout + (first - 1) * 4)
                lo = int.from_bytes(fh.read(4), "big")
            fh.seek(fanout + first * 4)
            hi = int.from_bytes(fh.read(4), "big")
            fh.seek(fanout + 255 * 4)
            total = int.from_bytes(fh.read(4), "big")
            if not 0 <= lo <= hi <= total:
                return None
            table = fanout + 256 * 4
            # v2: names[], then crc32[], then 4-byte offsets[], then the
            # 8-byte offsets for entries whose 4-byte slot has bit 31 set.
            # v1: one 24-byte record per object, offset first, then the name.
            offsets = table + total * oid_len + total * 4
            large = offsets + total * 4
            while lo < hi:
                mid = (lo + hi) // 2
                if version == 1:
                    fh.seek(table + mid * 24 + 4)
                else:
                    fh.seek(table + mid * oid_len)
                name = fh.read(oid_len)
                if len(name) != oid_len:
                    return None
                if name == target:
                    if version == 1:
                        fh.seek(table + mid * 24)
                        return int.from_bytes(fh.read(4), "big")
                    fh.seek(offsets + mid * 4)
                    packed = int.from_bytes(fh.read(4), "big")
                    if not packed & 0x80000000:
                        return packed
                    fh.seek(large + (packed & 0x7FFFFFFF) * 8)
                    return int.from_bytes(fh.read(8), "big")
                if name < target:
                    lo = mid + 1
                else:
                    hi = mid
    except OSError:
        return None
    return None


def _inflate_at(fh, start: int, size: int):
    """Exactly `size` inflated bytes starting at `start`, or None.

    Streamed in chunks with a max_length bound, so a corrupt or hostile entry
    claiming a small size cannot expand into memory unchecked. The declared
    size must also be where the stream actually ENDS: returning the first
    `size` bytes of an under-declaring entry yields a valid-looking TRUNCATED
    object (a cut-off `.delegation` tree entry reads LOCAL; one entry longer
    flips it to INHERITED). The header describes the stream, or the entry is
    not readable."""
    if size > MAX_OBJECT_BYTES:
        return None
    try:
        fh.seek(start)
        dec = zlib.decompressobj()
        out = bytearray()
        while len(out) < size:
            chunk = fh.read(_CHUNK)
            if not chunk:
                return None
            out += dec.decompress(chunk, size - len(out))
            if dec.eof and len(out) < size:
                return None
        # Drain what is left a byte at a time: any further inflated byte means
        # the entry holds more than declared. `max_length` can stop zlib at
        # `size` before it sees the end-of-stream marker, so eof is not yet
        # decisive.
        while not dec.eof:
            tail = dec.unconsumed_tail
            if not tail:
                tail = fh.read(_CHUNK)
                if not tail:
                    return None
            if dec.decompress(tail, 1):
                return None
    except (OSError, zlib.error):
        return None
    return bytes(out)


def _apply_delta(base: bytes, delta: bytes):
    """Git's delta encoding: copy-from-base and insert-literal instructions."""
    pos = 0

    def varint():
        nonlocal pos
        value = 0
        shift = 0
        while True:
            if pos >= len(delta) or shift > 63:
                return None
            byte = delta[pos]
            pos += 1
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value
            shift += 7

    src = varint()
    dst = varint()
    if src is None or dst is None or src != len(base):
        return None
    if dst > MAX_OBJECT_BYTES:
        return None
    out = bytearray()
    while pos < len(delta):
        op = delta[pos]
        pos += 1
        if op & 0x80:
            offset = 0
            size = 0
            for i in range(4):
                if op & (1 << i):
                    if pos >= len(delta):
                        return None
                    offset |= delta[pos] << (8 * i)
                    pos += 1
            for i in range(3):
                if op & (1 << (4 + i)):
                    if pos >= len(delta):
                        return None
                    size |= delta[pos] << (8 * i)
                    pos += 1
            if size == 0:
                size = 0x10000
            if offset + size > len(base):
                return None
            out += base[offset : offset + size]
        elif op:
            if pos + op > len(delta):
                return None
            out += delta[pos : pos + op]
            pos += op
        else:
            return None  # instruction 0 is reserved
        if len(out) > dst:
            return None
    return bytes(out) if len(out) == dst else None


class ObjectStore:
    """Just enough of git's object database to read a commit and two trees.

    Every method answers None rather than raising or guessing; the caller
    turns None into "provenance unknown", which stands the gate down."""

    def __init__(self, git_dir: Path, oid_len: int) -> None:
        self.dirs = _object_dirs(git_dir)
        self.oid_len = oid_len
        self._packs: list[tuple[Path, Path]] | None = None

    def packs(self) -> list[tuple[Path, Path]]:
        if self._packs is None:
            found: list[tuple[Path, Path]] = []
            for objects in self.dirs:
                try:
                    names = sorted((objects / "pack").glob("*.idx"))
                except OSError:
                    continue
                for idx in names:
                    pack = idx.with_suffix(".pack")
                    try:
                        if pack.is_file():
                            found.append((idx, pack))
                    except OSError:
                        continue
            self._packs = found
        return self._packs

    def get(self, sha: str, depth: int = 0):
        """(kind, payload) for an object id, or None."""
        if depth > MAX_DELTA_DEPTH or len(sha) != self.oid_len * 2:
            return None
        if not _SHA_RE.match(sha):
            return None
        sha = sha.lower()
        for objects in self.dirs:
            found = _read_loose_object(objects, sha)
            if found is not None:
                return found
        for idx, pack in self.packs():
            offset = _idx_lookup(idx, sha, self.oid_len)
            if offset is None:
                continue
            try:
                with pack.open("rb") as fh:
                    return self._entry(fh, offset, depth)
            except OSError:
                return None
        return None

    def _entry(self, fh, offset: int, depth: int):
        """One packfile entry, resolving delta chains as it goes."""
        if depth > MAX_DELTA_DEPTH or offset < 0:
            return None
        try:
            fh.seek(offset)
        except OSError:
            return None
        header = fh.read(32 + self.oid_len)
        if len(header) < 2:
            return None
        byte = header[0]
        obj_type = (byte >> 4) & 0x07
        size = byte & 0x0F
        shift = 4
        i = 1
        while byte & 0x80:
            if i >= len(header) or shift > 63:
                return None
            byte = header[i]
            i += 1
            size |= (byte & 0x7F) << shift
            shift += 7
        base_offset = None
        base_sha = None
        if obj_type == _OFS_DELTA:
            if i >= len(header):
                return None
            byte = header[i]
            i += 1
            rel = byte & 0x7F
            while byte & 0x80:
                if i >= len(header) or rel > offset:
                    return None
                byte = header[i]
                i += 1
                rel = ((rel + 1) << 7) | (byte & 0x7F)
            base_offset = offset - rel
        elif obj_type == _REF_DELTA:
            if i + self.oid_len > len(header):
                return None
            base_sha = header[i : i + self.oid_len].hex()
            i += self.oid_len
        elif obj_type not in _PACK_TYPES:
            return None
        data = _inflate_at(fh, offset + i, size)
        if data is None:
            return None
        if base_offset is None and base_sha is None:
            return _PACK_TYPES[obj_type], data
        # A delta borrows its type from the base it patches.
        if base_offset is not None:
            base = self._entry(fh, base_offset, depth + 1)
        else:
            base = self.get(base_sha, depth + 1)
        if base is None:
            return None
        patched = _apply_delta(base[1], data)
        return None if patched is None else (base[0], patched)


def tree_entries(data: bytes, oid_len: int):
    """[(mode, name, sha)] for a tree object, or None if it does not parse."""
    entries = []
    pos = 0
    while pos < len(data):
        space = data.find(b" ", pos)
        if space == -1:
            return None
        nul = data.find(b"\x00", space)
        if nul == -1 or nul + 1 + oid_len > len(data):
            return None
        entries.append(
            (
                data[pos:space],
                data[space + 1 : nul],
                data[nul + 1 : nul + 1 + oid_len].hex(),
            )
        )
        pos = nul + 1 + oid_len
    return entries


def _commit_root_tree(store: ObjectStore, sha: str):
    """The root tree id of the commit `sha` names, or None.

    Peels annotated tags, in case HEAD was detached onto one."""
    for _ in range(4):
        obj = store.get(sha)
        if obj is None:
            return None
        kind, body = obj
        head_line = body.split(b"\n", 1)[0]
        if kind == "tag":
            if not head_line.startswith(b"object "):
                return None
            sha = head_line[len(b"object ") :].strip().decode("ascii", "replace")
            continue
        if kind != "commit" or not head_line.startswith(b"tree "):
            return None
        return head_line[len(b"tree ") :].strip().decode("ascii", "replace")
    return None


def marker_provenance(root: Path) -> str:
    """Where this repo's `.delegation/` marker came from: MARKER_LOCAL,
    MARKER_INHERITED or MARKER_UNKNOWN.

    INHERITED: the HEAD commit carries one of the marker's own files
    (`.delegation/<file>`, including the live artifact), or `.delegation` is a
    gitlink or symlink there (checkout materialises a path the working-tree
    check answers True for; see MARKER_MODES). Only that means the marker
    arrived from somewhere other than the person sitting here.

    Not the index: a staged marker is a local act, and `git add .` on an
    unignored marker must not disarm the gate. Not the whole `.delegation/`
    subtree either (see `is_marker_own_path`): a committed
    `.delegation/history/` is an audit trail and leaves the gate armed.

    UNKNOWN: the HEAD commit resolves but the objects behind it cannot be read
    or parsed, or HEAD does not resolve in a repo that HAS refs (orphan
    branch): provenance is unknowable there. LOCAL: the repo holds no refs at
    all (a fresh `git init`), so nothing can have arrived inside a commit."""
    try:
        git_dir = resolve_git_dir(root)
        if git_dir is None:
            return MARKER_LOCAL
        head = read_head_sha(root)
        if head is None or head == HEAD_UNBORN or len(head) not in (40, 64):
            # No resolvable HEAD COMMIT. `git checkout --orphan fresh` leaves
            # HEAD naming a missing ref, yet git DOES author commits from that
            # state (rc=0), so with refs on disk provenance is unknowable:
            # stand down and say so. With no refs at all (a fresh `git init`)
            # nothing can have arrived inside a commit, so LOCAL is right and
            # the gate keeps enforcing. See `repo_has_history`.
            return MARKER_UNKNOWN if repo_has_history(git_dir) else MARKER_LOCAL
        store = ObjectStore(git_dir, len(head) // 2)
        tree_sha = _commit_root_tree(store, head)
        if tree_sha is None:
            return MARKER_UNKNOWN
        root_tree = store.get(tree_sha)
        if root_tree is None or root_tree[0] != "tree":
            return MARKER_UNKNOWN
        entries = tree_entries(root_tree[1], store.oid_len)
        if entries is None:
            return MARKER_UNKNOWN
        wanted = OPT_IN_MARKER.encode("utf-8")
        marker = next((e for e in entries if e[1] == wanted), None)
        if marker is None:
            return MARKER_LOCAL  # HEAD does not carry the marker at all
        mode, _, sha = marker
        if mode not in MARKER_MODES:
            return MARKER_LOCAL  # a FILE named .delegation; not this marker
        if mode != _TREE_MODE:
            # A submodule or a symlink: checkout materialises a `.delegation`
            # the working-tree check answers True for, with nobody here opting
            # in. Same answer as a committed directory. See MARKER_MODES.
            return MARKER_INHERITED
        subtree = store.get(sha)
        if subtree is None or subtree[0] != "tree":
            return MARKER_UNKNOWN
        children = tree_entries(subtree[1], store.oid_len)
        if children is None:
            return MARKER_UNKNOWN
        for child_mode, _, _ in children:
            if child_mode != _TREE_MODE:
                return MARKER_INHERITED  # a file of the marker's own
        return MARKER_LOCAL  # only subdirectories, e.g. history/
    except Exception:  # noqa: BLE001 - cannot tell is a real answer here
        return MARKER_UNKNOWN


def head_tracks_marker_contents(root: Path) -> bool:
    """True when the HEAD commit carries a `.delegation/` TREE, i.e. tracked
    files live under a marker that reads as a local opt-in (a committed
    `.delegation/history/` archive; see `is_marker_own_path`).

    ADVISORY ONLY, like `marker_is_staged`: it qualifies one sentence of the
    deny message. Escape hatch 2 says "delete the `.delegation/` directory";
    where those files are tracked, that destroys a committed review archive,
    and the deletion commit is itself ungated because deleting the marker
    disarms the gate first. A stranger should be told before, not after."""
    try:
        git_dir = resolve_git_dir(root)
        if git_dir is None:
            return False
        head = read_head_sha(root)
        if head is None or head == HEAD_UNBORN or len(head) not in (40, 64):
            return False
        store = ObjectStore(git_dir, len(head) // 2)
        tree_sha = _commit_root_tree(store, head)
        if tree_sha is None:
            return False
        root_tree = store.get(tree_sha)
        if root_tree is None or root_tree[0] != "tree":
            return False
        entries = tree_entries(root_tree[1], store.oid_len)
        if entries is None:
            return False
        wanted = OPT_IN_MARKER.encode("utf-8")
        return any(name == wanted and mode == _TREE_MODE
                   for mode, name, _ in entries)
    except Exception:  # noqa: BLE001 - advisory: no sentence, no harm
        return False


def freshness_problem(data: dict, root: Path) -> str | None:
    """One artifact waives one commit: it must name the HEAD it was reviewed
    against. The failure this gate walls off is forgetting, so staleness is
    checked structurally, not left to the "archive it afterwards" prose step.
    An artifact with no `head_sha` fails closed with an explicit message."""
    if "head_sha" not in data:
        return (
            "the review artifact has no 'head_sha', so it predates the "
            "one-commit binding and cannot be trusted for this commit"
        )
    recorded = data.get("head_sha")
    current = read_head_sha(root)
    if current is None:
        return None  # cannot read HEAD: infrastructure, so fail open here

    if current == HEAD_UNBORN:
        if recorded in (None, ""):
            return None
        return (
            "the review artifact names a commit but this repo has none yet; "
            "'head_sha' must be null in a repo with no commits"
        )
    if not isinstance(recorded, str) or not _SHA_RE.match(recorded):
        return (
            "the review artifact 'head_sha' must be the git commit SHA the "
            "review was run against (or null in a repo with no commits)"
        )
    if not current.startswith(recorded.lower()):
        # `recorded` is hex-validated above, so these 12 chars are safe to echo.
        return (
            f"the review artifact was written against commit "
            f"{scrub(recorded[:12])}, but HEAD is now {current[:12]}; "
            + HEAD_MISMATCH_MARKER
        )
    return None


def check_artifact(root: Path) -> str | None:
    """The artifact checks themselves. Callers use `artifact_problem`, which
    wraps this so that no exception can escape into a silent allow.

    Every branch reports positionally: the only artifact-derived value in a
    returned string is a hex-validated SHA prefix (module docstring)."""
    artifact_path = root / ARTIFACT_REL_PATH
    if not artifact_path.is_file():
        return f"no review artifact found at {ARTIFACT_REL_PATH.as_posix()}"
    try:
        # utf-8-sig, not utf-8: PowerShell and older Notepad write a UTF-8 BOM
        # by default, which makes a valid artifact fail as "not valid JSON
        # (line 1, column 1)". utf-8-sig reads plain UTF-8 unchanged.
        data = json.loads(artifact_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return (
            "the review artifact is not valid JSON "
            f"(line {exc.lineno}, column {exc.colno})"
        )
    except (OSError, UnicodeDecodeError):
        return "the review artifact could not be read as UTF-8 JSON"
    if not isinstance(data, dict):
        return "the review artifact must be a JSON object"
    deliverable = data.get("deliverable")
    if not isinstance(deliverable, str) or not deliverable.strip():
        return (
            "the review artifact 'deliverable' must be a non-empty string "
            "saying what was reviewed"
        )
    if data.get("mode") not in VALID_MODES:
        return "the review artifact 'mode' must be one of: swarm, deep, hybrid"
    reviews = data.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        return "the review artifact 'reviews' must be a non-empty array"
    for i, review in enumerate(reviews):
        if not isinstance(review, dict) or not review.get("lens"):
            return f"review #{i + 1} is malformed (needs 'lens' and 'verdict')"
        if review.get("verdict") != "PLEASED":
            return (
                f"review #{i + 1} has a verdict other than PLEASED; every "
                "verdict must be exactly PLEASED"
            )
        if review.get("blocking"):
            return f"review #{i + 1} still lists blocking findings"
    if data.get("consolidated_blocking"):
        return "the review artifact 'consolidated_blocking' is not empty"
    return freshness_problem(data, root)


def artifact_problem(root: Path) -> str | None:
    """A human-readable problem string, or None if the artifact passes.

    THE FAIL-CLOSED BOUNDARY. The repo has opted in, so an exception here must
    never become a silent allow by escaping into the top-level
    `except Exception: sys.exit(0)`. Two real ones did: a `RecursionError` from
    an artifact of 100k nested brackets (not an OSError, so the JSON handler
    missed it) and a `PermissionError` from an unreadable `.delegation/`
    (`Path.is_file()` does not swallow EACCES). Anything unforeseen gets the
    same treatment."""
    try:
        return check_artifact(root)
    except RecursionError:
        return (
            "the review artifact is nested too deeply to parse safely, so it "
            "cannot be verified"
        )
    except PermissionError:
        return (
            f"the review artifact at {ARTIFACT_REL_PATH.as_posix()} could not "
            "be read (permission denied)"
        )
    except Exception:  # noqa: BLE001 - unverifiable is never allowed
        return (
            "the review artifact could not be checked (unexpected error while "
            "reading it)"
        )


def deny_message(problem: str, scope: str = "", note: str = "",
                 tracked_contents: bool = False) -> str:
    """The whole user experience of the one structural feature: what is wrong,
    how to satisfy the gate, how to get rid of it, in that order. All three
    escape hatches are listed in priority order and the artifact schema is
    inlined so self-rescue needs no skill file.

    The frame is assembled as LINES because it is fixed text of ours, not what
    `scrub()` defends against: flattening the whole string turned a numbered
    list and an inline schema into one unselectable paragraph. The three
    INTERPOLATED values are scrubbed at the point of interpolation: `problem`
    (artifact-derived fragments in it are already positional or hex-validated),
    `scope` and `note`. Scrubbing kills newlines, so no value can add a line to
    this frame or forge a numbered hatch.

    `tracked_contents` is a fact about the HEAD tree, not text: it qualifies
    escape hatch 2 where following it would delete tracked files. See
    `head_tracks_marker_contents`."""
    lines = [
        "delegation-framework commit gate: BLOCKED.",
        "Problem: " + scrub(problem, 400) + ".",
        # States what the gate can check, not a claim about consent: "opted
        # in" greeted a colleague armed by a single `git pull` as if they had
        # chosen this. The gated commands are listed completely: `--amend` is
        # the deny a real user is likeliest to meet, and omitting it read like
        # a bug.
        f"Why: this repo has a {OPT_IN_MARKER}/ directory at its root that "
        "the HEAD commit does not carry, so every git command that authors a "
        "new commit (commit, cherry-pick, revert, am, including --amend and "
        "--continue) needs a review artifact that is all-PLEASED and bound to "
        "the current HEAD.",
    ]
    if HEAD_MISMATCH_MARKER in problem:
        # The cheap fix, said where only the binding is stale. After an
        # `--amend` deny, or any deny following a landed commit, it takes
        # seconds; sending a beginner to "run the skeptic panel" for a typo in
        # a commit message made the gate feel broken.
        lines.append(
            "Fastest fix here: only the artifact's binding is stale, not the "
            "review. Re-point 'head_sha' at `git rev-parse HEAD` and commit "
            "again. A fresh panel is needed only if WHAT you are committing "
            "changed since the review, which is the case `--amend` after "
            "`git add` creates."
        )
    if note:
        lines.append(scrub(note, 400))
    lines += [
        "Three ways forward, in priority order.",
        "(1) WRITE THE ARTIFACT: run the skeptic panel to an all-PLEASED "
        f"verdict, then save this shape at {ARTIFACT_REL_PATH.as_posix()} :",
        ARTIFACT_SCHEMA,
        "    Every verdict must be exactly PLEASED, every 'blocking' list "
        "empty, and 'head_sha' must match the current HEAD (git rev-parse "
        "HEAD). One artifact waives one commit.",
        f"(2) OPT THIS REPO OUT: delete the {OPT_IN_MARKER}/ directory at the "
        "repo root; this gate and both reminder hooks go silent in this repo "
        "immediately."
        + (
            f" CAREFUL: the HEAD commit carries files under {OPT_IN_MARKER}/ "
            "here (a committed review archive), so deleting the directory "
            "deletes TRACKED files somebody committed on purpose, and the "
            "deletion commit is itself ungated because the gate goes silent "
            "the moment the marker is gone. If that archive is not yours to "
            "delete, use (3)." if tracked_contents else ""
        ),
        "(3) TURN IT OFF EVERYWHERE: disable the delegation-framework hooks "
        "(/hooks) or remove the plugin.",
    ]
    if scope:
        lines.append(scrub(scope, 200))
    return "\n".join(lines)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0  # fail-open: infrastructure problem, not a gate decision

    if not isinstance(payload, dict):
        return 0
    if str(payload.get("tool_name")).lower() not in ("bash", "powershell"):
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

    # Candidate order: the repo the command names, then, FAIL-CLOSED, the
    # hook's own repo. A path we could not resolve, or one that hopped out of
    # the tree, must not read as "not gated": an ordinary `cd sub && ... && cd
    # .. && git commit` would walk out of a gated repo and take the gate with
    # it.
    candidates: list[Path] = []
    for candidate in (named_root, hook_root):
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)

    root = None
    for candidate in candidates:
        if path_is_dir(candidate / OPT_IN_MARKER):
            root = candidate
            break
    if root is None:
        # No opted-in repo in reach, so the gate does not apply. Say one word
        # only in the case where a marker exists but cannot possibly work.
        orphan = None
        for start in (target, hook_dir):
            if start is not None:
                orphan = find_orphan_marker(start)
                if orphan is not None:
                    break
        if orphan is not None:
            warn(
                "delegation-framework: found a "
                f"{OPT_IN_MARKER}/ marker at {scrub(orphan.as_posix(), 120)} "
                "but that directory is not inside a git repository, so there "
                "is no HEAD to bind a review artifact to and the commit gate "
                "is enforcing nothing. Run `git init` (then re-run the "
                f"delegation loop), or delete the {OPT_IN_MARKER}/ directory."
            )
        return 0

    # Where the marker CAME FROM decides whether it is an opt-in at all. Both
    # non-local answers stand the gate down and say so on every gated command
    # (module docstring: a one-shot hook cannot say it once without state that
    # outlives the session).
    provenance = marker_provenance(root)
    if provenance == MARKER_INHERITED:
        warn(
            "delegation-framework: this repo's "
            f"{OPT_IN_MARKER}/ marker is part of the HEAD commit, so it "
            "arrived with the repository rather than from anyone in this "
            "working copy opting in. The commit gate is NOT enforcing here. "
            f"To arm it deliberately: `git rm -r --cached {OPT_IN_MARKER}`, "
            f"add `{OPT_IN_MARKER}/` to .gitignore, and commit that removal "
            "(the marker counts as inherited for as long as HEAD carries it, "
            "and that un-arming commit is itself ungated). The opt-in then "
            "stays local to whoever wants it."
        )
        return 0
    if provenance == MARKER_UNKNOWN:
        warn(
            "delegation-framework: this repo has a "
            f"{OPT_IN_MARKER}/ marker, but the gate could NOT DETERMINE "
            "whether it was committed (so it arrived with the repository) or "
            "created locally: the HEAD commit tree could not be read. "
            "Provenance unknown, so the commit gate is standing down here "
            "rather than blocking someone who may never have opted in. "
            "What failed is reading this repo's own object store (a partial "
            "or filtered clone, a corrupt object, an orphan branch, or an "
            "object format this reader does not understand); `git fsck "
            "--connectivity-only` is the question worth asking next, and "
            "enforcement returns by itself once the HEAD commit tree can be "
            "read."
        )
        return 0

    problem = artifact_problem(root)
    if problem is not None:
        scope = ""
        if named_root is None or root != named_root:
            scope = (
                f"[gate scoped to {scrub(root.as_posix(), 80)}: the command's "
                "own target could not be resolved to an opted-in repo]"
            )
        note = ""
        if marker_is_staged(root):
            # They ran `git add .delegation`. Staging is a local act and
            # changes nothing; say what they did and how to undo it.
            note = (
                f"Note: {OPT_IN_MARKER}/ is STAGED here but not committed. "
                "Staging is a local act, not something that arrived with the "
                "repository, so it does not disarm the gate. If you did not "
                f"mean to stage it: `git restore --staged {OPT_IN_MARKER}`."
            )
        deny(deny_message(problem, scope, note,
                          head_tracks_marker_contents(root)))
        return 0

    # THE COMMIT THAT DISARMS THE GATE. With a valid artifact and a staged
    # marker the commit lands, the marker enters HEAD, and from then on it
    # reads INHERITED here and in every clone, so the gate stands down for
    # everyone, with that artifact shipped alongside it. Still an ALLOW,
    # because this may be exactly what the user meant; but never in silence.
    if marker_is_staged(root):
        warn(
            f"delegation-framework: {OPT_IN_MARKER}/ is STAGED, so this "
            "commit will carry the marker into the HEAD commit. From then on "
            "it counts as having arrived WITH the repository rather than as "
            "anyone opting in, and the commit gate stands down here and in "
            "every clone, with this review artifact shipped alongside it. To "
            f"keep the opt-in local: `git restore --staged {OPT_IN_MARKER}` "
            f"and add `{OPT_IN_MARKER}/` to .gitignore."
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a broken gate must never brick a commit
        # Last resort only: `artifact_problem` converts every artifact
        # exception into a deny, because a silent allow here is
        # indistinguishable from "the gate is off".
        sys.exit(0)
