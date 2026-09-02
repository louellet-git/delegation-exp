---
name: delegating
description: Use when running a substantial multi-part build as a manager delegating to implementation agents with skeptic review - covers the fresh-subagent-per-task loop, fan-out by disjoint write sets, test-first and evidence-before-claims postures, skeptic pairing, panels, reliability rules, conflict checklist, and the commit gate
---

<!--
  Owner authorization for the planner seam, the model ladder, and the
  parallel-by-default rule. The do-not-modify guard (../../README.md)
  requires framework changes to carry explicit owner authorization; this
  one's, verbatim: "I want for the planning framework to, like, finish
  planning, make its plan, and then, uh, spawn a delegation manager for
  actually implementation. And then when the delegation manager has a
  question, it should relay that message back to the planner, um, and so on
  and so forth, like, just like a back and forth. [...] I want there to be a
  firm, like, delegation is Opus. Planner is Opus or Fable, preference for
  Fable five, not five point one. And anything below the delegation manager
  should be, like, Haiku, Sonnet, or Opus. Like, even the reviewers.
  Reviewers do not need to be Opus. [...] I want the planning framework and
  the delegation framework to have, like, incentive to parallelize work when
  that's needed." (owner, 2026-09-02)

  And the ladder's standing order, same owner, same day: "if the scope
  warrants heavier reviewers/implementers then break the task down into
  smaller chunks don't just increase the model strength of the
  implementer/reviewer unless it's truly warranted."
-->

# Delegating

You are the manager. This skill carries both halves of the job: the mechanics
of the loop you run, and the rules this framework adds on top of it. There is
no companion plugin to *install*: nothing here loads, resolves, or validates
another plugin, and if a mechanic is not written down here or in a file this
skill links to, it is not part of the framework. One soft seam exists, by
name only: when the sibling planning-framework delivers a finished plan as
this run's task, the plan intake and the planner relay below apply. When that
sibling is absent, nothing here references it at runtime and nothing fails.

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

   **When the task arrives as a delivered plan** (the planning-framework's
   planning package, usually handed off by the very session you are in, which
   finished planning, shed the planner role, and adopted this one), the
   claims are already written: the package's success definition is the
   run-level claim and each leaf task card carries its own acceptance
   condition. Take them as given rather than re-deriving them, and map card
   to brief with the table the plan itself carries ("What the plan hands to
   an executor" in its `PLAN-FORMAT.md`): Objective to END GOAL and YOUR ONE
   TASK, Authority to the allowlist and the reserved list, Done when to the
   acceptance condition, Evidence required to evidence-before-claims,
   Non-goals to out-of-scope. The seat may be shared; the roles are not: as
   manager you execute the plan, you do not edit it, and where a card is
   ambiguous or silent the question goes back to the planner (the planner
   relay, below) rather than being decided by manager fiat.

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

   Use the same template, and save the brief to `.delegation/briefs/` like any
   other. The report needs a destination, or the slice has no deliverable, so
   its allowlist is exactly one path: `.delegation/scouting/<slice-id>.md`.
   That single file is the **one exception** to the template's standing
   "everything under `.delegation/` is reserved" line, and the brief must say
   so explicitly. Read-only here means it modifies nothing in the repo *except*
   the report it was dispatched to write. The test command slot says which
   commands it may run to *read* the repo, and the acceptance condition is that
   every fact in the report cites the file it came from. That report is a
   deliverable like any other, so the
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
   cannot collide on `000N`. A number you assigned and did not transmit is a
   number the agent will pick for itself: put each slice's numbers in that
   slice's brief, in the PRE-ASSIGNED NUMBERS slot of the template below.

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

**Naming convention, since this repo uses two.** Skills and commands are
addressed with the plugin namespace (`delegation-framework:delegating`,
`/delegate`); agents are spawned by the bare `name:` from their own frontmatter,
unnamespaced: `subagent_type: "skeptic"`, `subagent_type: "steward"`,
`subagent_type: "general-purpose"`. If your runtime lists plugin agents under
some other id, use the one it lists.

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
rather than by taking the task over (and where the missing fact is plan
content you do not own, by relaying the question first: the planner relay,
below); a BLOCKED report has its own procedure, two sections down.

### The model ladder: who runs on what

Model choice is part of the dispatch, not a mood. The ladder is owner-set
and firm:

- **The manager runs on Opus.** The manager is a role the top-level session
  adopts, so no frontmatter can enforce this: hold the role on an Opus
  session. When a planning session running Fable hands off to you, offer the
  owner the switch to Opus at the boundary; staying on Fable clears the bar,
  but the bar itself is Opus, and you never adopt the role on a Sonnet or
  Haiku session.
- **Everything below the manager runs on Haiku, Sonnet, or at most Opus.**
  Workers default to **Sonnet**. **Haiku** carries a mechanical, narrow
  slice: a rename, a regeneration, a report reformat, a scouting pass that
  reads shape and quotes files. **Opus** is the exception, not a tier you
  drift into: it goes to a slice that is genuinely hard (subtle concurrency,
  a load-bearing algorithm) and the brief's MODEL TIER slot records why.
  Nothing below the manager ever runs the frontier tier the planner may hold.
- **Reviewers do not get Opus.** Skeptics and the steward run on **Sonnet**
  (their agent definitions say so in frontmatter), and a narrow mechanical
  lens on a small diff can drop to Haiku. Depth in review comes from the
  two-phase understand-then-attack briefing and from lens choice, not from
  the model tier: a deep-mode reviewer is deep because of how it is briefed.

**Decompose before you escalate — the ladder's standing order.** When a
slice looks too hard for Sonnet, the first move is a sharper knife, not a
heavier model: cut the slice smaller, tear the dependency, freeze an
interface, split the batch. Escalating the tier is warranted only when the
slice is already as small as its write set allows and the difficulty is
irreducible at any size — and the reason recorded in the MODEL TIER slot
must say exactly that: why a smaller slice would not have done. The same
order governs review: a deliverable that seems to need a heavier reviewer
needs a smaller batch or a narrower lens first, which is why review depth
is bought with briefing and batch size, never with Opus. An escalation
whose reason does not address decomposition is tier inflation with
paperwork, and the steward reads for it.

The fixed-cost note in the README ("Who this is for") is about panel
*count*; this ladder is about panel *tier*, and it holds even on a
fixed-cost account. Seven Sonnet skeptics beat two Opus ones here, because
breadth is what a panel buys, and a subagent that outranks its manager is
spend without a reader.

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
  <a scouting slice names its own report here as the single exception>

PRE-ASSIGNED NUMBERS (use exactly these; never pick your own):
  <the ADR / doc numbers the conflict checklist reserved for this slice, or
   "none this run">

MODEL TIER (the tier this slice dispatches on; the ladder is in this skill):
  <haiku | sonnet | opus — sonnet unless said otherwise; haiku for a
   mechanical slice; opus only with the reason written here, and the reason
   must say why a smaller slice would not do. Reviewers get sonnet or
   haiku, never opus.>

WHAT THE PREDECESSOR CHANGED (serialized slices only):
  <the slice that ran before you and what it changed in the files you are about
   to touch, or "nothing: no slice ran before you on these paths">

PARTIAL WORK ALREADY IN THE TREE:
  <paths a stopped or BLOCKED predecessor left half-written, and what to do
   with each one: keep it, finish it, or replace it. "None: your paths are
   clean" if nothing was left behind.>

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
yours; the pre-assigned numbers, because a number assigned in the conflict
checklist and never transmitted is a number the agent invents, which is the
collision the checklist was filled to prevent; the model-tier slot, because
an undeclared tier drifts upward silently and the ladder is an owner-set
rule, not a habit — and its opus reason must argue against decomposition,
because "hard" alone justifies a re-cut, not an escalation; the
predecessor slot, because a
serialized slice briefed as if it were first will re-do or undo what just
landed; the partial-work slot, because half-written work nobody was told about
is what makes a later panel produce noise; the exact test command, because "run
the tests" is not copy-pasteable; posture 3, because general-purpose briefs
default to "commit your work" and a self-committed slice lands before any panel
runs; posture 4, because one-level-deep spawning is this framework's
load-bearing invariant; and the status contract, because it is what closes a
task instead of leaving it open.

**Every dispatch uses this template**, not just the first round: fix-round
briefs, re-briefs after a BLOCKED report, and the scouting brief are all
written from it and all saved to `.delegation/briefs/<slice-id>.md` before
dispatch. The steward reads that directory as its evidence base, and a fix
round is exactly where an unexplained delta is most likely to appear.

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
   - (a) First ask whose decision it is. Inside your own grant — a brief you
     wrote left two acceptable designs open within one slice's allowlist —
     decide it, concretely, and re-brief with the decision already made.
     Never re-dispatch an open-ended "figure out whether this is solvable";
     that framing is what the stall rule below is about. But when the brief
     came from a plan's leaf card and the ambiguity traces to the plan (the
     card is silent, two cards conflict, or the acceptance condition reads
     two ways), the decision is the planner's, not yours: relay it (the
     planner relay, below) and re-brief with the ruling that comes back.
     Deciding plan content by manager fiat is how a plan and its execution
     quietly diverge.
   - (b) Either extend the allowlist, but only if it stays disjoint from every
     live slice, or cut the extra work into its own slice and serialize. Never
     authorize an agent to write outside its allowlist "just this once": the
     filled checklist stops being true the moment you do.
   - (c) Serialize the two slices, re-fill the checklist, and brief the second
     on what the first changed, in the template's WHAT THE PREDECESSOR CHANGED
     slot.
   - (d) Re-decompose. Stop any sibling slice that depends on the shape you
     just found to be wrong, rather than letting it finish against it.
4. **Always a fresh agent.** Re-brief means a new agent with a complete brief,
   not another message to the blocked one. The blocked agent's context is now
   full of the dead end.
5. **Decide what happens to the partial work** it left in the tree, explicitly:
   keep it or revert those paths. Either way the decision goes in the fresh
   brief's PARTIAL WORK ALREADY IN THE TREE slot, path by path, so the next
   agent is not surprised by work it did not write. Half-written work nobody
   owns is what makes a later panel produce noise.
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

### The planner relay: questions go back up the seam

When the task arrived as a delivered plan, the plan has an author, and
questions about its content go back to that author instead of dying in your
lap or being settled by fiat. The planning-framework holds the other end of
this seam (its returned-question gate, named in its `QUESTIONS.md` and in
its re-plan rules); this is the delegation end.

**What relays.** A question is the planner's when answering it would decide
plan content: a leaf card silent on something the slice needs, two cards in
conflict, an acceptance condition readable two ways, a premise the tree has
just falsified. A question is yours when it sits inside authority a card
clearly granted — two acceptable designs inside one slice's allowlist stay
your call, decided concretely, as ever.

**How it moves.** The relay is written, both ways. Save the question to
`.delegation/questions/<slice-id>.md`: what the worker hit, what you ran or
read to confirm the plan does not answer it, and the smallest ruling that
would unblock the slice. Then put it to the planner. In the common case the
planner and you are the same top-level session wearing two hats in
sequence, so the relay is a role switch: set the manager role down, take the
planner role back up, run the question through that framework's
returned-question gate (where it is answered from the plan's records, or
goes to the issuer), and come back with the ruling. When planning ran
somewhere else — another session, a person — send the same file's content
there and wait. Either way the ruling is appended to the same file and
lands in the fresh brief's slots, so a steward checkpoint can reconcile why
the slice changed shape.

**What does not relay.** A dispute (an owner matter, as ever); a decision
the card already made, re-asked in the hope of a different answer; and
chatter. Batch questions that arrive together, and if the same slice relays
twice, the card was mis-cut: that is a re-decompose on your side or a
re-plan on theirs, not a third question. While a question is out, other
slices keep moving. A relay pauses a slice, never the run.

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

The rules above say when you may not fan out. Do not read them as a lean
toward serial: **parallel is the default for slices the checklist clears.**
Once write sets are disjoint and the checklist is filled, dispatch the
independent slices together, in one message, and prepare the next briefs
while they run. Serializing disjoint slices spends the one thing no panel
refunds — wall-clock — and it is a named steward finding
(`serialized-the-disjoint`), audited the same way over-spawning is. The
incentive cuts both ways on purpose: the steward flags a fan-out the
checklist did not clear, and it flags a clean checklist left to run one
slice at a time.

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
- **Receiving a finding is not the same as accepting it.** You adjudicate,
  and the procedure has a name and a yardstick: the **fluff gate**
  ([`../consolidating-review/SKILL.md`](../consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate)).
  Every numbered BLOCKING item is adjudicated REAL (it gates; into the fix
  round) or FLUFF (demoted to non-blocking or discarded, with a written
  reason the original reviewer gets exactly one structured round to rebut),
  and the adjudication record is written before the fix round is
  dispatched. No silent demotions. Two lenses demanding opposite fixes get
  resolved by you *before* dispatch, or the fix agent will thrash.
- **The fix round is dispatched, not performed by you**, and the fix agent is
  bound by the same posture rules as any implementer. Its brief comes from the
  same template and is saved to `.delegation/briefs/` before dispatch, like any
  other. This holds for the last, smallest round as much as the first: a round
  of one-line nits is still a dispatched round, never a manager edit.
- **Re-review the dissenters** against the revision, briefed to attack it as
  fresh work rather than to tick off their old list. Every dissenter has to
  come back PLEASED before an artifact exists; there is no round that ends with
  someone still holding NOT PLEASED.

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
   `rounds`, a non-empty `lens` on every review, every verdict exactly
   `PLEASED`, every `blocking` list empty, `consolidated_blocking` empty, and
   `head_sha` equal to `git rev-parse HEAD` **right now**. Fill `head_sha`
   last, once the tree has stopped changing; a fix round after you write it
   leaves the artifact bound to the same HEAD but describing an older tree.
   Those are the gate's own checks, so an artifact that fails one of them is a
   deny, not a warning.
6. **Check `.delegation/` is in this repo's `.gitignore`** and that neither the
   marker nor the artifact is staged. Staging does not disarm anything (the
   deny will tell you to run `git restore --staged .delegation`), but
   *committing* the marker does: it would stand the gate down here and in every
   clone.
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
  adjudicate (the fluff gate) → fix round → re-review dissenters → manager
  inspects the integrated tree → *then* commit.
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
          → CONSOLIDATE BLOCKING (consolidating-review)
          → ADJUDICATE (the fluff gate: real findings gate; fluff is demoted
            on the record, one rebuttal round) → FIX ROUND
          → RE-REVIEW dissenters → until every reviewer is PLEASED
          → MANAGER INSPECTS → COMMIT (gate checks the artifact)
```

- Each named step has a procedure above or in the skill it names:
  [DECOMPOSE](#decompose-the-procedure), the
  [BLOCKED branch](#blocked-the-procedure) of the status contract,
  [ADJUDICATE](../consolidating-review/SKILL.md#2-adjudicate-the-fluff-gate)
  (the fluff gate: yardstick, rebuttal round, and the required
  adjudication record at `.delegation/adjudications/`), and
  [MANAGER INSPECTS](#manager-inspects-the-procedure).
- Review the whole integrated tree, never half-written slices, and land it in
  **one** commit: the artifact binds to one HEAD.
- Convergence stop-rule: each re-review must find strictly less. If only new
  one-line nits keep appearing, you may close without convening another *full*
  panel: one final dispatched fix round for the nits, a re-review by the
  dissenters only, and your own exhaustive check on top. The verdicts are not
  what the shortcut skips. Every reviewer still has to return PLEASED, because
  that is the only state in which an honest artifact exists and the only state
  the gate accepts.
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
  **opt-in marker**: the commit gate and reminder hooks act only in repos that
  carry it *and whose HEAD commit does not*, because plugin hooks are
  session-global and must not wall off unrelated repos. A marker the HEAD
  commit carries arrived with the repository rather than from anyone in this
  working copy, so it is not consent and the gate stands down with a warning.
- **In the same step, add `.delegation/` to that repo's `.gitignore`** if it is
  not already there. This is not tidiness, it is required, and the reason is
  the opposite of the one you might assume. Trackedness *is* the provenance
  signal: the gate reads the HEAD commit tree, so a committed marker does not
  arm your colleagues, it **disarms the gate for everyone who clones the
  repo**, and for you as soon as that commit lands. Two failure modes, both one
  `git add .` away. First, an unignored marker plus an ordinary `git add .`
  sweeps `.delegation/` into your own commit and turns off the gate you just
  armed. Second, an all-PLEASED artifact committed alongside it ships a waiver
  over the network to every clone. Gitignoring the marker is what keeps it
  meaning "somebody here chose this". Removing `.delegation/` later is how a
  repo is **un-armed**, and it is the escape hatch of last resort if the gate
  ever denies something it should not. If you inherited a marker and want it
  as your own opt-in: `git rm -r --cached .delegation`, gitignore it, **and
  commit that removal** (that commit is ungated, because until it lands the
  marker still counts as inherited).
- When the panel is all-PLEASED, ensure the review artifact exists at
  `.delegation/review-artifact.json` (written per the `skeptical-review`
  skill), including `head_sha` from `git rev-parse HEAD`. The PreToolUse commit
  gate denies the git subcommands that introduce newly authored work
  (`commit`, `cherry-pick`, `revert`, `am`, their `--continue`, and `--amend`)
  without it. `pull`, `merge` and `rebase` are *not* gated: they integrate
  commits that were already gated when they were authored. Neither are `reset`,
  `restore`, `push` or `add`, which author no commit, nor any command carrying
  `--abort`, `--skip`, `--quit` or `--dry-run` outside quotes. `--amend` **is**
  gated, because an amend writes a new commit whose content is whatever is
  staged, so `git add unreviewed.py && git commit --amend --no-edit` would
  launder unreviewed work through a spent artifact; expect to need a fresh
  artifact even for a message-only amend. Two residuals worth knowing: landing
  a branch with `merge --no-ff` is not gated, because the review happened at
  the commits inside the branch rather than at the merge; and
  `git reset --soft HEAD~1` re-arms a spent artifact by moving HEAD back, which
  is deliberate and returns exactly the one commit that artifact already
  authorised. After committing, archive the artifact to `.delegation/history/`
  so it cannot waive the next batch. The gate has five honest limits, and they
  are stated in full in the
  [README](../../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline):
  it needs hooks enabled and a Python 3.7+ interpreter answering to `python3`,
  `python` or `py -3`; the artifact is fabricable; it
  reaches the local tree only; it can be evaded or mis-resolved by parsing
  (an unresolvable path falls back to the hook's own repo and the deny says so);
  and it can rarely over-reach.

## References (skill-referenced data, read on demand)

- [`../../docs/operating-model.md`](../../docs/operating-model.md): the full playbook
- [`../../docs/roles.md`](../../docs/roles.md): manager / implementer / skeptic
- [`../../docs/example-run.md`](../../docs/example-run.md): one worked run, end to end
