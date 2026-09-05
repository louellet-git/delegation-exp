# Comparison log — everything-claude-code (ECC) against the planning and delegation frameworks

**Logged:** 2026-09-05, by the frameworks' maintainer session, at the owner's request.
**Source:** `affaan-m/everything-claude-code` (now redirecting to `affaan-m/ECC`),
HEAD `e04ea0b` dated 2026-09-03, `VERSION` 2.2.1, MIT. Cloned at depth 1 and read on
disk; star count (roughly 250k) read once from the GitHub page and not otherwise relied on.
**Scope:** how ECC handles planning, delegation, review, and enforcement, set against
`planning-exp` (PETE / FATHOM / CASS, plugin v0.3.0) and `delegation-exp`
(manager / implementer / skeptic / steward, plugin v0.3.0).
**Method:** three dedicated agents produced one dissection of ECC and one distillation of
each framework; the maintainer session spot-checked the ECC counts and every quoted line
below against the clone. Nothing in the two frameworks was modified.
**Status:** COMPARISON ONLY. Candidate borrowings are listed at the end as candidates.
None is adopted, adjudicated, or turned into a change by this file. The same file is
logged in both repositories' `feedback/` directories because it covers both.

---

## The short version

ECC and the two frameworks are not the same kind of object, and the comparison is
mostly a comparison of kinds.

**ECC is a catalogue.** Sixty-eight agents, ninety-four commands, two hundred
eighty-six skills, one hundred twenty-two rule files in twenty-two packs, some fifty
hook scripts, adapters for eleven other harnesses, a paid tier. Its own README says
"Start with the workflow you need, not the full catalog" (`README.md`), and its policy
file says `skills/` is canonical while `commands/` is "a legacy slash-entry
compatibility surface" (`AGENTS.md`). It is opinionated about code style (immutability,
functions under fifty lines, eighty percent coverage) and permissive about process: at
least seven surfaces plan, three plan-artifact directories coexist, and nothing decides
which one you are in.

**The two frameworks are a single prescribed process each,** with one gate apiece,
built around one named failure and carrying a written ledger of what is and is not
backed by evidence. They are narrower than ECC on every axis but one, and that axis is
the point: they specify who may do what, in what order, with what cap, and what happens
when the cap runs out.

The one-line verdict: **ECC is much wider and has real machinery the frameworks
lack (a working native Workflow with an adversarial verifier, a mechanical
plan-mode gate, a fact-gathering pre-edit hook, cost tracking, learned instincts).
The frameworks are much deeper on the two things ECC leaves to the human: checking
the plan before it executes, and adjudicating what reviewers say.** Neither is a
replacement for the other. A handful of ECC mechanisms are worth studying as candidates;
the bulk of it is a different bet made for a different user.

---

## Side by side

| Dimension | ECC | planning-exp | delegation-exp |
|---|---|---|---|
| Shape | Catalogue plugin + npm + eleven harness adapters | One agent, one command, nine prose files | One manager role, two spawnable agents, three commands, three skills |
| Size | 68 agents / 94 commands / 286 skills / 122 rules / ~50 hooks | ~9,800 lines total, ~233 KB doctrine | ~4,900 lines prose, ~2,400 lines Python, 2,424 lines of gate tests |
| Planning surfaces | `/plan`, `/plan-prd`, `/prp-plan`, `/feature-dev`, `/multi-plan`, `orch-pipeline`, `planner` agent, `gan-planner`, `plan-canvas` | One flow, always full ceremony (ruling D17) | Consumes a plan; does not produce one |
| Elicitation | Strong in `plan-prd` (four gated phases) and `prp-plan` ("STOP and ask the user"); one bullet in `planner` | Six batches of 5–7 with mandatory follow-ups; "Prefer answers in numbers over answers in prose" | n/a |
| Plan verification | None. A plan waits for a typed "yes"; "Plan judge-panel" is listed as a future port (`workflows/README.md`) | FATHOM ×2 (depth), CASS ×2 (form), issuer gate ×2, all capped | n/a |
| Verdict on the ask | Confidence score 1–10 in `prp-plan`; nothing in `/plan` | `PROCEED / DESCOPE / DEFER / DON'T BUILD`, written before the how | n/a |
| Non-goals / unknowns | "NOT Building" and "Open questions" only in `plan-prd` / `prp-plan`; absent from `/plan` and `planner` | Mandatory `## Non-goals`, `## Deferred` with noticeable return condition, `AMBIGUOUS` frontier node | Brief carries out-of-scope from the card, "never invented" |
| Re-planning | Post-hoc "Assessment vs Reality" table in `prp-implement`; no trigger | Re-plan re-enters at decomposition, one branch; three cycles on one branch → spike; four → leaves the plan | Question relay to the planner; route (e) opens a re-plan |
| Orchestration topology | Any agent may spawn; completion contract added after "zombie tasks" were observed | Planner spawns exactly one manager session, then idles | "A flat org with one spawner": manager only, one level deep |
| Review | `code-reviewer` (>80% confidence, zero findings acceptable); `orch-review` Workflow with dedup + adversarial verifier; santa-method two reviewers both-must-pass; council of four | CASS: fresh context, six inputs or refuses, may not propose work | Panel of 2–3 or 5–7 skeptics, named lenses, swarm/deep/hybrid, `PLEASED` / `NOT PLEASED` only |
| Adjudication of findings | Verifier in `orch-review` only; elsewhere "dedupe, rank by severity" and the human decides | PETE must dispose every finding in writing; "You may not make it disappear" | Fluff gate (REAL / FLUFF), one rebuttal round, adjudication record required every round |
| Loop bounds | Santa 3 rounds then human; gan-build 15 iterations / plateau; `orch-pipeline` review→fix unbounded | FATHOM 3 passes, CASS 2 passes, `review_rounds_on_one_artifact` ≥3 re-scope, ≥5 ship or delete | "Each re-review must find strictly less"; standoff after rebuttal → owner |
| Commit gate | Prose in `security.md`; mechanical only in `strict` profile (`commit-quality`); `--no-verify` blocked in all profiles | None (no gate scripts by design) | Structural: `.delegation/` marker + all-PLEASED artifact, pure-Python git object reader, provenance from HEAD |
| Other hooks | Config-protection deny, GateGuard deny/force/allow, format+typecheck on Stop, cost tracker, memory persistence, plan-canvas pending | One SessionStart injection | SessionStart injection, SubagentStop and Stop nudges |
| Model tiers | Frontmatter: 58 sonnet / 4 opus / 6 haiku; README recommends forcing all subagents to haiku | Planner Fable 5 or Opus; manager Opus pinned at spawn; below that, judgment | Same ladder; "scale by decomposition, not by tier" |
| Cost stance | Per-token: haiku for workers, thinking capped, cost log | Fixed-cost: ceremony always runs | Fixed-cost: "a seven-skeptic panel and a two-skeptic panel cost the same" |
| Evidence for practices | Anecdotal ("battle-tested"); GateGuard's "+2.25" from two tasks | `EVIDENCE.md` grades Strong / Contested / Folklore / Wrong / Gaps; caps admitted ungraded | Defers to the planning ledger; gate has 192 tests |
| Tests | Hook scripts have tests in repo | None | 192 gate tests including forged-object cases |

---

## Planning, in detail

**Where ECC is stronger.** Two things.

1. *Pattern grounding.* `/plan` requires a codebase search for naming, error,
   logging, data-access, and test conventions before writing tasks, with `path:line`
   citations, and says "If no similar code exists, state that explicitly. Do not
   invent a pattern" (`commands/plan.md`). PETE's Phase 2 orients on the codebase, but
   the plan format has no mandatory "mirror this file" slot per leaf. That is a cheap,
   countable field.
2. *Right-sizing with an override.* `orch-pipeline` Step 0 classifies trivial / small
   / standard / large on files touched, new contracts, and design ambiguity, and
   "state[s] the result in one line so the user can override" (`skills/orch-pipeline/SKILL.md`).
   The planning framework runs full ceremony on everything by owner ruling D17; the
   delegation framework has a triviality check at `/delegate` only. ECC's tiers are a
   more graduated answer to the same question, and the tie-breaker ("anything touching
   a security trigger ... is at least standard") is the kind of rule CASS could check.

**Where the frameworks are stronger.** Almost everything after the questions.

- ECC has *no plan checker.* `/plan` emits a plan and waits for "yes" or "proceed".
  `planner` is read-only Opus and produces steps with Low/Medium/High risk labels and
  hour estimates; nobody reads it back. The framework's founding failure ("14 review
  rounds, 16 reviewers, and roughly 7,400 lines of instrument ... and never took the
  measurement", `README.md`) is exactly the failure a "yes" gate does not catch, and
  FATHOM's single discriminator (entailed versus new) has no ECC counterpart.
- ECC has *no verdict before the how.* The closest is `prp-plan`'s "Confidence Score:
  1–10, likelihood of single-pass implementation", which scores the plan, not the ask.
  `DESCOPE` and `DON'T BUILD` as live outputs of planning do not exist in ECC.
- ECC's *non-goals and unknowns are optional and scattered.* They live in the PRD
  command and the PRP command, not in the canonical `/plan` artifact, so a plan
  reaching execution can lack both. The frameworks make `## Non-goals`, `## Deferred`
  with a noticeable return condition, and the `AMBIGUOUS` node mandatory, and CASS
  greps for the marker.
- ECC has *no counters and no stop states.* Nothing in ECC corresponds to
  `outputs_of_intended_kind == 0 → HARD STOP`, an evaluator who is not the builder, or
  a readings ledger. Its loop bounds are iteration counts on review loops, not
  measurements of the project.
- ECC's *elicitation is uneven.* `plan-prd` is genuinely good ("Anti-fluff rule:
  When information is missing, write `TBD — needs validation via {method}`. Never
  invent plausible-sounding requirements", `commands/plan-prd.md`) and `prp-plan` has
  an "Ambiguity Gate" that says "Do NOT guess. Ask." But `planner` says only "Ask
  clarifying questions if needed", and `orch-pipeline` Intake just restates the
  request. Which one runs depends on which command the user typed.

**A mechanism the framework lacks and ECC has.** `plan-canvas` blocks the Stop event
while a plan verdict is pending (`stop:plan-canvas-pending`), so the session cannot
end with the issuer gate unanswered. The planning framework's issuer gate is a STOP by
prose and a SessionStart reminder; nothing mechanical holds the turn open.

---

## Delegation and review, in detail

**Where ECC is stronger.**

1. *A working native Workflow.* `workflows/orch-review.workflow.js` fans reviewers
   out per dimension, dedups "keyed on the normalized `evidence` snippet", and hands
   "every unique `CRITICAL`/`HIGH` finding to an independent adversarial verifier".
   The verifier prompt reads: "Uncertainty must never clear a blocker ... set
   isReal=true with a low `confidence`", and the schema forces a `proof` field on
   HIGH/CRITICAL. The command wrapper carries a "Fail-Closed Contract: This command
   must never present a clean APPROVE when the review could not fully run"
   (`commands/orch-review.md`). This is the delegation framework's panel, consolidation,
   and fluff gate, in code, with `incomplete` and `failedDimensions` as first-class
   outputs. The delegation framework runs the same shape through prose and a manager.
2. *Reviewer calibration.* `agents/code-reviewer.md`: "Only report issues you are
   confident about (>80% sure)", a four-question "Pre-Report Gate" (exact line,
   concrete failure mode, surrounding context, defensible severity), and "It Is
   Acceptable And Expected To Return Zero Findings ... Do not withhold approval to
   appear rigorous", plus a long false-positive list. The skeptic role sheet
   (`agents/skeptic.md`) has the rubric block and the lens but no equivalent
   pre-report checklist; the fluff gate catches the same thing one step later, at the
   manager, at the cost of a round.
3. *Anti-anchoring by construction.* `skills/council/SKILL.md` launches the four
   voices "as fresh subagents with only the question and relevant context ... That is
   the anti-anchoring mechanism" and requires synthesis to "always include the
   strongest dissent". Santa-method re-spawns "fresh agents" every round. The
   delegation framework's re-review of dissenters is fresh by discipline, not stated as
   a rule.
4. *A completion contract.* `rules/common/agents.md`: "Your final message IS the
   deliverable. Never end your turn with 'waiting for background agents' ... If you
   delegate, you own collection." ECC added this after observing "zombie tasks". The
   delegation framework's DONE/BLOCKED/NEEDS_CONTEXT status contract covers the
   implementer side; the manager side relies on the steward noticing.
5. *Operational hooks.* Format-and-typecheck on Stop, config-protection deny ("Steers
   agent to fix code instead of weakening configs"), `--no-verify` blocked in every
   profile, a cost log per session. None of these exist in either framework, and none
   conflicts with them.

**Where the frameworks are stronger.**

- *Who may spawn.* ECC lets anything spawn and then adds a contract to clean up the
  consequences. The delegation framework withholds spawning from every seat but the
  manager and says so is "upheld by what this repo withholds, not by what it grants"
  (`README.md`). The two are different bets; ECC's own agents.md documents the failure
  mode the framework designed out.
- *The verdict vocabulary.* ECC has Approve / Warning / Block, APPROVE /
  CHANGES_REQUESTED, PASS / FAIL, scores out of ten, and prose. The delegation
  framework has `PLEASED` / `NOT PLEASED` and `BLOCKING`, and nothing else. "No
  'PLEASED with reservations'" (`docs/rubric.md`) is a stronger rule than any single
  ECC surface carries.
- *Adjudication with a record.* Outside `orch-review`, ECC's reviewers are final:
  `review-pr` says "dedupe overlapping findings, rank by severity", and the human at
  GATE 2 resolves whatever is left. The fluff gate names REAL and FLUFF heads, gives
  the reviewer one `CONCEDE | STAND` round with new evidence, and requires
  `.delegation/adjudications/round-N.md` "even when it is the one line 'all findings
  adjudicated REAL; nothing demoted'" (`skills/consolidating-review/SKILL.md`).
- *Convergence as a rule, not a counter.* ECC bounds loops by iteration (three, fifteen,
  plateau). The delegation framework bounds them by monotonicity: "each re-review must
  find strictly less", "Relocated is not resolved ... renamed is not resolved", and a
  standoff goes to the owner. Both are bounds; the framework's is harder to game.
- *A reviewer of the manager.* Nothing in ECC reviews the orchestrator. The steward's
  "unexplained delta" detector (changes outside the union of allowlists and the
  reserved set) is a mechanical check that ECC's `loop-operator` and
  `harness-optimizer` do not approximate.
- *The structural commit gate.* ECC's commit gate is prose, mechanically enforced only
  under `ECC_HOOK_PROFILE=strict`, and then as a lint on the commit message and a
  secrets scan. The delegation gate ties every commit-authoring git command to a
  current all-PLEASED artifact whose `head_sha` matches, reads HEAD's tree with its own
  object reader to decide provenance, and fails closed on artifact problems with 192
  tests behind it. It is a different order of enforcement. Its weakness, admitted in
  its README, is that it "silently vanishes without Python" and needs a manual
  self-test; ECC's Node hooks have the same failure shape.

---

## Enforcement, in one paragraph

ECC says "Hooks can enforce deterministic checks outside the prompt" (`README.md`) and
means it more than either framework does for *operational* checks: config files,
formatting, type errors, `--no-verify`, MCP health, and a fact-gathering gate before
the first edit ("LLM self-evaluation doesn't work. Ask 'did you violate any policies?'
and the answer is always 'no'", `skills/gateguard/SKILL.md`). But its *process*
discipline (the TDD RED gate, the plan gate, coverage, reviewer proof) is prose, same
as the frameworks'. The frameworks enforce one process thing each structurally (a
SessionStart injection; a commit gate), and everything else by an LLM reading prose.
On process, all three are in the same position and only the delegation gate stands
out. On operations, ECC is ahead and the frameworks have nothing.

---

## Philosophy and evidence

ECC's stated problem is repetition: "Instead of rebuilding that process in every
prompt, you install it once" (`README.md`). The frameworks' stated problem is a
specific failure that repetition would not have prevented. That difference explains
most of the rest. ECC optimises for coverage of situations; the frameworks optimise
for termination and for the referee not being the player.

On evidence, ECC cites Anthropic posts and a two-task A/B; no rule carries a source.
The planning framework grades its methods into Strong / Contested / Folklore / Wrong
and leaves its own load-bearing citation in open dispute (`SOURCES.md`), while
admitting the caps and all 2026-09 machinery are ungraded. Neither is *proven*, but
only one of them says so.

On cost, they are opposite by design. ECC assumes per-token billing (haiku workers,
`MAX_THINKING_TOKENS: 10000`, a cost log). The frameworks assume fixed-cost accounts
and say per-token users "will cost you real money" (`delegation-exp/README.md`).
Borrowing ECC's cost machinery would be borrowing a premise, not a tool.

---

## Candidate borrowings, ranked by cost to adopt

Listed as candidates only. Each would need its own slot and its own reader under the
planning framework's maintenance rule, or it is not a mandate.

1. **Reviewer pre-report gate.** Four questions in `agents/code-reviewer.md` added to
   `agents/skeptic.md` before the rubric block. Zero machinery; would cut FLUFF before
   the fluff gate sees it. Risk: "It is acceptable to return zero findings" pulls
   against the fixed-cost bet that panels exist to find things; the skeptic's version
   would need to keep NOT PLEASED cheap.
2. **Pattern-to-mirror slot on the leaf card.** A `Mirror:` row with `path:line`, or
   the explicit "no similar code exists" statement, in `PLAN-FORMAT.md`. CASS can
   check presence. Cheap, countable, and it targets the one thing ECC's `/plan` does
   that PETE's Phase 2 does not force onto the page.
3. **Stop-hook hold on an open issuer gate.** ECC's `stop:plan-canvas-pending` shows a
   Stop hook can refuse to end the turn while a verdict is pending. The planning
   framework's issuer gate is the one step no agent may perform; a hook that keeps the
   turn open until the note is written is a second structural slice, and a small one.
4. **Fresh-context rule stated, not assumed.** Council's "fresh subagents with only
   the question and relevant context" as an explicit line in the re-review of
   dissenters. Zero machinery.
5. **Operational hooks that do not touch process.** `block-no-verify`,
   `config-protection`, format-and-typecheck on Stop. Node scripts, each self-contained,
   installable beside the delegation gate without changing it. Cost: more milliseconds
   on every Bash call, on top of the gate's forty-four.
6. **Porting the panel to a native Workflow.** `orch-review.workflow.js` is the proof
   that the delegation loop's shape (fan-out, dedup, verifier, fail-closed verdict)
   runs as code. It would make the panel's `incomplete` state mechanical and the
   artifact machine-written. This is the expensive one, and it changes what the manager
   is; the framework's own "capability claims, not behavioural guarantees" posture
   would need re-stating.

## What not to borrow

- **The catalogue.** Seven planning surfaces that disagree on artifact directory and
  on whether the planner agent runs. The frameworks' single flow with byte-identical
  diagrams in six files is the opposite choice, deliberately.
- **Iteration counts as convergence.** "Three rounds then escalate" is weaker than
  "strictly less each round" and the planning framework's counters.
- **Haiku-by-default subagents and thinking caps.** A per-token premise.
- **Learned instincts and memory persistence.** Interesting, but ECC's own line
  "Memory is unreviewed context, not executable policy" (`skills/unified-memory`)
  puts it outside what either framework would let a seat act on, and the planning
  framework's D22 rule ("a seat that trusts an instruction because it arrived in a
  poke is a seat a forged poke can move") would apply to an instinct file as well.

## Caveats

- ECC is read at one commit, depth one. Its pull-request history and the paid tier were
  not examined.
- The frameworks' own gaps are not softened by this comparison: the planning repo has
  no tests and no mechanical check; the delegation gate is silent when Python is
  missing; both carry undefined cross-references (D-, F-, I-, S-numbers) and shipped
  records that were meant to stay out of the plugin tree. Those are recorded in the
  2026-08-09 maintainer findings and remain open.
- The agents that produced the three inputs read prose and reported quotes; the
  maintainer session verified the ECC counts, the `/plan` inline rule, the verifier's
  uncertainty rule, the santa cap, the hook profile table, and the "Plan judge-panel"
  line against the clone. Other quotes are as the agents reported them.
