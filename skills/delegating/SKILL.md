---
name: delegating
description: Use when running a substantial multi-part build as a manager delegating to implementation agents with skeptic review - covers the fresh-subagent-per-task loop, fan-out by disjoint write sets, test-first and evidence-before-claims postures, skeptic pairing, panels, reliability rules, conflict checklist, and the commit gate
---

# Delegating

You are the manager. This skill carries both halves of the job: the mechanics
of the loop you run, and the rules this framework adds on top of it. There is
no companion plugin to install and no mechanic routed away by name. If a
mechanic is not written down here or in a file this skill links to, it is not
part of the framework.

**First: the trivial-edit gate.** Do NOT delegate a trivial edit or a
single-file fix; the overhead isn't worth it, so just do it. Use this loop for
substantial, multi-part builds where independent review adds real safety.

## The loop mechanics

### DECOMPOSE: the procedure

Decomposition is the step the loop names first and explains least, so here it
is as a procedure. Run it in order.

1. **Write the end goal as a falsifiable claim.** Not a topic ("harden the
   API") but a claim whose *non*-movement you could catch ("the export endpoint
   returns valid CSV for empty, single-row and unicode inputs"). Every brief
   quotes it, every skeptic scores against it, and the steward refuses to score
   VISION without it. If you cannot write one, get it from the owner before
   dispatching anything.

2. **Scout before you cut slices, and delegate the scouting.** Here is a real
   circularity: a brief must carry a per-file allowlist and the exact test
   command, and on a repo you have never seen you cannot produce either, yet
   you are told not to read the tree. The resolution is not to relax the rule.
   It is that **reconnaissance is itself a slice**, and it is the default:
   dispatch one read-only **scouting agent** first, briefed from the same
   template as any other, whose deliverable is a written map and which modifies
   nothing. Ask it for exactly what a brief needs:

   - the directory map to depth two, and which directories are actually live;
   - **where the tests live and the exact command that runs them, quoted from
     the config file it read** (`pyproject.toml`, `package.json`, `Makefile`,
     CI config), not inferred from convention;
   - the build / lint / typecheck commands, the same way;
   - the shared index files, front-door docs and generated files, which you
     will reserve to yourself;
   - the set of files that would have to change for the stated claim, grouped
     into candidate slices with the overlaps between them named.

   Use the same template: the allowlist is empty (it writes nothing outside its
   own report), the test command slot says which commands it may run to *read*
   the repo, and the acceptance condition is that every fact in the report cites
   the file it came from. That report is a deliverable like any other, so the
   law applies with no exception: pair it with at least one skeptic. A cheap
   `evidence-vs-claim` lens is the right one, and the question it should ask is
   whether the test command was quoted from a file or guessed.

3. **The one narrow exception: a bounded manager scouting pass.** For a small
   or already-familiar repo, a scouting slice is overhead. You may then scout
   yourself, but only for *structural* facts, and the cap is explicit: commands
   that return shape rather than content (`git ls-files`, `ls`, `rg --files`),
   plus reading the manifest and the test-runner config. **You may not read
   module bodies.** The line is sharp and worth holding: learning *where things
   are* and *how they run* is manager work; reading a module to decide *how a
   slice should be written* is the implementer's job, and it spends the context
   window the whole loop exists to protect. If the pass starts pulling you into
   source files, stop and dispatch a scouting slice instead.

4. **Cut slices by write set, not by topic.** Each slice is one outcome, one
   owner, one test command. Two "different" tasks that write the same file are
   one slice or two sequential slices, never two parallel ones.

5. **Reserve the shared files to yourself** (indexes, front-door routing docs,
   capability maps) and pre-assign any ADR or doc numbers, so parallel agents
   cannot collide on `000N`.

6. **Fill the conflict-avoidance checklist** (section 4 below). If it shows an
   overlap you cannot remove, serialize those slices; do not fan out anyway.

7. **Size the batch to one panel and one commit.** The review artifact binds to
   a single HEAD, so a batch is reviewed once and lands once. A batch big
   enough that one panel cannot really read the integrated diff is too big:
   cut it into two batches, each with its own panel and its own commit.

8. **Write the briefs from the template below** and save each one to
   `.delegation/briefs/<slice-id>.md` *before* dispatching it.

### One scoped task per fresh subagent

Spawn **one implementation agent per task**. There is no implementer agent
definition to spawn, by design: implementers are briefed inline, one per slice,
so spawn your runtime's **general-purpose worker subagent** (in Claude Code,
`subagent_type: "general-purpose"`) and put the entire brief in its prompt.
Never grant a worker a spawn tool.

Every brief is written from [the template below](#the-brief-template). Build it
from the template rather than from memory: a brief assembled ad hoc reliably
drops the no-self-commit re-brief, which this skill also says cannot be
assumed, and that omission alone makes the commit gate gate nothing.

The agent then opens whatever files it needs, does the work, runs its own
tests, and reports back with a status of **DONE**, **BLOCKED**, or
**NEEDS_CONTEXT**, plus the evidence behind it (what it ran and what came
back). Then it is finished. The next task gets a **new** agent, briefed from
scratch, not the same agent carrying the last task's residue. A NEEDS_CONTEXT
report comes back for a fuller brief, and you answer it by extending the brief
rather than by taking the task over; a BLOCKED report has its own procedure,
two sections down.

### The brief template

Copy this whole block, fill every slot, save it to
`.delegation/briefs/<slice-id>.md`, then dispatch it. Nothing in it is
decorative: the postures and the status contract are the parts an ad-hoc brief
drops, and each one is load-bearing somewhere else in this framework.

```
BRIEF <slice-id>

END GOAL (the falsifiable claim this run must move, quoted):
  <the claim; not a topic>

YOUR ONE TASK (an outcome, not a direction to explore):
  <the single outcome this slice delivers>

FILE-OWNERSHIP ALLOWLIST (create or modify ONLY these):
  <paths / globs>
  Everything else in this repo is READ-ONLY to you. Read whatever you need.

RESERVED, DO NOT TOUCH (the manager wires these at integration):
  <shared index files, front-door routing docs, capability maps>
  plus everything under .delegation/ (briefs, checklist, review artifact).

EXACT TEST COMMAND (copy-pasteable; run it yourself):
  <command>

ACCEPTANCE CONDITION (what must be true for this to be done):
  <checkable condition>

POSTURES (requirements, not preferences):
  1. TEST-FIRST where the deliverable is code: write the failing test, watch it
     fail for the reason you expected, then write the code that makes it pass.
     Where the deliverable is not code, write the acceptance condition down
     before you build.
  2. EVIDENCE BEFORE CLAIMS: report what you ran and what came back. "Tests
     pass" is not a report; the command and its output are.
  3. YOU DO NOT COMMIT OR PUSH. Leave your work in the working tree. The
     manager commits once, after the review panel. This overrides any default
     you carry about committing your own work.
  4. YOU DO NOT SPAWN. If you need a helper, say so in your report and the
     manager spawns it as your sibling; coordinate laterally by messaging.

REPORT BACK exactly one status, with the evidence behind it:
  DONE          <what you built, plus the test command and its actual output>
  BLOCKED       <what stopped you, what you ran, and the decision you need>
  NEEDS_CONTEXT <the specific missing fact you need in the brief>
Then stop. The next task gets a fresh agent.
```

Why each part is there, in one line each: the end goal, because a reviewer or a
worker without it optimizes line coverage; the allowlist and the reserved list,
because parallel writers clobber each other silently and the index files are
yours; the exact test command, because "run the tests" is not copy-pasteable;
posture 3, because general-purpose briefs default to "commit your work" and a
self-committed slice lands before any panel runs; posture 4, because
one-level-deep spawning is this framework's load-bearing invariant; and the
status contract, because it is what closes a task instead of leaving it open.

### BLOCKED: the procedure

A BLOCKED report is a **decision request**, not a failure and not an invitation
to take the task over yourself.

1. **Read the evidence.** What it ran, what came back. A BLOCKED report with no
   evidence is not actionable: ask for the evidence rather than guessing at the
   cause.
2. **Classify the blocker.** There are four kinds and they have different fixes:
   (a) a **decision only you can make** (the brief was ambiguous, or two
   acceptable designs exist); (b) a **missing input** (a file outside the
   allowlist has to change, a credential, an absent dependency); (c) a
   **collision** with another live slice's writes; (d) the slice is
   **mis-scoped**, or its acceptance condition is not achievable as stated.
3. **Act by class.**
   - (a) Decide it, concretely, and re-brief with the decision already made.
     Never re-dispatch an open-ended "figure out whether this is solvable";
     that framing is what the stall rule below is about.
   - (b) Either extend the allowlist, but only if it stays disjoint from every
     live slice, or cut the extra work into its own slice and serialize. Never
     authorize an agent to write outside its allowlist "just this once": the
     filled checklist stops being true the moment you do.
   - (c) Serialize the two slices, re-fill the checklist, and brief the second
     on what the first changed.
   - (d) Re-decompose. Stop any sibling slice that depends on the shape you
     just found to be wrong, rather than letting it finish against it.
4. **Always a fresh agent.** Re-brief means a new agent with a complete brief,
   not another message to the blocked one. The blocked agent's context is now
   full of the dead end.
5. **Decide what happens to the partial work** it left in the tree, explicitly:
   keep it (and say so in the next brief, so the fresh agent is not surprised
   by it) or revert those paths. Half-written work nobody owns is what makes a
   later panel produce noise.
6. **Append the resolution to the saved brief** in `.delegation/briefs/`. That
   file is the record a steward checkpoint reconciles against, and "why did
   this slice change shape" is exactly what it cannot recover otherwise.

**You do not do the reading.** The whole point of the brief is that the
subagent, not you, opens the files. If you find yourself reading a module in
order to decide how a slice should be written, you have quietly taken the
implementer's job: write the brief and hand it over instead. The exceptions
are narrow and named elsewhere in this skill (you own the reserved index files
and you inspect the integrated tree before committing).

**Why this preserves your coherence over a long run.** You and each subagent
have separate, finite context windows. The subagent spends its own window on
the files: it opens them, holds them, reasons over them, and returns you a
report. Your window receives the report and never the file contents. So across
a long run your window accumulates summaries rather than files, and you can
still hold the shape of the whole job at task forty because you never paid
full price for tasks one through thirty-nine. Be accurate about what that is.
It is an ordinary consequence of delegating well, available to anyone who
delegates the same way, and this framework ships no compaction engine and no
context management of its own. What the framework contributes is organizing
the practice (one scoped task per agent, a brief complete enough that the
agent never has to come back, a status contract that closes the task) and
pressing you not to abandon it, because the failure mode is not that the
technique stops working. It is that a manager under time pressure starts
reading files itself, and spends the window it was protecting.

### Fan-out: disjoint-parallel, shared-sequential

Two agents that write the same file clobber each other, and the loser's work
disappears without an error. So parallelism is decided by **write sets**, not
by how independent the tasks feel:

- **Disjoint write sets run in parallel.** Two tasks in unrelated directories,
  with no file in common, dispatch together.
- **Overlapping write sets serialize.** Two tasks touching the same file, the
  same package, or the same shared index run one after the other, and the
  second is briefed on what the first changed.
- **Shared reads are fine.** Agents may read the same files freely. It is the
  writes that collide.
- **Reviewers always parallelize safely**, because a skeptic never modifies
  what it reviews.
- **Shared index files (ADR indexes, front-door routing docs, capability maps)
  belong to you**, not to any agent, and you wire them at integration.

Before any parallel dispatch, fill the conflict-avoidance checklist. It is a
forced artifact rather than advice, and the rules and rationale live there, so
they are not restated here: see section 4 below and
[`../../docs/conflict-avoidance-checklist.md`](../../docs/conflict-avoidance-checklist.md).

### Requesting and receiving review

Review is not something an implementer performs on its own work. When a task
reports DONE, you request review separately, from agents that did not build
the thing. The panel machinery itself is
[`../skeptical-review/SKILL.md`](../skeptical-review/SKILL.md); what belongs
here is the connective tissue around it:

- **Request review of the integrated tree**, and only after every parallel
  slice has reported DONE. A tree with a half-written slice in it produces
  noise instead of findings.
- **Give each reviewer what it needs to be adversarial**: the deliverable, the
  end goal the work was supposed to move, and the claim the work makes. A
  reviewer with no stated end goal returns line-coverage nitpicking.
- **Receiving a finding is not the same as accepting it.** You adjudicate.
  A numbered BLOCKING item either enters the fix round or gets an explicit,
  recorded reason for rejection. Two lenses demanding opposite fixes get
  resolved by you *before* dispatch, or the fix agent will thrash.
- **The fix round is dispatched, not performed by you**, and the fix agent is
  bound by the same posture rules as any implementer.
- **Re-review the dissenters** against the revision, briefed to attack it as
  fresh work rather than to tick off their old list.

### MANAGER INSPECTS: the procedure

The last step before the one commit, and the only step in the loop that is
yours alone. A unanimous panel is necessary, not sufficient. Work the list:

1. **Read the integrated diff.** `git status --porcelain` and `git diff` over
   the whole tree. You are reading the diff, not the modules: this is a
   reconciliation pass, not the reading the implementers did for you.
2. **Reconcile every changed path** against the union of the dispatched
   allowlists (from `.delegation/briefs/`) plus your reserved set. Anything
   outside both is an **unexplained delta**, and it is one of two things: work
   you did yourself, which is exactly what the steward flags, or an agent that
   wrote outside its allowlist, which means the filled checklist was not true
   and the parallel dispatch was unsafe. Neither ships silently.
3. **Run the full test command yourself and keep the output.** Not the slice
   commands, and not the slices' reports of them. Evidence before claims
   applies hardest here, because you are about to relay it upward.
4. **Check the reserved files are actually wired**, since nobody else was
   allowed to touch them and it is the step that gets forgotten at the end of a
   long run.
5. **Check the artifact**: non-empty `deliverable`, a valid `mode`, an accurate
   `rounds`, every verdict exactly `PLEASED`, every `blocking` list empty, and
   `head_sha` equal to `git rev-parse HEAD` **right now**. Fill `head_sha`
   last, once the tree has stopped changing; a fix round after you write it
   leaves the artifact bound to the same HEAD but describing an older tree.
6. **Check `.delegation/` is in this repo's `.gitignore`** and that neither the
   marker nor the artifact is staged.
7. **Stage explicit paths and commit once.** Never `git add -A`. One panel, one
   commit.
8. **Archive the artifact** to `.delegation/history/` after the commit lands,
   so a spent all-PLEASED file cannot waive the next batch.

If your own inspection finds something, that is a fix round and a re-review,
not a note in the commit message.

### Test-first implementation

Where the deliverable is code, the brief says test-first: write the failing
test, watch it fail for the reason you expected, then write the code that
makes it pass. A test written after the code tends to encode what the code
does rather than what it was supposed to do, and it has never been observed
failing, so nothing establishes that it *can* fail. Where the deliverable is
not code, the equivalent is to write down the acceptance condition before
building, so there is something to check against that was not chosen after the
fact. This is a posture in the brief, not a system: the framework has no way to
verify a test was written first.

### Evidence before claims

An agent reports what it ran and what came back, not what it concluded.
"Tests pass" is not a report; the command and its output are. The same holds
one level up: when you tell the owner a slice is done, you are relaying
evidence you actually saw, and where you did not see it, say so rather than
smoothing it over. The `evidence-vs-claim` lens in
[`../../docs/lenses.md`](../../docs/lenses.md) exists because this is the
posture that decays first under time pressure, in agents and in managers
alike.

## What this framework adds on top of the loop

### 1. The law

> Every deliverable carries at least one adversarial skeptic before it is
> trusted — **research, design, implementation — all of them. The floor is
> one. No exceptions.**

A code review after each task covers code. This law covers *every* deliverable
kind. Attach skeptics via the `skeptical-review` skill; the reviewer definition is
`agents/skeptic.md` (spawn as `subagent_type: "skeptic"`).

### 2. Panel sizing

**2–3 skeptics for a small change, 5–7 for a feature batch.** Scale to risk,
not habit. Lens choice: [`../../docs/lenses.md`](../../docs/lenses.md).
Verdict format: [`../../docs/rubric.md`](../../docs/rubric.md).

### 3. TWO standing posture rules

Both are load-bearing; hold both or the commit gate gates nothing:

- **Rule 1, no auto-commit on DONE.** "Don't stop between tasks" still governs
  *within* a slice: an implementation agent runs to DONE without check-ins.
  But the manager does **not** commit on a DONE report. Between "slice DONE"
  and "commit" sits the panel gate: attach ≥1 skeptic → consolidate BLOCKING →
  fix round → re-review dissenters → manager inspects the integrated tree →
  *then* commit.
- **Rule 2, the implementer does not self-commit (the commit gate depends on
  this).** The implementation agent does NOT commit or push. It leaves work in
  the tree and **only the manager commits**, after the panel. General-purpose
  implementer briefs commonly default to "commit your work," so this cannot be
  assumed: **you must re-brief every implementation agent explicitly:** *"You
  do not commit or push. Leave your work in the tree; the manager commits
  after review."* Without this re-brief, the slice self-commits mid-work and
  the PreToolUse commit gate gates nothing.

### 4. The forced conflict-avoidance checklist (before ANY fan-out)

Before dispatching agents in parallel, copy and fill
[`../../docs/conflict-avoidance-checklist.md`](../../docs/conflict-avoidance-checklist.md)
into the working repo (suggested: `.delegation/conflict-checklist.md`). This
is a forced artifact, not advice: **no parallel dispatch until every line is
filled.** If filling it shows overlapping write sets you cannot remove,
serialize those slices. Summary of what it forces: disjoint per-agent write
sets; index files reserved to the manager; pre-assigned ADR/doc numbers; a
file-ownership allowlist and exact test command in every brief.

### 5. Pair a standing steward (it governs YOU)

The panel governs deliverables; nothing in the loop governs *you*, the manager.
You drift in two ways you cannot see: **losing the prize** (commissioning
locally-satisfying motion that does not move the end goal) and **failing to
delegate** (doing implementer work yourself, over-spawning make-work, or
under-delegating the substantive builds). Pair a standing steward
([`../../agents/steward.md`](../../agents/steward.md), spawn as
`subagent_type: "steward"`) and consult it repeatedly, at checkpoints and
before big fan-outs, sized to the run: skip it for a short, low-stakes loop;
consult it often on a long or high-stakes one where drift would go unnoticed.
It returns a MANAGER SCORECARD (VISION + DELEGATION) with cited evidence. It is
disciplined accountability, not a gate. No hook enforces its verdict, you
can ignore it, and your judgment stays yours; it only raises the cost of
self-deception. Role detail: [`../../docs/roles.md`](../../docs/roles.md#steward).

**Give it the two things it reads from disk, or it cannot do the job.** The
steward reconciles what landed against what was dispatched, so it needs the
dispatch briefs on disk: **save every brief to `.delegation/briefs/<slice-id>.md`
before dispatch** (the template above is written to be saved as-is). Without
them the steward cannot separate your direct work from delegated work, and its
DELEGATION line is unrecoverable for that window, which it will say rather than
fake. It also compares each checkpoint against its own earlier ones to catch
slow directional drift, so **save each returned scorecard to
`.delegation/steward/<checkpoint>.md`**, which is where it looks for them.

### 6. Reliability / stall rules

- **Silence ≠ progress.** Watch file-write activity (mtimes / `git status`),
  not completion notifications. An agent with *no* output after several
  minutes is stalled: stop it (`TaskStop`) and **re-brief with a concrete
  design decided for it**, never an open-ended "figure out whether this is
  solvable" (that framing once caused a 26-minute no-output stall; the
  concrete re-brief finished in ~2 minutes).
- **One panel, one commit: integrate, review the integrated tree once, then
  make a single commit staging explicit paths.** **Never `git add -A` while
  another agent writes.** Do not try to land disjoint slices individually as
  they finish. The review artifact is bound to HEAD, so it waives exactly one
  commit, and this is also what the framework already asked for on its own
  terms: review the integrated tree, never half-written slices. The reliability
  point underneath the older per-slice advice is real and survives: do not let
  a large pile of unreviewed work accumulate in the tree, because a huge diff
  is a diff no panel really reads. Honour it by keeping the *batch* small,
  fewer slices per panel and panels more often, not by slipping single slices
  past the gate.
- Full detail: [`../../docs/operating-model.md`](../../docs/operating-model.md).

### 7. The loop and the commit gate

```
DECOMPOSE → IMPLEMENT (fresh subagent per task, parallel where safe)
          → REVIEW PANEL (skeptical-review: 2–7 skeptics, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING (consolidating-review) → FIX ROUND
          → RE-REVIEW dissenters → until every reviewer is PLEASED
          → MANAGER INSPECTS → COMMIT (gate checks the artifact)
```

- Each named step has a procedure above:
  [DECOMPOSE](#decompose-the-procedure), the
  [BLOCKED branch](#blocked-the-procedure) of the status contract, and
  [MANAGER INSPECTS](#manager-inspects-the-procedure).
- Review the whole integrated tree, never half-written slices, and land it in
  **one** commit: the artifact binds to one HEAD.
- Convergence stop-rule: each re-review must find strictly less; if only
  new one-line nits keep appearing, fix them and close on an exhaustive
  manager check.
- **Read convergence by severity and region, not by count.** A fix round can
  raise the count while genuinely improving the deliverable — the new findings
  are usually *in the part you just rewrote*, which is the rule working, not
  failing. Two questions decide it: are the new findings less severe, and are
  they concentrated in the changed region? If findings cluster in one component
  across rounds, that component needs a different *form* (see below), not
  another revision.
- **Brief re-reviewers to attack the revision as fresh work**, not merely to
  tick off their old list. Most defects in a fix round are newly introduced.
  Two failure modes to name explicitly in the re-brief: **relocated is not
  resolved** (an overclaim moved to another section is still an overclaim), and
  **renamed is not resolved** (a field renamed but still read by nothing).
- **When a component keeps producing contradictions in prose, change its
  form.** If two rounds of increasingly precise English about the same ordering
  or algorithm each yield a *new* contradiction, stop specifying and build it,
  with the reviewers' findings as test cases. Then have the prose point at the
  code as normative rather than restate it. Building surfaces defects prose
  review structurally cannot reach, and the tests keep them fixed.
- **Arm the gate at loop start:** create a `.delegation/` directory at the
  repo root when you begin the loop (it also holds the filled conflict
  checklist and, later, the review artifact). This directory is the
  **opt-in marker**: the commit gate and reminder hooks act only in repos
  that carry it, because plugin hooks are session-global and must not wall
  off unrelated repos.
- **In the same step, add `.delegation/` to that repo's `.gitignore`** if it is
  not already there. This is not tidiness, it is required, and it closes two
  real failure modes at once. If the marker gets committed, every contributor
  who has this plugin installed starts getting their commits denied by a
  framework they never installed, since the marker carries no ownership or
  provenance, so its mere presence is the entire authorization model. And if a
  review artifact gets committed while all-PLEASED, every clone carries a
  permanent waiver and the gate enforces nothing while still reporting that it
  is on. Both are one `git add .` away by default. Removing `.delegation/`
  later is how a repo is **un-armed**, and it is the escape hatch of last
  resort if the gate ever denies something it should not.
- When the panel is all-PLEASED, ensure the review artifact exists at
  `.delegation/review-artifact.json` (written per the `skeptical-review`
  skill), including `head_sha` from `git rev-parse HEAD`. The PreToolUse commit
  gate denies the git subcommands that introduce newly authored work
  (`commit`, `cherry-pick`, `revert`, `am`) without it. `pull`, `merge` and
  `rebase` are *not* gated: they integrate commits that were already gated when
  they were authored. The residual is honest and worth knowing: landing a
  branch with `merge --no-ff` is not gated, because the review happened at the
  commits inside the branch, not at the merge. After
  committing, archive the artifact to `.delegation/history/` so it
  cannot waive the next batch. The gate has five honest limits, and they are
  stated in full in the
  [README](../../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline):
  it needs hooks enabled and `python3` on PATH, the artifact is fabricable, it
  reaches the local tree only, it can be evaded or mis-resolved by parsing,
  and it can rarely over-reach.

## References (skill-referenced data, read on demand)

- [`../../docs/operating-model.md`](../../docs/operating-model.md): the full playbook
- [`../../docs/roles.md`](../../docs/roles.md): manager / implementer / skeptic
- [`../../docs/example-run.md`](../../docs/example-run.md): one worked run, end to end
