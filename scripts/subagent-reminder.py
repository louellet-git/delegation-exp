#!/usr/bin/env python3
"""SubagentStop reminder nudge: discipline, not structure.

Requires Python 3.7 or newer (`from __future__ import annotations`).

When a subagent finishes IN A REPO THAT HAS OPTED IN to the framework (an
untracked `.delegation/` directory at the repo root, the same scoping marker
the commit gate uses; plugin hooks are session-global, and a nudge in every
unrelated session is noise), surface a one-line reminder of the skeptic law.
This is explicitly a REMINDER hook: it cannot know whether the subagent
produced a deliverable, whether a skeptic was already attached, or whether
the work is off-tree. It never blocks anything.

A `.delegation/` marker that is TRACKED in git is not an opt-in (it arrived
with the clone rather than from anyone in this working copy choosing it), so
this hook stays quiet there too. Same rule as the commit gate.

Always exits 0, and hooks.json invokes it as a single `python3 ... || exit 0`
so that a missing interpreter or script degrades to silence rather than to a
nonzero hook exit.
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
    `marker_is_tracked` rule, so None simply means "nudge as before"."""
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
        return 0  # not a repo: stay quiet
    try:
        if not (root / OPT_IN_MARKER).is_dir():
            return 0  # repo has not opted in: stay quiet
    except OSError:
        return 0

    gate = load_gate()
    if gate is not None and gate.marker_is_tracked(root):
        return 0  # marker came with the clone, not from an opt-in here

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
