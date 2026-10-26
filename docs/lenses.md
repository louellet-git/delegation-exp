# The lens catalogue

A **lens** is the adversarial angle a skeptic is assigned; a panel diversifies
lenses, since five reviewers with one lens are one reviewer. Lenses assume no
end goal: the dispatch supplies it. Verdict format: [`rubric.md`](rubric.md).

## Code lenses

### correctness

Inputs nobody tried (malformed, empty, boundary, adversarial), concurrent or
repeated use, the error path. Smell: swallowing catch blocks.

### coupling / boundary-integrity

A forbidden import, layering violation or reversed dependency; an internal
type leaking across a public seam; a consumer breaking silently.

### overfit / generalization

Right, or tuned to this fixture, benchmark or environment (the real target
versus a proxy you built)? Would a harder realistic input flip it?

### evidence-vs-claim

What ran where, and does the output prove the sentence above it? Is "tests
pass" standing in for "feature works"?

### honesty / overclaim

Docs, comments or reports promising more than the code delivers: a convention
called a guarantee, a known gap not recorded as a labelled `xfail` or residual
with a reason, a deleted failing test.

### derived-output / ranking

Anything that scores, ranks, classifies, prioritizes or derives a verdict: does
it order reality correctly? Run [the skeptic's ranking patterns](../agents/skeptic.md#attack-patterns-name-the-ones-that-apply), executing the
deliverable and its own worked example. Smells: a threshold with no stated
headroom; two promotion rules that can stack.

**The discount rule.** A self-declared field that lowers a derived score is an
attack surface (one word in a diff): what cross-check binds it to reality, and
if none, does setting it warn? Silence plus a discount is the defect. Closing
one field moves the attack to the next, so check every such field as a set.

### per-feature

A slot: one skeptic attacks one risky feature or slice in depth, with whichever
angles apply.

## Non-code lenses

### design-review

Specs and design docs: are stated invariants closed, open decisions labelled
open, every component owning one thing and every failure mode an owner? Smell:
a dependency stated as hard when nothing declares it.

### research / claim-verification

Memos and recommendations: is each claim traced to a source that says it, with
its conditions, and were disconfirming sources sought?

### compact

A created or changed doc: is it as compact as [compact.md](compact.md) asks? A
skeptic loads [compact-review](../skills/compact-review/SKILL.md).

## Choosing lenses for a panel

- Seats and sizing: [panel setup](../skills/skeptical-review/SKILL.md#panel-setup).
- Candidates for a larger batch: correctness, coupling/boundary-integrity,
  overfit/generalization, evidence-vs-claim, honesty/overclaim, plus
  per-feature skeptics for the riskiest slices.
- Non-code deliverables: design-review or research/claim-verification as the
  anchor, honesty/overclaim second.
- Anything that scores, ranks or derives a verdict: **derived-output/ranking**,
  mandatory ([modes](../skills/skeptical-review/SKILL.md#the-three-modes)).
