---
description: Decompose a task and run it through the manager -> implementer -> skeptic loop (delegation-framework)
argument-hint: [the task to delegate]
---

**Trivial-edit gate first:** if `$ARGUMENTS` describes a trivial edit or a
single-file fix, do NOT run the delegation machinery. Say so and just make
the edit directly. The overhead is only worth it for substantial,
multi-part work.

Otherwise, use the **delegation-framework:delegating** skill to run the full
loop for this task (which may be a delivered planning-framework package — the
skill's plan intake says how its leaf cards become briefs, and its planner
relay is where plan-content questions go back):

$ARGUMENTS

You are now the **manager** for this task, in this top-level session. Do not
spawn a "manager" subagent; read
`${CLAUDE_PLUGIN_ROOT}/agents/manager.md` if you want the role in full, and
hold it yourself.

Follow the skill exactly:

1. **Arm the repo, and gitignore the marker in the same step.** Create the
   `.delegation/` directory at the repo root, **and add `.delegation/` to that
   repo's `.gitignore` if it is not already there.** The directory is the
   opt-in marker that arms the commit gate and the reminder hooks for THIS
   repo, and it is the home of the checklist, the dispatch briefs, and the
   review artifact. The `.gitignore` line is required, not tidiness, and the
   reason is the reverse of the obvious one: the gate reads the marker's
   provenance from the HEAD commit tree, so a **committed marker turns the gate
   off**, here and in every clone, rather than arming anybody. An unignored
   marker plus an ordinary `git add .` therefore disarms the gate you just
   armed, and a committed all-PLEASED artifact ships a waiver alongside it.
   Both are one `git add .` away.
2. **Run the loop mechanics the skill describes**: one scoped task per fresh
   subagent, fan-out by disjoint write sets, test-first, evidence before
   claims.
3. **Fill the conflict-avoidance checklist before any fan-out.**
4. **Write every brief from the canonical template** in the skill (it already
   carries the file-ownership allowlist, the exact test command, the acceptance
   condition, the pre-assigned ADR / doc numbers, what a predecessor changed
   and any partial work it left, the status contract, the postures, and the
   re-brief that the implementation agent does **not** commit or push). That
   means *every* dispatch: scouting slices and fix rounds too. Save each brief
   under `.delegation/briefs/` before dispatching it, so a steward checkpoint
   can reconcile against it.
5. **Attach at least one skeptic to every deliverable.**
6. **Integrate, then run ONE panel over the integrated tree, then make ONE
   commit.** The review artifact binds to the current HEAD, so it waives
   exactly one commit; do not commit slices individually as they land. Commit
   only after the panel is all-PLEASED, the artifact is written (with
   `head_sha` from `git rev-parse HEAD`), and you have inspected the integrated
   tree yourself.
