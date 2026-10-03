---
name: skeptical-review
description: Use when a deliverable (code, design, research) needs adversarial review - sizes the panel, picks lenses, selects swarm vs deep vs hybrid mode, dispatches skeptics, and produces the review artifact the commit gate reads
---

# Skeptical Review

How to run — and read — an adversarial review panel. The reviewer is
[`../../agents/skeptic.md`](../../agents/skeptic.md) (spawn as
`subagent_type: "skeptic"`, one per lens); lenses come from
[`../../docs/lenses.md`](../../docs/lenses.md); every reviewer reports in the
[`../../docs/rubric.md`](../../docs/rubric.md) format.

**The floor:** every deliverable gets **at least one** skeptic — research,
design, implementation, all of them. No exceptions.

## Panel setup

1. **Size it:** 2–3 skeptics for a small change, 5–7 for a feature batch: scale to the risk; the numbers are guidance, not a ceiling.
2. **Pick lenses** per the catalogue's guidance — diversify; duplicate
   lenses add noise, not coverage.
3. **State the end goal in each dispatch.** Skeptics rate usefulness toward
   the end goal you state; a dispatch without one gets line-coverage noise.
4. **Review the integrated tree**, only after all slices report DONE.
5. **Dispatch the whole panel in parallel.** Reviewers are read-only, so they
   cannot collide; the write-set rules that constrain implementer fan-out
   ([`../delegating/SKILL.md`](../delegating/SKILL.md#the-loop-mechanics)) do
   not apply to them.

## The three modes

- **SWARM** — many independent-lens reviewers in parallel, each skimming
  broadly. Optimizes **breadth**. Best for large-but-surface work: wide
  diffs, many small files, repetitive changes where the risk is "did we miss
  a spot," not "is this subtle logic correct."
- **DEEP** — one or a few **specialists** running a **two-phase
  understand-then-attack**: *first* fully understand the subsystem (read it,
  trace the calls, reproduce the behaviour), *then* turn skeptical against
  that earned understanding. Optimizes **depth**. Best for the devil in the
  details a swarm skims: subtle concurrency, a load-bearing algorithm, a
  claim that needs reproduction. Brief a deep reviewer in two explicit
  phases and require evidence of phase 1 (what it traced/reproduced) in its
  report.
- **HYBRID** — a swarm for breadth **plus** one deep reviewer on the
  highest-risk slice.

## Mode selection — dual placement (deliberate)

Selection responsibility sits in **both** of these places, on purpose:

1. **Manager triages upfront.** Before dispatching, pick swarm / deep /
   hybrid by **breadth-vs-depth × risk**:
   - High breadth, low per-unit subtlety → **swarm**
   - Low breadth, high subtlety, or a claim needing reproduction → **deep**
   - High on both axes → **hybrid**

   **A lens can override that choice.** Check the lens catalogue before you
   settle the mode: `derived-output/ranking` is **mandatory and deep-only** for
   any deliverable that scores, ranks, classifies, prioritizes, or derives a
   verdict, because the inversion and fail-open defects it exists to catch are
   only reachable by running the thing ([`../../docs/lenses.md`](../../docs/lenses.md),
   [`../../agents/skeptic.md`](../../agents/skeptic.md)). So a breadth-shaped
   deliverable that also ranks something is **hybrid**, not swarm: the swarm
   for breadth, plus that lens run deep. A mandatory deep lens dispatched in
   swarm mode is a review of what the thing looks like, not of what it does.
2. **Any swarm reviewer can escalate mid-flight.** A swarm reviewer that
   hits "this needs a specialist — I'm skimming something that deserves a
   trace/repro" outputs an `ESCALATE` block (see the rubric). **Escalation
   is a first-class output, not a failure.** The manager then dispatches
   that thread as a deep review before trusting the swarm's verdict on it.

Record the mode chosen in the review artifact's `mode`, and any escalations
taken in the optional `escalations` array described with the schema below.

## The review artifact (feeds the commit gate)

When — and only when — every reviewer in the final round is PLEASED, write
`.delegation/review-artifact.json` at the repo root of the tree under
review:

```json
{
  "deliverable": "<what was reviewed, one line>",
  "mode": "swarm | deep | hybrid",
  "rounds": <number of review rounds run>,
  "head_sha": "<output of `git rev-parse HEAD`, or null if the repo has no commits yet>",
  "reviews": [
    {"reviewer": "<id>", "lens": "<lens name>", "verdict": "PLEASED", "blocking": []}
  ],
  "consolidated_blocking": []
}
```

`head_sha` is **required** and binds the artifact to **one** commit: the
gate compares it against the repo's current HEAD, so once the reviewed
commit lands the artifact is spent and the next commit needs a fresh panel.
Fill head_sha last; if a fix lands after the artifact is written, write the artifact again: the gate checks only HEAD.
An artifact written without the field fails closed with an explicit message —
re-run the panel rather than patching the SHA in.

Keys the gate does not define are ignored, so the artifact can carry more than
the minimum. Record the mode you chose in `mode`, and **if any swarm reviewer
escalated, record that too**, as an optional `escalations` array alongside the
required keys:

```json
  "escalations": [
    {"from": "<reviewer id>", "thread": "<what needed a specialist>",
     "dispatched_as": "<the deep review that answered it>"}
  ]
```

The same holds for the optional `adjudications` array, which summarizes the
on-disk adjudication record (`.delegation/adjudications/round-<N>.md`,
format in
[`../consolidating-review/SKILL.md`](../consolidating-review/SKILL.md#4-the-adjudication-record-a-required-artifact))
when any BLOCKING finding was demoted as fluff on the way to this artifact:

```json
  "adjudications": [
    {"finding": "<#: one line>", "lens": "<lens>", "ruling": "FLUFF",
     "reason": "<the written reason>", "rebuttal": "conceded | stood: <new evidence>",
     "final": "demoted to non-blocking | discarded | gates (rebuttal flipped it) | escalated to owner"}
  ]
```

Both arrays are for the manager, the steward and the next reader, not for the
gate: the gate neither requires nor validates them. Do not invent other fields
and expect them to mean anything.

The PreToolUse commit gate denies the git commands that author a new commit
unless this file is valid and its `head_sha` matches HEAD (what is gated and
what is not, the `.delegation/` opt-in marker, the deny message and its escape
hatches, the five honest limits: the section "Enforcement, honestly" of the
[README](../../README.md)). After the manager commits, archive the artifact
to `.delegation/history/`.

## Reading the panel

- Any NOT PLEASED → hand the numbered BLOCKING lists to
  [`../consolidating-review/SKILL.md`](../consolidating-review/SKILL.md): it
  adjudicates, runs one fix round and re-reviews the dissenters.
- All PLEASED → write the artifact, then the
  [manager still inspects](../delegating/SKILL.md#manager-inspects-the-procedure)
  — a unanimous panel is necessary, not sufficient.
