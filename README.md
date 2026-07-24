# delegation-framework

**Playbook, roles, and adversarial review machinery for a manager →
implementer → skeptic operating model, packaged as a Claude Code plugin.**

---

## ⚠ DO NOT MODIFY THIS FRAMEWORK — read it, apply it, operate by it

**Any agent pointed at this framework MUST NOT modify it — ever — unless the
owner explicitly asks.** Read it, apply it, operate by it; do **not** edit it.
Framework changes require **explicit owner authorization**. There is no
exception for "it would be an improvement," "the steward suggested it," or "a
run seemed to need it" — an agent's job is to *operate by* this framework, not
to rewrite the rules it runs on. If you believe a change is warranted, surface
it to the owner and stop; only the owner authorizes a change, and an authorized
change is made by an agent the owner directs to make it.

This rule is **family-wide** — it binds every framework in the
[framework family](#the-framework-family-a-family-of-governance-frameworks)
(delegation, cyber-security, doc-review, code-doc, dreaming, and more to come), and
it binds **every role, the owner-facing manager and the steward (VZ) included.**
(See [roles](docs/roles.md) for who may authorize what.)

## The roles at a glance (so any agent knows what they are)

A flat org with **one spawner**: the owner talks only to the manager; the manager
is the single top-level orchestrator and the **only agent that can spawn**;
everything else is a **flat sibling** it spawns, one level deep. Full detail:
[`docs/roles.md`](docs/roles.md).

- **Owner** *(the human).* The authority the framework answers to and the only
  one that may change the framework. It **interacts only with the manager**, is
  the final adjudicator of a manager↔steward dispute, and starts (and
  coordinates) any *separate session* when genuinely-parallel deep work is needed.
- **Manager** ([`agents/manager.md`](agents/manager.md)) *(the single top-level
  orchestrator; the ONLY spawner).* Owner-facing. It decomposes, **spawns**
  implementers and skeptics as flat siblings, runs the review panel, integrates,
  and **commits**. It also **spawns the steward (VZ)** and stays in continuous
  dialogue with it. It invokes the gated dreaming-framework — consulting the
  steward — only when the owner has authorized a dream session.
- **Steward = VZ** ([`agents/steward.md`](agents/steward.md)) *(a flat sibling the
  manager spawns).* The owner's sharp, plain-spoken partner, whose standing job is
  to **keep the manager on track** — govern VISION alignment and DELEGATION
  discipline and stop the manager *going too deep and losing the plot.* It runs a
  VISION + DELEGATION scorecard, holds the yardstick (the owner's goal made
  concrete), carries a minor hurdle-anticipation instinct, and **advises and
  flags; it does not command.** It holds one **narrow andon-cord** —
  *escalate-before-proceed* on a small closed class (major allocations, new
  workstreams, trading away a proven invariant), where the manager pauses until
  the **owner** rules. An unresolved manager↔steward dispute escalates to the
  **owner**. It **cannot spawn**.
- **Implementation agents + Skeptics** *(flat-sibling workers).* Implementers
  build one scoped slice each; skeptics ([`agents/skeptic.md`](agents/skeptic.md))
  adversarially review every deliverable. **Neither can spawn** — a worker that
  needs a helper asks the manager to spawn one.

**The spawn rule (load-bearing).** This framework enforces **one-level-deep
spawning** as a *design choice*, not as a runtime constraint. Subagent tool grants
are set per agent definition — see the `tools:` frontmatter in
[`agents/skeptic.md`](agents/skeptic.md) and [`agents/steward.md`](agents/steward.md),
which withhold any spawn tool, against [`agents/manager.md`](agents/manager.md),
which holds `Task`. A runtime *may* hand a subagent its own spawn tool; this
framework declines to. Stated honestly, because the difference matters: this is a
rule we impose and can therefore be broken by an agent definition that grants
`Task` to a worker — not a wall the platform holds for us. So: the manager is the
**sole spawner**; there are **no fake tiers** (a spawned agent cannot build its own
sub-team — solo work must never be presented as a delegated team); and
**genuinely-parallel deep teams are separate SESSIONS**, each with its own
manager, coordinated by the owner. Lateral coordination is by messaging, not
spawning. The manager **auto-consults** the steward on a standing, binding rule at
execution checkpoints, so the owner never has to be the reminder
([operating model](docs/operating-model.md#manager-auto-consults--a-standing-binding-rule)).

---

Installing it gives a project the *organized discipline* — the decomposition
checklist, the adversarial review panel, the reliability rules, the lens
catalogue — extracted from one project's operating model into one composable,
versioned place.

**On authorship, up front.** This framework was drafted with Claude Code and
reviewed by the adversarial panel it describes — the machinery was pointed at
itself. It is roughly 2,700 lines of doctrine over ~660 lines of Python. Both
facts are visible in the commit history and the file sizes; stating them here
saves you checking, and neither is a reason to discount the ideas or to inflate
them.

It does **not** guarantee that any given delegation is well-judged.
Decomposition quality, whether a finding is truly blocking, and the go/no-go
on a commit stay **human-owned** (or owned by whichever agent plays manager).
The framework supplies the machinery and the reminders; the judgment is not
something a plugin can certify. Every claim in this repo is written to that
standard: capability claims, not behavioural guarantees.

## What it owns (and what it deliberately does not)

The `superpowers` plugin already ships the orchestration loop, the
parallelism rules, and code review. This framework **delegates those
mechanics to `superpowers` by name** and owns only the residual:

1. **The always-pair-a-skeptic discipline** — every deliverable (research,
   design, implementation) carries at least one adversarial skeptic. Floor of
   one. No exceptions. `superpowers` reviews code; this rule covers everything.
2. **The scaled adversarial panel** — 2–3 skeptics for a small change, 5–7 for
   a feature batch, with diverse lenses.
3. **The lens catalogue + PLEASED / NOT PLEASED rubric** — named adversarial
   lenses (code *and* non-code) and a numbered-BLOCKING verdict format.
4. **The reliability / stall rules** — silence ≠ progress; watch file
   activity, not completion notifications; concrete re-briefs for stalled
   agents; commit disjoint slices as they land.
5. **Doc-collision avoidance** — reserved index files, pre-assigned doc
   numbers, and a fill-before-you-fan-out conflict checklist.
6. **Swarm vs. deep review modes** with a dual-placement selection rule.
7. **The steward (VZ)** — a standing, read-only adversarial **flat sibling the
   manager spawns**, whose whole purpose is to stop the manager going too deep
   and losing the plot. It reviews the *manager* (not deliverables): it scores
   VISION (on-prize vs drifting into motion) and DELEGATION (orchestrating vs
   doing IC work / over-spawning / under-delegating / fake sub-team). It
   **advises and flags; it does not command** — the manager can weigh or ignore
   its scorecard, judgment stays human-owned, and an unresolved dispute escalates
   to the **owner**. It is disciplined accountability, not enforcement.

See [`skills/delegating/SKILL.md`](skills/delegating/SKILL.md) for the seam
tables — one routing loop mechanics to `superpowers`, one routing whole
*deliverable kinds* to the three sibling frameworks — and
[`docs/operating-model.md`](docs/operating-model.md) for the full model.

## Install

### 1. Git-installable (the default, precedented path)

The repo lists itself as a single-plugin source
([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)), so it
installs directly from git:

```
/plugin marketplace add louellet-git/delegation-framework
/plugin install delegation-framework@delegation-framework-source
```

Note: the self-listing `marketplace.json` is only the *mechanism* for direct
git install. It is **not** the shared-marketplace distribution channel
discussed below.

### 2. Marketplace — intended, pending a decision

Publishing to a personal/org marketplace (so a `v1.1 → v1.2` bump propagates
to every consumer that upgrades) is the *intended* fast-follow, **not a
settled fact**. Cross-consumer propagation is conditional on marketplace
tooling that is not yet in place; until it lands, upgrades are per-consumer
(re-install / re-vendor). We do not state one-shot propagation as a current
capability.

### 3. Vendoring — a frozen-snapshot escape hatch

A project that cannot install plugins copies these directories into its own
tree:

```
agents/ skills/ commands/ hooks/ scripts/ docs/ LICENSE
```

and **records the vendored upstream commit** in its README. This is a
**frozen snapshot** by nature — it drifts the moment either side changes —
so the update story is explicit and minimal:

1. `git fetch` the upstream repo.
2. `git diff <vendored-commit>..<target-tag> -- agents/ skills/ commands/ hooks/ scripts/ docs/ LICENSE`
3. Re-apply the diff to your copy.
4. Record the new commit in your README.

We say plainly: vendored copies do **not** stay current on their own.

## Dependency on `superpowers` (soft, by name — stated honestly)

`superpowers` has **no machine-readable dependency field** another plugin can
declare against, so the composition is a **soft, by-name reference**:

- The skills here invoke `superpowers` skills **by their exact names** (e.g.
  `superpowers:subagent-driven-development`). This resolves **only if**
  `superpowers` is installed and its skill names are unchanged.
- **Pinned surface** — validated against **`superpowers` 6.1.x** (developed on
  6.1.1). The skills composed with, by name:
  `subagent-driven-development`, `dispatching-parallel-agents`,
  `requesting-code-review`, `receiving-code-review`,
  `test-driven-development`, `verification-before-completion`,
  `brainstorming`, `writing-plans`, `executing-plans`,
  `finishing-a-development-branch`.
- **Discoverability check** — a SessionStart hook
  ([`scripts/session-start-check.py`](scripts/session-start-check.py)) probes
  the standard plugin-cache locations for those skills and **warns loudly**
  when any are missing: install `superpowers` or the loop mechanics will be
  missing. This is a **warning, not a hard block** — the hook surface cannot
  guarantee skill resolution, and we do not pretend it can. The probe is
  best-effort: a nonstandard install location can evade it.

## Companion frameworks — private, and named here only so the seams make sense

This repo is **standalone and complete**. Everything it needs to run is in this
tree plus `superpowers`.

It was, however, built alongside several companion frameworks that own one kind
of deliverable each — security review of repos where agents act; documenting a
codebase and measuring doc drift; reviewing non-code deliverables; a gated
generative faculty. **None of them is public, and this repo does not depend on
any of them.** They are named in a few places below and in
[`docs/family.md`](docs/family.md) because the design decisions here only make
sense against them — this repo deliberately does *not* own security lenses or a
documenter role, and a reader deserves to know that was a boundary rather than an
omission.

**Do not go looking for them.** There is no link, no install path, and no
version to pin. If any becomes public it will be linked from here; until then,
treat every companion reference in this tree as design rationale, not as a
routing instruction you can act on.

**What this means for the machinery:** the SessionStart hook
([`scripts/session-start-check.py`](scripts/session-start-check.py)) probes for
companion plugins alongside `superpowers`. Those probes will simply not find
anything, and that is fine — they **warn, never block**, and nothing in this repo
fails when a companion is absent. There is **no registry, no registration step,
no auto-discovery, and no machine-readable dependency field**; no code path here
reads a companion's files.

**The governance model, which does apply here:** the
[do-not-modify guard](#-do-not-modify-this-framework--read-it-apply-it-operate-by-it)
at the top of this README binds every framework built this way — an agent pointed
at one must **read it, apply it, and operate by it, not edit it**, unless the
owner explicitly asks.

## Enforcement, honestly: one structural slice, the rest is discipline

Most of this framework is **organized discipline + reminders**, and we call
it that. Exactly **one** slice is structural:

**The commit gate.** The review panel produces a **review artifact** — a file
at `.delegation/review-artifact.json` in the consumer repo recording the
deliverable reviewed, the mode (swarm / deep / hybrid), each lens's verdict,
and the consolidated BLOCKING list (format:
[`skills/skeptical-review/SKILL.md`](skills/skeptical-review/SKILL.md)). A
PreToolUse hook on `git commit`
([`scripts/commit-gate.py`](scripts/commit-gate.py)) **denies the commit**
unless a well-formed, all-PLEASED artifact exists — but **only in repos that
have opted in** by having a `.delegation/` directory at the repo root (the
`delegating` skill / `/delegate` creates it when a loop starts; it is also
the natural home of the artifact and checklist). Command matching is
**anchored**: only a `git commit` at a command position triggers the gate —
prose that merely mentions it (`echo please run git commit later`,
`grep 'git commit' docs/`) does not. Within its reach, skipping review takes
a *visible act* — deleting or faking an artifact, or removing the marker —
not merely forgetting a rule.

**Its five honest limits**, stated so we never oversell it:

1. It fires **only where this plugin's hooks are installed and enabled** in
   the environment running the committing agent, **and only if `python` (or
   `python3`) is on PATH** — the hook commands are Python; with neither
   interpreter present the gate silently vanishes. A different environment,
   or hooks disabled, means no gate.
2. It verifies the artifact **exists, is well-formed (including a non-empty
   `deliverable` saying what was reviewed), and is all-PLEASED** — *not*
   that the review was rigorous. A determined agent could fabricate a
   PLEASED artifact. The gate is a wall against **forgetting**, not against
   **bad faith**.
3. It gates the **local commit** (matching the model's "manager commits"
   rule); it cannot reach agents that never touch this git working tree.
4. Even where hooks are enabled, it gates **only commits issued through the
   hooked tool invocations** the PreToolUse matcher sees, and only as its
   parsing understands them. Alternate invocations bypass it — a `git`
   alias, a subprocess or heredoc (`bash -c "git commit"`), or an IDE/GUI
   commit that never crosses the matcher. The gate resolves *which* repo to
   consult from the hook's cwd plus **minimal** parsing of a leading
   `cd <path> &&` prefix and `git -C <path>` flags; paths built from
   variables or nested quoting are not resolved and can make it consult the
   **wrong repo silently**. Matcher evasion is a **bad-faith** route, not an
   accident, but it is *possible*: the gate walls off the forgetful default
   path, not every path to a commit.
5. **Over-reach (the flip side).** Plugin hooks are **session-global** — the
   gate script is consulted for tool calls in *every* repo the session
   touches, not just this one. It is scoped by the `.delegation/` opt-in
   marker (no marker → silent allow) and by anchored command matching, but
   an exotic compound command can still **false-positive** and deny
   something it shouldn't. Escape hatches, in order of preference: write the
   review artifact; remove the repo's `.delegation/` directory (un-opt-in);
   or disable the hook.

Everything else — the always-pair-a-skeptic breadth, the reliability rules,
panel sizing — is skill guidance plus **reminder hooks** (nudges, never
structural enforcement): a SubagentStop nudge ("attach a skeptic") and a
Stop nudge (uncommitted work with no all-PLEASED artifact at session stop),
both scoped by the same `.delegation/` opt-in marker so they stay silent in
unrelated repos. A hook cannot know an off-tree research deliverable went
unreviewed.

## Layout

```
.claude-plugin/plugin.json     manifest (+ marketplace.json self-listing for git install)
agents/manager.md              the single top-level orchestrator and ONLY spawner; owner-facing; runs the loop and commits (the top-level session agent)
agents/skeptic.md              the reusable adversarial reviewer of deliverables (spawnable)
agents/steward.md              the reusable adversarial reviewer of the MANAGER, a flat sibling the manager spawns (spawnable, standing; VZ in this framework)
skills/delegating/             THIN manager layer; routes mechanics to superpowers
skills/skeptical-review/       run a panel; lenses; swarm/deep/hybrid modes
skills/consolidating-review/   batch BLOCKING findings; drive convergence
commands/                      /delegate, /skeptic-review, /review-panel
hooks/hooks.json               SessionStart check; reminders; the commit gate
scripts/                       gate + check scripts (portable Python)
docs/                          skill-referenced data (NOT auto-loaded):
                               operating-model, roles, lenses, rubric,
                               conflict-avoidance checklist, worked example,
                               family (the sibling frameworks)
```

`docs/` and the rubric files are **skill-referenced data** — a skill points
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
adversarial review, not by the grep — two distinct mechanisms, stated as two.

Note: the design spec named the gate/check scripts as shell scripts (`.sh`);
they ship as **portable Python** (`.py`) so the same scripts run on Windows
and POSIX — a deliberate, flagged divergence with identical contracts. The
hook commands therefore require `python` or `python3` on PATH (limit 1
above).

## What green does NOT buy you

- Passing validation proves the machinery **runs**, not that any delegation
  was **well-judged**. Manager judgment remains human-owned.
- The commit gate is a wall against **forgetting** a review, not against a
  **fabricated** one — and only where hooks are installed and enabled, only
  in repos carrying the `.delegation/` opt-in marker, and with the residuals
  of limits 4–5 (wrong-repo mis-resolution; rare false positives).
- Reminder hooks and the skeptic-pairing breadth are discipline, not
  structure: they reduce, but do not eliminate, the chance an off-tree
  deliverable ships unreviewed.
