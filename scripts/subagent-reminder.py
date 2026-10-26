#!/usr/bin/env python3
"""SubagentStop reminder nudge: discipline, not structure.

Requires Python 3.7 or newer (`from __future__ import annotations`).
Always exits 0; the hooks.json interpreter chain ends in `exit 0`, so a missing interpreter is silent.

When a subagent finishes IN A REPO THAT HAS OPTED IN to the framework (a
`.delegation/` directory at the repo root that the HEAD commit does not carry,
the commit gate's own three-state `marker_provenance()`; plugin hooks are
session-global, and a nudge in every unrelated session is noise), surface a
one-line reminder of the skeptic law. This is explicitly a REMINDER hook: it
cannot know whether the subagent produced a deliverable, whether a skeptic was
already attached, or whether the work is off-tree. It never blocks anything.

A marker carried by the HEAD commit arrived with the repository rather than
from anyone in this working copy choosing it, and one whose provenance cannot
be determined is no opt-in either, so this hook stays quiet in both cases.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

OPT_IN_MARKER = ".delegation"
GATE_PATH = Path(__file__).resolve().parent / "commit-gate.py"


def load_gate():
    """Import commit-gate.py by path, or None. Used only for its shared
    `marker_provenance` rule, so None simply means "nudge as before"."""
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
    """Only the gate's `marker_provenance()` == MARKER_LOCAL nudges. A gate that
    will not load falls back to nudging, this hook's whole failure posture."""
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

    if not marker_is_local_opt_in(root, load_gate()):
        return 0

    print(
        json.dumps(
            {
                "systemMessage": (
                    "delegation-framework reminder: a subagent finished. If it "
                    "produced a deliverable (research, design, or "
                    "implementation), attach at least one skeptic before "
                    "trusting or committing it: floor of one, no exceptions "
                    "(/skeptic-review)."
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
