# Worked example — one delegation, end to end

A domain-neutral walkthrough of the full loop: decompose → implement →
panel → consolidate → fix → re-review → commit. The deliverable is
deliberately generic — a small web service gaining three unrelated
improvements — so you see the machinery without inheriting anyone's domain
assumptions.

**The task:** a `reports-service` needs (1) a **CSV export** endpoint,
(2) a **rate limiter** on its public API, and (3) a **docs update**
describing both.

## 1. DECOMPOSE (manager)

Trivial-edit gate: this is a three-part build touching separate modules —
substantial enough to delegate. Three slices:

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

All disjoint → the three slices may run in parallel via
`superpowers:dispatching-parallel-agents`; each implementer runs under
`superpowers:subagent-driven-development` with the override re-brief:
**"You do not commit. Leave work in the tree; the manager commits."**

## 2. IMPLEMENT

Agents A, B, C work test-first (`superpowers:test-driven-development`) and
report DONE with test evidence. Nothing is committed yet. The manager
watches file-write activity (mtimes / `git status`), not just completion
notifications.

## 3. REVIEW PANEL (manager triage)

Mode triage (breadth-vs-depth × risk): three small, mostly independent
slices; no subtle shared algorithm → **swarm**, 3 skeptics (small change →
2–3 per the sizing heuristic). Lenses: `correctness`,
`evidence-vs-claim`, `honesty/overclaim`. Panel dispatched in parallel over
the **whole integrated tree** — only after all three agents report DONE.

Panel returns:

- correctness — **NOT PLEASED**. `BLOCKING: 1. export/csv.py crashes on an
  empty dataset (unguarded header write on zero rows); the green suite only
  covers populated tables.`
- evidence-vs-claim — **PLEASED** (notes, non-blocking: rate-limiter test
  asserts limiter object configured, would prefer a behavioural
  over-the-limit test; usefulness 3/5).
- honesty/overclaim — **PLEASED**.

## 4. CONSOLIDATE → FIX ROUND

One blocking finding; `consolidating-review` batches it (with the
non-blocking note attached as context) into **one** fix brief for agent A:
add the empty-dataset guard + a red-first regression test. The fix agent
also does not commit.

## 5. RE-REVIEW the dissenter

Only the correctness skeptic re-runs — briefed to probe for inputs that
still slip through (empty dataset, single row, unicode field, delimiter in
value), not just to confirm the diff. It returns **PLEASED**. Strictly less
found than round 1 → the loop converged; no further rounds.

## 6. ARTIFACT → MANAGER INSPECTS → COMMIT

The manager writes the review artifact the commit gate reads:

```json
{
  "deliverable": "reports-service batch: CSV export, rate limiter, API docs",
  "mode": "swarm",
  "rounds": 2,
  "reviews": [
    {"reviewer": "skeptic-A", "lens": "correctness", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-B", "lens": "evidence-vs-claim", "verdict": "PLEASED", "blocking": []},
    {"reviewer": "skeptic-C", "lens": "honesty/overclaim", "verdict": "PLEASED", "blocking": []}
  ],
  "consolidated_blocking": []
}
```

The manager inspects the integrated tree itself (unanimous panel is
necessary, not sufficient), then commits **explicit paths per slice** —
never `git add -A` — as `.delegation/review-artifact.json` satisfies the
PreToolUse gate (the repo opted in when the manager created `.delegation/`
for the checklist in step 1; the gate's five honest limits are in the
[README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline)).
Afterwards it archives the artifact to `.delegation/history/` so the stale
PLEASED cannot waive the next slice.

## A steward checkpoint on this run

The [steward](../agents/steward.md) governs the *manager*, not the deliverable,
and is consulted repeatedly across a run. Here it is run twice against this
exact scenario — once where the manager is healthy, once on a counterfactual
where it drifts — so the discipline is demonstrated, not asserted. The
**load-bearing claim** the manager was handed (a falsifiable claim, not a
topic): *"reports-service exposes a CSV export and a rate limiter, both
documented, and the export produces valid CSV for empty, single-row, and
unicode inputs."* SHAs below are illustrative for this walkthrough.

**Building the allowlist set (the mechanical detector).** Only the manager
commits, so authorship is useless; the steward reconciles against the briefs
instead. From the checklist in step 1: agent allowlists are `export/` +
`tests/export/` (A), `middleware/` + `tests/middleware/` (B), `docs/api.md`
(C); the reserved-index set is `docs/README.md`. Anything committed outside
that union is the **unexplained delta** = direct manager work.

**Checkpoint 1 — taken just before commit (step 6).** Commits this window:
`a1f30c2` (A, in `export/`), `b7e2d41` (B, in `middleware/`), `c4a8f09` (C, in
`docs/api.md`), `4f2a1c9` (fix round on A, in `export/`), plus a `docs/README.md`
index touch. Reconciliation: every change lands inside an allowlist except
`docs/README.md`, which is in the reserved set (legitimate integration wiring).
**Unexplained delta: empty.**

```
MANAGER SCORECARD (window: decompose → re-review, pre-commit)

VISION: on-prize
  Prize-movement (MANDATORY): 4f2a1c9 — the empty-dataset guard closed the last
    open correctness gap; the claim now holds for empty / single-row / unicode.
  Evidence: A, B, C each moved a conjunct of the stated claim (export, limiter,
            docs); no slice was off-claim polish.

DELEGATION: delegating-well
  Spawn count (MANDATORY): 4 (A, B, C, + one fix agent).
  Kept-or-delegated (MANDATORY): highest-risk build = CSV export correctness
    (empty-dataset edge); delegated to agent A and caught by its own correctness
    skeptic, fix delegated too. Nothing risky kept in the manager's lap.
  Evidence: unexplained delta empty; only reserved docs/README.md touched
            directly; panel 3 skeptics with diverse lenses, right-sized for a
            small change.

RECOMMENDATION: stay the course — write the artifact, inspect, ship.
```

**Checkpoint 2 — a counterfactual drift.** Suppose the manager does *not* stop
at step 6. Over the next three checkpoints it spawns **5** thin agents on polish
(rename variables in `export/`, reword `docs/api.md`, split it into two pages,
tidy imports, reformat) — all inside allowlists, none moving any claim — while
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

- The trivial-edit gate, checklist-forced fan-out, and disjoint parallelism.
- The skeptic law: every slice (including the docs slice) faced at least one
  adversarial reviewer.
- A green suite hiding a real bug (empty dataset) that an adversarial
  correctness lens caught — the reason the panel exists.
- One consolidated fix round, dissenter-only re-review, convergence.
- Both posture overrides: no auto-commit on DONE; implementers never
  self-commit — the manager committed once, after the gate.
- The steward run twice against the same scenario — a mechanical allowlist
  reconciliation, mandatory falsifiable slots, and both a `stay-the-course` and
  a `drifting` scorecard — governing the manager, not the deliverable.
