---
description: Run a multi-part task through the manager, implementer and skeptic loop; not for trivial edits
argument-hint: "[the task to delegate]"
---

If `$ARGUMENTS` is a trivial edit or single-file fix, do NOT delegate: say so
and make the edit directly.

Otherwise run the full loop with the **delegation-framework:delegating** skill
(a planning package, usually the opening prompt, enters at its plan intake;
plan questions go back by its planner relay):

$ARGUMENTS

You are the **manager**, in this top-level session: do not spawn a manager
subagent; hold the role in `${CLAUDE_PLUGIN_ROOT}/agents/manager.md`. Follow
the skill exactly:

1. **Arm the repo:** create `.delegation/` and gitignore it in the same step
   ([why](../skills/delegating/SKILL.md#7-the-loop-and-the-commit-gate)).
2. Run the loop mechanics; fill the conflict-avoidance checklist before any
   fan-out.
3. Write every brief, scouting and fix rounds included, from the skill's
   template, and save it under `.delegation/briefs/` before dispatch.
4. Seat at least one skeptic on every deliverable, plus one with lens
   `compact` (compact-review skill) on any doc.
5. Run ONE panel over the integrated tree and make ONE commit, per
   `${CLAUDE_PLUGIN_ROOT}/commands/review-panel.md`.
