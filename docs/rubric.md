---
id: DOC-RUBRIC
type: description
item: 10.38 Process description
status: current
date: 2026-10-26
scope: The skeptic verdict format and how the manager reads a panel.
---

# The verdict rubric: PLEASED | NOT PLEASED

Every skeptic reports in this format, so a manager can
consolidate a panel mechanically and the commit gate can key on the result.
BLOCKING findings are adjudicated against the
[fluff-gate yardstick](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate).

## Per-finding format

```
### <target: file:line, test id, claim, or section>
- Claims to establish: <what a reader would assume this proves or promises>
- Actually establishes: <the narrower true statement>
- What it would MISS: <a concrete break or wrong decision that stays green>
- Tags: <lens-specific, e.g. weak-oracle, overclaim>
- Severity: BLOCKING | non-blocking
- Residual usefulness: <0-5> toward the end goal (0 = theater; 5 = catches a
  real error nothing else catches)
- To make it real: <smallest change that would raise the score, or "drop it -
  X covers this">
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

NOT PLEASED whenever the BLOCKING list is non-empty; no "PLEASED with
reservations". Non-blocking findings go in the body, not the list. Number the
BLOCKING items: [consolidation](../skills/consolidating-review/SKILL.md)
reconciles panels by number.

## The REBUTTAL block (only after a demotion)

A BLOCKING finding ruled FLUFF comes back with the manager's reason; you owe
exactly one reply:

```
REBUTTAL (finding <#>): CONCEDE | STAND
Evidence (STAND only, and it must be NEW): <the command run, the line cited,
  the consumer named>
```

STAND requires new evidence: restating the old is a concession. After this one
round the demotion is a recorded limit: re-listing it on the same evidence
gates nothing, new evidence is a new finding, adjudicated fresh.

## How the manager reads a panel

- Any NOT PLEASED: no commit; consolidate, adjudicate and fix per
  [consolidating-review](../skills/consolidating-review/SKILL.md).
- All PLEASED: write `.delegation/review-artifact.json`
  ([format](../skills/skeptical-review/SKILL.md)); the manager still inspects:
  unanimity is necessary, not sufficient.
- ESCALATE is a routing instruction, not a verdict: dispatch the named thread
  as a deep review before trusting the swarm's PLEASED on it.
