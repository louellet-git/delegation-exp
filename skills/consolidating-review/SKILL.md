---
name: consolidating-review
description: Use after a skeptic panel returns findings - adjudicates every BLOCKING item against the fluff-gate yardstick (real defects gate; fluff is demoted on the record, with one rebuttal round), batches the survivors into one reconciled fix round, re-reviews only the dissenters, and drives the loop to convergence
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

The steps between a panel's verdicts and a commit-worthy tree. Two rules
govern them. Never dispatch fixes piecemeal, one per finding: batch them.
And never let a finding gate work just because a reviewer wrote the word
BLOCKING next to it: adjudicate it first.

## 1. Consolidate

Collect every numbered BLOCKING item from every NOT PLEASED reviewer into
**one** consolidated list, then reconcile it:

- **Deduplicate.** Two lenses often hit the same defect from different
  angles; merge them, keep both framings as context.
- **Resolve contradictions.** If two reviewers demand opposite fixes, the
  manager adjudicates *before* dispatching, or the fix agent will thrash.
  Record the adjudication next to the item.
- **Attach relevant non-blocking notes** as context for the fix agent, but
  keep them clearly labelled, because they do not gate.

## 2. Adjudicate: the fluff gate

A BLOCKING finding is a claim, and this framework trusts no claim on
arrival — not an implementer's DONE, and not a reviewer's BLOCKING either.
Before any fix round is dispatched, the manager adjudicates **every**
consolidated BLOCKING item against the yardstick below. REAL findings gate:
they enter the fix round and the commit waits on them. FLUFF is **demoted
to non-blocking or discarded**, with a written reason, on the record, and
the reviewer is told (sections 3 and 4 — there are no silent demotions).

The gate lives in this skill rather than in a sibling, deliberately: every
NOT PLEASED verdict already routes through consolidation, so adjudication
placed here cannot be skipped without skipping consolidation itself.

### The yardstick: REAL | FLUFF

A finding is **REAL** — it gates — if its own evidence establishes at least
one of:

1. **A concrete user-visible failure.** Someone using the thing hits it:
   named input, named action, named wrong result. Not "could confuse
   users" — a user, doing what, seeing what.
2. **A violated written contract or invariant.** A requirement, spec line,
   config rule, or invariant that this repo or the dispatch wrote down,
   cited by file:line, that the deliverable breaks. Prose that promises what
   the machinery cannot deliver breaks the contract it is itself writing,
   which is where honesty/overclaim findings land.
3. **A data, money, privacy, or security exposure.** A path by which data is
   lost or leaked, money is spent or mischarged, or an attacker gains
   something — with the path named, not gestured at.
4. **A reproducible defect with evidence.** A command that was run and
   output that shows the wrong behaviour: "I ran X, got Y, expected Z."

It is **FLUFF** — demote or discard — if, once its evidence fields are
actually read, what it is turns out to be:

1. **Taste.** A style, naming, or structure preference with no failure
   behind it.
2. **Scope creep.** Work the dispatch never asked for, filed as a defect in
   the work it did ask for.
3. **Hypothetical without a trigger — or a trigger that dissolves on
   reproduction.** "Could break if…" with no named, observable condition
   that reaches it; or concrete-looking evidence that does not survive
   re-running the finding's own repro. The steward's rule for hurdles
   applies to skeptics too: no trigger, no raise — and a trigger that was
   checked and shown not to fire is no trigger.
4. **Redundant with an accepted limit.** The deliverable, the dispatch, or a
   previous adjudication already names this limit and accepts it. Restating
   an accepted limit is not finding a defect.
5. **An improvement framed as a defect.** "Should also", "should instead",
   "would be better" — possibly true, never blocking.

**The tie-break runs toward REAL.** A finding you cannot confidently place
under one of the five fluff heads gates. The gate exists to stop taste from
gating work, not to hand the manager a shrug that outranks evidence. And
the heads do not compete: **REAL trumps FLUFF.** A finding that establishes
any REAL head gates, however much taste or scope creep is wrapped around
it — demote the wrapping in your written reason if you must, never the
defect. The reproduction clause of fluff head 3 cuts the other way only by
being *used*: demoting on it means actually re-running the repro and citing
the re-run, not asserting that a re-run would probably clear it.

**What makes a finding adjudicable is the rubric.** The per-finding format
([`../../docs/rubric.md`](../../docs/rubric.md)) forces a "what it would
MISS" line, a file:line citation, and a claims-vs-establishes split, and
those fields are exactly what you adjudicate against: a finding whose MISS
line names a concrete break is halfway to REAL on its own, and a finding
whose MISS line is empty or vibes is adjudicated on that emptiness. A
BLOCKING item that did not arrive in rubric shape goes back to its reviewer
for the missing fields before it is adjudicated at all — do not guess at
evidence the reviewer failed to supply.

**Close calls may go to the steward.** Not to review the deliverable — that
is the skeptic's job and stays it — but to review *you*: whether the
demotion you are about to write serves the stated goal or your convenience
is manager conduct, which is the steward's exact subject. Its read is
advisory like every other steward read, and a manager↔steward disagreement
about a demotion escalates where those disputes always go: the owner.

### Worked adjudications (three, kept generic)

**"The confirmation badge is clipped by the tab bar" → FLUFF, demoted.** A UI
skeptic files BLOCKING: on a small viewport the confirmation badge is cut
off by the bottom tab bar, evidence a screenshot. Re-running its own repro
shows the badge sits *below the scroll fold* and is fully visible after the
ordinary scroll the page is built for; the screenshot was an unscrolled
viewport read as a final state. No written requirement says the badge must
sit above the fold. That is fluff head 3's reproduction clause — a trigger
that dissolves when the finding's own repro is re-run — demoted with the
re-run as the written reason. The reviewer, shown the re-run, conceded.

**"The public endpoint sets no maxInstances" → REAL, gates.** An
infrastructure skeptic files BLOCKING: the new public function omits an
instance cap. The dispatch's requirements say every public endpoint carries
a bounded blast radius, cited to the config rule file:line, and an
uncapped public endpoint under abuse is an unbounded bill. That is REAL
twice over — a violated written invariant (head 2) and a money exposure
with the path named (head 3). It enters the fix round; nothing to rebut.

**"The CSV writer buffers instead of streaming" → FLUFF, then REAL on
rebuttal.** A correctness skeptic files BLOCKING: the export buffers the
whole result in memory and should stream. The dispatch caps exports at ten
thousand rows, which buffers comfortably, so the manager demotes: an
improvement framed as a defect (head 5), inside an accepted limit (head 4).
The reviewer does not concede — it **stands, with new evidence**: an
existing consumer already exports two million rows through the old path,
cited to the code that does it, so the "accepted limit" was never true of
the system. Re-adjudicated REAL (head 1: a named user, doing a named
export, hitting a named failure) and into the fix round it goes. That is
the rebuttal round doing its job: the gate raised the cost of a lazy
demotion, and new evidence flipped it.

## 3. The rebuttal round: no silent demotions

Every demotion is told to the finding's original reviewer, with the written
reason, and the reviewer gets **exactly one** structured reply — the
REBUTTAL block in [`../../docs/rubric.md`](../../docs/rubric.md):

- **CONCEDE.** The demotion stands; the finding lives on as non-blocking or
  is discarded, per the record.
- **STAND, with NEW evidence.** Evidence the original finding did not
  contain: a command run, a line cited, a consumer named. The manager
  re-adjudicates against the yardstick with the new evidence in hand.
  Standing on the *old* evidence restated louder is a concession with extra
  words, and is recorded as one.

One round, then it is spent. In practice reviewers are one-shot spawns, so
"tell the original reviewer" usually means re-dispatching the same lens
fresh, briefed with its predecessor's finding, the demotion, and the
reason; if the runtime still holds the original reviewer, message it
instead. Run the rebuttals **before** dispatching the fix round, so a
demotion that flips re-enters the same batch instead of forcing a second
round — that ordering is what keeps one-reconciled-fix-round true.

There is no round three. A finding demoted after its rebuttal is spent is
an **accepted, recorded limit of this batch**, and re-raising it with the
same evidence at re-review is noise, not dissent (section 6). Genuinely new
evidence is different: it makes a **new finding**, adjudicated fresh like
any other. That asymmetry is the whole design — evidence always has a door,
repetition never does.

## 4. The adjudication record (a required artifact)

Adjudication that leaves no record is indistinguishable from bulldozing,
so the record is mandatory, in the same register as the review artifact:
write `.delegation/adjudications/round-<N>.md` **before** the fix round is
dispatched, every round, even when it is the one line "all findings
adjudicated REAL; nothing demoted" — an absent record must never be
ambiguous between "nothing demoted" and "demotions nobody wrote down". Per
finding:

```
ADJUDICATION <deliverable> round <N>

Finding <#> (<lens> / <reviewer>): REAL | FLUFF
  Yardstick: <the REAL head it satisfies, or the FLUFF head it falls under>
  Reason: <one concrete sentence, engaging the same evidence the finding cited>
  Rebuttal: n/a (REAL) | conceded | stood — <the new evidence> | spent — <restated old evidence>
  Final: gates (fix round) | demoted to non-blocking | discarded | escalated to owner
```

The record is for the reviewers, the steward, and the next reader, not for
the commit gate: the gate does not read it (honest limits, below). The
steward *does* read it — `.delegation/` is its evidence base — and a round
where half the BLOCKING list was demoted is exactly the skipping-its-own-gate
conduct it exists to flag. The review artifact may also carry an optional
`adjudications` array summarizing the record, same status as `escalations`
([`../skeptical-review/SKILL.md`](../skeptical-review/SKILL.md)): read by
people, ignored by the gate.

## 5. One reconciled fix round

Dispatch one fix round covering every **surviving** finding — the REAL
ones, plus any demotion a rebuttal flipped (grouped by slice owner if
slices are disjoint) to a fresh subagent per group
([`../delegating/SKILL.md`](../delegating/SKILL.md#the-loop-mechanics)), with
the standing re-brief: **the fix agent does not commit**; work stays in the
tree. Fix agents re-run the tests covering their changes and report the
command and its output, not a claim that it passed. Demoted findings ride
along only as clearly-labelled non-blocking context, exactly like any other
non-blocking note: the fix agent must be able to tell what gates from what
merely informs.

**A fix brief is a brief.** Write it from
[the canonical template](../delegating/SKILL.md#the-brief-template) like any
other dispatch, filling the same slots (allowlist, exact test command,
acceptance condition, postures, status contract) plus the surviving
consolidated list this round is fixing, and **save it to
`.delegation/briefs/<slice-id>-fix.md` before dispatching it**. That
directory is the steward's evidence base and the set the manager reconciles
the integrated diff against, and a fix round is where an unexplained delta
is most likely to appear: it is the round most often improvised, and the
one whose changes nobody planned an allowlist for.

## 6. Re-review the dissenters

Re-dispatch only the specific reviewers who were NOT PLEASED, with their
own BLOCKING list, the fix report, **and the adjudication record**. Brief
them to **probe for inputs that still slip through, not just confirm the
diff**: "re-verify, don't trust the fix report." PLEASED reviewers from the
prior round are not re-run unless the fix touched what they reviewed.

Closure is on the *surviving* findings. A reviewer whose real findings were
fixed, and whose demoted findings sat through a rebuttal round it conceded
or spent, returns PLEASED — the demoted items belong in its body as
non-blocking, which the rubric has always allowed under PLEASED. This is
the owner's own closure condition for the gate: the reviewers make sure
they are pleased *after* the adjudication, not despite never hearing about
it. What a re-reviewer may not do is re-list a spent demotion in BLOCKING
with the same evidence; that re-raise gates nothing and goes back with a
pointer to the record. What it may always do is bring **new** evidence,
which is a new finding and is adjudicated fresh.

And if, with every rebuttal spent, a reviewer still holds NOT PLEASED
because it genuinely believes a demoted finding is real? Then the loop is
at a standoff the machinery cannot honestly close: there is no artifact you
can write (every verdict must be exactly PLEASED, and recording a verdict
nobody returned is fabrication), and grinding more rounds is the ping-pong
this gate exists to end. That dispute goes where every unresolved dispute
in this framework goes: **up to the owner**, the final adjudicator, with
the record as the case file. Escalation is a first-class move here exactly
as it is everywhere else in this framework.

## 7. Convergence discipline

- The loop converges: each re-review must find **strictly less** than
  the round before. Same-or-more findings two rounds running means the slice
  was mis-scoped or the fix round was dispatched piecemeal. Stop and
  re-plan; do not grind rounds.
- **The one-line-nit shortcut, stated precisely.** If late rounds surface only
  one-line nits, what you may skip is convening another **full panel**, not the
  verdicts. Close it like this: batch the nits into one final **dispatched**
  fix round (the manager does not fix them itself; that is IC work and the
  steward flags it), re-review **only the dissenters**, and add the manager's
  own exhaustive check on top of their PLEASED. Anything else leaves a reviewer
  holding NOT PLEASED, and then there is no artifact you can honestly write:
  the gate requires every verdict to be exactly PLEASED, so the only way to
  "close" on a dissent is to record a verdict nobody returned, which is
  fabrication, the one weakness this framework names in its own gate. A
  shortcut that ends in a forged artifact is not a shortcut.
- Only when **every** reviewer is PLEASED does the artifact get written
  ([`../skeptical-review/SKILL.md`](../skeptical-review/SKILL.md)), followed by
  [the manager's own inspection](../delegating/SKILL.md#manager-inspects-the-procedure)
  and **one** commit for the whole batch: the artifact is bound to a single
  HEAD, so a panel waives one commit, not one per slice. Fill the artifact's
  `head_sha` after the last fix round, not before it.

## Honest limits (of the fluff gate)

- **It raises the cost of fluff; it cannot certify judgment.** The
  yardstick makes "is this a blocker?" a question with named answers
  instead of a mood, and the record makes the answer auditable. Whether a
  given adjudication was *right* stays a judgment call, human/manager-owned
  like every judgment call in this framework. Same standard as everywhere
  else: capability claims, not behavioural guarantees.
- **The named failure mode: bulldozing.** A manager can misuse this gate to
  demote its way to all-PLEASED — real findings stamped FLUFF until the
  artifact writes itself. The countermeasures are the parts that are not
  optional: the rebuttal round (no demotion lands unheard), the steward
  (bulk demotion in `.delegation/adjudications/` is legible manager conduct,
  and its flag escalates to the owner), and the record itself (a bulldozed
  round is a *written* bulldozed round; the audit trail is the deterrent).
  Raised cost, not prevention.
- **The commit gate does not read the adjudication record.** The structural
  slice still checks verdicts and blocking lists, nothing more. A
  fabricated record, like a fabricated artifact, is possible: this gate is
  a wall against carelessness and quiet taste-gating, not against bad
  faith.
- **A reviewer can cave.** Nothing detects a reviewer that concedes a real
  finding to end the round. The record at least preserves what was
  originally found, in the reviewer's own words, for the steward and the
  next reader.

Verdict, per-finding, and REBUTTAL formats:
[`../../docs/rubric.md`](../../docs/rubric.md).
