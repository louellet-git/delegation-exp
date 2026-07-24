#!/usr/bin/env python3
"""Stop reminder nudge — discipline, not structure.

At session stop, IF the current repo has opted in (`.delegation/` at the
repo root — the same scoping marker as the commit gate) AND the working
tree has uncommitted changes AND there is no all-PLEASED review artifact,
surface a one-line reminder that a delegation slice may be in flight
without its panel. Reminder only — the commit gate is the structural
check; this hook never blocks the stop.

Silent in every other case (no marker, clean tree, valid artifact, or any
error running git). Always exits 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

OPT_IN_MARKER = ".delegation"
ARTIFACT_REL_PATH = Path(".delegation") / "review-artifact.json"


def find_repo_root(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        return None
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def artifact_is_all_pleased(root: Path) -> bool:
    try:
        data = json.loads((root / ARTIFACT_REL_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    reviews = data.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        return False
    return all(
        isinstance(r, dict)
        and r.get("verdict") == "PLEASED"
        and not r.get("blocking")
        for r in reviews
    ) and not data.get("consolidated_blocking")


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
        return False  # cannot tell — stay quiet rather than nag wrongly
    return result.returncode == 0 and bool(result.stdout.strip())


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
        return 0
    if artifact_is_all_pleased(root):
        return 0
    if not tree_is_dirty(root):
        return 0

    print(
        json.dumps(
            {
                "systemMessage": (
                    "delegation-framework reminder (session stop): this repo "
                    "has a .delegation/ marker and uncommitted work, but no "
                    "all-PLEASED review artifact. If a delegation slice is in "
                    "flight, run the skeptic panel before committing "
                    "(/review-panel). Reminder only — the commit gate is the "
                    "structural check."
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
