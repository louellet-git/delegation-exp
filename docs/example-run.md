# Worked example: one delegation, end to end

A domain-neutral walkthrough of the full loop: decompose → implement →
panel → consolidate → adjudicate → fix → re-review → commit. The deliverable is
deliberately generic (a small web service gaining three unrelated
improvements) so you see the machinery without inheriting anyone's domain
assumptions.

**The task:** a `reports-service` needs (1) a CSV export endpoint,
(2) a rate limiter on its public API, and (3) a docs update
describing both.

## 1. DECOMPOSE (manager)

Trivial-edit gate: this is a three-part build touching separate modules,
substantial enough to delegate.

**Arm the repo, and gitignore the marker in the same step.** Before anything
else the manager runs:

```
mkdir -p .delegation/briefs .delegation/steward
grep -qxF '.delegation/' .gitignore || echo '.delegation/' >> .gitignore
```

The `.gitignore` line is required: a marker committed with the repo turns the
gate off ([README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline)).

**Scouting.** `reports-service` is a repo this manager already knows, so the
bounded structural pass applies: `git ls-files`, the `pyproject.toml` test
config, nothing else. The manager reads no module bodies. On an unfamiliar repo
this step would instead be a delegated read-only scouting slice, because the
allowlists and the exact test commands below cannot be invented
([the DECOMPOSE procedure](../skills/delegating/SKILL.md#decompose-the-procedure)).

**Sizing the batch.** Three unrelated changes to one service, integrated and
landed together under one panel and one commit, is a **feature batch**, not a
small change. That word decides the panel size later (5 to 7, not 2 to 3), so
it is worth settling here rather than at dispatch time.

Three slices:

| Slice | Scope | Risk |
|-------|-------|------|
| A | `export/csv.py` + tests | medium (data edge cases) |
| B | `middleware/ratelimit.py` + tests | medium (timing, limits) |
| C | `docs/api.md` update | low |

Fill the [conflict-avoidance checklist](conflict-avoidance-checklist.md)
**before** fanning out:

```markdown
# Conflict-avoidance checklist — reports-service batch — 2026-07-21

- [x] Disjoint directories: A=export/, B=middleware/, C=docs/ — pairwise disjoint.
- [x] Reserved index files: docs/README.md index reserved to the manager.
- [x] Pre-assigned numbers: no ADRs this run — n/a.
- [x] File-ownership allowlists: in each brief (below).
- [x] Exact test command: A: pytest tests/export/ ; B: pytest tests/middleware/ ; C: n/a (docs), link check instead.
```

All disjoint → the three slices may run in parallel: one fresh implementer
per slice, spawned as a general-purpose worker subagent with the whole brief in
its prompt, each brief written from
[the template](../skills/delegating/SKILL.md#the-brief-template) and saved to
`.delegation/briefs/A.md`, `B.md`, `C.md` **before** dispatch (the steward
reconciles against those files later; without them its DELEGATION line is
unrecoverable). Every brief carries the allowlist, the exact test command, the
acceptance condition, the test-first and evidence-before-claims postures, the
status contract, and the standing re-brief **"You do not commit or push. Leave
work in the tree; the manager commits once, after review."** The template's
other slots are filled rather than dropped, even when the answer is nothing:
PRE-ASSIGNED NUMBERS reads "none this run" (the checklist assigned no ADRs),
and because all three slices run in parallel on clean paths, WHAT THE
PREDECESSOR CHANGED reads "nothing: no slice ran before you on these paths" and
PARTIAL WORK ALREADY IN THE TREE reads "none: your paths are clean". A slot
filled with "none" tells the agent the question was asked; a missing slot tells
it nothing.

## 2. IMPLEMENT

Agents A, B, C work test-first, read the files their own slices need, and
report DONE with test evidence. The manager reads none of those files; it
reads three reports. Nothing is committed yet. The manager
watches file-write activity (mtimes / `git status`), not just completion
notifications.

## 3. REVIEW PANEL (manager triage)

Size first: this is a feature batch, so the heuristic says 5 to 7 and this
panel is **5**. Mode triage (breadth-vs-depth × risk): three separate slices,
no subtle shared algorithm, and nothing here scores or ranks anything, so no
lens forces deep mode → **swarm**, all five in parallel. Lenses, from the
catalogue's feature-batch line: `correctness`,
`coupling/boundary-integrity`, `overfit/generalization`, `evidence-vs-claim`,
`honesty/overclaim`. Panel dispatched in parallel over
the whole integrated tree, only after all three agents report DONE.

Panel returns:

- correctness: **NOT PLEASED**. `BLOCKING: 1. export/csv.py crashes on an
  empty dataset (unguarded header write on zero rows); the green suite only
  covers populated tables.`
- coupling/boundary-integrity: **PLEASED**.
- overfit/generalization: **NOT PLEASED**. `BLOCKING: 1.
  middleware/ratelimit.py counts per fixed calendar minute and the only test
  drives it with the clock frozen at the start of a window; a burst straddling
  the boundary passes twice the limit and the suite stays green.`
- evidence-vs-claim: **PLEASED** (notes, non-blocking: rate-limiter test
  asserts limiter object configured, would prefer a behavioural
  over-the-limit test; usefulness 3/5).
- honesty/overclaim: **PLEASED**.

## 4. CONSOLIDATE → ADJUDICATE → FIX ROUND

Two blocking findings, in disjoint slices, deduplicated into one consolidated
list. A BLOCKING tag does not gate work by itself, so before any fix is
dispatched the manager adjudicates both against
[the fluff-gate yardstick](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate):

- The empty-dataset crash is **REAL** — a reproducible defect with evidence
  (REAL head 4): the reviewer named the unguarded header write and the
  zero-row input that reaches it, and the green suite's silence on exactly
  that input is the finding's own MISS line.
- The window-boundary burst is **REAL** — a concrete user-visible failure
  (REAL head 1): a named caller, bursting across a minute boundary, passes
  twice the limit; and the limit is the slice's own written acceptance
  condition, so head 2 holds too.

Nothing demoted, so no rebuttal round runs, but the record is written anyway,
**before** the fix briefs. `.delegation/adjudications/round-1.md`, in full:
*"all findings adjudicated REAL; nothing demoted."*

`consolidating-review` then reconciles the two survivors into **one** fix
round and dispatches it grouped by slice owner, a fresh agent per group:

- **A-fix** (`export/`): add the empty-dataset guard plus a red-first
  regression test.
- **B-fix** (`middleware/`): make the window behaviour correct across a
  boundary, plus a behavioural over-the-limit test. The `evidence-vs-claim`
  non-blocking note about the limiter test asserting configuration rather than
  behaviour is attached to this brief as context, clearly labelled as
  non-blocking, because it is the same defect seen from another angle.

Both fix briefs are written from the same canonical template as A, B and C and
saved to `.delegation/briefs/A-fix.md` and `.delegation/briefs/B-fix.md`
**before** dispatch, with each one's PARTIAL WORK slot naming what its
predecessor left in those paths. Otherwise the fix round is the part of the run
the steward cannot reconcile later. The fix agents also do not commit.

## 5. RE-REVIEW the dissenters

Only the two dissenters re-run, `correctness` and `overfit/generalization` —
briefed to probe for inputs that still slip through (empty dataset, single row,
unicode field, delimiter in value; a burst straddling the window boundary, a
clock that jumps), not just to confirm the diff. The three PLEASED reviewers
are not re-run: the fix touched only what the dissenters reviewed. Both return
**PLEASED**. No finding left, so the loop converged by severity and region
([consolidating-review](../skills/consolidating-review/SKILL.md#7-convergence-discipline)); no further
rounds, and because nobody is left holding NOT PLEASED there is an artifact to
write.

## 6. ARTIFACT → MANAGER INSPECTS → COMMIT

The gate binds a review artifact to **one** commit, so this batch is landed by
a single commit over the integrated tree, not one commit per slice. The manager
reads the SHA the artifact must be bound to, which is the current HEAD, the
parent of the commit it is about to make:

```
$ git rev-parse HEAD
7c1d9ab4f2e08d3c5b6a1907e4d2f83c9a0b5e61
```

then writes `.delegation/review-artifact.json`:

```json
{
  "deliverable": "reports-service batch: CSV export, rate limiter, API docs",
  "mode": "swarm",
  "rounds": 2,
  "head_sha": "7c1d9ab4f2e08d3c5b6a1907e4d2f83c9a0b5e61",
  "reviews": [
    {"reviewer": "skeptic-1", "lens": "correctness", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-2", "lens": "coupling/boundary-integrity", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-3", "lens": "overfit/generalization", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-4", "lens": "evidence-vs-claim", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-5", "lens": "honesty/overclaim", "verdict": "PLEASED", "blocking": []}
  ],
  "consolidated_blocking": []
}
```

In a repo with no commits at all, `git rev-parse HEAD` fails and `head_sha` is
`null`.

The manager then works
[the MANAGER INSPECTS list](../skills/delegating/SKILL.md#manager-inspects-the-procedure)
itself, because a unanimous panel is necessary and not sufficient: it reads
`git diff` over the integrated tree, reconciles every changed path against the
five saved briefs (A, B, C, A-fix, B-fix) plus the reserved index set, re-runs
the full test command and keeps the output, checks the artifact field by field
(non-empty `deliverable`, valid `mode`, a `lens` on every review, every verdict
exactly `PLEASED`, every `blocking` list and `consolidated_blocking` empty,
`head_sha` equal to HEAD right now), and checks `.delegation/` is gitignored
and unstaged.
Then **one** commit, staging explicit paths, never `git add -A`, which
`.delegation/review-artifact.json` satisfies for the PreToolUse gate (the repo
opted in when the manager created `.delegation/` in step 1; the gate's five
honest limits are in the
[README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline)).
Afterwards it archives the artifact to `.delegation/history/` so the spent
PLEASED cannot waive the next batch.

## A steward checkpoint on this run

The [steward](../agents/steward.md) governs the *manager*, not the deliverable,
and is consulted repeatedly across a run. Here it is run twice against this
exact scenario, once where the manager is healthy and once on a counterfactual
where it drifts, so the discipline is demonstrated, not asserted. The
**load-bearing claim** the manager was handed (a falsifiable claim, not a
topic): *"reports-service exposes a CSV export and a rate limiter, both
documented, and the export produces valid CSV for empty, single-row, and
unicode inputs."* SHAs below are illustrative for this walkthrough.

**Building the allowlist set (the mechanical detector).** Only the manager
commits, so authorship is useless; the steward reconciles against the briefs
saved in `.delegation/briefs/` instead. From those briefs and the checklist in
step 1: agent allowlists are `export/` + `tests/export/` (A), `middleware/` +
`tests/middleware/` (B), `docs/api.md` (C); the reserved-index set is
`docs/README.md`. Anything outside that union is the **unexplained delta** =
direct manager work. Each scorecard below is saved to
`.delegation/steward/checkpoint-1.md` and `checkpoint-2.md`, so the next
checkpoint can compare against it and catch slow directional drift.

**Checkpoint 1 (taken just before the commit in step 6).** This batch has not
been committed yet, which is the normal state at this checkpoint: one panel
waives one commit, so nothing lands until step 6. The window is therefore
reconciled against the **working tree**, not against commits. `git status`
shows changes in `export/` + `tests/export/` (A, including the fix round from
brief `A-fix`), `middleware/` + `tests/middleware/` (B, including brief
`B-fix`), `docs/api.md` (C), and
`docs/README.md`. Reconciliation: every path lies inside an agent allowlist
except `docs/README.md`, which is in the reserved set (legitimate integration
wiring). **Unexplained delta: empty.** That reconciliation only works because
the two fix briefs were saved like the other three: an unsaved fix round would
have turned its own changes into an unexplained delta.

```
MANAGER SCORECARD (window: decompose → re-review, pre-commit)

VISION: on-prize
  Prize-movement (MANDATORY): brief A-fix (uncommitted, in export/csv.py) — the
    empty-dataset guard closed the last open correctness gap; the claim now
    holds for empty / single-row / unicode. Brief B-fix closed the limiter's
    window-boundary gap behind it.
  Evidence: A, B, C each moved a conjunct of the stated claim (export, limiter,
            docs); no slice was off-claim polish.

DELEGATION: delegating-well
  Spawn count (MANDATORY): 5 (A, B, C, + two fix agents, one per affected slice).
  Kept-or-delegated (MANDATORY): highest-risk build = CSV export correctness
    (empty-dataset edge); delegated to agent A and caught by its own correctness
    skeptic, fix delegated too. Nothing risky kept in the manager's lap.
  Evidence: unexplained delta empty; only reserved docs/README.md touched
            directly; panel 5 skeptics with diverse lenses, right-sized for a
            feature batch (2-3 would have been the small-change size, and this
            is not one).

RECOMMENDATION: stay the course — write the artifact, inspect, ship.
```

**Checkpoint 2: a counterfactual drift.** Suppose the manager does *not* stop
at step 6. Over the next three checkpoints, three further batches each panelled
and landed as one commit, it spawns **5** thin agents on polish
(rename variables in `export/`, reword `docs/api.md`, split it into two pages,
tidy imports, reformat), all inside allowlists and none moving any claim, while
**hand-writing a new `auth/session.py` module itself** and committing it as
`9d1b6e0`. `auth/` is outside every agent allowlist and outside the reserved
set → it is the unexplained delta. A new stated claim, *"the API requires
authenticated sessions,"* is gated entirely on that un-reviewed module.

```
MANAGER SCORECARD (window: last 3 checkpoints)

VISION: drifting
  Prize-movement (MANDATORY): none in 3 checkpoints — the claim "the API
    requires authenticated sessions" is gated on 9d1b6e0 (auth/session.py),
    which carries no skeptic, so no reviewed work has moved it.
  Evidence: 5 agents produced only renames / reformat / prose — zero claim
            movement; the stated claim quoted vs. what the window optimized
            (tidiness) shows the gap.

DELEGATION: doing-IC-work, over-spawning, under-delegating
  Spawn count (MANDATORY): 5 this window, all peripheral.
  Kept-or-delegated (MANDATORY): highest-risk build = auth/session.py (9d1b6e0),
    kept in the manager's own lap / unexplained delta — no independent builder,
    no skeptic. Brief-id that should have owned it: none was written.
  Evidence: unexplained delta = auth/session.py, outside {export/, middleware/,
            docs/api.md, tests/...} and outside reserved {docs/README.md}; the
            5 spawns hid the one build that most needed delegating.

RECOMMENDATION: stop. Pull auth/session.py back into a proper slice with a
                skeptic (correctness + injection-path); cancel the polish
                agents; re-anchor the next dispatch on the load-bearing claim.
```

Running the template surfaced two things the prose alone hid: authorship cannot
detect direct manager work (the delta reconciliation had to replace it), and an
adjective in an Evidence line hides drift that a forced SHA / spawn-count /
brief-id exposes.

## What this run demonstrates

- The trivial-edit gate, arming the repo and gitignoring the marker in one
  step, checklist-forced fan-out, and disjoint parallelism.
- Briefs written from the template and persisted to `.delegation/briefs/`
  before dispatch, **fix-round briefs included**, which is what makes the
  steward's reconciliation possible.
- Panel sized to the work rather than to habit: a feature batch got 5 lenses,
  not the 2 to 3 a small change would have got.
- The skeptic law: every slice (including the docs slice) faced at least one
  adversarial reviewer.
- A green suite hiding two real bugs (an empty dataset, a rate-limit window
  boundary) that adversarial `correctness` and `overfit/generalization` lenses
  caught, which is the reason the panel exists.
- Both BLOCKING findings adjudicated through the fluff gate before any fix was
  dispatched — both REAL, each pinned to a yardstick head, and the
  adjudication record written first even with nothing demoted, so what gated
  had earned it and the record says so.
- One consolidated fix round covering both surviving findings, dissenter-only
  re-review, convergence with every reviewer PLEASED before any artifact was
  written.
- Both posture rules: no auto-commit on DONE; implementers never
  self-commit; the manager committed once, after the gate.
- One panel, one commit: the whole batch integrated, reviewed as a tree, and
  landed in a single commit whose parent SHA is the artifact's `head_sha`.
- The steward run twice against the same scenario (a mechanical allowlist
  reconciliation, mandatory falsifiable slots, and both a `stay-the-course` and
  a `drifting` scorecard), governing the manager, not the deliverable.
