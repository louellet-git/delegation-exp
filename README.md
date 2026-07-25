# delegation-framework

**Playbook, roles, and adversarial review machinery for a manager →
implementer → skeptic operating model, packaged as a Claude Code plugin.**

---

## Who this is for (read this before you install)

This framework is tuned for **fixed-cost personal accounts**, where you pay a flat
monthly subscription rather than per token. That assumption is load-bearing, and it
shapes every default here.

When each token has a marginal price, thoroughness competes with cost, and the
sensible move is the smallest review that plausibly suffices. When the monthly cost
is fixed, that tradeoff disappears: a seven-skeptic panel and a two-skeptic panel
cost the same, so the only question left is which one catches more. This framework
answers that question the same way every time, and it is why the defaults look
extravagant — panels of 5 to 7 reviewers with deliberately redundant lenses, an
adversarial reviewer attached to every deliverable with no exceptions, re-review of
dissenters after each fix round, a standing steward that reviews the manager itself.
None of that is calibrated to be cheap. All of it is calibrated to find things.

**If you are billed per token, these defaults will cost you real money.** They are
not wrong for metered use, but they are not tuned for it. Scale the panel sizes down
(the sizing rules are in [`docs/operating-model.md`](docs/operating-model.md)), treat
the always-pair-a-skeptic floor as the one rule worth keeping at full strength, and
expect to make the cost/thoroughness call yourself. This framework will not make it
for you, because it was built somewhere that never had to.

## The roles at a glance (so any agent knows what they are)

A flat org with one spawner: the owner talks only to the manager; the manager
is the single top-level orchestrator and the only agent that can spawn;
everything else is a flat sibling it spawns, one level deep. Full detail:
[`docs/roles.md`](docs/roles.md).

- **Owner** *(the human).* The authority the framework answers to and the only
  one that may change the framework. It interacts only with the manager, is
  the final adjudicator of a manager↔steward dispute, and starts (and
  coordinates) any *separate session* when genuinely-parallel deep work is needed.
- **Manager** ([`agents/manager.md`](agents/manager.md)) *(the single top-level
  orchestrator; the ONLY spawner).* Owner-facing. It decomposes, spawns
  implementers and skeptics as flat siblings, runs the review panel, integrates,
  and commits. It also spawns the steward and stays in continuous
  dialogue with it.
- **Steward** ([`agents/steward.md`](agents/steward.md)) *(a flat sibling the
  manager spawns).* Its standing job is to keep the manager on track: govern
  VISION alignment and DELEGATION discipline and stop the manager *going too deep
  and losing the plot.* It runs a VISION + DELEGATION scorecard, holds the
  yardstick (the owner's goal made concrete), carries a minor
  hurdle-anticipation instinct, and advises and flags; it does not command.
  It holds one narrow **andon-cord**, *escalate-before-proceed*, on a small
  closed class (major allocations, new workstreams, trading away a proven
  invariant), where the manager pauses until the owner rules. An unresolved
  manager↔steward dispute escalates to the owner. It cannot spawn.
- **Implementation agents + Skeptics** *(flat-sibling workers).* Implementers
  build one scoped slice each; skeptics ([`agents/skeptic.md`](agents/skeptic.md))
  adversarially review every deliverable. Neither can spawn; a worker that
  needs a helper asks the manager to spawn one.

**The spawn rule (load-bearing).** This framework enforces one-level-deep
spawning as a *design choice*, not as a runtime constraint. Subagent tool grants
are set per agent definition: see the `tools:` frontmatter in
[`agents/skeptic.md`](agents/skeptic.md) and [`agents/steward.md`](agents/steward.md),
which withhold any spawn tool, against [`agents/manager.md`](agents/manager.md),
which holds `Task`. A runtime *may* hand a subagent its own spawn tool; this
framework declines to. The difference matters: this is a rule we impose, and it
can therefore be broken by an agent definition that grants `Task` to a worker.
It is not a wall the platform holds for us. So: the manager is the sole
spawner; there are no fake tiers (a spawned agent cannot build its own
sub-team, and solo work must never be presented as a delegated team); and
genuinely-parallel deep teams are separate SESSIONS, each with its own
manager, coordinated by the owner. Lateral coordination is by messaging, not
spawning. The manager auto-consults the steward on a standing, binding rule at
execution checkpoints, so the owner never has to be the reminder
([operating model](docs/operating-model.md#manager-auto-consults--a-standing-binding-rule)).

---

Installing it gives a project the *organized discipline* (the decomposition
checklist, the adversarial review panel, the reliability rules, the lens
catalogue) extracted from one project's operating model into one composable,
versioned place.

**On authorship.** This framework was drafted with Claude Code and reviewed by
the adversarial panel it describes; the machinery was pointed at itself. It is
roughly 2,500 lines of doctrine over about 1,000 lines of Python, with a
further ~700 lines of tests covering the one structural gate. Both facts are
visible in the commit history and the file sizes. Stating them here saves you
checking, and neither is a reason to discount the ideas or to inflate them.

It does not guarantee that any given delegation is well-judged.
Decomposition quality, whether a finding is truly blocking, and the go/no-go
on a commit stay human-owned (or owned by whichever agent plays manager).
The framework supplies the machinery and the reminders; the judgment is not
something a plugin can certify. Every claim in this repo is written to that
standard: capability claims, not behavioural guarantees.

## What it owns

The framework is standalone. It writes down the loop it runs, one scoped task
per fresh subagent, fan-out decided by disjoint write sets, test-first
implementation, and evidence before claims, in
[`skills/delegating/SKILL.md`](skills/delegating/SKILL.md) and
[`docs/operating-model.md`](docs/operating-model.md). One property of that loop
is worth naming, because it is the reason the pattern holds up over a long run:
the subagent spends its own context window on the files it reads and returns
the manager a report, so the manager's window accumulates summaries rather
than file contents. That is a consequence of delegating well and not a
mechanism this repo invents; what the repo adds is organizing it and pressing
the manager not to abandon it under pressure.

Around that loop it adds the parts that are the actual reason to install it:

1. **The always-pair-a-skeptic discipline.** Every deliverable (research,
   design, implementation) carries at least one adversarial skeptic. Floor of
   one. No exceptions. A code review covers code; this rule covers everything.
2. **The scaled adversarial panel.** 2–3 skeptics for a small change, 5–7 for
   a feature batch, with diverse lenses.
3. **The lens catalogue + PLEASED / NOT PLEASED rubric.** Named adversarial
   lenses (code *and* non-code) and a numbered-BLOCKING verdict format.
4. **The reliability / stall rules.** Silence ≠ progress; watch file
   activity, not completion notifications; concrete re-briefs for stalled
   agents; commit disjoint slices as they land.
5. **Doc-collision avoidance.** Reserved index files, pre-assigned doc
   numbers, and a fill-before-you-fan-out conflict checklist.
6. Swarm vs. deep review modes with a dual-placement selection rule.
7. **The steward.** A standing, read-only adversarial flat sibling the
   manager spawns, whose whole purpose is to stop the manager going too deep
   and losing the plot. It reviews the *manager* (not deliverables): it scores
   VISION (on-prize vs drifting into motion) and DELEGATION (orchestrating vs
   doing IC work / over-spawning / under-delegating / fake sub-team). It
   **advises and flags; it does not command.** The manager can weigh or ignore
   its scorecard, judgment stays human-owned, and an unresolved dispute escalates
   to the owner. It is disciplined accountability, not enforcement.

See [`skills/delegating/SKILL.md`](skills/delegating/SKILL.md) for the loop
mechanics and these rules in operational form, and
[`docs/operating-model.md`](docs/operating-model.md) for the full model.

## Install

### 1. Git-installable (the default, precedented path)

The repo lists itself as a single-plugin source
([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)), so it
installs directly from git:

```
/plugin marketplace add louellet-git/delegation-framework-public
/plugin install delegation-framework@delegation-framework-source
```

Note: the self-listing `marketplace.json` is only the *mechanism* for direct
git install. It is not the shared-marketplace distribution channel
discussed below.

### 2. Marketplace (intended, pending a decision)

Publishing to a personal/org marketplace (so a `v1.1 → v1.2` bump propagates
to every consumer that upgrades) is the *intended* fast-follow, not a
settled fact. Cross-consumer propagation is conditional on marketplace
tooling that is not yet in place; until it lands, upgrades are per-consumer
(re-install / re-vendor). We do not state one-shot propagation as a current
capability.

### 3. Vendoring: the frozen-snapshot escape hatch

A project that cannot install plugins copies these directories into its own
tree:

```
agents/ skills/ commands/ hooks/ scripts/ docs/ LICENSE
```

and records the vendored upstream commit in its README. A vendored copy is a
frozen snapshot by nature; it drifts the moment either side changes. So the
update story is explicit and minimal:

1. `git fetch` the upstream repo.
2. `git diff <vendored-commit>..<target-tag> -- agents/ skills/ commands/ hooks/ scripts/ docs/ LICENSE`
3. Re-apply the diff to your copy.
4. Record the new commit in your README.

Vendored copies do **not** stay current on their own.

## Dependencies

None. This repo is standalone: everything it needs to run is in this tree.
There is no companion plugin to install, no skill invoked by name from
somewhere else, and no version to pin. The manifest
([`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)) declares no
`dependencies`.

The one external requirement is an interpreter: the hook commands are portable
Python, so `python` or `python3` must be on PATH for the commit gate and the
reminder hooks to run at all (see limit 1 below).

## Enforcement, honestly: one structural slice, the rest is discipline

Most of this framework is organized discipline plus reminders. Exactly
one slice is structural:

**The commit gate.** The review panel produces a **review artifact**: a file
at `.delegation/review-artifact.json` in the consumer repo recording the
deliverable reviewed, the mode (swarm / deep / hybrid), each lens's verdict,
and the consolidated BLOCKING list (format:
[`skills/skeptical-review/SKILL.md`](skills/skeptical-review/SKILL.md)). A
PreToolUse hook on the commit-creating git subcommands (`commit`, `merge`,
`rebase`, `cherry-pick`, `revert`, `pull`, `am`)
([`scripts/commit-gate.py`](scripts/commit-gate.py)) denies the command
unless a well-formed, all-PLEASED artifact **bound to the current HEAD**
exists, but **only in repos that
have opted in** by having a `.delegation/` directory at the repo root (the
`delegating` skill / `/delegate` creates it when a loop starts; it is also
the natural home of the artifact and checklist). Command matching is
anchored on command *position*, not on quoting. Prose inside a running
command (`echo please run git commit later`, `grep 'git commit' docs/`) does
not trigger it. But a command separator inside quotes is still a separator
(`echo "step1; git commit -m msg"`), and a heredoc line starting at column 0
with `git commit` still matches. Both over-matches are deliberate and pinned
by tests: parsing quoting and heredocs means writing a shell, and every bug
in that shell would fail open. Within its reach, skipping review takes
a *visible act* (deleting or faking an artifact, or removing the marker)
rather than merely forgetting a rule.

**Its five honest limits:**

1. It fires only where this plugin's hooks are installed and enabled in
   the environment running the committing agent, and only if `python` (or
   `python3`) is on PATH. The hook commands are Python; with neither
   interpreter present the gate silently vanishes. A different environment,
   or hooks disabled, means no gate.
2. It verifies the artifact exists, is well-formed (including a non-empty
   `deliverable` saying what was reviewed), is all-PLEASED, and is bound to
   the commit it was reviewed against (`head_sha` must match current HEAD,
   so one artifact waives exactly one commit). It does
   *not* verify that the review was rigorous. A determined agent could
   fabricate a PLEASED artifact. The gate is a wall against forgetting,
   not against bad faith.
3. It gates the local commit (matching the model's "manager commits"
   rule); it cannot reach agents that never touch this git working tree.
4. Even where hooks are enabled, it gates only commits issued through the
   hooked tool invocations the PreToolUse matcher sees, and only as its
   parsing understands them. Alternate invocations bypass it: a `git`
   alias, a subprocess (`bash -c "git commit"`, quoted, so no anchor), or an
   IDE/GUI commit that never crosses the matcher. The gate resolves *which*
   repo to consult from the hook's cwd plus parsing of the full `cd` chain
   preceding the command and the `git -C`, `--git-dir` and `--work-tree`
   flags. Paths built from variables or nested quoting are still not
   resolved, but they no longer waive: an unresolvable or out-of-tree target
   falls back to the hook's own repo and gates there, which can deny a
   commit aimed at a different, ungated repo (fail closed, see limit 5). Matcher evasion is a bad-faith route rather than
   an accident, but it is *possible*: the gate walls off the forgetful
   default path, not every path to a commit.
5. **Over-reach (the flip side).** Plugin hooks are session-global: the
   gate script is consulted for tool calls in *every* repo the session
   touches, not just this one. It is scoped by the `.delegation/` opt-in
   marker (no marker → silent allow) and by anchored command matching, but a
   compound command, a separator inside a quoted string, a heredoc
   documenting a commit, or the fail-closed fallback in limit 4 can still
   false-positive and deny something it shouldn't. Escape hatches, in order of preference: write the
   review artifact; remove the repo's `.delegation/` directory (un-opt-in);
   or disable the hook.

Everything else (the always-pair-a-skeptic breadth, the reliability rules,
panel sizing) is skill guidance plus **reminder hooks**, which nudge and
never structurally enforce: a SubagentStop nudge ("attach a skeptic") and a
Stop nudge (uncommitted work with no all-PLEASED artifact at session stop),
both scoped by the same `.delegation/` opt-in marker so they stay silent in
unrelated repos. A hook cannot know an off-tree research deliverable went
unreviewed.

## The do-not-modify rule — what it does and does not mean

One operating rule governs agents that run *under* this framework:

> **An agent pointed at this framework does not modify it.** It reads it, applies
> it, and operates by it. Changes require the owner's explicit authorization.
> There is no exception for "it would be an improvement," for a reviewer
> suggesting it, or for a run that seemed to need it. An agent's job is to operate
> by the rules, not to rewrite the rules it runs on. If an agent believes a change
> is warranted, it surfaces the change to the owner and stops.

**This is not a restriction on you.** This is MIT-licensed. Fork it, edit it,
vendor it, rip out the parts you disagree with. That is what the licence is for,
and "the owner" below means *you*, the person running the framework, not its
author.

The rule exists because an agent that can rewrite its own operating rules will
eventually rewrite an inconvenient one mid-run and report success. It is a
governance discipline addressed to agents, enforced by nothing but the instruction
itself. See [`docs/roles.md`](docs/roles.md) for who may authorize what.

## Layout

```
.claude-plugin/plugin.json     manifest (+ marketplace.json self-listing for git install)
agents/manager.md              the single top-level orchestrator and ONLY spawner; owner-facing; runs the loop and commits (the top-level session agent)
agents/skeptic.md              the reusable adversarial reviewer of deliverables (spawnable)
agents/steward.md              the reusable adversarial reviewer of the MANAGER, a flat sibling the manager spawns (spawnable, standing)
skills/delegating/             the manager's loop: mechanics, the rules on top of them, the commit gate
skills/skeptical-review/       run a panel; lenses; swarm/deep/hybrid modes
skills/consolidating-review/   batch BLOCKING findings; drive convergence
commands/                      /delegate, /skeptic-review, /review-panel
hooks/hooks.json               reminder hooks; the commit gate
scripts/                       gate + validation scripts (portable Python)
docs/                          skill-referenced data (NOT auto-loaded):
                               operating-model, roles, lenses, rubric,
                               conflict-avoidance checklist, worked example
```

`docs/` and the rubric files are skill-referenced data: a skill points
at them by relative path and reads them on demand. They are not auto-loaded
plugin surfaces.

## Validation

Two mechanical gates keep the repo honest; both must be green:

```
python scripts/validate-structure.py      # manifest, frontmatter, hooks, links
python scripts/check-domain-neutral.py    # denylist grep: no source-domain vocabulary
```

The domain-neutrality gate greps the whole tree against a denylist of
source-domain terms (see the script for the list) and fails on any hit. It
catches the obvious leaks; subtler domain-shaped *assumptions* are policed by
adversarial review, not by the grep. Two distinct mechanisms, not one.

Note: the design spec named the gate/check scripts as shell scripts (`.sh`);
they ship as portable Python (`.py`) so the same scripts run on Windows
and POSIX, a deliberate and flagged divergence with identical contracts. The
hook commands therefore require `python` or `python3` on PATH (limit 1
above).

## What green does NOT buy you

- Passing validation proves the machinery runs, not that any delegation
  was well-judged. Manager judgment remains human-owned.
- The commit gate is a wall against **forgetting** a review, not against a
  **fabricated** one, and only where hooks are installed and enabled, only
  in repos carrying the `.delegation/` opt-in marker, and with the residuals
  of limits 4 and 5 (unparsed paths now fall back and over-gate rather than
  mis-resolve silently; rare false positives).
- The published git history is a single commit. This repo was rebuilt from a
  clean tree for public release rather than being published in place, so the
  history here is not a record of how long the work took or how it evolved.
- Reminder hooks and the skeptic-pairing breadth are discipline, not
  structure: they reduce, but do not eliminate, the chance an off-tree
  deliverable ships unreviewed.
