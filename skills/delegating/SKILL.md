---
name: delegating
description: Use when running a substantial multi-part build as a manager delegating to implementation agents with skeptic review - routes loop/parallelism/review mechanics to superpowers skills by name and owns only the residual (skeptic pairing, panels, reliability rules, conflict checklist, commit gate)
---

# Delegating

You are the **manager**. This skill is deliberately **thin**: every mechanic
that `superpowers` already ships is invoked from `superpowers` **by name**,
never re-described here. This skill owns only the residual. If you find
yourself re-implementing something in the seam table below, stop — that is a
scope defect.

**First: the trivial-edit gate.** Do NOT delegate a trivial edit or a
single-file fix — the overhead isn't worth it; just do it. Use this loop for
substantial, multi-part builds where independent review adds real safety.

## The seam table — route these mechanics to superpowers

| Mechanic | Use this superpowers skill (by name) |
|----------|--------------------------------------|
| The implement → review → fix loop, fresh subagent per task | `superpowers:subagent-driven-development` |
| Disjoint-parallel / shared-sequential fan-out | `superpowers:dispatching-parallel-agents` |
| Requesting / receiving code review | `superpowers:requesting-code-review`, `superpowers:receiving-code-review` |
| Test-first implementation | `superpowers:test-driven-development` |
| Evidence-before-claims gating | `superpowers:verification-before-completion` |
| Turning an idea into a spec | `superpowers:brainstorming`, `superpowers:writing-plans` |
| Plan execution in a separate session; branch completion | `superpowers:executing-plans`, `superpowers:finishing-a-development-branch` |

This composition is a **soft, by-name dependency** validated against
`superpowers` 6.1.x. If those skills are not discoverable, warn the user and
stop — the loop mechanics live there (the SessionStart hook also checks
this, best-effort).

## The sibling seam table — route these deliverable kinds to a sibling framework

Several **companion frameworks** own one kind of deliverable each: security
review of a repo where agents act; documenting a codebase and measuring doc
drift; producing and quality-gating non-code deliverables (.docx / .pptx).

**None of them is public, and none is installable.** They are named here only so
you understand why this framework has no security lenses and no documenter role —
those were deliberate hand-offs, not omissions. When you hold one of those
deliverables, you are on your own machinery; there is no specialist to route to.

- **Nothing auto-discovers a companion.** There is no registry, no registration
  step, no manifest field, and no code path in this repo that reads a companion's
  files. If one were present, a manager would read a table and name a skill in a
  dispatch — that is the whole mechanism.
- **Nothing is pinned**, because there is nothing public to pin to. Treat any
  companion name in this tree as design rationale, not as a routing instruction.
- **The SessionStart hook does not probe for them**
  ([`../../scripts/session-start-check.py`](../../scripts/session-start-check.py)).
  Probing for something a consumer cannot install would open every session with a
  warning about a plugin that does not exist for them. Only `superpowers` — which
  is real, public, and required — is probed, and that probe **warns, never
  blocks**.

Background on where the boundaries were drawn:
[`../../docs/family.md`](../../docs/family.md).

## The residual — what THIS skill owns

### 1. The law

> Every deliverable carries at least one adversarial skeptic before it is
> trusted — **research, design, implementation — all of them. The floor is
> one. No exceptions.**

`superpowers` reviews code; this law covers *every* deliverable kind. Attach
skeptics via the `skeptical-review` skill; the reviewer definition is
`agents/skeptic.md` (spawn as `subagent_type: "skeptic"`).

### 2. Panel sizing

**2–3 skeptics for a small change, 5–7 for a feature batch.** Scale to risk,
not habit. Lens choice: [`../../docs/lenses.md`](../../docs/lenses.md).
Verdict format: [`../../docs/rubric.md`](../../docs/rubric.md).

### 3. TWO deliberate posture overrides of `superpowers:subagent-driven-development`

Both are load-bearing; wire both or you get an unguided contradiction:

- **Override 1 — no auto-commit on DONE.** The "don't stop between tasks"
  default still governs *within* a slice: an implementation agent runs to
  DONE without check-ins. But the manager does **not** auto-commit on a DONE
  report. Between "slice DONE" and "commit" sits the panel gate: attach ≥1
  skeptic → consolidate BLOCKING → fix round → re-review dissenters →
  manager inspects the integrated tree → *then* commit.
- **Override 2 — the implementer does not self-commit (the commit gate
  depends on this).** The stock `superpowers` implementer template says
  "Commit your work." Here the implementation agent does **NOT** commit or
  push — it leaves work in the tree and **only the manager commits**, after
  the panel. **You must re-brief every implementation agent explicitly:**
  *"You do not commit or push. Leave your work in the tree; the manager
  commits after review."* Without this re-brief, the slice self-commits
  mid-work and the PreToolUse commit gate gates nothing.

### 4. The forced conflict-avoidance checklist (before ANY fan-out)

Before dispatching agents in parallel, **copy and fill**
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
under-delegating the substantive builds). Pair a **standing steward**
([`../../agents/steward.md`](../../agents/steward.md), spawn as
`subagent_type: "steward"`) and consult it repeatedly — at checkpoints and
before big fan-outs — sized to the run: skip it for a short, low-stakes loop;
consult it often on a long or high-stakes one where drift would go unnoticed.
It returns a MANAGER SCORECARD (VISION + DELEGATION) with cited evidence. It is
**disciplined accountability, not a gate** — no hook enforces its verdict, you
can ignore it, and your judgment stays yours; it only raises the cost of
self-deception. Role detail: [`../../docs/roles.md`](../../docs/roles.md#steward).

### 6. Reliability / stall rules

- **Silence ≠ progress.** Watch file-write activity (mtimes / `git status`),
  not completion notifications. An agent with *no* output after several
  minutes is stalled: stop it (`TaskStop`) and **re-brief with a concrete
  design decided for it** — never an open-ended "figure out whether this is
  solvable" (that framing once caused a 26-minute no-output stall; the
  concrete re-brief finished in ~2 minutes).
- **Commit disjoint slices as they land**, staging explicit paths. **Never
  `git add -A` while another agent writes.**
- Full detail: [`../../docs/operating-model.md`](../../docs/operating-model.md).

### 7. The loop and the commit gate

```
DECOMPOSE → IMPLEMENT (superpowers, parallel where safe)
          → REVIEW PANEL (skeptical-review: 2–7 skeptics, swarm/deep/hybrid)
          → CONSOLIDATE BLOCKING (consolidating-review) → FIX ROUND
          → RE-REVIEW dissenters → until every reviewer is PLEASED
          → MANAGER INSPECTS → COMMIT (gate checks the artifact)
```

- Review the **whole integrated tree**, never half-written slices.
- Convergence stop-rule: each re-review must find **strictly less**; if only
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
  review structurally cannot reach — and the tests keep them fixed.
- **Arm the gate at loop start:** create a `.delegation/` directory at the
  repo root when you begin the loop (it also holds the filled conflict
  checklist and, later, the review artifact). This directory is the
  **opt-in marker** — the commit gate and reminder hooks act only in repos
  that carry it, because plugin hooks are session-global and must not wall
  off unrelated repos.
- When the panel is all-PLEASED, ensure the review artifact exists at
  `.delegation/review-artifact.json` (written per the `skeptical-review`
  skill) — the PreToolUse commit gate denies `git commit` without it. After
  committing, **archive the artifact** to `.delegation/history/` so it
  cannot waive the next slice. The gate has five honest limits (hooks +
  Python-on-PATH enabled only; artifact fabricable; local tree only;
  matcher/parse evasion and wrong-repo mis-resolution possible; over-reach:
  session-global hook scoped by the `.delegation/` marker, rare false
  positives on exotic compound commands — escape: write the artifact,
  remove `.delegation/`, or disable the hook) — see the
  [README](../../README.md).

## References (skill-referenced data, read on demand)

- [`../../docs/operating-model.md`](../../docs/operating-model.md) — the full playbook
- [`../../docs/roles.md`](../../docs/roles.md) — manager / implementer / skeptic
- [`../../docs/example-run.md`](../../docs/example-run.md) — one worked run, end to end
