---
name: consolidating-review
description: Use after a skeptic panel returns findings - batches all BLOCKING items into one reconciled fix round, re-reviews only the dissenters, and drives the loop to convergence
---

# Consolidating Review

The step between a panel's verdicts and a commit-worthy tree. Never
dispatch fixes piecemeal, one per finding — batch.

## 1. Consolidate

Collect every numbered BLOCKING item from every NOT PLEASED reviewer into
**one** consolidated list, then reconcile it:

- **Deduplicate** — two lenses often hit the same defect from different
  angles; merge them, keep both framings as context.
- **Resolve contradictions** — if two reviewers demand opposite fixes, the
  manager adjudicates *before* dispatching, or the fix agent will thrash.
  Record the adjudication next to the item.
- **Attach relevant non-blocking notes** as context for the fix agent, but
  keep them clearly labelled — they do not gate.

## 2. One reconciled fix round

Dispatch **one fix round** covering the whole consolidated list (grouped by
slice owner if slices are disjoint), via
`superpowers:subagent-driven-development` — with the standard override
re-brief: **the fix agent does not commit**; work stays in the tree.
Fix agents re-run the tests covering their changes and report evidence
(`superpowers:verification-before-completion` applies).

## 3. Re-review the dissenters

Re-dispatch **only the specific reviewers who were NOT PLEASED**, with their
own BLOCKING list and the fix report. Brief them to **probe for inputs that
still slip through, not just confirm the diff** — "re-verify, don't trust
the fix report." PLEASED reviewers from the prior round are not re-run
unless the fix touched what they reviewed.

## 4. Convergence discipline

- The loop **converges**: each re-review must find **strictly less** than
  the round before. Same-or-more findings two rounds running means the slice
  was mis-scoped or the fix round was dispatched piecemeal — stop and
  re-plan; do not grind rounds.
- If late rounds only surface new one-line nits, fix them directly and close
  on an **exhaustive manager check** instead of another panel round.
- Only when **every** reviewer is PLEASED does the artifact get written
  ([`../skeptical-review/SKILL.md`](../skeptical-review/SKILL.md)) and the
  manager inspect + commit.

Verdict format being consolidated: [`../../docs/rubric.md`](../../docs/rubric.md).
