# The verdict rubric — PLEASED | NOT PLEASED

Every skeptic, whatever its lens, reports in this format. The format is the
contract that lets a manager consolidate a panel mechanically and lets the
commit gate key on the result.

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
ESCALATE (optional, swarm mode): <thread that needs a deep specialist,
and what a deep review should trace or reproduce>
```

Rules:

- **NOT PLEASED whenever the BLOCKING list is non-empty.** No "PLEASED with
  reservations." Non-blocking findings go in the body, not the list.
- Number the BLOCKING items — the consolidation step
  ([`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md))
  reconciles panels by number.
- **Rate usefulness toward the end goal** stated in the dispatch, never
  toward line coverage. A test can be correct, useful for regression safety,
  and still score low because it does not move the stated goal — say so
  plainly.
- Distinguish **"weak but honest"** (a characterization test or hedged claim
  that documents a floor, clearly labelled) from **"weak and over-trusted"**
  (something whose green check or confident prose will be read as proof of
  more than it is). Reserve the harshest severity for the second.
- **Credit the honest ones.** If a deliverable genuinely closes a stated
  gap, say so and score it high. A skeptic that cries theater at everything
  has no signal.
- Be specific and technical; cite file:line or quote the claim. A skeptic
  who hand-waves is as useless as the work it criticizes.

## How the manager reads a panel

- Any NOT PLEASED → the slice does not commit. Consolidate all BLOCKING
  items into one fix round; re-review **the dissenters only**.
- All PLEASED → record the verdicts in the review artifact
  (`.delegation/review-artifact.json`, format in
  [`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md)),
  then the manager still inspects before committing. A unanimous panel is
  necessary, not sufficient.
- An ESCALATE output is not a verdict — it is a routing instruction: dispatch
  the named thread as a deep review before trusting the swarm's PLEASED on
  that thread.
