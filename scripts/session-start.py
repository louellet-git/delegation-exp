#!/usr/bin/env python3
"""SessionStart context injection: make the framework visible before it is needed.

Requires Python 3.7 or newer (`from __future__ import annotations`).
Always exits 0; the hooks.json interpreter chain ends in `exit 0`, so a missing interpreter is silent.

Claude Code lazy-loads plugin skills. Without this hook the only thing in a
session's context is the one-line description from the skills list, so the
framework is reached only if the model happens to reach for it, which is the
one thing a discipline about not trusting your own judgement cannot rely on.
This hook injects `hooks/session-start-context.md` at session start.

It injects that short file and NOT `skills/delegating/SKILL.md`. The skill is
the playbook, read when the loop is actually run; this is the doorbell.
Carrying the playbook in every session would cost more context than the
sessions that never delegate can justify.

SCOPING is a deliberate departure from the sibling hooks. `subagent-reminder`,
`stop-reminder` and `commit-gate` stay silent unless the repo opted in with a
local `.delegation/` marker, because an interrupting nudge in an unrelated
session is noise. This hook is unconditional instead, for two reasons: it
interrupts nothing, and the moment the framework is most needed is BEFORE a
`.delegation/` directory exists, when the work is being decomposed for the
first time. Scoping it would make it appear only once it was no longer news.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONTEXT_PATH = (
    Path(__file__).resolve().parent.parent / "hooks" / "session-start-context.md"
)


def main() -> int:
    # Read and discard the payload (this hook is unconditional) so the host is
    # never left writing into a closed pipe.
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        pass

    try:
        body = CONTEXT_PATH.read_text(encoding="utf-8-sig")
    except OSError:
        return 0  # context file missing: stay silent rather than half-speak

    body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", body, count=1, flags=re.S)  # doc-standard header
    if not body.strip():
        return 0

    context = (
        "<EXTREMELY_IMPORTANT>\n"
        f"{body.strip()}\n\n"
        "Reading the above is not a substitute for invoking the skill. It names the "
        "disciplines; the skill carries the mechanics, and the mechanics are where "
        "the loop is actually run.\n"
        "</EXTREMELY_IMPORTANT>"
    )
    out = {"additionalContext": context}
    if "--copilot" not in sys.argv:  # Copilot CLI reads the top-level shape
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", **out}}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a context hook never breaks a session
        sys.exit(0)
