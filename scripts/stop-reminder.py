#!/usr/bin/env python3
"""Stop reminder nudge: discipline, not structure.

Requires Python 3.7 or newer (`from __future__ import annotations`,
`subprocess.run(capture_output=True)`).

At session stop, IF the current repo has opted in (an untracked
`.delegation/` directory at the repo root, the same marker the commit gate
uses) AND the working tree has uncommitted changes AND there is no review
artifact the commit gate would accept, surface a one-line reminder that a
delegation slice may be in flight without its panel. Reminder only: the
commit gate is the structural check and this hook never blocks the stop.

"An artifact the commit gate would accept" is not re-implemented here, it is
literally `commit-gate.py`'s own `artifact_problem()`. This file used to
check verdicts only, which meant it stayed quiet in the exact state where
the gate denies: an all-PLEASED artifact whose `head_sha` no longer matches
HEAD. The user ended the session believing they were covered and met the
deny on their next commit. The two notions of "valid" must not drift, so
there is now only one of them.

Silent in every other case (no marker, a marker that is tracked in git and
therefore not an opt-in, clean tree, valid artifact, or any error running
git). Always exits 0, and hooks.json invokes it as a single `python3 ... ||
exit 0` so that a missing interpreter or script degrades to silence.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

OPT_IN_MARKER = ".delegation"
ARTIFACT_REL_PATH = Path(".delegation") / "review-artifact.json"
GATE_PATH = Path(__file__).resolve().parent / "commit-gate.py"


def load_gate():
    """Import commit-gate.py by path (its filename is not an identifier).

    Returns the module, or None if it cannot be loaded. Callers degrade to
    nagging: this hook only ever prints, so a false reminder costs a line of
    text while a missed one costs the thing this hook exists for."""
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
    """Exactly the commit gate's own verdict on the artifact, including the
    `head_sha` binding to current HEAD."""
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
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0

    cwd = payload.get("cwd")
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
    # A marker tracked in git arrived with the clone; nobody in this working
    # copy opted in, so nagging every contributor would be the noise the
    # opt-in marker exists to prevent. Same rule as the commit gate.
    if gate is not None and gate.marker_is_tracked(root):
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
