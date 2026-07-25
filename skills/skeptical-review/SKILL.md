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

1. **Size it:** 2–3 skeptics for a small change, 5–7 for a feature batch.
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
2. **Any swarm reviewer can escalate mid-flight.** A swarm reviewer that
   hits "this needs a specialist — I'm skimming something that deserves a
   trace/repro" outputs an `ESCALATE` block (see the rubric). **Escalation
   is a first-class output, not a failure.** The manager then dispatches
   that thread as a deep review before trusting the swarm's verdict on it.

Record the mode chosen (and any escalations taken) in the review artifact.

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
Record it when you write the artifact. An artifact written without the
field fails closed with an explicit message — re-run the panel rather than
patching the SHA in.

The PreToolUse commit gate denies commit-creating git commands (`commit`,
`merge`, `rebase`, `cherry-pick`, `revert`, `pull`, `am`) unless this file
exists, is valid JSON, has a non-empty `deliverable` string, a valid `mode`,
a `head_sha` matching current HEAD, a non-empty `reviews` array, and every
`verdict` is exactly `"PLEASED"` with no non-empty `blocking` list. The
gate acts only in repos carrying the
`.delegation/` **opt-in marker** directory (created by the `delegating`
skill at loop start). Honest framing — the gate has five limits: it
verifies the artifact, not the review's rigor; it only fires where hooks
are enabled with Python on PATH; it gates only the local tree;
matcher evasion is possible and an unresolvable path falls back to gating
the hook's own repo; and being
session-global it is scoped by the opt-in marker yet can still
false-positive on compound commands, quoted separators, and heredocs
(escape: write the artifact,
remove `.delegation/`, or disable the hook — all five limits in the
[README](../../README.md)). After the manager commits, archive the artifact
to `.delegation/history/`.

## Reading the panel

- Any NOT PLEASED → hand the numbered BLOCKING lists to
  [`../consolidating-review/SKILL.md`](../consolidating-review/SKILL.md) for
  one reconciled fix round; re-review the dissenters only.
- All PLEASED → write the artifact, then the **manager still inspects** —
  a unanimous panel is necessary, not sufficient.
