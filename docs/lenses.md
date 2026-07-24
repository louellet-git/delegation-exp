# The lens catalogue

A **lens** is the specific adversarial angle a skeptic is assigned. A panel
diversifies lenses; five reviewers with the same lens are one reviewer. Each
lens below lists what it attacks and the questions it asks. The verdict
format every lens reports in is [`rubric.md`](rubric.md).

Lenses are deliberately **domain-neutral**. Where a lens needs an "end goal"
to measure against, the manager's dispatch supplies it — the lens never
assumes one.

## Code lenses

### correctness

Attacks whether the thing actually works — especially on inputs nobody
tried. Questions: What malformed, empty, boundary, or adversarial input
breaks this? What concurrent or repeated use breaks it? Does the error path
work, or only the happy path? Smells: only round-number fixtures; no empty /
null / zero-length case; catch blocks that swallow.

### coupling / boundary-integrity

Attacks architectural seams. Questions: Does this change reach across a
boundary it shouldn't (a forbidden import, a layering violation, a
dependency direction reversal)? Does it leak an internal type across a
public seam? Would a consumer on the other side of the boundary break
silently? Smells: "just this once" imports; a util module that knows about
two layers.

### overfit / generalization

Attacks work tuned to the surface it was developed on. Questions: Does this
pass because it is right, or because it was tuned to *this* fixture, *this*
benchmark, *this* dev environment? Distinguish **the real target from a
proxy you built** — does it generalize beyond the surface it was tuned on?
Would a slightly harder-but-still-realistic input flip the result? Smells:
constants that happen to match the test data; assertions that hold only
under a generously chosen parameter; green on a clean synthetic fixture when
the real target is messy.

### evidence-vs-claim

Attacks the gap between what was *run* and what is *claimed*. Questions:
What has actually executed, where, and does the output shown prove the
sentence written above it? Is "tests pass" doing the work of "feature
works"? Does a test assert behaviour, or assert that a mock was called?
Smells: "did not crash" oracles; `assert result` with no expected value;
tautologies (asserting a getter returns what a setter set); a claim of
cross-environment behaviour verified in only one environment.

### honesty / overclaim

Attacks the documentation and reporting around the work. Questions: Does any
doc, comment, or report promise more than the code delivers? Is a convention
described as a guarantee? Is a known gap silently dropped instead of
recorded as a labelled `xfail` / accepted residual with a reason? Smells:
"ensures", "guarantees", "always" in prose about best-effort machinery;
deleted failing tests; a README that describes the intended system, not the
built one.

### derived-output / ranking

For anything that scores, ranks, classifies, prioritizes, or derives a verdict
— a risk model, a triage signal, a scoring rubric, a health check. Attacks
whether the output *orders reality correctly*. Questions: Does something
genuinely dangerous score low, and something benign score high? Check both
directions — a signal that fires on everything and a signal that fires on
nothing are the same failure, and they hide each other. Is every ordering the
prose appeals to ("at minimum", "ranks with", "the minimum over") actually
published and total? Does declaring *nothing* score better than declaring
something honest? Run the deliverable's own worked example or shipped fixture
through its own rules. Smells: a threshold with no stated headroom; two
independent promotion rules that can stack; "any X such that Y" over a set that
can be empty; a guarantee proven against enumerated failure modes but never
against the default path.

**The discount rule.** Any *self-declared* field that lowers a derived score is
an attack surface, and the attack is always one word in a diff. For each such
field ask: what cross-check binds it to reality, and if none, does setting it
at least emit a warning? Silence plus a discount is the defect. Expect this to
recur — closing it for one field tends to move it to the next one, so enumerate
every field that can lower the output and check them as a set, not one at a
time.

### per-feature

A slot, not a fixed lens: one skeptic assigned to a single feature or slice,
attacking it in depth with whichever of the above angles apply. Use it when
a slice is risky enough to deserve a dedicated adversary.

## Non-code lenses

### design-review

For design docs and specs. Questions: Does the design **close its stated
invariants**, or route around them? Where does it overclaim — promising
behaviour its mechanisms cannot enforce? Are its open decisions labelled as
open, or silently assumed settled? Does each component own one thing, or do
two components own the same thing? What failure mode has no owner? Smells: a
"law" enforced only by convention while described as a wall; a dependency
stated as hard when nothing declares it.

### research / claim-verification

For research memos, comparisons, and recommendations. Questions: Is **each
claim traced to a source** that actually says it? Is any assertion asserted
beyond its evidence — an n=1 anecdote generalized, a benchmark from a
different context, a version-specific fact stated timelessly? Were
disconfirming sources looked for, or only confirming ones? Smells:
citations that don't contain the claim; "it is well known"; measurements
without their conditions.

## Choosing lenses for a panel

- Small change (2–3 skeptics): correctness + evidence-vs-claim, plus the one
  lens matching the change's dominant risk.
- Feature batch (5–7): cover correctness, coupling/boundary-integrity,
  overfit/generalization, evidence-vs-claim, honesty/overclaim, plus
  per-feature skeptics for the riskiest slices.
- Non-code deliverables: design-review or research/claim-verification is the
  anchor; add honesty/overclaim as the second.
- Anything that scores, ranks, or derives a verdict: **derived-output/ranking**
  is mandatory, and it must be run in **deep** mode — the inversion and
  fail-open findings it exists to catch are only reachable by executing the
  thing, never by reading it.

Mode selection (swarm / deep / hybrid) is a separate dimension from lens choice —
see [`../skills/skeptical-review/SKILL.md`](../skills/skeptical-review/SKILL.md).
