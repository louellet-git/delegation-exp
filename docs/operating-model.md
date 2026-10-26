---
id: DOC-OPERATING-MODEL
type: description
item: 10.38 Process description
status: current
date: 2026-10-26
scope: Index of how work is built and graded: the loop, spawn topology, steward and commit gate, each linked to its home.
---

# Operating model

Index: one home per concept. Also [roles](roles.md), [rubric](rubric.md).

The law: every deliverable gets at least one adversarial skeptic before it is
trusted, no exceptions
([skeptical-review](../skills/skeptical-review/SKILL.md)).

## The loop

- [Substantial builds only](../README.md#when-not-to-delegate-and-how-to-un-arm-a-repo), never a trivial edit.
- [Decompose](../skills/delegating/SKILL.md#decompose-the-procedure);
  [implement](../skills/delegating/SKILL.md#one-scoped-task-per-fresh-subagent),
  [brief template](../skills/delegating/SKILL.md#the-brief-template);
  [BLOCKED](../skills/delegating/SKILL.md#blocked-the-procedure); the manager
  [does not read](../skills/delegating/SKILL.md#the-loop-mechanics);
  [model ladder](../skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what).
- [Test-first](../skills/delegating/SKILL.md#test-first-implementation),
  [evidence before claims](../skills/delegating/SKILL.md#evidence-before-claims),
  [never commit or push](../skills/delegating/SKILL.md#3-two-standing-posture-rules),
  [silence is not progress](../skills/delegating/SKILL.md#6-reliability--stall-rules).
- Parallel by write set:
  [fan-out](../skills/delegating/SKILL.md#fan-out-disjoint-parallel-shared-sequential),
  [checklist](conflict-avoidance-checklist.md).
- Review: [panel](../skills/skeptical-review/SKILL.md#panel-setup),
  [modes](../skills/skeptical-review/SKILL.md#the-three-modes),
  [lenses](lenses.md), [skeptic](../agents/skeptic.md).
- Consolidate:
  [adjudicate](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate),
  [rebuttal](../skills/consolidating-review/SKILL.md#3-the-rebuttal-round-no-silent-demotions),
  [record](../skills/consolidating-review/SKILL.md#4-the-adjudication-record-a-required-artifact),
  [fix round](../skills/consolidating-review/SKILL.md#5-one-reconciled-fix-round),
  [re-review](../skills/consolidating-review/SKILL.md#6-re-review-the-dissenters)
  until every reviewer is PLEASED,
  [convergence](../skills/consolidating-review/SKILL.md#7-convergence-discipline);
  [manager inspects](../skills/delegating/SKILL.md#manager-inspects-the-procedure).

## Spawn topology and steward

Spawn rules: [roles](roles.md),
[topology](../agents/manager.md#the-spawn-topology-the-load-bearing-rule-of-this-framework),
[do not spawn it](../agents/manager.md#how-to-use-this-file-do-not-spawn-it).
[Steward](../agents/steward.md):
[pairing](../agents/manager.md#spawn-the-steward-and-stay-in-dialogue-with-it),
[scorecards](../skills/delegating/SKILL.md#5-pair-a-standing-steward-it-governs-you),
[andon-cord](../agents/steward.md#the-one-narrow-andon-cord--escalate-before-proceed),
[auto-consult](../agents/manager.md#auto-consult-a-standing-binding-rule).

## The commit gate (the one structural slice)

[README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline):
five honest limits,
[un-arming](../README.md#when-not-to-delegate-and-how-to-un-arm-a-repo);
[artifact schema](../skills/skeptical-review/SKILL.md#the-review-artifact-feeds-the-commit-gate).
