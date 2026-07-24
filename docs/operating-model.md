# The operating model — how work gets built and graded

Work is run by a **manager agent** that delegates to **implementation
agents**, whose work is graded by **skeptical reviewer agents**. This file is
the playbook, written so a *new* manager agent can run the loop without prior
context. Role definitions live in [`roles.md`](roles.md); lenses in
[`lenses.md`](lenses.md); the verdict format in [`rubric.md`](rubric.md).

This model **composes with** the `superpowers` plugin: the per-task
implement/review loop, parallel fan-out, and code-review mechanics are
`superpowers` skills invoked by name (the seam table is in
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md)). This file
carries only what `superpowers` does not.

## The law

> Every deliverable carries at least one adversarial skeptic before it is
> trusted — **research, design, implementation — all of them. The floor is
> one. No exceptions.**

This breadth is the framework's core contribution. `superpowers` reviews
*code* after each task with a single reviewer; this law covers **every kind
of deliverable** — a research memo, a design spec, a migration plan, an
implementation slice — and it holds even when the deliverable "looks fine."
It is a **discipline**, carried here and in the skills, plus one structural
slice (the commit gate, below). We do not pretend the whole law is a wall: a
hook cannot know an off-tree research deliverable went unreviewed.

## The loop

```
DECOMPOSE → IMPLEMENT (parallel where safe) → REVIEW PANEL (2–7 skeptics, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING → FIX ROUND → RE-REVIEW the dissenters
          → until every reviewer is PLEASED → MANAGER INSPECTS → COMMIT
```

- The **IMPLEMENT** step and per-slice flow are
  `superpowers:subagent-driven-development` and
  `superpowers:dispatching-parallel-agents` — not re-described here.
- **Review the whole integrated tree, not half-written slices.** Reviewing a
  tree an agent is still writing produces noise, not findings.
- **Batch blocking issues** into one reconciled fix round
  ([`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md))
  rather than dispatching piecemeal.
- **Re-verify, don't trust the fix report.** Re-run the *specific* reviewers
  who were NOT PLEASED; have them probe for inputs that still slip through,
  not just confirm the diff.
- **Loop-convergence stop-rule:** the loop **converges** — each re-review
  should find **strictly less** than the round before. If it keeps finding
  new one-line nits, fix them and close on an exhaustive manager check
  instead of another full round.

## The spawn topology — one level deep, the manager is the sole spawner

This framework holds **one-level-deep spawning** by construction, and the whole
org is shaped to it. The mechanism is per-agent tool grants: **only the manager
is given a spawn tool; the steward and every worker are given none**, leaving them
`SendMessage` to siblings that already exist. This is a rule the framework imposes
through its own agent definitions, not a constraint the runtime imposes on it —
grant `Task` to a worker and the topology breaks, which is exactly why no agent
definition here does:

1. **The manager is the sole spawner.** The steward and every worker
   (implementers, skeptics, researchers) are **flat siblings** under the manager.
   **No role below the manager can delegate downward.**
2. **No fake tiers.** The manager cannot spawn a "sub-manager" that assembles its
   own team — a spawned agent has no spawn tool, so it can only do that work
   **solo**. An agent that *appears* to run a delegated sub-team but is really
   working alone is a failure mode to name and refuse: **never present solo work
   as a delegated team.** An agent that needs helpers **asks the manager to spawn
   them** as further flat siblings.
3. **Genuinely-parallel deep teams are SEPARATE SESSIONS.** When work truly needs
   several independent orchestrators each running their own sub-team, that is
   **more than one session**, each with its **own top-level manager**;
   **cross-session coordination is the owner's job**, not a nested spawn.
4. **Lateral coordination is by messaging, not spawning.** Siblings coordinate
   with `SendMessage`; spawning is the single downward edge and only the manager
   holds it.

Role detail and the ASCII picture: [`roles.md`](roles.md#the-org--who-sits-where).

## The steward — beside the loop, governing the manager

The loop above governs *deliverables* (skeptics) and *decomposition* (the
manager runs it). Nothing in the loop governs the **manager itself**, which
drifts in two self-invisible ways: it **loses the prize** (commissions
locally-satisfying motion that does not move the end goal) or **stops
delegating** (does implementer work itself, over-spawns make-work, or
under-delegates the substantive builds). The **steward**
([`roles.md`](roles.md#steward), [`../agents/steward.md`](../agents/steward.md))
sits *beside* this loop, not inside the implement→review cycle: it reviews
neither slices nor decompositions but the manager's own conduct, returning a
MANAGER SCORECARD on VISION and DELEGATION. It is a **standing** flat sibling the
manager **spawns** (VZ — the owner's plain-spoken partner) and keeps in dialogue,
consulted repeatedly across a run — at checkpoints and before big fan-outs. Its
whole purpose is to keep the manager from going too deep and losing the plot.
**Honest limit:** it is discipline and adversarial accountability, *not* a
structural wall — no gate sits behind it, the manager can ignore its scorecard,
and manager judgment stays human-owned. Its recourse on an ignored load-bearing
flag is to **escalate to the owner**, not to command. It raises the cost of
self-deception; it does not enforce.

## Manager auto-consults — a standing, binding rule

The manager does **not** wait to be told to consult its peers. Consultation is
**automatic and binding** — a standing rule of the operating model, not something
the owner has to remember to trigger. The owner should never have to say "did you
check with the steward?" or "run this by VZ first"; the manager convenes the
steward itself, at the moments below, every time.

It is **tightly scoped, not "every commit."** The checkpoints below are a short,
defined list, and most consults should return **fast** — a "no concern, proceed"
is the common, cheap case, and a peer that only ever returns that on a genuinely
clean run is doing its job, not failing to. The point is a **standing, binding,
low-friction default**, not a tax on every action.

**Consult the STEWARD ([`../agents/steward.md`](../agents/steward.md)) — the
execution check — at these fixed checkpoints:**

- **Before any major or irreversible commit.** Anything that is costly to undo
  gets a steward read first — is this on-prize, and did it come from delegation
  rather than the manager quietly doing IC work?
- **On any allocation or spawn decision (fleet size).** Before scaling a
  fan-out up or down — how many agents, how big the panel — the manager checks
  with the steward, which watches exactly for over-spawning make-work and
  under-delegating the substance.
- **After any significant result.** A workstream landing, a panel converging, a
  hard build finishing — the moment a run *feels* productive is the moment drift
  hides best, so it is a fixed checkpoint, not an optional one.

The steward also holds the **yardstick** — the direction, the prize (the
load-bearing end-goal claim), and the on-plan-vs-off line, all derived from the
owner's stated goal — and scores VISION against it. The consult answers *"are you
delegating well and still on-prize?"* Because the steward is a flat sibling and
not a boss, a steward flag the manager rejects, if the two cannot resolve it
between them, **escalates to the owner** — the only authority above the manager —
see [`roles.md`](roles.md#the-org--who-sits-where).

**The one andon-cord exception.** Most steward consults are advisory — flag,
manager decides, work continues. On **one narrow, closed class** the steward's
consult is *escalate-before-proceed*: **major allocations, new workstreams, and
any change that trades away a proven invariant.** On those the manager **pauses
that specific action** until the **owner** rules — a targeted pause, not a general
veto (see [`../agents/steward.md`](../agents/steward.md#the-one-narrow-andon-cord--escalate-before-proceed)).

**Dreaming is a separate, per-session-authorized framework.** The generative
faculty — imagining better end-states and opportunities — is **not** a built-in
of this framework. It lives in the sibling
`dreaming-framework`, is **OFF
by default**, and the **manager — consulting the steward (VZ) on direction — may
invoke it only when the owner has authorized a dream session.** Enabling a session
is the owner's deliberate, per-session act — not a cadence the manager triggers.

**Honest limit, same as everywhere else:** this is a standing *discipline* the
manager holds itself to, not a hook-enforced wall — there is no gate that denies
the manager's next act for skipping a consult, and even the andon-cord pause is a
rule the manager honors rather than a structural block. It is binding as a rule
and owner-visible when skipped; it is not structural enforcement. The point is
that the manager consults *by default*, so the owner never has to be the reminder.

## When to use this model (the trivial-edit gate)

Use it for **substantial, multi-part builds** where independent review adds
real safety — a feature batch, a hardening pass, a migration.

**Do NOT delegate a trivial edit or a single-file fix** — the overhead isn't
worth it; just do it. (The `/delegate` command states this gate up front.)

**Panel-sizing heuristic:** **2–3 skeptics for a small change, 5–7 for a
feature batch.** Scale the panel to the risk, not to habit.

## When the deliverable belongs to a sibling framework

Three sibling frameworks own one kind of deliverable each: security review of a
repo where agents act (`cyber-security-framework`), documenting or
drift-checking a codebase (`code-doc-framework`), and reviewing a deck or memo
(`doc-review-framework`). This model still governs — the loop, the law, the
panel, the gate are unchanged; the sibling supplies the *specialist lenses,
agents or rubrics* for that deliverable kind.

Reaching for one is always a **deliberate act by the manager**: read the
sibling seam table in
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md) and invoke by
name. Nothing auto-discovers a sibling and nothing registers one — if it is not
installed, the name simply does not resolve. What genuinely composes, and which
seams are still aspiration, is in [`family.md`](family.md); read it before
building on a seam.

## Reliability / stall rules

- **Silence ≠ progress.** A working agent writes files. Watch file-write
  activity (mtimes / `git status`), not just completion notifications. An
  agent that has produced *nothing* after several minutes is stalled — stop
  it (`TaskStop`) and **re-brief with a concrete design decided for it**, not
  an open-ended "figure out whether this is solvable." *(In one recorded run
  that open-ended framing caused a **26-minute** no-output stall; the
  re-brief with a concrete spec finished in **~2 minutes**.)*
- **Commit disjoint slices as they land**, staging explicit paths — **never
  `git add -A` while another agent writes.** This protects completed work and
  satisfies any commit-time hooks without racing.
- **The implementation agent does NOT commit or push.** It leaves work in the
  tree; **the manager commits** — after the panel gate. (This is also what
  makes the commit gate meaningful: the gate fires on the manager's commit,
  which happens *after* review. An implementer that self-commits mid-slice
  would land work before any panel ran.)
- **Never let a green suite read as more than it is.** Distinguish "passes
  against a proxy we built" from "proven on the real target." Keep that
  honest in the docs the deliverable ships with.
- **Keep an accepted-residual honest.** A known gap the current design can't
  close is a labelled `xfail` canary with a reason — not a deleted test.

## Conflict avoidance (hard-won)

Parallel agents that write the same files clobber each other. Prevent it
**structurally**:

- **Disjoint directories run in parallel; a shared directory runs
  sequentially.** Two tasks touching the same package are sequential; a task
  in an unrelated package runs parallel to them.
- **Reserve shared index files for the manager** — an ADR index, a front-door
  routing file, a capability map. Forbid agents from touching them; the
  manager wires them at integration.
- **Pre-assign ADR / doc numbers** so parallel agents don't collide on the
  same `000N`.
- **Give each agent an explicit file-ownership allowlist** in its prompt, and
  the **exact test command** to run.

Before *any* parallel dispatch, the manager fills the
[conflict-avoidance checklist](conflict-avoidance-checklist.md) — a forced
artifact, not a suggestion. The `delegating` skill will not fan out without
it.

## The commit gate (the one structural slice)

The panel produces a review artifact
(`.delegation/review-artifact.json`; format in
[`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md)).
A PreToolUse hook denies `git commit` unless a well-formed, all-PLEASED
artifact exists — in repos that have **opted in** by carrying a
`.delegation/` directory at the repo root (the `delegating` skill creates it
when a loop starts). Within its reach, skipping review takes a *visible
act*, not a lapse of memory.

Five honest limits, always stated together: (1) it fires only where this
plugin's hooks are installed and enabled, and only with `python`/`python3`
on PATH; (2) it checks the artifact exists, is well-formed (including a
non-empty `deliverable`), and is all-PLEASED — not that the review was
rigorous; a PLEASED artifact can be fabricated, so it is a wall against
forgetting, not bad faith; (3) it gates the local commit only — it cannot
reach agents that never touch this working tree; (4) it sees only commits
issued through the hooked tool invocations, resolved by minimal
`cd <path>` / `git -C <path>` parsing — aliases, subprocesses/heredocs, or
IDE commits bypass the matcher, and variable or nested-quoted paths can make
it consult the wrong repo silently; (5) over-reach: the hook is
session-global, scoped by the `.delegation/` opt-in marker and anchored
command matching, but exotic compound commands can still false-positive —
escape hatches are: write the artifact, remove `.delegation/`, or disable
the hook. Details in the
[README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline).

After a gated commit lands, the manager **archives the artifact** (e.g. move
it to `.delegation/history/`) so a stale all-PLEASED file cannot silently
waive review for the *next* slice.
