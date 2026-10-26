# Worked example: one delegation, end to end

**Task:** `reports-service` gains a CSV export, a rate limiter and docs for
both. **Claim:** *"reports-service exposes a CSV export and a rate limiter, both
documented, and the export produces valid CSV for empty, single-row, and unicode
inputs."*

## 1. DECOMPOSE

Arm the repo and gitignore the marker together, since a committed marker turns
the gate off ([README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline)):

```
mkdir -p .delegation/briefs .delegation/steward
grep -qxF '.delegation/' .gitignore || echo '.delegation/' >> .gitignore
```

Three unrelated changes under one panel and one commit are a
[feature batch](../skills/skeptical-review/SKILL.md#panel-setup). The [checklist](conflict-avoidance-checklist.md) clears
disjoint slices, each an allowlist plus its exact test command: A `export/`, B
`middleware/`, C `docs/api.md`; `docs/README.md` stays the manager's. They run in
parallel, one fresh test-first worker subagent each.

Briefs from [the template](../skills/delegating/SKILL.md#the-brief-template) are
saved to `.delegation/briefs/A.md`, `B.md`, `C.md` before dispatch, or the
steward's DELEGATION line is unrecoverable.

## 2. REVIEW PANEL

One skeptic per distinct high-impact risk, here **5** in
[swarm](../skills/skeptical-review/SKILL.md#the-three-modes) mode: five lenses
in parallel over the whole tree once all report DONE, docs slice included. `correctness` is **NOT
PLEASED** (`export/csv.py` crashes on an empty dataset; the suite covers only
populated tables), `overfit/generalization` **NOT PLEASED** (`ratelimit.py`
counts per fixed calendar minute, so a boundary burst passes twice the limit);
the other three are **PLEASED**.

## 3. ADJUDICATE → FIX ROUND

A BLOCKING tag does not gate by itself: adjudicate each finding against
[fluff gate, consolidating-review §2](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate)
before any fix. Both are **REAL**: a reproducible crash with evidence (finding 4); a
user-visible failure of the slice's own acceptance condition (findings 1, 2).
Nothing is demoted, so no rebuttal round, yet write the record before the fix
briefs: `.delegation/adjudications/round-1.md`, *"all findings adjudicated REAL;
nothing demoted."*

One fix round, sent by SendMessage to the original agents A and B, context
intact: **A-fix** and **B-fix**. Save `A-fix.md` and `B-fix.md` before sending,
or the steward cannot reconcile the round. Fix agents do not commit.

## 4. RE-REVIEW the dissenters

Send the `correctness` and `overfit/generalization` skeptics back (SendMessage), briefed to probe inputs
that still slip, not to confirm the diff; the PLEASED three stay, since the fix
touched only what the dissenters reviewed. Both return **PLEASED**: converged
([convergence](../skills/consolidating-review/SKILL.md#7-convergence-discipline)),
so write the artifact.

## 5. ARTIFACT → MANAGER INSPECTS → COMMIT

The gate binds an artifact to **one** commit, so the whole tree lands in one.
Write `.delegation/review-artifact.json`
([schema](../skills/skeptical-review/SKILL.md#the-review-artifact-feeds-the-commit-gate)),
its `head_sha` the output of `git rev-parse HEAD`, the parent of that commit
(`null` in a repo with no commits, where it fails).

Work
[the MANAGER INSPECTS list](../skills/delegating/SKILL.md#manager-inspects-the-procedure)
yourself, reconciling every changed path against the five saved briefs (A, B, C,
A-fix, B-fix) plus the reserved set, and re-running the full test command. Then
**one** commit, explicit paths, never `git add -A`; the artifact satisfies the
PreToolUse gate, which step 1 opted the repo into. Archive the artifact to
`.delegation/history/` so the spent PLEASED cannot waive the next batch.

## A steward checkpoint on this run

The [steward](../agents/steward.md) governs the *manager*, not the deliverable.
It runs twice here, healthy and on a counterfactual drift, against the claim
above (falsifiable, not a topic); SHAs are illustrative. Only the manager
commits, so authorship is useless: reconcile against the saved briefs, and a
path outside every allowlist and the reserved `docs/README.md` is the
**unexplained delta**, direct manager work. Save each scorecard to
`.delegation/steward/checkpoint-N.md` so the next catches slow drift.

**Checkpoint 1, just before the commit.** Nothing is committed yet, so reconcile
the working tree: every path is in an allowlist or reserved, and the delta is
empty only because the fix briefs were saved.

```
MANAGER SCORECARD (window: decompose → re-review, pre-commit)

VISION: on-prize
  Prize-movement (MANDATORY): A-fix and B-fix (uncommitted) closed the claim's
    last gaps.
  Evidence: A, B, C each moved a conjunct of the claim.

DELEGATION: delegating-well
  Spawn count (MANDATORY): 8 (A, B, C and five skeptics); fixes went back to A and B.
  Kept-or-delegated (MANDATORY): riskiest build, CSV export, went to A; its
    skeptic caught the bug.
  Evidence: unexplained delta empty; five reviewers cover five distinct risks.

RECOMMENDATION: stay the course — write the artifact, inspect, ship.
```

**Checkpoint 2: a counterfactual drift.** The manager skips the stop at step 5.
Over three more batches it spawns **5** thin polish agents inside allowlists,
moving no claim, while **hand-writing `auth/session.py`**, committed as
`9d1b6e0`: the unexplained delta. A new claim, *"the API requires authenticated
sessions,"* rests on that unreviewed module.

```
MANAGER SCORECARD (window: last 3 checkpoints)

VISION: drifting
  Prize-movement (MANDATORY): none in 3 checkpoints; "the API requires
    authenticated sessions" is gated on 9d1b6e0, which has no skeptic.
  Evidence: 5 agents made only renames / rewording: tidiness, not the claim.

DELEGATION: doing-IC-work, over-spawning, under-delegating
  Spawn count (MANDATORY): 5, all peripheral.
  Kept-or-delegated (MANDATORY): riskiest build, auth/session.py (9d1b6e0),
    stayed in the manager's lap: no builder, skeptic or brief-id.
  Evidence: unexplained delta = auth/session.py; the 5 spawns hid it.

RECOMMENDATION: stop. Pull auth/session.py into a slice with a skeptic.
```
