#!/usr/bin/env python3
"""SessionStart context injection: make the framework visible before it is needed.

Requires Python 3.7 or newer (`from __future__ import annotations`).

Claude Code lazy-loads plugin skills. Without this hook the only thing in a
session's context is the one-line description from the skills list, so the
framework is reached only if the model happens to reach for it — which is the
one thing a discipline about not trusting your own judgement cannot rely on.
This hook injects `hooks/session-start-context.md` at session start.

It injects that short file and NOT `skills/delegating/SKILL.md`, which is
~34KB. The skill is the playbook, read when the loop is actually run; this is
the doorbell. Carrying the playbook in every session would cost more context
than the sessions that never delegate can justify.

SCOPING — a deliberate departure from the sibling hooks. `subagent-reminder`,
`stop-reminder` and `commit-gate` stay silent unless the repo opted in with a
local `.delegation/` marker, because an interrupting nudge in an unrelated
session is noise. This hook is unconditional instead, for two reasons: it
interrupts nothing, and the moment the framework is most needed is BEFORE a
`.delegation/` directory exists, when the work is being decomposed for the
first time. Scoping it would make it appear only once it was no longer news.
To scope it anyway, gate `main()` on the same rule the siblings use —
`marker_provenance(root) == MARKER_LOCAL` from `commit-gate.py`, imported the
way `subagent-reminder.py` imports it.

Always exits 0, and hooks.json invokes it as `python3 ... || python ... ||
py -3 ... || exit 0` so that a missing interpreter or script degrades to
silence rather than to a nonzero hook exit (the python.org Windows installer
ships no `python3.exe`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CONTEXT_PATH = (
    Path(__file__).resolve().parent.parent / "hooks" / "session-start-context.md"
)

FOOTER = (
    "Reading the above is not a substitute for invoking the skill. It names the "
    "disciplines; the skill carries the mechanics, and the mechanics are where "
    "the loop is actually run."
)


def build_context(body: str) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        f"{body.strip()}\n\n"
        f"{FOOTER}\n"
        "</EXTREMELY_IMPORTANT>"
    )


def main() -> int:
    # The payload is read and discarded: SessionStart carries cwd and source,
    # and this hook is unconditional. Reading it keeps stdin drained so the
    # host is never left writing into a closed pipe.
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        pass

    try:
        body = CONTEXT_PATH.read_text(encoding="utf-8")
    except OSError:
        return 0  # context file missing: stay silent rather than half-speak

    if not body.strip():
        return 0

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": build_context(body),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a context hook never breaks a session
        sys.exit(0)
