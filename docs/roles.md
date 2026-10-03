# Roles: owner, manager, steward, implementation agent, skeptical reviewer

## Owner

No green panel or steward scorecard overrides the owner, who talks only to the
manager and settles any manager-steward dispute the peers cannot. A second
orchestrator is a new session the owner starts, never nested. The owner is the
only authority that may authorize a change to this framework itself
([README](../README.md), do-not-modify rule).

## Manager

[Definition](../agents/manager.md): top-level, owner-facing, the only spawner, a
role you adopt, never spawned. Every other role is a flat sibling one level
below; skeptic and steward have no spawn tool
([topology](../agents/manager.md#the-spawn-topology-the-load-bearing-rule-of-this-framework)).

## Steward

[Definition](../agents/steward.md). Does **NOT** review deliverables (the
skeptic's job) or decompose or dispatch (the manager's); it judges how the
manager did. Pair one with any run long or high-stakes enough that manager drift
would go unnoticed.

## Implementation agent

Builds exactly one scoped slice; reports what it did plus test evidence
([brief template](../skills/delegating/SKILL.md#the-brief-template)).

## Skeptical reviewer

[Definition](../agents/skeptic.md): adversarial, finds problems, never blesses.
Read-only, spawned by the manager (`subagent_type: "skeptic"`, or a
general-purpose agent told to adopt it). Rates each finding by usefulness toward
the end goal, not line coverage; verdict per [rubric](rubric.md).
