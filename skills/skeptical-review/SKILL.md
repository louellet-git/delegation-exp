---
name: skeptical-review
description: Runs a skeptic panel on a deliverable and writes the review artifact the commit gate reads. Use before trusting any code, design or research.
id: DOC-SKILL-SKEPTICAL-REVIEW
type: procedure
item: 10.30 Life-cycle procedure
status: current
date: 2026-10-26
scope: Steps to run a skeptic panel on a deliverable and write the review artifact the commit gate reads.
---

# Skeptical Review

Every deliverable gets at least one skeptic, no exceptions. Spawn
[skeptic](../../agents/skeptic.md) as `subagent_type: "skeptic"`, one per
[lens](../../docs/lenses.md), reporting in [rubric](../../docs/rubric.md)
format. Where that type is not installed (Copilot CLI, a session without the
install), spawn a general-purpose worker told to read `agents/skeptic.md`
first and act as it; the same holds for the [steward](../../agents/steward.md).
Claude Code enforces `haiku` through the spawn tool's `model`; under Copilot
CLI the model is guidance unless its spawn takes one (unverified).

## Panel setup

One reviewer per distinct high-impact risk, no quota: a small change gets one
skeptic, and a reviewer earns its seat by naming a risk no other seat covers.
Diversify lenses. State the end goal in each dispatch, or get line-coverage
noise. Once every slice is DONE, review the integrated tree, all reviewers in
parallel (they are read-only). A deliverable that creates or changes a doc also
seats a skeptic with lens `doc-standard`, which loads the
[doc-review](../doc-review/SKILL.md) skill; it may rerun
`scripts/doc_check.py`. Its verdict goes in the artifact.

## The three modes

Pick before dispatch: SWARM, many one-lens reviewers skimming, for breadth;
DEEP, one or a few specialists who understand (read, trace, reproduce) before
attacking and report that work, for subtlety or a claim to reproduce; HYBRID,
a swarm plus one deep reviewer on the riskiest slice, for both. Run
`derived-output/ranking`, mandatory and deep-only, on anything that scores,
ranks, classifies, prioritizes or derives a verdict: its defects show only
when run. A swarm reviewer may emit `ESCALATE`: review that thread deep
before trusting the swarm on it.

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

Fill `head_sha` last, once the tree stops changing, and rewrite it if a fix
lands after: it binds one commit, and a stale or missing SHA fails closed:
re-run the panel, never patch it in. Record escalations and demotions
([the record](../consolidating-review/SKILL.md#4-the-adjudication-record-a-required-artifact))
in the optional `escalations` and `adjudications`, which the gate ignores,
as it ignores any key it does not define: invent no field expecting meaning.
Gate scope, five honest limits:
[README](../../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline).
Then
[the manager inspects](../delegating/SKILL.md#manager-inspects-the-procedure).
Any NOT PLEASED goes to
[consolidating-review](../consolidating-review/SKILL.md).
