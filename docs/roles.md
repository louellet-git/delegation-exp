# Roles: owner, manager, steward, implementation agent, skeptical reviewer

The roles of the operating model
([`operating-model.md`](operating-model.md)). Generalized: they apply to any
deliverable, whether code, design docs, research memos, or migrations. The
manager runs and drives everything; the steward keeps the manager on
track; implementers and skeptics build and grade the work.

## The org — who sits where

One spawner, flat siblings one level deep. Diagram and the four spawn rules:
[`../agents/manager.md`](../agents/manager.md#the-spawn-topology-the-load-bearing-rule-of-this-framework).

## Owner

The human the whole framework answers to. Judgment is owner-owned at the top:
neither a green panel nor a steward scorecard overrides the owner. The owner
interacts only with the manager (never with the workers below it), is the
final adjudicator of any manager↔steward dispute the two peers cannot settle, and
is the only authority that may authorize a change to this framework itself
(see the do-not-modify guard in the [README](../README.md)). Spinning up a second,
independent orchestrator for genuinely-parallel deep work is a new session the
owner starts and coordinates, not something an agent nests below itself.

## Manager

The single top-level orchestrator, the owner-facing agent, and the **only
agent that can spawn**. Full definition:
[`../agents/manager.md`](../agents/manager.md).

## Steward

Full definition: [`../agents/steward.md`](../agents/steward.md). The steward
does **NOT** review deliverables. That is the skeptic's job, on its lenses; a
weak deliverable is a finding *for a skeptic*, not the steward. It does **NOT**
decompose or dispatch. That is the manager's job; the steward only judges how
the manager did it.

Pair a standing steward with any run long or high-stakes enough that manager
drift would go unnoticed.

## Implementation agent

Builds exactly one scoped slice: it writes the
code and reports what it
did plus test evidence. Brief template:
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-brief-template).

## Skeptical reviewer

Adversarial by design. Its job is to *find problems*, not to bless. A
flat-sibling worker the manager spawns; it cannot spawn. It:

- Rates each finding's usefulness toward the end goal, not line coverage.
- Returns `VERDICT: PLEASED | NOT PLEASED` and a numbered `BLOCKING` list per
  [`rubric.md`](rubric.md).
- Is read-only: it never modifies the deliverable it reviews.

The reusable definition is [`../agents/skeptic.md`](../agents/skeptic.md);
spawn it with `subagent_type: "skeptic"`, or spawn general-purpose agents
told to adopt it. Unlike the manager, this one *is* meant to be spawned: it is
a flat sibling one level below the manager, which is exactly where a subagent
definition belongs.
