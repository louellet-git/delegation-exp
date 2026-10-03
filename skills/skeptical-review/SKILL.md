---
name: skeptical-review
description: Runs a skeptic panel on a deliverable and writes the review artifact the commit gate reads. Use before trusting any code, design or research.
---

# Skeptical Review

Every deliverable gets at least one skeptic, no exceptions. Spawn
[skeptic](../../agents/skeptic.md) as `subagent_type: "skeptic"`, one per
[lens](../../docs/lenses.md), reporting in [rubric](../../docs/rubric.md)
format.

## Panel setup

Size to risk: 2–3 for a small change, 5–7 for a feature batch, no ceiling.
Diversify lenses. State the end goal in each dispatch, or get line-coverage
noise. Once every slice is DONE, review the integrated tree, all reviewers in
parallel (they are read-only).

## The three modes

Pick before dispatch: SWARM, many one-lens reviewers skimming, for breadth;
DEEP, one or a few specialists who understand (read, trace, reproduce) before
attacking and report that work, for subtlety or a claim to reproduce; HYBRID,
a swarm plus one deep reviewer on the riskiest slice, for both. Run
`derived-output/ranking`, mandatory and deep-only, on anything that scores,
ranks, classifies, prioritizes or derives a verdict, since its defects show
only when run (breadth plus ranking: hybrid). A swarm reviewer may emit
`ESCALATE`, a first-class output: review that thread deep before trusting the
swarm on it.

## The review artifact (feeds the commit gate)

Only when every final-round reviewer is PLEASED, write
`.delegation/review-artifact.json` at the root of the tree under review:

```json
{
  "deliverable": "<one line: what was reviewed>",
  "mode": "swarm | deep | hybrid",
  "rounds": <review rounds run>,
  "head_sha": "<git rev-parse HEAD, or null if the repo has no commits yet>",
  "reviews": [
    {"reviewer": "<id>", "lens": "<lens>", "verdict": "PLEASED", "blocking": []}
  ],
  "consolidated_blocking": [],
  "escalations": [
    {"from": "<reviewer id>", "thread": "<what needed a specialist>",
     "dispatched_as": "<the deep review>"}
  ],
  "adjudications": [
    {"finding": "<#: one line>", "lens": "<lens>", "ruling": "FLUFF",
     "reason": "<written reason>", "rebuttal": "conceded | stood: <new evidence>",
     "final": "demoted to non-blocking | discarded | gates (rebuttal flipped it) | escalated to owner"}
  ]
}
```

Fill `head_sha` last, and rewrite the artifact if a fix lands after: it binds
one commit. Without it the artifact fails closed: re-run the panel, never
patch the SHA in. Record escalations and demotions
([the record](../consolidating-review/SKILL.md#4-the-adjudication-record-a-required-artifact))
in the optional `escalations` and `adjudications`, which the gate ignores,
as it ignores any key it does not define: invent no field expecting meaning.
Gate scope, five honest limits:
[README](../../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline).
Before the commit the
[manager still inspects](../delegating/SKILL.md#manager-inspects-the-procedure),
since unanimity is necessary, not sufficient; after it, archive the artifact
to `.delegation/history/`. Any NOT PLEASED goes to
[consolidating-review](../consolidating-review/SKILL.md).
