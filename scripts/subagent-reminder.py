#!/usr/bin/env python3
"""SubagentStop reminder nudge — discipline, not structure.

When a subagent finishes IN A REPO THAT HAS OPTED IN to the framework
(`.delegation/` directory at the repo root — same scoping marker as the
commit gate; plugin hooks are session-global, and a nudge in every
unrelated session is noise), surface a one-line reminder of the skeptic
law. This is explicitly a REMINDER hook: it cannot know whether the
subagent produced a deliverable, whether a skeptic was already attached,
or whether the work is off-tree. It never blocks anything.

Always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OPT_IN_MARKER = ".delegation"


def find_repo_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0

    cwd = payload.get("cwd")
    start = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    root = find_repo_root(start)
    if root is None or not (root / OPT_IN_MARKER).is_dir():
        return 0  # repo has not opted in — stay quiet

    print(
        json.dumps(
            {
                "systemMessage": (
                    "delegation-framework reminder: a subagent finished. If it "
                    "produced a deliverable (research, design, or "
                    "implementation), attach at least one skeptic before "
                    "trusting or committing it — floor of one, no exceptions "
                    "(/skeptic-review)."
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
