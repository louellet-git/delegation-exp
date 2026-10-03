# The verdict rubric: PLEASED | NOT PLEASED

Every skeptic, whatever its lens, reports in this format: the contract that
lets a manager consolidate a panel mechanically and the commit gate key on the
result. BLOCKING findings are adjudicated against the
[fluff-gate yardstick](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate).

## Per-finding format

For each finding (a file, a function, a test, a claim, a design section):

```
### <target: file:line, test id, claim, or section>
- Claims to establish: <what a reader would assume this proves or promises>
- Actually establishes: <the narrower true statement>
- What it would MISS:   <a concrete real-world break or wrong decision that
                         stays green / stays credible despite this>
- Tags: <lens-specific taxonomy tags, e.g. weak-oracle, proxy-not-target,
        overclaim, untraced-claim>
- Severity: BLOCKING | non-blocking
- Residual usefulness: <0-5> toward the end goal stated in the dispatch
    (0 = theater; 5 = catches a real, goal-relevant regression or error
     nothing else catches)
- To make it real: <the smallest change that would raise the score, or
  "drop it - X already covers what little this does">
```

## The verdict block

After the findings, exactly this:

```
VERDICT: PLEASED | NOT PLEASED
BLOCKING:
1. <numbered, concrete, actionable finding>
2. ...
COMPACT: <one line reminding the author to be more compact; never the compact form>
ESCALATE (optional, swarm mode): <thread that needs a deep specialist,
and what a deep review should trace or reproduce>
```

Rules:

- **NOT PLEASED whenever the BLOCKING list is non-empty.** No "PLEASED with
  reservations." Non-blocking findings go in the body, not the list.
- Number the BLOCKING items, because the consolidation step
  ([`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md))
  reconciles panels by number.

## The REBUTTAL block (only after a demotion)

When the manager adjudicates one of your BLOCKING findings FLUFF, it tells
you the ruling and the written reason, and you owe exactly one reply, in
exactly this shape:

```
REBUTTAL (finding <#>): CONCEDE | STAND
Evidence (STAND only, and it must be NEW): <the command run, the line
  cited, the consumer named — something the original finding did not
  contain>
```

Rules:

- **STAND requires new evidence.** Restating the original evidence louder
  is a concession with extra words, and the adjudication record will say
  so. If the demotion is wrong, something checkable proves it: run it,
  cite it, name it.
- **One round.** After it, the demotion is an accepted, recorded limit of
  the batch. Re-listing a spent demotion in a later BLOCKING list with the
  same evidence gates nothing. Genuinely new evidence is always a door: it
  makes a new finding, adjudicated fresh.
- **Concede honestly.** A skeptic that stands on everything has no signal,
  exactly like one that cries theater at everything.

## How the manager reads a panel

- Any NOT PLEASED → the slice does not commit; consolidate, adjudicate and fix per
  [consolidating-review](../skills/consolidating-review/SKILL.md).
- All PLEASED → write `.delegation/review-artifact.json`
  ([format](../skills/skeptical-review/SKILL.md)), then the manager still
  inspects before committing: a unanimous panel is necessary, not sufficient.
- An ESCALATE output is not a verdict. It is a routing instruction: dispatch
  the named thread as a deep review before trusting the swarm's PLEASED on
  that thread.
