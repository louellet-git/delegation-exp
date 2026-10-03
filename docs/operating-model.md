# The operating model: how work gets built and graded

A manager agent delegates to implementation agents; skeptical reviewer agents grade the work. This file is an index: each concept gets one line pointing at its canonical home. Roles: [`roles.md`](roles.md); lenses: [`lenses.md`](lenses.md); verdict format: [`rubric.md`](rubric.md).

The law: every deliverable (research, design, implementation) gets at least one adversarial skeptic before it is trusted; the floor is one, no exceptions ([skeptical-review](../skills/skeptical-review/SKILL.md)). It is discipline plus one structural slice, the commit gate, not a wall ([README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline)).

## The loop

```
DECOMPOSE → IMPLEMENT (parallel where safe) → REVIEW PANEL (skeptics sized to the risk, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING → ADJUDICATE (the fluff gate: real gates, fluff demoted on the record)
          → FIX ROUND → RE-REVIEW the dissenters
          → until every reviewer is PLEASED → MANAGER INSPECTS → COMMIT
```

- Standalone, with an optional planner seam: [README](../README.md#dependencies).
- When to use it: substantial multi-part builds only; never delegate a trivial edit or single-file fix: [delegating](../skills/delegating/SKILL.md).
- Decompose: plan intake, scouting slice, bounded manager pass, slicing by write set, the batch as one panel and one commit: [delegating](../skills/delegating/SKILL.md#decompose-the-procedure).
- Implement: one scoped task per fresh subagent, the status contract: [delegating](../skills/delegating/SKILL.md#one-scoped-task-per-fresh-subagent).
- The brief template: every dispatch uses it, saved to `.delegation/briefs/` first: [delegating](../skills/delegating/SKILL.md#the-brief-template).
- BLOCKED is a decision request: [delegating](../skills/delegating/SKILL.md#blocked-the-procedure). The manager does not do the reading: [delegating](../skills/delegating/SKILL.md#the-loop-mechanics).
- Model ladder: [delegating](../skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what).
- Test-first: [delegating](../skills/delegating/SKILL.md#test-first-implementation). Evidence before claims: [delegating](../skills/delegating/SKILL.md#evidence-before-claims). The implementer never commits or pushes: [delegating](../skills/delegating/SKILL.md#3-two-standing-posture-rules).
- Silence is not progress; re-brief concretely: [delegating](../skills/delegating/SKILL.md#6-reliability--stall-rules).
- Panel setup: [skeptical-review](../skills/skeptical-review/SKILL.md#panel-setup). Panel size is guidance, not a ceiling: [delegating](../skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what). Modes: [skeptical-review](../skills/skeptical-review/SKILL.md#the-three-modes). Lenses and attack patterns: [lenses.md](lenses.md), [skeptic](../agents/skeptic.md).
- Consolidate, then the fluff gate: [consolidating-review](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate). Rebuttal round: [consolidating-review](../skills/consolidating-review/SKILL.md#3-the-rebuttal-round-no-silent-demotions). Adjudication record: [consolidating-review](../skills/consolidating-review/SKILL.md#4-the-adjudication-record-a-required-artifact).
- One reconciled fix round: [consolidating-review](../skills/consolidating-review/SKILL.md#5-one-reconciled-fix-round). Re-review the dissenters: [consolidating-review](../skills/consolidating-review/SKILL.md#6-re-review-the-dissenters). Convergence and the one-line-nit shortcut: [consolidating-review](../skills/consolidating-review/SKILL.md#7-convergence-discipline).
- MANAGER INSPECTS: [delegating](../skills/delegating/SKILL.md#manager-inspects-the-procedure).

## The spawn topology: one level deep, the manager is the sole spawner

No spawnable agent definition (skeptic, steward) grants a spawn tool; the manager is a role you adopt, never spawned: [manager](../agents/manager.md#the-spawn-topology-the-load-bearing-rule-of-this-framework), [manager](../agents/manager.md#how-to-use-this-file-do-not-spawn-it).

## The steward: beside the loop, governing the manager

- Role: [steward](../agents/steward.md), [`roles.md`](roles.md#steward). Pairing it and staying in dialogue: [manager](../agents/manager.md#spawn-the-steward-and-stay-in-dialogue-with-it); persisting briefs and scorecards: [delegating](../skills/delegating/SKILL.md#5-pair-a-standing-steward-it-governs-you).
- The one narrow andon-cord: [steward](../agents/steward.md#the-one-narrow-andon-cord--escalate-before-proceed). Yardstick, attack patterns, scorecard, honest limit: [steward](../agents/steward.md).

## Manager auto-consults — a standing, binding rule

Pairing a steward is optional for a short, low-stakes loop; once paired, auto-consult at its fixed checkpoints is binding: [manager](../agents/manager.md#auto-consult-a-standing-binding-rule). A flag the manager rejects and cannot resolve with the steward escalates to the owner: [`roles.md`](roles.md#owner).

## Conflict avoidance (hard-won)

Fan-out by write set, parallel by default, the forced checklist: [delegating](../skills/delegating/SKILL.md#fan-out-disjoint-parallel-shared-sequential), [checklist](conflict-avoidance-checklist.md). Reserved shared files and pre-assigned numbers: [delegating](../skills/delegating/SKILL.md#decompose-the-procedure).

## The commit gate (the one structural slice)

- The marker as opt-in, inherited, gitignored, claimed; what is gated and what is not; the five honest limits and escape hatches; the interpreter fallback: [README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline). Un-arming: [README](../README.md#when-not-to-delegate-and-how-to-un-arm-a-repo).
- Review artifact schema: [skeptical-review](../skills/skeptical-review/SKILL.md#the-review-artifact-feeds-the-commit-gate). `head_sha` filled last: [delegating](../skills/delegating/SKILL.md#manager-inspects-the-procedure).
- One panel waives exactly one commit; archive the artifact to `.delegation/history/` after it lands: [delegating](../skills/delegating/SKILL.md#manager-inspects-the-procedure).
