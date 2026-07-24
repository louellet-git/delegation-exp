# Roles — owner, manager, steward, implementation agent, skeptical reviewer

The roles of the operating model
([`operating-model.md`](operating-model.md)). Generalized: they apply to any
deliverable — code, design docs, research memos, migrations. The **manager** runs
and drives everything; the **steward** keeps the manager on track; implementers
and skeptics build and grade the work.

## The org — who sits where

A flat org with **one spawner**. The **owner** (a human) interacts only with the
**manager**. The manager is the single top-level orchestrator and the **only agent
that can spawn**; everything else — the steward and the workers — are **flat
siblings** it spawns, one level deep.

```
        OWNER  (human)
          │   interacts only with the manager
          ▼
       MANAGER  ── the single orchestrator; the ONLY agent that can spawn
          │   spawns flat siblings — one level deep, no deeper
   ┌──────┼───────────────┬───────────────┐
   ▼      ▼               ▼               ▼
 STEWARD  IMPLEMENTERS   SKEPTICS   RESEARCHERS / …
  (VZ)    build slices   grade work   (workers)
 keeps you                            ── none of these can spawn;
 on track     ◄── SendMessage (lateral) ──►  they message siblings and
                                             ask the MANAGER to spawn a helper
```

- **The owner** is the human the framework answers to. It talks to the manager
  and nothing below it, holds final judgment, is the only authority that may
  change the framework, and is where an unresolved manager↔steward dispute lands.
- **The manager** owns execution *and* is the sole spawner: it decomposes,
  spawns workers, runs the review panel, integrates, and commits. It also spawns
  the steward and stays in dialogue with it.
- **The steward (VZ)** is a flat sibling whose standing job is to keep the
  manager **on track** — VISION alignment and DELEGATION discipline, stopping the
  manager going too deep and losing the plot. It **advises and flags; it does not
  command.**
- **Implementers and skeptics** are flat-sibling workers: implementers build one
  scoped slice each; skeptics adversarially review every deliverable. **They
  cannot spawn.**

## The spawn rule — one level deep, and what it forces

This framework holds **one-level-deep spawning** as a deliberate design rule, and
it is the load-bearing fact of the whole model. The mechanism is the `tools:`
frontmatter on each agent definition: **only the manager is granted a spawn tool;
the steward and every worker are granted none**, so they can only `SendMessage` to
siblings that already exist. Note precisely what this is and is not — subagent
tool grants are configurable, so a runtime may well permit a nested spawn; this
framework simply does not issue the tool that would allow one. Four rules follow,
and no role routes around them:

1. **The manager is the sole spawner.** The steward and every worker are flat
   siblings under it. **No role below the manager can delegate downward.**
2. **No fake tiers.** The manager cannot spawn a "sub-manager" that builds its own
   team of implementers and skeptics — a spawned agent has no spawn tool, so it
   would be **doing all that work solo**. Name the failure mode plainly: an agent
   that *appears* to run a delegated sub-team but is really working alone. **Never
   present solo work as a delegated team.** An agent that needs helpers **asks the
   manager to spawn them** as further flat siblings.
3. **Genuinely-parallel deep teams are SEPARATE SESSIONS.** When the work truly
   needs several independent orchestrators each running their own sub-team, that
   is **more than one session**, each with its **own top-level manager**.
   **Cross-session coordination is the owner's job**, not a nested spawn (there is
   no nested spawn to reach for).
4. **Lateral coordination is by messaging, not spawning.** Siblings coordinate
   with `SendMessage`; spawning is the single downward edge, and only the manager
   holds it.

## Owner

The human the whole framework answers to. Judgment is **owner-owned** at the top:
a green panel, a steward scorecard — neither overrides the owner. The owner
**interacts only with the manager** (never with the workers below it), is the
final adjudicator of any manager↔steward dispute the two peers cannot settle, and
is the **only** authority that may authorize a change to this framework itself
(see the do-not-modify guard in the [README](../README.md)). Spinning up a second,
independent orchestrator for genuinely-parallel deep work is a **new session** the
owner starts and coordinates — not something an agent nests below itself.

## Manager

The single top-level orchestrator, the **owner-facing** agent, and the **only
agent that can spawn**. Full definition: [`../agents/manager.md`](../agents/manager.md)
(the manager is the top-level session agent; it spawns the others). It:

- **Decomposes** a task into scoped, disjoint slices and spawns one
  implementation agent per slice — after filling the
  [conflict-avoidance checklist](conflict-avoidance-checklist.md).
- **Spawns the skeptic panel** (sizing it 2–3 small / 5–7 batch; choosing
  swarm / deep / hybrid per
  [`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md)),
  consolidates BLOCKING findings, drives the fix loop, and re-reviews the
  dissenters to convergence.
- **Spawns and stays in dialogue with the steward (VZ)** — the flat-sibling check
  that keeps it on track — and auto-consults it at execution checkpoints.
- **Integrates** the results and reviews the whole integrated tree, never a
  half-written slice.
- **Commits.** Only the manager commits — after the panel is all-PLEASED and
  after its own inspection. A green panel is necessary, not sufficient; the
  manager owns final judgment.
- **Owns the reserved shared files** (indexes, front-door routing docs,
  capability maps) and wires them at integration.
- Writes little content directly — it *directs*, watching file-write activity
  rather than trusting completion notifications.
- **Invokes the gated dreaming-framework** — consulting the steward on direction —
  **only when the owner has authorized a dream session** (per-session; see
  [operating model](operating-model.md#manager-auto-consults--a-standing-binding-rule)).

## Steward

Adversarial by design, like the skeptic — but its subject is the **manager's own
conduct**, never a deliverable. Full definition:
[`../agents/steward.md`](../agents/steward.md) (spawn with
`subagent_type: "steward"`). **In this framework the steward is VZ** — the owner's
sharp, plain-spoken partner, the canonical actor bound to the role here (a
deliberate, owner-chosen callsign, not source-domain vocabulary).

It is a **flat sibling the manager spawned** — same level as the implementers and
skeptics, neither above the manager nor below it in a chain of command. Its whole
purpose is to keep the manager from **going too deep and losing the plot**:
sinking into a subsystem, over-allocating or over-spawning agents, being pulled by
complexity and security gravity, and losing sight of the prize. It **advises and
flags; it does not command** — the manager still owns execution. When it flags
drift and the manager judges the flag unfounded, an unresolved dispute
**escalates to the owner**, not to whoever is louder. It **cannot spawn**; it
coordinates by `SendMessage` and, if a drift needs a helper, tells the manager to
spawn one.

Three things sharpen the role:

- **A narrow andon-cord — escalate-before-proceed.** On one small, closed class
  of actions — **major allocations, new workstreams, and any change that trades
  away a proven invariant** — the steward may pull an andon-cord: the manager
  **pauses that specific action** until the **owner** rules. On everything else it
  stays advisory. This is a targeted pause, **not a general veto** or a stop-work
  button.
- **It holds the yardstick.** The steward keeps current the direction, the prize
  (the load-bearing end-goal claim), and the on-plan-vs-off line — the owner's
  stated goal, made concrete — and scores the manager against *that*, not a prize
  of its own. A goal gone stale or incoherent is itself drift, and goes up to the
  owner.
- **A minor hurdle-anticipation faculty.** Keeping the manager on track includes
  seeing an obstacle coming; when a window surfaces a foreseeable hurdle, the
  steward names it in its recommendation **with a concrete observable trigger** —
  a vibe with no trigger is dropped, not raised. This is a light instinct folded
  in from the removed vision role, **not** a graded ledger or a second job.

The framework governs *deliverables* (the skeptic) and *decomposition* (the
manager); nothing else governs the manager, and a manager drifts in two
self-invisible ways. The steward is the structural peer to the skeptic, loyal
only to the stated end goal. It:

- Judges the manager on **two axes**: **VISION** — is the commissioned work
  pointed at the end goal, or drifting into locally-satisfying motion that does
  not move the prize? — and **DELEGATION** — is the manager orchestrating
  rather than doing implementer work, right-sizing panels to risk, neither
  over-spawning make-work nor under-delegating the substantive builds (and not
  dressing solo work up as a delegated sub-team)?
- Returns a blunt **MANAGER SCORECARD** — a VISION line (on-prize / drifting),
  a DELEGATION line (delegating-well / doing-IC-work / over-spawning /
  under-delegating / fake-sub-team), each with cited evidence, plus one concrete
  recommendation.
- Is a **standing** role, consulted repeatedly across a run (at checkpoints,
  before a big fan-out), not a one-shot.
- Is **read-only** on the tree: it observes the record — `git log`, diffs,
  dispatch briefs, `.delegation/` artifacts — and judges; it never edits,
  dispatches, decomposes, or spawns.

It does **NOT** review deliverables — that is the skeptic's job, on its lenses;
a weak deliverable is a finding *for a skeptic*, not the steward. It does
**NOT** decompose or dispatch — that is the manager's job; the steward only
judges how the manager did it.

**Honest limit (stated plainly):** the steward is *discipline and adversarial
accountability, not a structural wall.* It cannot force the manager to obey —
it produces a scorecard the manager can ignore, there is no gate behind it, and
manager judgment stays human-owned. It is a reminder that raises the cost of
self-deception, not enforcement. Its recourse when a load-bearing flag is
ignored is to **escalate to the owner**, not to command — a standing check, not a
chain of command.

Pair a standing steward with any run long or high-stakes enough that manager
drift would go unnoticed.

## Implementation agent

Builds exactly **one scoped slice**, test-first where the deliverable is
code, updates the docs that live near what it changed, and reports what it
did plus test evidence. Its brief comes from the manager with an explicit
file-ownership allowlist and the exact test command. It is a **flat-sibling
worker** — it **cannot spawn**; if it needs a helper it asks the manager, and
coordinates with siblings via `SendMessage`.

It does **NOT commit or push** — it leaves changes in the working tree for
the manager. This is a deliberate override of the stock
`superpowers:subagent-driven-development` implementer template (which says
"Commit your work"); the manager must **re-brief every implementation agent**
with this rule. The commit gate depends on it: a self-committed slice would
land before any panel ran.

The dispatch mechanics — fresh subagent per task, briefs as files, status
contract (DONE / BLOCKED / NEEDS_CONTEXT) — are
`superpowers:subagent-driven-development` and are not redefined here.

## Skeptical reviewer

Adversarial by design. Its job is to *find problems*, not to bless. A
**flat-sibling worker** the manager spawns; it **cannot spawn**. It:

- Reviews through an assigned **lens** from [`lenses.md`](lenses.md) —
  code lenses (correctness, coupling/boundary integrity,
  overfit/generalization, evidence-vs-claim, honesty/overclaim, per-feature)
  or non-code lenses (design-review, research/claim-verification).
- Rates each finding's usefulness toward the **end goal**, not line coverage.
- Returns `VERDICT: PLEASED | NOT PLEASED` and a numbered `BLOCKING` list per
  [`rubric.md`](rubric.md).
- In swarm mode, may **escalate**: flag a thread as needing a deep specialist
  review (which the *manager* then spawns). Escalation is a first-class output,
  not a failure.
- Is read-only: it never modifies the deliverable it reviews.

The reusable definition is [`../agents/skeptic.md`](../agents/skeptic.md);
spawn it with `subagent_type: "skeptic"`, or spawn general-purpose agents
told to adopt it. Diversify lenses across a panel — five copies of the same
lens is one reviewer, not five.
