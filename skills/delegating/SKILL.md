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

### One scoped task per fresh subagent

Decompose the work into scoped tasks and spawn **one implementation agent per
task**. Give each agent a brief that names four things:

1. **The one task**, stated as an outcome, not as a direction to explore.
2. **An explicit file-ownership allowlist**: the files and directories this
   agent may create or modify, and nothing else.
3. **The exact test command** for its slice, copy-pasteable.
4. **The acceptance condition**: what has to be true for the task to be done.

The agent then opens whatever files it needs, does the work, runs its own
tests, and reports back with a status of **DONE**, **BLOCKED**, or
**NEEDS_CONTEXT**, plus the evidence behind it (what it ran and what came
back). Then it is finished. The next task gets a **new** agent, briefed from
scratch, not the same agent carrying the last task's residue. A BLOCKED report
comes back to you for a decision; a NEEDS_CONTEXT report comes back for a
fuller brief, and you answer it by extending the brief rather than by taking
the task over.

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

### 6. Reliability / stall rules

- **Silence ≠ progress.** Watch file-write activity (mtimes / `git status`),
  not completion notifications. An agent with *no* output after several
  minutes is stalled: stop it (`TaskStop`) and **re-brief with a concrete
  design decided for it**, never an open-ended "figure out whether this is
  solvable" (that framing once caused a 26-minute no-output stall; the
  concrete re-brief finished in ~2 minutes).
- Commit disjoint slices as they land, staging explicit paths. **Never
  `git add -A` while another agent writes.**
- Full detail: [`../../docs/operating-model.md`](../../docs/operating-model.md).

### 7. The loop and the commit gate

```
DECOMPOSE → IMPLEMENT (fresh subagent per task, parallel where safe)
          → REVIEW PANEL (skeptical-review: 2–7 skeptics, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING (consolidating-review) → FIX ROUND
          → RE-REVIEW dissenters → until every reviewer is PLEASED
          → MANAGER INSPECTS → COMMIT (gate checks the artifact)
```

- Review the whole integrated tree, never half-written slices.
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
  is on. Both are one `git add .` away by default.
- When the panel is all-PLEASED, ensure the review artifact exists at
  `.delegation/review-artifact.json` (written per the `skeptical-review`
  skill). The PreToolUse commit gate denies `git commit` without it. After
  committing, archive the artifact to `.delegation/history/` so it
  cannot waive the next slice. The gate has five honest limits, and they are
  stated in full in the
  [README](../../README.md#enforcement-honestly-one-structural-slice-the-rest-is-discipline):
  it needs hooks enabled and Python on PATH, the artifact is fabricable, it
  reaches the local tree only, it can be evaded or mis-resolved by parsing,
  and it can rarely over-reach.

## References (skill-referenced data, read on demand)

- [`../../docs/operating-model.md`](../../docs/operating-model.md): the full playbook
- [`../../docs/roles.md`](../../docs/roles.md): manager / implementer / skeptic
- [`../../docs/example-run.md`](../../docs/example-run.md): one worked run, end to end
