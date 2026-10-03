---
description: Run a scaled skeptic panel over an integrated deliverable and drive it to convergence
argument-hint: [the integrated deliverable or slice set to review]
---

Run a full review panel over:

$ARGUMENTS

1. Use the **delegation-framework:skeptical-review** skill: size the panel
   (2-3 small change, 5-7 feature batch), diversify lenses, triage the mode
   (swarm, deep or hybrid by breadth-versus-depth and risk), dispatch over the
   whole integrated tree, not half-written slices.
2. If any reviewer is NOT PLEASED, use the
   **delegation-framework:consolidating-review** skill: consolidate the
   BLOCKING findings, adjudicate each through the fluff gate (real defects
   gate; fluff is demoted with a written reason after one rebuttal round; write
   the adjudication record before any fix), batch the survivors into one
   reconciled fix round, re-review only the dissenters, converge by severity
   and region (its section 7).
3. When every reviewer is PLEASED, write the review artifact, filling
   `head_sha` from `git rev-parse HEAD` **last**, once the tree has stopped
   changing. Then inspect the tree yourself: reconcile the integrated diff
   against the dispatched allowlists, re-run the full test command, check the
   artifact's fields. The artifact binds to that HEAD: make one commit for the
   whole batch, not one per slice.
