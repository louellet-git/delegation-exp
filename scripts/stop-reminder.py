#!/usr/bin/env python3
"""Stop reminder nudge: discipline, not structure.

Requires Python 3.7 or newer (`from __future__ import annotations`, `subprocess.run(capture_output=True)`).
Always exits 0; the hooks.json interpreter chain ends in `exit 0`, so a missing interpreter is silent.

At session stop, IF the repo opted in (a `.delegation/` directory at the repo
root that the HEAD commit does not carry: the commit gate's own three-state
`marker_provenance()`) AND the working tree has uncommitted changes AND there
is no review artifact the commit gate would accept, surface a one-line
reminder that a delegation slice may be in flight without its panel. Reminder
only: the commit gate is the structural check and this hook never blocks the
stop.

A marker carried by the HEAD commit arrived with the repository, and one whose
provenance cannot be determined is no evidence of consent either, so both
silence this hook as they stand the gate down; nagging every contributor is
the noise the opt-in marker exists to prevent.

"An artifact the commit gate would accept" is literally `commit-gate.py`'s own
`artifact_problem()`, so the two notions of "valid" cannot drift (a
verdict-only check stayed quiet on an all-PLEASED artifact whose `head_sha` no
longer matched HEAD, the exact state where the gate denies).

Silent in every other case (no marker, clean tree, valid artifact, or any
error running git).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

OPT_IN_MARKER = ".delegation"
GATE_PATH = Path(__file__).resolve().parent / "commit-gate.py"


def load_gate():
    """Import commit-gate.py by path (its filename is not an identifier), or None.

    Callers degrade to nagging: this hook only prints, so a false reminder
    costs a line of text while a missed one costs what the hook exists for."""
    try:
        spec = importlib.util.spec_from_file_location(
            "delegation_commit_gate", GATE_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # noqa: BLE001 - a reminder hook never breaks a stop
        return None


def marker_is_local_opt_in(root: Path, gate) -> bool:
    """Only the gate's `marker_provenance()` == MARKER_LOCAL nudges; an unusable gate nudges too."""
    if gate is None:
        return True
    try:
        return gate.marker_provenance(root) == gate.MARKER_LOCAL
    except Exception:  # noqa: BLE001 - broken gate: nudge rather than vanish
        return True


def find_repo_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        try:
            if (candidate / ".git").exists():
                return candidate
        except OSError:
            continue
    return None


def artifact_is_acceptable(root: Path, gate) -> bool:
    """The commit gate's own verdict on the artifact, `head_sha` binding to HEAD included."""
    if gate is None:
        return False  # cannot tell: nudge rather than stay silently wrong
    try:
        return gate.artifact_problem(root) is None
    except Exception:  # noqa: BLE001
        return False


def tree_is_dirty(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False  # cannot tell: stay quiet rather than nag wrongly
    return result.returncode == 0 and bool(result.stdout.strip())


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0

    roots = payload.get("workspace_roots")  # Cursor: no top-level cwd
    cwd = payload.get("cwd") or (roots[0] if isinstance(roots, list) and roots else None)
    start = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    root = find_repo_root(start)
    if root is None:
        return 0
    try:
        if not (root / OPT_IN_MARKER).is_dir():
            return 0
    except OSError:
        return 0

    gate = load_gate()
    if not marker_is_local_opt_in(root, gate):
        return 0
    if artifact_is_acceptable(root, gate):
        return 0
    if not tree_is_dirty(root):
        return 0

    print(
        json.dumps(
            {
                "systemMessage": (
                    "delegation-framework reminder (session stop): this repo "
                    "has a .delegation/ marker and uncommitted work, but no "
                    "review artifact the commit gate would accept (missing, "
                    "not all-PLEASED, or no longer bound to the current "
                    "HEAD). If a delegation slice is in flight, run the "
                    "skeptic panel before committing (/review-panel). "
                    "Reminder only: the commit gate is the structural check."
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a reminder must never break a stop
        sys.exit(0)
