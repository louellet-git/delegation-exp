---
description: Decompose a task and run it through the manager -> implementer -> skeptic loop (delegation-framework)
argument-hint: [the task to delegate]
---

**Trivial-edit gate first:** if `$ARGUMENTS` describes a trivial edit or a
single-file fix, do NOT run the delegation machinery. Say so and just make
the edit directly. The overhead is only worth it for substantial,
multi-part work.

Otherwise, use the **delegation-framework:delegating** skill to run the full
loop for this task:

$ARGUMENTS

Follow the skill exactly: create the `.delegation/` directory at the repo
root when the loop starts (this is the opt-in marker that arms the commit
gate and reminder hooks for THIS repo, and the home of the checklist and
review artifact); run the loop mechanics the skill describes (one scoped task
per fresh subagent, fan-out by disjoint write sets, test-first, evidence
before claims); fill the conflict-avoidance checklist before any
fan-out; re-brief every implementation agent that it does not commit; attach
at least one skeptic to every deliverable; and only commit after the panel
is all-PLEASED, the review artifact is written, and you have inspected the
integrated tree yourself.
