# The operating model: how work gets built and graded

Work is run by a manager agent that delegates to implementation
agents, whose work is graded by skeptical reviewer agents. This file is
the playbook, written so a *new* manager agent can run the loop without prior
context. Role definitions live in [`roles.md`](roles.md); lenses in
[`lenses.md`](lenses.md); the verdict format in [`rubric.md`](rubric.md).

This model is standalone. The per-task implement/review loop, the fan-out
rules, and the review mechanics are written down in this repo, in this file
and in [`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md).
Nothing here routes a mechanic to another plugin by name, and there is no
companion to install. One soft seam exists, by name only: a run whose task
arrives as the sibling planning-framework's delivered plan takes its intake
and its planner relay from the `delegating` skill; when that sibling is
absent, nothing here references it at runtime and nothing fails.

## The law

> Every deliverable carries at least one adversarial skeptic before it is
> trusted — **research, design, implementation — all of them. The floor is
> one. No exceptions.**

This breadth is the framework's core contribution. A single reviewer looking
at *code* after each task covers code; this law covers every kind
of deliverable — a research memo, a design spec, a migration plan, an
implementation slice — and it holds even when the deliverable "looks fine."
It is a **discipline**, carried here and in the skills, plus one structural
slice (the commit gate, below). The whole law is not a wall: a
hook cannot know an off-tree research deliverable went unreviewed.

## The loop

```
DECOMPOSE → IMPLEMENT (parallel where safe) → REVIEW PANEL (2–7 skeptics, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING → ADJUDICATE (the fluff gate: real gates, fluff demoted on the record)
          → FIX ROUND → RE-REVIEW the dissenters
          → until every reviewer is PLEASED → MANAGER INSPECTS → COMMIT
```

- The **DECOMPOSE** step has its own procedure, including how to get an
  allowlist and an exact test command out of a repo the manager is not supposed
  to be reading (a delegated scouting slice, or a bounded structural pass):
  [`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#decompose-the-procedure).
- The **IMPLEMENT** step is **one scoped task per fresh subagent.** The
  manager writes the brief from the canonical template
  ([`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-brief-template)),
  which carries the single task, the explicit file-ownership allowlist, the
  reserved files, the exact test command, the acceptance condition, the
  pre-assigned ADR / doc numbers, what a predecessor slice already changed and
  any partial work it left in the tree, the test-first and
  evidence-before-claims postures, the re-brief that the agent does not commit
  or push, and the status contract itself. Build briefs from
  that template rather than from a partial list; the items an ad-hoc brief
  drops are the ones other parts of this model depend on. Save **every** brief
  to `.delegation/briefs/` before dispatching it, fix-round and scouting briefs
  included, so a steward checkpoint has something to reconcile
  against. The
  subagent reads whatever files it needs, does the work, runs its tests, and
  reports DONE / BLOCKED / NEEDS_CONTEXT with the evidence behind it. A BLOCKED
  report is a decision request with its own procedure
  ([`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#blocked-the-procedure)),
  never a signal to take the task over. The next
  task gets a new agent, not the same one carrying the last task's residue.
  **The manager does not do the reading**, and that is not an efficiency
  preference: the subagent spends its own context window on the files and
  returns a report, so the manager's window accumulates summaries rather
  than file contents and stays coherent across a long run. The full statement,
  including what the framework does and does not contribute to that effect, is
  in
  [`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-loop-mechanics).
- **Fan-out is decided by write set**, not by how independent two tasks feel:
  disjoint write sets run in parallel, overlapping ones serialize, shared
  reads are fine, and reviewers always parallelize safely because they never
  write. Parallel is the default once the checklist clears: slices with
  disjoint write sets dispatch together, and needless serialization is a
  named steward finding (`serialized-the-disjoint`). The forced checklist
  that holds this is
  [`conflict-avoidance-checklist.md`](conflict-avoidance-checklist.md); the
  rules behind it are [below](#conflict-avoidance-hard-won).
- **Implementation is test-first where the deliverable is code** (write the
  failing test, watch it fail for the expected reason, then make it pass), and
  where it is not code the equivalent is writing the acceptance condition down
  before building. Both are postures carried in the brief; nothing verifies
  the ordering after the fact.
- **Evidence before claims.** An agent reports what it ran and what came back,
  never a conclusion standing in for output. The same applies to the manager
  reporting up to the owner.
- Review the whole integrated tree, not half-written slices. Reviewing a
  tree an agent is still writing produces noise, not findings.
- **A BLOCKING finding must earn its gate.** Before any fix round is
  dispatched, the manager adjudicates every consolidated BLOCKING item
  against the fluff-gate yardstick
  ([`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate)):
  REAL (a concrete user-visible failure, a violated written
  contract/invariant, a data/money/privacy/security exposure, or a
  reproducible defect with evidence) gates; FLUFF (taste, scope creep, a
  hypothetical without a trigger, an accepted limit restated, an
  improvement framed as a defect) is demoted to non-blocking or discarded —
  with a written reason, one structured rebuttal round for the original
  reviewer (concede, or stand with new evidence), and a mandatory
  adjudication record at `.delegation/adjudications/round-<N>.md`. No
  silent demotions; doubt resolves toward REAL; judgment stays
  manager-owned, and the record is what makes it auditable.
- Batch the surviving blocking issues into one reconciled fix round
  ([`../skills/consolidating-review/SKILL.md`](../skills/consolidating-review/SKILL.md))
  rather than dispatching piecemeal.
- Re-verify, don't trust the fix report. Re-run the *specific* reviewers
  who were NOT PLEASED, with the fix report **and the adjudication
  record**; have them probe for inputs that still slip through, not just
  confirm the diff. Closure is PLEASED on the *surviving* findings: a spent
  demotion is an accepted, recorded limit and belongs in the body as
  non-blocking, while genuinely new evidence is a new finding, adjudicated
  fresh. A reviewer that still holds NOT PLEASED with every rebuttal spent
  is an unresolved dispute, and it escalates to the owner rather than being
  ground down or written around.
- **Loop-convergence stop-rule:** the loop converges. Each re-review should
  find strictly less than the round before. If late rounds surface only
  one-line nits, you may close without convening another *full* panel: send
  the nits to one final dispatched fix round, re-review **only the dissenters**,
  and add your own exhaustive check on top. What the shortcut never skips is
  the verdicts. The artifact is written only when every reviewer has returned
  PLEASED, and the gate accepts nothing else, so a "shortcut" that leaves a
  dissenter holding NOT PLEASED leaves no artifact anyone can honestly write.
  It also never means the manager fixes the nits itself; a smaller round is
  still a dispatched round.
- **MANAGER INSPECTS** is a procedure, not a glance: reconcile the integrated
  diff against the dispatched allowlists, run the full test command yourself,
  check the artifact's fields including `head_sha`, then stage explicit paths.
  The steps are in
  [`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#manager-inspects-the-procedure).
- **One panel, one commit.** The batch is integrated, reviewed once as a whole,
  and landed in a single commit. The review artifact is bound to one HEAD, so
  it waives exactly one commit; and reviewing the integrated tree rather than
  half-written slices is what this model already asked for.

## The spawn topology: one level deep, the manager is the sole spawner

This framework holds **one-level-deep spawning** by design, and the whole org is
shaped to it. The mechanism is **withholding**, not granting: the spawnable
agent definitions here (`agents/skeptic.md`, `agents/steward.md`) carry `tools:`
frontmatter with no spawn tool in it, leaving them `SendMessage` to siblings
that already exist. The manager's own ability to spawn is not something this
repo issues either; it comes from the manager being the **top-level session**,
which is why `agents/manager.md` is a role you adopt and nothing in the repo
loads it. This is a rule the framework imposes through its own agent
definitions, not a constraint the runtime imposes on it. Grant a spawn tool to a
worker and the topology breaks, which is exactly why no agent definition here
does:

1. **The manager is the sole spawner.** The steward and every worker
   (implementers, skeptics, researchers) are flat siblings under the manager.
   No role below the manager can delegate downward.
2. **No fake tiers.** The manager cannot spawn a "sub-manager" that assembles its
   own team: a spawned agent has no spawn tool, so it can only do that work
   solo. An agent that *appears* to run a delegated sub-team but is really
   working alone is a failure mode to name and refuse: **never present solo work
   as a delegated team.** An agent that needs helpers asks the manager to spawn
   them as further flat siblings.
3. **Genuinely-parallel deep teams are SEPARATE SESSIONS.** When work truly needs
   several independent orchestrators each running their own sub-team, that is
   more than one session, each with its own top-level manager;
   **cross-session coordination is the owner's job**, not a nested spawn.
4. **Lateral coordination is by messaging, not spawning.** Siblings coordinate
   with `SendMessage`; spawning is the single downward edge and only the manager
   holds it.

Role detail and the ASCII picture: [`roles.md`](roles.md#the-org--who-sits-where).

## The steward: beside the loop, governing the manager

The loop above governs *deliverables* (skeptics) and *decomposition* (the
manager runs it). Nothing in the loop governs the manager itself, which
drifts in two self-invisible ways: it **loses the prize** (commissions
locally-satisfying motion that does not move the end goal) or **stops
delegating** (does implementer work itself, over-spawns make-work, or
under-delegates the substantive builds). The steward
([`roles.md`](roles.md#steward), [`../agents/steward.md`](../agents/steward.md))
sits *beside* this loop, not inside the implement→review cycle: it reviews
neither slices nor decompositions but the manager's own conduct, returning a
MANAGER SCORECARD on VISION and DELEGATION. It is a standing flat sibling the
manager spawns and keeps in dialogue, consulted repeatedly across a run, at
checkpoints and before big fan-outs. Its whole purpose is to keep the manager
from going too deep and losing the plot. Honest limit: it is discipline and
adversarial accountability, *not* a structural wall. No gate sits behind it, the
manager can ignore its scorecard, and manager judgment stays human-owned. Its
recourse on an ignored load-bearing flag is to escalate to the owner, not to
command. It raises the cost of self-deception; it does not enforce.

## Manager auto-consults — a standing, binding rule

The manager does not wait to be told to consult its peers. Consultation is
automatic and binding, a standing rule of the operating model rather than
something the owner has to remember to trigger. The owner should never have to
say "did you check with the steward?"; the manager convenes the
steward itself, at the moments below, every time.

It is **tightly scoped, not "every commit."** The checkpoints below are a short,
defined list, and most consults should return fast. A "no concern, proceed"
is the common, cheap case, and a peer that only ever returns that on a genuinely
clean run is doing its job, not failing to. The point is a standing, binding,
low-friction default, not a tax on every action.

Consult the STEWARD ([`../agents/steward.md`](../agents/steward.md)), the
execution check, at these fixed checkpoints:

- **Before any major or irreversible commit.** Anything that is costly to undo
  gets a steward read first: is this on-prize, and did it come from delegation
  rather than the manager quietly doing IC work?
- **On any allocation or spawn decision (fleet size).** Before scaling a
  fan-out up or down (how many agents, how big the panel) the manager checks
  with the steward, which watches exactly for over-spawning make-work and
  under-delegating the substance.
- **After any significant result.** A workstream landing, a panel converging, a
  hard build finishing: the moment a run *feels* productive is the moment drift
  hides best, so it is a fixed checkpoint, not an optional one.

The steward also holds the **yardstick** (the direction, the prize, meaning the
load-bearing end-goal claim, and the on-plan-vs-off line, all derived from the
owner's stated goal) and scores VISION against it. The consult answers *"are you
delegating well and still on-prize?"* Because the steward is a flat sibling and
not a boss, a steward flag the manager rejects, if the two cannot resolve it
between them, escalates to the owner, the only authority above the manager;
see [`roles.md`](roles.md#the-org--who-sits-where).

**The one andon-cord exception.** Most steward consults are advisory: flag,
manager decides, work continues. On one narrow, closed class the steward's
consult is *escalate-before-proceed*: **major allocations, new workstreams, and
any change that trades away a proven invariant.** On those the manager **pauses
that specific action** until the owner rules, a targeted pause rather than a
general veto (see [`../agents/steward.md`](../agents/steward.md#the-one-narrow-andon-cord--escalate-before-proceed)).

**Honest limit:** this is a standing *discipline* the
manager holds itself to, not a hook-enforced wall. There is no gate that denies
the manager's next act for skipping a consult, and even the andon-cord pause is a
rule the manager honors rather than a structural block. It is binding as a rule
and owner-visible when skipped; it is not structural enforcement. The point is
that the manager consults *by default*, so the owner never has to be the reminder.

## When to use this model (the trivial-edit gate)

Use it for substantial, multi-part builds where independent review adds
real safety: a feature batch, a hardening pass, a migration.

**Do NOT delegate a trivial edit or a single-file fix.** The overhead isn't
worth it; just do it. (The `/delegate` command states this gate up front.)

One consequence to know before the first run: the opt-in persists. Once a loop
has armed a repo, the `.delegation/` marker stays, and every later commit there
needs a current all-PLEASED artifact, trivial edits included. That is the gate
working, not a bug, but it is reversible: **deleting `.delegation/` un-arms the
repo**, and the gate plus both reminder hooks go silent in it immediately. The
marker holds no state the framework needs afterwards, so re-arming is just
running the loop again.

**Panel-sizing heuristic:** **2–3 skeptics for a small change, 5–7 for a
feature batch.** Scale the panel to the risk, not to habit. Tier the panel
too: skeptics run on Sonnet, or Haiku for a narrow mechanical lens, never
Opus — the full model ladder (manager on Opus; everything below on Haiku or
Sonnet, Opus by written exception) is in
[`../skills/delegating/SKILL.md`](../skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what).

## Reliability / stall rules

- **Silence ≠ progress.** A working agent writes files. Watch file-write
  activity (mtimes / `git status`), not just completion notifications. An
  agent that has produced *nothing* after several minutes is stalled — stop
  it (`TaskStop`) and **re-brief with a concrete design decided for it**, not
  an open-ended "figure out whether this is solvable." *(In one recorded run
  that open-ended framing caused a **26-minute** no-output stall; the
  re-brief with a concrete spec finished in **~2 minutes**.)*
- **Integrate the slices, run one panel over the integrated tree, then make one
  commit**, staging explicit paths. **Never `git add -A` while another agent
  writes.** Do not land disjoint slices as they finish: the review artifact
  binds to a single HEAD, so one panel waives one commit, and reviewing the
  integrated tree rather than half-written slices is the rule this model
  already holds. The reliability concern behind the older per-slice advice
  stands and is worth naming: unreviewed work should not pile up in the tree,
  because a diff too large to read is a panel that reviews nothing. The way to
  honour it is a **smaller batch**, fewer slices per panel and panels more
  often, not more commits per panel.
- **The implementation agent does NOT commit or push.** It leaves work in the
  tree; the manager commits, after the panel gate. (This is also what
  makes the commit gate meaningful: the gate fires on the manager's commit,
  which happens *after* review. An implementer that self-commits mid-slice
  would land work before any panel ran.)
- Never let a green suite read as more than it is. Distinguish "passes
  against a proxy we built" from "proven on the real target." Keep that
  honest in the docs the deliverable ships with.
- Keep an accepted-residual honest. A known gap the current design can't
  close is a labelled `xfail` canary with a reason, not a deleted test.

## Conflict avoidance (hard-won)

Parallel agents that write the same files clobber each other. Prevent it
structurally:

- Disjoint directories run in parallel; a shared directory runs
  sequentially. Two tasks touching the same package are sequential; a task
  in an unrelated package runs parallel to them.
- Reserve shared index files for the manager: an ADR index, a front-door
  routing file, a capability map. Forbid agents from touching them; the
  manager wires them at integration.
- Pre-assign ADR / doc numbers so parallel agents don't collide on the
  same `000N`.
- Give each agent an explicit file-ownership allowlist in its prompt, and
  the exact test command to run.

Before *any* parallel dispatch, the manager fills the
[conflict-avoidance checklist](conflict-avoidance-checklist.md), a forced
artifact rather than a suggestion. The `delegating` skill will not fan out
without it.

## The commit gate (the one structural slice)

The panel produces a review artifact
(`.delegation/review-artifact.json`; format in
[`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md)).
A PreToolUse hook denies the git subcommands that introduce newly authored work
(`commit`, `cherry-pick`, `revert`, `am`, including their `--continue` and
including `--amend`) unless a well-formed, all-PLEASED artifact bound to the
current HEAD exists. It acts only in repos that have opted in by carrying a
`.delegation/` directory at the repo root **that the HEAD commit does not
carry** (the `delegating` skill creates it when a loop starts, and adds it to
that repo's `.gitignore` in the same step). A marker HEAD *does* carry arrived
with the repository rather than from anyone in this working copy, so it is not
consent: the gate warns and stands down. Staging the marker with `git add`
changes nothing to the verdict, because staging is a local act, but the gate
warns on the way past: the next commit would carry the marker into HEAD and
stand the gate down everywhere. Claiming an inherited marker as your own opt-in
takes `git rm -r --cached .delegation`, a gitignore line, **and a commit of
that removal**, which is itself ungated precisely because the marker counts as
inherited until HEAD stops carrying it. Note the direction: that sequence turns
enforcement **on**. Switching it off is `rm -rf .delegation`. Within its reach, skipping
review takes a *visible act*, not a lapse of memory.

`pull`, `merge` and `rebase` are **not** gated, and neither are `reset`,
`restore`, `push`, `add` or anything read-only. They integrate or replay
commits that were already gated when they were authored, or author no commit at
all, so re-gating them would demand a fresh panel for reviewed work and would
deny routine integration in every armed repo. Nor is any command carrying
`--abort`, `--skip`, `--quit` or `--dry-run` outside quotes. Two residuals,
stated plainly: landing a branch with `git merge --no-ff` produces a merge
commit no artifact covers, because the review happened at the commits inside
the branch rather than at the merge; and `git reset --soft HEAD~1` moves HEAD
back, which re-arms a spent artifact, so one artifact can waive more than one
commit that way. The second is deliberate and strictly weaker than the already
documented `bash -c "git commit"` bypass: the only way to spend an artifact is
to make the commit it authorised, so the re-arm returns exactly what was just
used.

`--amend` is gated for a reason worth knowing before it surprises you at the
keyboard: an amend writes a new commit whose content is whatever is staged, so
allowing it would let `git add unreviewed.py && git commit --amend --no-edit`
launder unreviewed work through an artifact that was already spent. Amending
the message of a commit you just landed therefore needs a fresh artifact, since
HEAD moved when that commit landed.

Because the artifact binds to a single HEAD, **one panel waives exactly one
commit**: integrate, review once, commit once.

Five honest limits travel with it: it fires only where this plugin's hooks are
installed and enabled and a Python 3.7+ interpreter answers to `python3`,
`python` or `py -3`; it checks that the artifact exists, is well-formed
(including a non-empty `lens` on every review and an empty
`consolidated_blocking`), and is all-PLEASED, never that the review was
rigorous, so it walls off forgetting rather than bad faith; it gates the local
commit only; commits the matcher never sees (aliases, subprocesses, IDE
commits) bypass it, and a path built from variables or nested quoting still
does not resolve, though it no longer waives: the gate falls back to the hook's
own repo and prints a line saying which repo it scoped itself to; and, being
session-global, it can false-positive on an exotic compound command. The full
text of all five, with the escape hatches, is the canonical statement in the
[README](../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline).

After a gated commit lands, the manager **archives the artifact** (e.g. move
it to `.delegation/history/`) so a stale all-PLEASED file cannot silently
waive review for the *next batch*, which under one panel one commit is the
unit that follows.
