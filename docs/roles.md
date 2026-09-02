# Roles: owner, manager, steward, implementation agent, skeptical reviewer

The roles of the operating model
([`operating-model.md`](operating-model.md)). Generalized: they apply to any
deliverable, whether code, design docs, research memos, or migrations. The
manager runs and drives everything; the steward keeps the manager on
track; implementers and skeptics build and grade the work.

## The org — who sits where

A flat org with one spawner. The owner (a human) interacts only with the
manager. The manager is the single top-level orchestrator and the only agent
that can spawn; everything else, the steward and the workers, are flat
siblings it spawns, one level deep.

```
        OWNER  (human)
          │   interacts only with the manager
          ▼
       MANAGER  ── the single orchestrator; the ONLY agent that can spawn
          │   spawns flat siblings — one level deep, no deeper
   ┌──────┼───────────────┬───────────────┐
   ▼      ▼               ▼               ▼
 STEWARD  IMPLEMENTERS   SKEPTICS   RESEARCHERS / …
          build slices   grade work   (workers)
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
- **The steward** is a flat sibling whose standing job is to keep the
  manager on track: VISION alignment and DELEGATION discipline, stopping the
  manager going too deep and losing the plot. It **advises and flags; it does not
  command.**
- **Implementers and skeptics** are flat-sibling workers: implementers build one
  scoped slice each; skeptics adversarially review every deliverable. **They
  cannot spawn.**

## The spawn rule: one level deep, and what it forces

This framework holds one-level-deep spawning as a deliberate design rule, and
it is the load-bearing fact of the whole model. The mechanism is what the
`tools:` frontmatter **withholds**: the spawnable definitions here,
[`../agents/skeptic.md`](../agents/skeptic.md) and
[`../agents/steward.md`](../agents/steward.md), list no spawn tool, so they can
only `SendMessage` to siblings that already exist. The manager's ability to
spawn is not a grant this repo issues; it comes from the manager being the
**top-level session**, which is also why nothing here loads
[`../agents/manager.md`](../agents/manager.md) and why the `Task` in that file's
`tools:` line describes the role rather than conferring anything. Note
precisely what this is and is not. Subagent tool grants are configurable, so a
runtime may well permit a nested spawn; this framework simply does not issue
the tool that would allow one. Four rules follow, and no role routes around
them:

1. **The manager is the sole spawner.** The steward and every worker are flat
   siblings under it. No role below the manager can delegate downward.
2. **No fake tiers.** The manager cannot spawn a "sub-manager" that builds its own
   team of implementers and skeptics: a spawned agent has no spawn tool, so it
   would be doing all that work solo. Name the failure mode plainly, an agent
   that *appears* to run a delegated sub-team but is really working alone.
   **Never present solo work as a delegated team.** An agent that needs helpers
   asks the manager to spawn them as further flat siblings.
3. **Genuinely-parallel deep teams are SEPARATE SESSIONS.** When the work truly
   needs several independent orchestrators each running their own sub-team, that
   is more than one session, each with its own top-level manager.
   **Cross-session coordination is the owner's job**, not a nested spawn (there is
   no nested spawn to reach for).
4. **Lateral coordination is by messaging, not spawning.** Siblings coordinate
   with `SendMessage`; spawning is the single downward edge, and only the manager
   holds it.

**How the two naming conventions in this repo differ.** Skills and commands are
addressed with the plugin namespace: `delegation-framework:skeptical-review`,
`/delegate`. **Agents are spawned by the bare `name:` in their own frontmatter,
with no namespace**: `subagent_type: "skeptic"`, `subagent_type: "steward"`,
and `subagent_type: "general-purpose"` for the inline-briefed implementers,
which have no definition file at all. Every example in this repo follows that
split; if a runtime lists plugin agents under some other id, use the one it
lists.

## Owner

The human the whole framework answers to. Judgment is owner-owned at the top:
neither a green panel nor a steward scorecard overrides the owner. The owner
interacts only with the manager (never with the workers below it), is the
final adjudicator of any manager↔steward dispute the two peers cannot settle, and
is the only authority that may authorize a change to this framework itself
(see the do-not-modify guard in the [README](../README.md)). Spinning up a second,
independent orchestrator for genuinely-parallel deep work is a new session the
owner starts and coordinates, not something an agent nests below itself.

One instrument sits beside this hierarchy without changing it: when the
sibling planning-framework delivered the run's task as a plan, the planner
is the owner's planning instrument — usually the same top-level session that
now holds the manager role, wearing its previous hat. Plan content is the
planner's to rule on, so plan-content questions go back to it through the
[planner relay](../skills/delegating/SKILL.md#the-planner-relay-questions-go-back-up-the-seam);
final judgment and disputes stay the owner's alone, exactly as above.

## Manager

The single top-level orchestrator, the owner-facing agent, and the **only
agent that can spawn**. Full definition:
[`../agents/manager.md`](../agents/manager.md).

**How you become the manager: you read that file and hold the role in your own
top-level session. You never spawn it.** It lives in `agents/` because that is
where this plugin keeps role definitions, but nothing in the repo loads it, and
spawning it as a subagent would put the manager one level deep and everything
it spawns two levels deep, breaking the one-level-deep invariant this whole
model rests on. `/delegate` is the shortcut: it runs the `delegating` skill in
the session you typed it in, which *is* the top-level session. See
[`../agents/manager.md`](../agents/manager.md#how-to-use-this-file-do-not-spawn-it).

The manager:

- Decomposes a task into scoped, disjoint slices
  ([the DECOMPOSE procedure](../skills/delegating/SKILL.md#decompose-the-procedure))
  and spawns one implementation agent per slice, after filling the
  [conflict-avoidance checklist](conflict-avoidance-checklist.md).
- Spawns the skeptic panel (sizing it 2–3 small / 5–7 batch; choosing
  swarm / deep / hybrid per
  [`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md)),
  consolidates BLOCKING findings, **adjudicates every one through the fluff
  gate** (real defects gate; fluff is demoted on the record, with one
  rebuttal round for the original reviewer — no silent demotions; see
  [`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate)),
  drives the fix loop, and re-reviews the dissenters to convergence.
- Spawns and stays in dialogue with the steward, the flat-sibling check
  that keeps it on track, and auto-consults it at execution checkpoints.
- Integrates the results and reviews the whole integrated tree, never a
  half-written slice.
- **Commits, once per panel.** Only the manager commits, after the panel is
  all-PLEASED and after
  [its own inspection](../skills/delegating/SKILL.md#manager-inspects-the-procedure).
  A green panel is necessary, not sufficient; the manager owns final judgment.
  The review artifact binds to a single HEAD, so one panel waives exactly one
  commit: the batch is integrated, reviewed as a whole, and landed in one
  commit rather than slice by slice.
- Owns the reserved shared files (indexes, front-door routing docs,
  capability maps) and wires them at integration.
- Writes little content directly. It *directs*, watching file-write activity
  rather than trusting completion notifications.
- Lets the implementers do the reading. A slice's files are opened by the
  agent that owns the slice, which reports back a summary; the manager's own
  context stays spent on the arc of the work rather than on the tree (see
  [`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-loop-mechanics)).

## Steward

Adversarial by design, like the skeptic — but its subject is the manager's own
conduct, never a deliverable. Full definition:
[`../agents/steward.md`](../agents/steward.md) (spawn with
`subagent_type: "steward"`).

It is a flat sibling the manager spawned, at the same level as the
implementers and skeptics, neither above the manager nor below it in a chain of
command. Its whole purpose is to keep the manager from going too deep and losing
the plot: sinking into a subsystem, over-allocating or over-spawning agents,
being pulled by complexity and security gravity, and losing sight of the prize.
It advises and flags; it does not command, and the manager still owns
execution. When it flags drift and the manager judges the flag unfounded, an
unresolved dispute escalates to the owner, not to whoever is louder. It
cannot spawn; it coordinates by `SendMessage` and, if a drift needs a helper,
tells the manager to spawn one.

Three things sharpen the role:

- **A narrow andon-cord, escalate-before-proceed.** On one small, closed class
  of actions (**major allocations, new workstreams, and any change that trades
  away a proven invariant**) the steward may pull an andon-cord: the manager
  **pauses that specific action** until the owner rules. On everything else it
  stays advisory. This is a targeted pause, not a general veto or a stop-work
  button.
- **It holds the yardstick.** The steward keeps current the direction, the prize
  (the load-bearing end-goal claim), and the on-plan-vs-off line, all derived
  from the owner's stated goal made concrete, and scores the manager against
  *that*, not a prize of its own. A goal gone stale or incoherent is itself
  drift, and goes up to the owner.
- **A minor hurdle-anticipation faculty.** Keeping the manager on track includes
  seeing an obstacle coming; when a window surfaces a foreseeable hurdle, the
  steward names it in its recommendation with a concrete observable trigger.
  A vibe with no trigger is dropped, not raised. This is a light instinct, not
  a graded ledger and not a second job: the steward is not a forecasting
  function and keeps no separate hurdle scorecard.

The framework governs *deliverables* (the skeptic) and *decomposition* (the
manager); nothing else governs the manager, and a manager drifts in two
self-invisible ways. The steward is the structural peer to the skeptic, loyal
only to the stated end goal. It:

- Judges the manager on two axes. **VISION**: is the commissioned work
  pointed at the end goal, or drifting into locally-satisfying motion that does
  not move the prize? **DELEGATION**: is the manager orchestrating
  rather than doing implementer work, right-sizing panels to risk, neither
  over-spawning make-work nor under-delegating the substantive builds (and not
  dressing solo work up as a delegated sub-team), dispatching in parallel the
  slices a clean checklist cleared rather than serializing them, and holding
  the model ladder (tiers matched to slices, with Opus exceptions written
  down)?
- Returns a blunt **MANAGER SCORECARD**: a VISION line (on-prize / drifting),
  a DELEGATION line (delegating-well / doing-IC-work / over-spawning /
  under-delegating / fake-sub-team / serialized-the-disjoint /
  tier-inflation), each with cited evidence, plus one concrete
  recommendation.
- Is a standing role, consulted repeatedly across a run (at checkpoints,
  before a big fan-out), not a one-shot.
- Is read-only on the tree: it observes the record (`git log`, diffs,
  dispatch briefs, `.delegation/` artifacts) and judges; it never edits,
  dispatches, decomposes, or spawns.
- Depends on the manager having **persisted** that record. It reconciles what
  landed against the dispatch briefs saved under `.delegation/briefs/`, it
  compares each checkpoint against its own earlier scorecards saved under
  `.delegation/steward/`, and it reads the fluff-gate record under
  `.delegation/adjudications/` — judging a demotion is judging the manager's
  conduct, not the deliverable, so a round where most of a BLOCKING list was
  ruled FLUFF is in its scope, not a panel verdict it is relitigating. With no
  briefs on disk its DELEGATION line is
  unrecoverable for that window, and it says so rather than inventing one from
  authorship (in this model only the manager commits, so authorship attributes
  everything to the manager and proves nothing).

It does **NOT** review deliverables. That is the skeptic's job, on its lenses;
a weak deliverable is a finding *for a skeptic*, not the steward. It does
**NOT** decompose or dispatch. That is the manager's job; the steward only
judges how the manager did it.

Honest limit: the steward is *discipline and adversarial
accountability, not a structural wall.* It cannot force the manager to obey.
It produces a scorecard the manager can ignore, there is no gate behind it, and
manager judgment stays human-owned. It is a reminder that raises the cost of
self-deception, not enforcement. Its recourse when a load-bearing flag is
ignored is to **escalate to the owner**, not to command: a standing check, not a
chain of command.

Pair a standing steward with any run long or high-stakes enough that manager
drift would go unnoticed.

## Implementation agent

Builds exactly one scoped slice, test-first where the deliverable is
code, updates the docs that live near what it changed, and reports what it
did plus test evidence. It is a flat-sibling worker and it cannot spawn; if it
needs a helper it asks the manager, and coordinates with siblings via
`SendMessage`.

**There is no `agents/implementer.md`, and that is deliberate**: an implementer
is defined entirely by its brief, one per slice, so there is nothing reusable to
put in a file (`validate-structure.py` actively fails if such a file appears).
Spawn implementers as the runtime's **general-purpose worker subagent** (in
Claude Code, `subagent_type: "general-purpose"`) with the whole brief in the
prompt. Never grant a worker a spawn tool. Dispatch each one on the tier its
brief's MODEL TIER slot names: Sonnet by default, Haiku for a mechanical
slice, Opus only with the reason written in the brief — the ladder is in
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what). The brief itself is written from the
canonical template, which carries the allowlist, the reserved files, the exact
test command, the acceptance condition, the postures, the no-self-commit
re-brief, and the status contract:
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-brief-template).

It does **NOT commit or push**. It leaves changes in the working tree for
the manager. General-purpose implementer briefs commonly default to "commit
your work," so the manager must re-brief every implementation agent with this
rule explicitly rather than assume it. The commit gate depends on it: a
self-committed slice would land before any panel ran.

The dispatch mechanics (one scoped task per fresh subagent, the brief template,
and the status contract of DONE / BLOCKED / NEEDS_CONTEXT, including what the
manager does with a BLOCKED report) are in
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-loop-mechanics).

## Skeptical reviewer

Adversarial by design. Its job is to *find problems*, not to bless. A
flat-sibling worker the manager spawns; it cannot spawn. It:

- Reviews through an assigned lens from [`lenses.md`](lenses.md):
  code lenses (correctness, coupling/boundary integrity,
  overfit/generalization, evidence-vs-claim, honesty/overclaim,
  derived-output/ranking, per-feature) or non-code lenses (design-review,
  research/claim-verification). `derived-output/ranking` is **mandatory**, in
  deep mode, for anything that scores, ranks, classifies, prioritizes, or
  derives a verdict.
- Rates each finding's usefulness toward the end goal, not line coverage.
- Returns `VERDICT: PLEASED | NOT PLEASED` and a numbered `BLOCKING` list per
  [`rubric.md`](rubric.md). Writes each BLOCKING finding to survive
  adjudication (a concrete failure, a violated written contract, an
  exposure, or a reproduced defect — not taste), and on a demotion owes
  exactly one structured rebuttal: concede, or stand with new evidence.
- In swarm mode, may escalate: flag a thread as needing a deep specialist
  review (which the *manager* then spawns). Escalation is a first-class output,
  not a failure.
- Is read-only: it never modifies the deliverable it reviews.
- Runs on Sonnet (its frontmatter says so), or Haiku for a narrow mechanical
  lens — never Opus. Review depth comes from the two-phase briefing and the
  lens, not the tier.

The reusable definition is [`../agents/skeptic.md`](../agents/skeptic.md);
spawn it with `subagent_type: "skeptic"`, or spawn general-purpose agents
told to adopt it. Unlike the manager, this one *is* meant to be spawned: it is
a flat sibling one level below the manager, which is exactly where a subagent
definition belongs. Diversify lenses across a panel; five copies of the same
lens is one reviewer, not five.
