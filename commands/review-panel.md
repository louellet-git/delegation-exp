---
description: Spin up a scaled skeptic panel (2-3 small / 5-7 batch), consolidate findings, and drive it to convergence
argument-hint: [the integrated deliverable or slice set to review]
---

Run a full review panel over:

$ARGUMENTS

1. Use the **delegation-framework:skeptical-review** skill: size the panel
   (2–3 for a small change, 5–7 for a feature batch), diversify lenses,
   triage the mode (swarm / deep / hybrid by breadth-vs-depth × risk), and
   dispatch, reviewing the whole integrated tree, not half-written slices.
2. If any reviewer is NOT PLEASED, use the
   **delegation-framework:consolidating-review** skill: consolidate the
   BLOCKING findings, adjudicate every one through the fluff gate (real
   defects gate; taste, scope creep and triggerless hypotheticals are
   demoted with a written reason, one rebuttal round for the reviewer, and
   the adjudication record written before any fix is dispatched), batch the
   survivors into one reconciled fix round, then re-review only the
   dissenters, converging by severity and region (the skill's section 7).
3. When every reviewer is PLEASED, write the review artifact so the commit
   gate will pass, filling `head_sha` from `git rev-parse HEAD` **last**, once
   the tree has stopped changing. Then inspect the tree yourself before
   committing (reconcile the integrated diff against the dispatched
   allowlists, re-run the full test command, check the artifact's fields). The
   artifact binds to that one HEAD, so this panel waives exactly **one**
   commit: land the whole batch in a single commit, not one per slice.
