# Companion frameworks — design rationale, not a routing table

**None of the frameworks named in this document is public.** `delegation-framework`
does not depend on any of them, does not load or resolve them, and works
completely without them. They are described here for one reason: several
boundaries in this repo — no security lenses, no documenter role, no built-in
generative faculty — are deliberate hand-offs rather than gaps, and that is only
legible if you know what they were handed off *to*.

Read this as an account of why the seams are where they are. Do not read it as
something to go install. There is no link, no version to pin, and no registry;
if a companion becomes public it will be linked from the README.

The companions own one kind of deliverable each: security review of repos where
agents act; documenting a codebase and measuring doc drift; producing and
quality-gating non-code deliverables; and a gated generative faculty
(`dreaming-framework`) that is OFF by default and runs only under a per-session
owner authorization.

## Family-wide governance — the do-not-modify guard

One rule binds **every framework in the family**, not just this one:

> **Agents pointed at a framework MUST NOT modify it — ever — unless the owner
> explicitly asks.** Read it, apply it, operate by it; do not edit it. Framework
> changes require **explicit owner authorization.**

An agent's job is to *operate by* a framework, not to rewrite the rules it runs
on — and that holds whether the agent is pointed at `delegation`,
`cyber-security`, `doc-review`, `code-doc`, `dreaming`, or a future member. The guard is
stated in full at the top of this repo's
[README](../README.md#-do-not-modify-this-framework--read-it-apply-it-operate-by-it);
it applies identically across the family. This is a **governance discipline**,
consistent with the rest of the family's posture: it is a binding rule and an
owner-visible one, not a hook-enforced structural wall. If an agent believes a
change is warranted, it surfaces the change to the owner and stops; only the
owner authorizes it.

## Family-wide capability pattern — the gated generative faculty

One capability is written to be a **reusable pattern across the family**, not a
one-off of this repo: the **generative DREAMER faculty**, held in the
`dreaming-framework` behind a
per-session owner-authorization gate. Any companion that needs to imagine a
better end-state reaches for it in the same shape rather than re-inventing one.

**How this repo uses it.** `delegation-framework` itself has **no built-in vision
tier** — the earlier Director role was removed; the manager is the single
top-level orchestrator and the steward (VZ) keeps it on track. When the owner
authorizes a dream session, the **manager**, consulting the **steward** on
direction, invokes the dreaming-framework's dreamer under its gate; between
authorized sessions dreaming is dormant.

**The gated generative faculty — the dreaming-framework:**

- **DREAMER (generative), OFF by default.** Inside an **owner-authorized, expiring,
  single-use session**, run a *bounded, ephemeral* sweep: imagine what the work
  *could* look like — better local maxima, opportunities, adjacent shapes —
  diverging then converging. **Not** a persistent, always-on mind, and **not** a
  standing cadence: the persistent form was unanimously rejected on sustainability
  grounds, so reach is available only when the owner deliberately turns it on for one
  session. Graded on its own **Vision / Opportunity Ledger** (imagined end-state +
  concrete how-we'd-evaluate criterion; discard if un-evaluable; scored REACH-MISS),
  with the kill-switch being the owner declining to authorize further sessions.

**Why it generalizes.** Every family member runs work toward an end-state and can
fail to imagine a better one; a `cyber-security` program, a `doc-review`
engagement, or a `code-doc` effort each has a direction worth dreaming forward when
the owner enables it. The pattern is **domain-neutral by construction** — it names
a faculty, a ledger, and a gate, never a domain — so a sibling adopts it by
pointing its own top-level orchestrator at the gated dreamer and at its own
initiatives. What must **not** be dropped when adopting it: the ephemerality
(bounded, one session, then dormant), the ledger with a load-bearing evaluable
field, the grade-on-ledger kill-switch, and the **off-by-default per-session
gate**. Those are what keep "dreaming forward" from degrading into fluent,
un-scored, always-on fantasy.

## 1. Who owns what

| Framework | Owns | Its central artifact | Status |
|---|---|---|---|
| **`delegation-framework`** (this repo) | The manager → implementer → skeptic loop: skeptic pairing, panel sizing, the lens catalogue and PLEASED / NOT PLEASED rubric, reliability rules, conflict avoidance, the commit gate; **the manager (sole spawner) + the steward (VZ) that keeps it on VISION + DELEGATION** | `.delegation/review-artifact.json` + a PreToolUse gate on `git commit` | This repo — plugin, self-listing marketplace |
| **`cyber-security-framework`** | Security of repos **where agents act**: a declared threat model, eight containment primitives, four security lenses, an agent-runtime containment gate | `.security/threat-model.json` + `scripts/validate-threat-model.mjs` | Not public |
| **`code-doc-framework`** | The method a documenter agent wields on a **codebase**: docs-near-code, MVD, README-as-truth, an ADR log, front-door routing, the Intended-vs-Actual drift map | a drift-map JSON + `scripts/validate-drift-map.mjs` | Not public |
| **`doc-review-framework`** | Producing and quality-gating **non-code client deliverables** (.docx memos, .pptx decks): reviewer agents, canonical rubrics, a defensibility audit | its rubrics (`memo-review-rubric.md`, `deck-review-rubric.md`) | Not public; no manifest, no version |
| **`dreaming-framework`** | The **gated generative faculty**: the DREAMER (imagine better local maxima / opportunities), graded on a Vision / Opportunity Ledger; **OFF by default, per-session owner-authorized**; invoked by this repo's manager (consulting the steward) under the gate | `.dreaming/session-authorization.json` (the gate) + `.dreaming/vision-ledger.md` (the ledger instance) | Not public |

### The deliberate non-overlap

- **Deliverable kind is the dividing line, not subject matter.** Code that
  happens to be security-relevant is still reviewed by this repo's panel; what
  sends you to `cyber-security-framework` is holding a *threat model* or a
  *containment claim*, not the topic of the code.
- **This repo stays domain-neutral** (`scripts/check-domain-neutral.py` enforces
  it mechanically). The siblings are where domain vocabulary is allowed to live.
  That is why the security lenses are defined in `cyber-security-framework`'s
  `docs/security-lenses.md` and not added to [`lenses.md`](lenses.md).
- **Each sibling is thin where this repo is thick.** `cyber`'s `security-review`
  skill owns four lens *definitions* and explicitly routes panel sizing,
  dispatch, consolidation and the verdict rubric back here — the same
  "don't re-describe what a dependency already ships" discipline this repo
  applies to `superpowers`.
- **`doc-review-framework` is the exception, and it is a real one.** It ships a
  *complete parallel* review model: its own reviewer agents, its own weighted
  rubrics with a 1–4 scale, red-flag caps and tiers, its own PASS / REVISE
  verdict, and its own PostToolUse hook. It does not thin out into this repo's
  panel. See §3.

## 2. Where they genuinely compose — three seams that are real

### 2.1 The review panel is the seam (BUILT for `cyber`)

This repo's law — *every deliverable carries at least one adversarial skeptic;
the floor is one; no exceptions* — is deliberately deliverable-agnostic, so a
sibling can supply lenses without supplying machinery.

`cyber-security-framework` uses that seam as designed and *as written down*: its
`skills/security-review/SKILL.md` declares a soft, by-name dependency on
`delegation-framework:skeptical-review`, `:consolidating-review` and
`:delegating`, states that its four lenses are **additions to**
[`lenses.md`](lenses.md) rather than replacements, and reports in this repo's
`docs/rubric.md` verdict format. Both sides of that seam exist today.

**Built.** Both repos describe it, and the mechanism it needs (name a lens in a
skeptic dispatch) requires nothing new on either side.

### 2.2 `evidence-of-containment` is a specialisation of `evidence-vs-claim` (BUILT)

This repo's [`evidence-vs-claim`](lenses.md) lens attacks the gap between what
was *run* and what is *claimed*. `cyber`'s `evidence-of-containment` attacks the
same gap with one variable bound: the claim is always "this control contains
that action", and the evidence is always a **reproduction** — an attack actually
run, against a stated attacker capability, at a commit, with the files under
test recorded. Its extra questions are the ones that only make sense once the
claim is a containment claim: *if the control were silently removed today, what
check would notice?*

The generalisation runs the same way at the catalogue level: `cyber`'s four
lenses share this repo's lens *format* and verdict *rubric*, which is what lets
a mixed panel (two general lenses, two security lenses) consolidate into one
BLOCKING list.

**Built**, with one weak spot named in `cyber`'s own docs: the two catalogues
would collide on the basename `lenses.md`, and the *entire* disambiguation
mechanism is that `cyber` named its file `security-lenses.md`. That is weak. It
is also the appropriate strength for a soft reference, and pretending otherwise
would be the overclaim.

### 2.3 `deriveDrift()` and `deriveExposure()` are the same architecture (BUILT, independently)

The strongest technical kinship in the family is not a dependency at all — it is
a **shared pattern**, arrived at in two repos for two domains:

> A **declaration in a data file**, plus a **validator that derives the verdict
> from it**, with the verdict **derived, never stored**.

| | `code-doc-framework` | `cyber-security-framework` |
|---|---|---|
| Declaration | drift-map JSON: per node, `intended` × `actual` | `.security/threat-model.json`: principals, boundaries, sinks, toolchain, controls |
| Derivation | `deriveDrift()` → `match` / `missing` / `partial` / `undocumented` | `deriveExposure()`, `deriveAssurance()`, `deriveContainment()` |
| Honesty contract | a node carrying `drift`, `state` or `color` is **rejected** | node schemas are **closed by allowlist**, so a committed derived state cannot exist |
| Enforced by | `scripts/validate-drift-map.mjs` | `scripts/validate-threat-model.mjs` |

Both repos state the rule in the same words — *derived, never stored* — and both
enforce it by making a stored verdict a **schema violation** rather than a
convention. The reason is identical in both domains: a stored verdict is a
verdict someone can edit in a diff, and the edit is always one word.

This repo runs a **third, weaker instance** of the same pattern, and the
difference is worth knowing: `.delegation/review-artifact.json` *does* store each
lens's `verdict`, because a review verdict is a **record of a judgement**, not a
function of the data. What is derived — and never stored — is the go/no-go: the
commit gate computes it at commit time from the per-lens verdicts and the
consolidated BLOCKING list. There is no top-level "approved" field for anyone to
flip. Same instinct, one rung less strict, because the input is human judgement
rather than a declaration.

**Built** in all three repos. Note what this seam is *not*: there is no shared
library, no common schema, and no code reuse. Convergent design, independently
implemented. If one repo improves its derivation, the others do not benefit.

## 3. Where the family story is ahead of the wiring — say it plainly

Four gaps. Each is a seam a reader might reasonably assume exists.

1. **This repo defines no documenter role.** Its roles are manager /
   implementation agent / skeptical reviewer, and that is all
   ([`roles.md`](roles.md)). The clean seam "the manager dispatches a documenter,
   which loads `code-doc-framework`" is a **wiring task, not a fact** —
   `code-doc-framework`'s own README says so explicitly. What works today: a
   manager dispatches an ordinary implementation agent and points it at
   `code-doc-framework`'s skills directly. The role-shaped version does not
   exist on either side.

2. **`doc-review-framework` does not reference this repo at all.** The
   composition is one-directional and, at present, one-*sided*: nothing in that
   repo mentions delegation, skeptics, panels, or the PLEASED / NOT PLEASED
   rubric. Worse for the family story, its review model is **not merely absent
   but different in kind** — a weighted rubric producing a score, a tier and
   PASS / REVISE, versus this repo's numbered-BLOCKING, all-must-be-PLEASED
   panel. Those two verdicts do not consolidate into one list without someone
   deciding a mapping, and **no such mapping is written anywhere**. Treat "the
   panel is the seam all three plug into" as true of two and **aspirational for
   the third**.

3. **`doc-review-framework` cannot be pinned or namespaced.** It ships no
   `.claude-plugin/` manifest, so there is no version to validate against and no
   plugin prefix to invoke its agents under. Its README instructs consumers to
   **rename** its agents to their own domain when vendoring — which is the
   documented path, not a misuse, and which defeats by-name reference and the
   SessionStart probe simultaneously. This is the weakest link in the family and
   should not be described as equivalent to the other two.

4. **Two session-global gates, if a consumer installs both.** This repo's
   PreToolUse commit gate (scoped by a `.delegation/` marker) and `cyber`'s
   PreToolUse agent-runtime gate (scoped by a `.security/` marker, matcher `*`)
   are independent hooks with independent opt-in markers. They do not contend
   for the same decision, but they **do both run on tool calls in every repo the
   session touches**, and each carries its own false-positive residual. Nothing
   coordinates them; no combined limit has been analysed. Install both knowing
   that.

## 4. What none of this buys you

- **No auto-discovery, no registration, no registry.** Every connection above is
  a human reading a table and typing a name. Asserting a registry that does not
  exist was a blocking review finding against `cyber-security-framework`'s own
  design; this document does not repeat it in the one place where three
  consumers would inherit it.
- **No propagation.** Independently versioned repos with nothing shared between
  them. An improvement in one does not reach
  the others, and a rename in one **silently breaks** the by-name references in
  the others — there is no check anywhere that would notice.
- **No transitive guarantee.** A green panel in this repo certifies nothing about
  a sibling's artifact, and a green sibling validator certifies nothing about
  the judgement that produced its declaration. Both remain what they were:
  machinery that runs, and judgement that stays human-owned.
