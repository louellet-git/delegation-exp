---
name: consolidating-review
description: Adjudicates a panel's BLOCKING findings with the fluff gate, runs one fix round and re-reviews the dissenters. Use when any reviewer returns NOT PLEASED.
---

<!--
  Owner authorization for the fluff gate. The do-not-modify guard
  (../../README.md) requires framework changes to carry explicit owner
  authorization; this one's, verbatim: "I'd like it to have this, like, gate
  that is effectively, like, is this fluff or is this required? Because...
  after the reviewer agents actually do their review, on things that they're
  not pleased about or supposed blockers, we need to actually consider if
  those blockers are blockers or if they're just fluff. If you can figure out
  a way to implement that, and then obviously have reviewers make sure
  they're pleased after doing it."
-->

# Consolidating Review

## 1. Consolidate

Merge every numbered BLOCKING item from every NOT PLEASED reviewer into one
list, deduplicated across lenses with each framing kept. Rule on
contradicting fixes before dispatch and record the ruling in
`.delegation/adjudications/`, or the fix agent thrashes. Attach relevant non-blocking notes, labelled so.

## 2. Adjudicate: the fluff gate

Before any fix round, adjudicate every consolidated BLOCKING item: REAL
gates; FLUFF is demoted to non-blocking or discarded, with a written reason.

REAL if the finding's own evidence shows one of:

1. **A concrete user-visible failure**: named input, action and wrong
   result, not "could confuse users".
2. **A violated written contract or invariant** of the repo or dispatch,
   cited file:line; prose overclaiming what the machinery does breaks one.
3. **A data, money, privacy or security exposure**, path named.
4. **A reproducible defect with evidence**: "I ran X, got Y, expected Z."

FLUFF if its evidence, once read, shows:

1. **Taste**: style, naming or structure, no failure behind it.
2. **Scope creep**: work the dispatch never asked for.
3. **Hypothetical without a trigger**: none named and observable, or one
   that dissolves when you re-run its own repro (cite the re-run).
4. **Redundant with an accepted limit**: one the deliverable, dispatch or a
   prior adjudication names, and the system really holds.
5. **An improvement framed as a defect**: "should also", "would be better".

A finding not confidently FLUFF, or meeting any REAL head, gates; demote
only the wrapping around a REAL defect. Adjudicate on its
[rubric](../../docs/rubric.md) fields (MISS line, file:line, claims vs
establishes); return an item lacking them to its reviewer, never guessing.
Close calls may go to the [steward](../../agents/steward.md), whose subject
is manager conduct; its read is advisory, and a dispute goes to the owner.

## 3. The rebuttal round: no silent demotions

Tell each demotion, with its reason, to the finding's reviewer: the
original if still live, else its lens re-dispatched fresh with the finding.
It gets one REBUTTAL (rubric): CONCEDE, and the demotion stands, or STAND
with new evidence, and you re-adjudicate; restated old evidence concedes.
Rebut before the fix round, so a flip joins its batch. No round three: once
spent, the demotion is an accepted limit of this batch, and a same-evidence
re-raise goes back with a pointer to the record. New evidence is a new
finding.

## 4. The adjudication record (a required artifact)

Before every fix round write `.delegation/adjudications/round-<N>.md`, even
just "all findings adjudicated REAL; nothing demoted", so a missing record
never hides demotions. Per finding:

```
ADJUDICATION <deliverable> round <N>

Finding <#> (<lens> / <reviewer>): REAL | FLUFF
  Yardstick: <the REAL or FLUFF head>
  Reason: <one concrete sentence on the evidence the finding cited>
  Rebuttal: n/a (REAL) | conceded | stood — <new evidence> | spent — <old evidence restated>
  Final: gates (fix round) | demoted to non-blocking | discarded | escalated to owner
```

The steward reads it and flags heavy demotion; the review artifact may
summarize it ([skeptical-review](../skeptical-review/SKILL.md)).

## 5. One reconciled fix round

One fix round, never one per finding, covers every surviving finding (REAL
plus flipped demotions), sent back to each slice's original agent
([rule](../delegating/SKILL.md#one-scoped-task-per-fresh-subagent)). Write its brief
from [the template](../delegating/SKILL.md#the-brief-template), every slot
plus the surviving list, and save it to `.delegation/briefs/<slice-id>-fix.md`
before dispatch, for the steward and diff reconciliation. The fix agent does
not commit; it re-runs the tests covering its change and reports command and
output. Demoted findings ride along labelled non-blocking.

## 6. Re-review the dissenters

Send only the NOT PLEASED reviewers back
with their BLOCKING list, the fix report and the record, briefed: "re-verify, don't trust the fix report";
probe for inputs that still slip through. Re-run a PLEASED reviewer only if
the fix touched its area. With its REAL findings fixed and its demotions
conceded or spent, a reviewer returns PLEASED, listing them non-blocking.
If one still holds NOT PLEASED, escalate to the owner with the record:
verdicts must be exactly PLEASED, and writing one nobody returned is
fabrication.

## 7. Convergence discipline

- Converge by severity and region: each round's findings must be less severe and sit in the region the last fix changed; a blocker at the same severity in the same file section two rounds running means stop and re-plan.
  Such a repeat means a mis-scoped slice or piecemeal fixes.
- One-line-nit shortcut: if late rounds surface only one-line nits, skip
  another full panel, never the verdicts. Dispatch one final fix round
  (fixing them yourself is implementer work), re-review only the dissenters, and add
  your own exhaustive check.
- All PLEASED: write
  [the artifact](../skeptical-review/SKILL.md#the-review-artifact-feeds-the-commit-gate),
  then [the manager inspects](../delegating/SKILL.md#manager-inspects-the-procedure)
  and commits once.

## Honest limits (of the fluff gate)

- It raises the cost of fluff and of bulldozing (demoting real findings to
  reach all-PLEASED) through the rebuttal round, the steward's flag to the
  owner and the record; it prevents neither, and cannot certify a ruling.
- The commit gate never reads the record: a fabricated one passes.
- A reviewer can cave undetected; the record keeps its original finding.
