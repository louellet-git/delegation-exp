---
description: Run a multi-part task through the manager, implementer and skeptic loop; not for trivial edits
argument-hint: [the task to delegate]
---

If `$ARGUMENTS` is a trivial edit or single-file fix, do NOT delegate: say so
and make the edit directly.

Otherwise run the full loop with the **delegation-framework:delegating** skill
(a planning-framework package, usually this session's opening prompt, enters at
its plan intake, which turns leaf cards into briefs; plan-content questions go
back by its planner relay):

$ARGUMENTS

You are the **manager**, in this top-level session: do not spawn a manager
subagent; hold the role in `${CLAUDE_PLUGIN_ROOT}/agents/manager.md`. Follow
the skill exactly:

1. **Arm the repo.** Create `.delegation/` at the repo root, the marker that
   arms the commit gate and reminder hooks, and add it to `.gitignore` in the
   same step: the gate reads the marker from the HEAD commit tree, so a
   committed marker turns the gate off, here and in every clone, and a
   committed all-PLEASED artifact ships a waiver.
2. Run the loop mechanics; fill the conflict-avoidance checklist before any
   fan-out.
3. Write every brief, scouting slices and fix rounds included, from the
   skill's canonical template, with its postures and the re-brief that the
   implementer does not commit or push. Save it under `.delegation/briefs/`
   before dispatching, so a steward checkpoint can reconcile against it.
4. Attach at least one skeptic to every deliverable.
5. Integrate, run ONE panel over the integrated tree, make ONE commit
   (the artifact binds to HEAD; never commit slices as they land), following
   `${CLAUDE_PLUGIN_ROOT}/commands/review-panel.md`.
