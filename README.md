# delegation-framework

**Playbook, roles, and adversarial review machinery for a manager →
implementer → skeptic operating model, packaged as a Claude Code plugin.**

---

## Quickstart

In a repo you want to build in, type one command:

```
/delegate add a CSV export endpoint to the reports service, with tests and a docs update
```

That puts you in the manager role: the task gets decomposed into scoped slices,
one fresh implementation agent builds each slice, an adversarial skeptic panel
reviews the integrated result, fix rounds run to convergence, and only then does
anything get committed.

**The four words you will have to type or recognise:**

| Word | What it means |
|------|---------------|
| `PLEASED` / `NOT PLEASED` | The only two verdicts a skeptic returns. There is no "PLEASED with reservations", and every reviewer must be `PLEASED` before the commit. Format: [`docs/rubric.md`](docs/rubric.md). |
| `BLOCKING` | A numbered finding that must be fixed before that commit. Everything else is non-blocking and does not gate. A BLOCKING tag is itself adjudicated before it may gate: the manager runs every one through the **fluff gate** ([`skills/consolidating-review/SKILL.md`](skills/consolidating-review/SKILL.md)) — real defects gate, fluff is demoted on the record with one rebuttal round for the reviewer. Format: [`docs/rubric.md`](docs/rubric.md). |
| `swarm` \| `deep` \| `hybrid` | The three panel modes: many reviewers skimming broadly, one or a few tracing deeply, or both. You pick one per panel and it is recorded in the review artifact. |
| `lens` | The adversarial angle one skeptic is assigned (`correctness`, `evidence-vs-claim`, `honesty/overclaim`, `derived-output/ranking`, and the rest). A panel diversifies them. Catalogue: [`docs/lenses.md`](docs/lenses.md). |

> ⚠️ **Running the loop arms this repo, and arming is what turns the gate on.**
> `/delegate` first checks whether the change is trivial enough to just do
> directly, and stops there if it is. Once it does start a loop it creates a
> `.delegation/` directory at the repo root, and that directory is the opt-in
> marker: from that point on, **every git command in this repo that authors a
> new commit** (`commit`, `cherry-pick`, `revert`, `am`, their `--continue`,
> and `--amend`), including a one-line typo fix, is denied unless a current
> all-PLEASED [review artifact](#enforcement-honestly-one-structural-slice-the-rest-is-discipline)
> sits in `.delegation/`.
>
> **Add `.delegation/` to that repo's `.gitignore` in the same breath**, before
> you commit anything, and keep the marker out of your commits. Two concrete
> failures sit behind that instruction. First, an unignored marker plus an
> ordinary `git add .` sweeps `.delegation/`, and any all-PLEASED artifact
> sitting in it, straight into your own commit. Second, and this is the one
> that matters: **a marker the HEAD commit carries turns the gate OFF**, for
> you and for everyone who clones the repo. Provenance is read from the HEAD
> commit tree. A marker HEAD does not carry was created by whoever is sitting
> here, which is an act of consent, so the gate enforces. A marker HEAD does
> carry arrived with the repository, which is nobody in this working copy
> consenting to anything, so the gate warns and stands down rather than arming
> a repo its contributors never opted into. Committing the marker does not arm
> your colleagues; it disarms you. The warning repeats on every gated command,
> which is deliberate noise: it should be fixed, not tuned out.
>
> **To switch the gate off** in a repo you armed: `rm -rf .delegation`. Check
> `git status` first, because if someone committed an archive under it you would
> be deleting their files. If the marker is already part of HEAD the gate is
> already standing down and says so on every gated command, so there is nothing
> to switch off.
>
> **`git rm -r --cached .delegation` does the opposite.** It leaves the
> directory on disk untracked, which is the armed state. That is the way to
> claim an inherited marker as your own opt-in, and it is covered under
> [claiming an inherited marker](#enforcement-honestly-one-structural-slice-the-rest-is-discipline). Do not reach for it when
> what you want is quiet.

**Check the gate is actually live before you trust it.** A misconfigured
install fails silently by design, because a hook that cannot run must not block
your commits. That means a dead gate and a working one look identical from the
outside. To tell them apart, in a repo you do not mind dirtying:

```
mkdir -p .delegation
grep -qxF '.delegation/' .gitignore 2>/dev/null || echo '.delegation/' >> .gitignore
git commit --allow-empty -m "gate check"
```

An armed gate denies that commit and prints the artifact schema. Silence means
the hooks are not running, whatever the install said. A *warning* instead of a
deny means the hooks are running but this repo's marker is not an opt-in: its
HEAD commit already carries `.delegation/`, or the directory is not inside a
git repo at all, and the warning says which. Remove `.delegation/` afterwards
if you were only testing.

**The worked example.** [`docs/example-run.md`](docs/example-run.md) is one
delegation start to finish: decompose, fan out, panel, consolidate,
adjudicate, fix, re-review, artifact, commit, plus two steward scorecards on
the same run. If you
read one more thing before your first `/delegate`, read that.

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

One default *is* calibrated, and it is firm rather than tuned: the **model
ladder** — amended by its own owner on 2026-09-02, issuer note 4. The manager
holds its role on an Opus session; the two seats (planner, manager) are
unchanged. Below the manager, tier is judgment — Haiku through Opus, Fable
seat-only, workers and reviewers alike, recorded in the brief and never gated
— while agent count is the strengthened half: a growing job is cut into more
agents, never handed to one bigger one, with scouts to size it first. Panels
stay extravagant in count, not tuned down to it: more slices, more lenses,
more reviewers is what a panel buys, and tier on any of them is left to what
the slice in front of it actually needs. The ladder lives in
[`skills/delegating/SKILL.md`](skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what).

The planner seam has its own standing cost, separate from panel sizing: **one
idle planner session plus one Opus manager session per project**, both live
for the run's duration, the planner idling between turns rather than polling
or scheduling itself awake. That is the seam's fixed price of admission,
whether or not any single question ever crosses it.

Liveness across that seam has a second, separate cost (F36): **one idle
Sonnet watchdog session held open for the run, plus one Routine firing per
hour while the run is live.** Neither seat can see whether its counterpart
has stalled or finished, so a standing watchdog session — created by the
planner at handoff, deleted with its Routine at project close — reads both
seats' titles hourly (the platform's floor for a Routine) and wakes a seat,
raises a stall to the owner, or does nothing. Full doctrine, the rubric, and
the two title tokens it reads: [`agents/manager.md`](agents/manager.md#the-watchdog-a-third-seat-standing-s5-v2).

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
  dialogue with it. **You do not spawn the manager.** `agents/manager.md` is
  the role definition you adopt in your own top-level session (that is what
  `/delegate` does); spawning it as a subagent would push it and everything
  it spawns one level too deep. See
  [how to become the manager](agents/manager.md#how-to-use-this-file-do-not-spawn-it).
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

**Two naming conventions, so you can tell them apart.** *Skills and commands*
are addressed with the plugin namespace, as `delegation-framework:delegating`
or `/delegate`. *Agents are spawned by the bare `name:` in their own
frontmatter*, with no namespace: `subagent_type: "skeptic"`,
`subagent_type: "steward"`, and `subagent_type: "general-purpose"` for the
inline-briefed implementers, which have no definition file at all. That is the
convention every example in this repo follows; if your runtime lists plugin
agents under some other id, use the one it lists.

**The spawn rule (load-bearing).** This framework enforces one-level-deep
spawning as a *design choice*, not as a runtime constraint, and it is upheld by
what this repo **withholds**, not by what it grants. The spawnable agent
definitions, [`agents/skeptic.md`](agents/skeptic.md) and
[`agents/steward.md`](agents/steward.md), carry `tools:` frontmatter with no
spawn tool in it, so a skeptic or steward cannot start a second tier. The
manager's own ability to spawn comes from being the **top-level session**, not
from any grant this repo issues: nothing here loads
[`agents/manager.md`](agents/manager.md) (you adopt that role yourself, you
never spawn it), so the `Task` in its `tools:` line describes the role and
confers nothing. A runtime *may* hand a subagent its own spawn tool; this
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
mostly doctrine: substantially more lines of prose than of Python, and the one
structural gate carries more lines of test than of implementation.
Those proportions are visible in the file sizes, and they move whenever the
repo does, so count them yourself rather than trusting a number written here.
Neither the authorship nor the ratio is a reason to discount the ideas or to
inflate them.

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
4. **The fluff gate (blocker adjudication).** An adversarial panel earns its
   keep by finding real defects, and it pays for that by also producing
   taste, scope creep, and triggerless hypotheticals dressed as blockers. So
   a BLOCKING tag does not gate work by itself: after a panel returns NOT
   PLEASED, the manager adjudicates every BLOCKING finding REAL or FLUFF
   against an explicit yardstick before any fix round is dispatched
   ([`skills/consolidating-review/SKILL.md`](skills/consolidating-review/SKILL.md)).
   Real defects gate; fluff is demoted with a written reason the original
   reviewer gets exactly one structured round to rebut — concede, or stand
   with new evidence. No silent demotions, no endless ping-pong, and the
   adjudication record is a required artifact, so a manager that bulldozes
   real findings does it in writing, where the steward and the owner can
   read it.
5. **The reliability / stall rules.** Silence ≠ progress; watch file
   activity, not completion notifications; concrete re-briefs for stalled
   agents; integrate the slices, run one panel over the integrated tree, and
   land the batch in **one** commit (the review artifact binds to a single
   HEAD, and the framework's own rule is to review the integrated tree rather
   than half-written slices).
6. **Doc-collision avoidance.** Reserved index files, pre-assigned doc
   numbers, and a fill-before-you-fan-out conflict checklist.
7. Swarm vs. deep review modes with a dual-placement selection rule.
8. **The steward.** A standing, read-only adversarial flat sibling the
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
discussed at the end of this section.

### 2. Vendoring: the frozen-snapshot escape hatch

A project that cannot install plugins copies these paths into its own tree,
keeping their names and their positions relative to one another:

```
.claude-plugin/ agents/ skills/ commands/ hooks/ scripts/ docs/ test/ README.md LICENSE
```

They go at the **plugin root** of the copy. **Use a subdirectory**, something
like `vendor/delegation-framework/`, and point the plugin loader at it. Copying
to your project root overwrites your own `README.md` with this one, and nothing
will warn you. The layout inside that directory has to be preserved: every cross-file link in this tree is relative, and every hook
command resolves its script through `${CLAUDE_PLUGIN_ROOT}/scripts/...`.

Two entries in that list are easy to drop and are not optional.
`.claude-plugin/` carries the manifest; without it the copy is a pile of
markdown, not an installable plugin. `README.md` is the canonical text of the
commit gate's five honest limits, and seven files in the other directories link
to it by relative path, so a copy without it ships seven broken links. `test/`
is there because this README tells you to run the suite before trusting the
gate, and a copy without it cannot. Run
`python3 scripts/validate-structure.py <your-copy-root>` after vendoring: it
checks the manifest, the frontmatter, the hook script paths, the required docs,
and every relative link, so a wrong list fails there rather than in a session.

Record the vendored upstream commit in your project's own README. A vendored
copy is a frozen snapshot by nature; it drifts the moment either side changes.
So the update story is explicit and minimal:

1. `git fetch` the upstream repo.
2. `git diff <vendored-commit>..<target-tag> -- .claude-plugin/ agents/ skills/ commands/ hooks/ scripts/ docs/ test/ README.md LICENSE`
3. Re-apply the diff to your copy.
4. Re-run `python3 scripts/validate-structure.py <your-copy-root>`.
5. Record the new commit in your README.

Vendored copies do **not** stay current on their own.

**On marketplace distribution (not an install path).** Publishing to a
personal/org marketplace, so that a `v1.1` to `v1.2` bump propagates to every
consumer that upgrades, is the *intended* fast-follow, not a settled fact and
not something you can do today. Cross-consumer propagation is conditional on
marketplace tooling that is not yet in place; until it lands, upgrades are
per-consumer (re-install or re-vendor). We do not state one-shot propagation as
a current capability.

## When not to delegate, and how to un-arm a repo

**The trivial-edit gate.** Do not run this loop on a trivial edit or a
single-file fix. The overhead is not worth it, and `/delegate` states the gate
up front and stops rather than decomposing anything. The loop is for
substantial, multi-part builds where independent review adds real safety: a
feature batch, a hardening pass, a migration. Over-processing a cosmetic change
is a real failure mode here, not a safe default, and the steward flags it.

**Un-arming a repo.** The opt-in persists: once `/delegate` has run,
`.delegation/` stays on disk, and every later commit in that repo needs a
current all-PLEASED artifact, trivial edits included. That is deliberate, but it
is reversible at any time by removing the marker:

```
rm -rf .delegation                       # un-arm
mv .delegation .delegation.off           # or set it aside, keeping the history
```

The commit gate and both reminder hooks go silent in that repo immediately. The
marker holds no state the framework needs later, so re-arming is just running
the loop again (or `mv .delegation.off .delegation`). If you want to keep the
archived artifacts in `.delegation/history/` as a record, move them somewhere
outside the repo root before deleting, or use the second form. (Committing that
archive is allowed and does not disarm your gate, but every clone then gets a
`.delegation/` directory and an armed gate: see the second residual under
[Enforcement, honestly](#enforcement-honestly-one-structural-slice-the-rest-is-discipline).)

**If the marker is one you inherited** (HEAD carries it, so the gate is already
standing down and warning), there is nothing to un-arm: it is already off. You
have two choices, and they go in opposite directions.

To make the warning stop and leave enforcement off, delete the directory:
`rm -rf .delegation`. Run `git status` first. Those files may be tracked, in
which case you are deleting somebody's committed archive, and the deletion
commit is itself ungated so nothing will stop you.

To turn enforcement **on** for yourself, claim the marker:
`git rm -r --cached .delegation`, add `.delegation/` to `.gitignore`, and commit
that removal. Until it is committed the marker still counts as inherited, which
is exactly what makes that commit ungated. Be clear that this arms the gate. It
is not a way to quieten it.

## Dependencies

None. This repo is standalone: everything it needs to run is in this tree.
There is no companion plugin to install, no skill invoked by name from
somewhere else, and no version to pin. The manifest
([`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)) declares no
`dependencies`.

One *soft* seam exists, by name only: the sibling planning-framework's
planner session, when it finishes planning, CREATES this manager session on
Opus and hands it the plan as its opening prompt — it does not shed its role
into `/delegate`, and it stays alive, session-to-session, for the seam's
duration. When the seam is live, the `delegating` skill's plan intake and
planner relay apply — the plan's leaf cards arrive as briefs-in-waiting, and
questions about plan content go back to the planner session rather than
being decided by manager fiat. Nothing loads, resolves, or validates that
sibling; if it is absent, nothing here references it at runtime and nothing
fails. Standalone stays true, and the planner-as-front-door inversion is
scoped to the seam being live, not a rewrite of the standalone story above.

The one external requirement is an interpreter: the hook commands are portable
Python 3.7+, and each one tries `python3`, then `python`, then `py -3`, then
gives up quietly. One of those three has to answer for the commit gate and the
reminder hooks to run at all (see limit 1 below). The fallbacks are why Windows
works: the python.org installer ships `python.exe` and no `python3.exe`.

## Enforcement, honestly: one structural slice, the rest is discipline

Most of this framework is organized discipline plus reminders. Exactly
one slice is structural:

**The commit gate.** The review panel produces a **review artifact**: a file
at `.delegation/review-artifact.json` in the consumer repo recording the
deliverable reviewed, the mode (swarm / deep / hybrid), each lens's verdict,
and the consolidated BLOCKING list (format:
[`skills/skeptical-review/SKILL.md`](skills/skeptical-review/SKILL.md)). A
PreToolUse hook on the git subcommands that introduce *newly authored* work
(`commit`, `cherry-pick`, `revert`, `am`)
([`scripts/commit-gate.py`](scripts/commit-gate.py)) denies the command
unless a well-formed, all-PLEASED artifact **bound to the current HEAD**
exists. No command carrying `--abort`, `--skip`, `--quit` or `--dry-run` is
ever gated, wherever on the line the flag sits, as long as it sits outside
quotes: none of them can create a commit and `git rebase --abort` has to work
mid-conflict above all. (A flag *named inside a commit message*,
`git commit -m "fix --abort handling"`, does not waive anything.) `--continue`
is gated on the four subcommands above, because it writes the commit the
conflicted operation stopped short of, and so is `--amend` (below). The gate
acts **only in repos that have opted in** by having a `.delegation/` directory
at the repo root **that the HEAD commit does not carry** (the `delegating`
skill / `/delegate` creates it when a loop starts; it is also the natural home
of the artifact and checklist). Command matching is
anchored on command *position*, not on quoting. Prose inside a running
command (`echo please run git commit later`, `grep 'git commit' docs/`) does
not trigger it. But a command separator inside quotes is still a separator
(`echo "step1; git commit -m msg"`), and a heredoc line starting at column 0
with `git commit` still matches. Both over-matches are deliberate and pinned
by tests: parsing quoting and heredocs means writing a shell, and every bug
in that shell would fail open. Within its reach, skipping review takes
a *visible act* (deleting or faking an artifact, or removing the marker)
rather than merely forgetting a rule.

**When the marker counts as an opt-in.** Only when the HEAD commit does not
carry it. The gate reads the HEAD commit tree, never the index. Three readings,
across six states:

| What HEAD's tree holds at `.delegation` | Reading | Gate |
|---|---|---|
| A file directly inside `.delegation/`, or a submodule, or a symlink | inherited: it arrived with the repository | **off**, and it warns |
| `.delegation/` holding only subdirectories, such as `history/` | local: an archive is not the marker | **on** |
| No `.delegation` entry at all, or a plain file of that name | local: someone here created it | **on** |
| No refs anywhere, so no history at all (fresh `git init`) | local: nothing can have arrived in a commit that does not exist | **on** |
| Refs exist but HEAD does not resolve (orphan branch, garbled HEAD) | unknown provenance | **off**, and it warns |
| HEAD resolves but its objects cannot be read, fail their hash, or come from a pack entry whose declared size does not match its stream | unknown provenance | **off**, and it warns |
| The marker is not inside a git repo at all | nothing to bind an artifact to | **off**, and it warns |

Alternates are followed transitively, so chained `--shared` or `--reference`
clones read correctly, capped at 64 object directories so a circular chain
terminates.

`git add .delegation` changes none of this: staging is a local act, so a staged
marker leaves the gate **on**. But the *next* commit would carry the marker into
HEAD and stand the gate down for you and every clone, so a staged marker now
draws a warning on allow as well as a line on deny. That is the one case where
the gate speaks while letting a commit through, and it exists because the
silence was the whole danger: the commit that disarms this thing used to be the
one commit it had nothing to say about.

Warnings repeat on every gated command by decision, not by oversight. A hook is
a one-shot process, so saying it once would take a state file that outlives the
session it describes, and a stale "already told you" file would suppress the
only signal that the gate is not enforcing.

**Claiming an inherited marker as your own opt-in.** Read the heading twice
before you run this, because it is the opposite of switching the gate off. An
inherited marker means the gate is already standing down, so there is nothing
to un-arm; what follows turns enforcement **on** for you.

```
git rm -r --cached .delegation      # stop tracking it
echo ".delegation/" >> .gitignore   # keep it local from now on
git commit -m "keep .delegation local"
```

The first two steps alone change nothing, because the marker counts as
inherited for exactly as long as HEAD carries it. That is also what makes this
commit itself ungated, so there is no deadlock where you need a panel to escape
a gate that is not enforcing. If what you actually wanted was to stop the
warnings without arming anything, delete the directory instead: `rm -rf
.delegation`, and check `git status` first in case someone committed an archive
you would be deleting from under them.

**One panel, one commit.** Because the artifact is bound to HEAD, it waives
exactly one commit and is spent the moment that commit lands. So the loop is:
integrate every slice, run one panel over the integrated tree, then make one
commit. That is also what the framework already asked for on its own terms,
which is to review the integrated tree rather than half-written slices. The
reliability point behind the older "commit each slice as it lands" advice is
real and survives intact: do not let a large pile of unreviewed work accumulate
in the tree. The way to honour it now is to keep the *batch* small (fewer
slices per panel, panels more often), not to sneak individual slices past the
gate in separate commits.

**What is deliberately not gated.** `pull`, `merge` and `rebase` are not gated.
They move or replay commits that were already gated when they were authored, so
gating them again would demand a fresh panel for work that already carried one,
and would deny routine integration in every armed repo. Neither are `reset`,
`restore`, `push`, `add`, or anything read-only: none of them authors a commit,
and gating things that author no commit is the over-reach that denying
`git rebase --abort` taught us not to repeat. The residual, stated
plainly: landing a branch with `git merge --no-ff` creates a merge commit that
no review artifact covers. Review happened at the commits *inside* the branch,
not at the merge. If those commits were authored somewhere this gate does not
reach (limits 1, 3 and 4 below), nothing on the merge path re-checks them.

**`--amend` is gated**, and it is the one that costs an honest user something:
amending a typo in the message of a commit you *just* landed needs a fresh
artifact, because HEAD moved when that commit landed. It stays gated because an
amend writes a **new commit whose content is whatever is staged**, so allowing
it would make `git add unreviewed.py && git commit --amend --no-edit` a laundry
route for unreviewed work through an artifact that was already spent. Telling a
message-only amend from a content amend means diffing the index against the HEAD
tree on every command, and *forgetting what got included* is the exact failure
this gate exists to wall off. The honest price of the typo is re-pointing
`head_sha` at the new HEAD.

**Two residuals worth naming.** First: `git reset --soft HEAD~1` is not gated,
and it moves HEAD back, which makes a spent artifact fresh again. One artifact
can therefore waive more than one commit that way. This is deliberate. The only
way to spend an artifact is to make the commit it authorised, so the re-arm
returns exactly what was just used and nothing more, and closing it would
mean gating `reset`, which authors no commit. It is strictly weaker than the
`bash -c "git commit"` bypass in limit 4, which is already documented.
Second: a committed `.delegation/history/` deliberately does **not** disarm
your gate (an archive of spent artifacts is an audit trail, the opposite intent
of committing the marker), but checking it out materializes a `.delegation/`
directory in every clone, and by the same rule that directory reads as local
there. So a cloner who has this plugin installed is **gated** in a repo they
never opted into. Accepted trade, and the escape is the ordinary one: delete
`.delegation/`, or keep the archive outside the repo. Note the sharp edge on
that escape, which the deny message now warns about: if the archive is tracked,
deleting the directory deletes somebody's committed files, and the deletion
commit is itself ungated, so nothing stops you.

Third: an orphan branch or a garbled HEAD stands the gate **down** in a repo
whose owner armed it. `git checkout --orphan` leaves HEAD pointing at a ref that
does not exist, so provenance becomes unknowable, and unknowable resolves to
standing down rather than enforcing. That direction is deliberate: at this
decision, guessing wrong toward enforcement blocks a contributor who never
opted into anything, and guessing wrong toward standing down costs one
unreviewed commit. The gate returns on its own once HEAD resolves again.

**A cost, not a limit.** The hooks add roughly 44ms to **every** `Bash` and
`PowerShell` tool call, not only gated ones, because the matcher fires on all of
them and the script's imports run before the command is inspected. About 30ms of
that is Python interpreter startup plus stdlib imports; the provenance read
itself is about 0.36ms and stays flat on repositories with millions of objects.
That is the price of the gate being a hook rather than a git hook, and you pay
it on `ls` as well as on `git commit`.

**Its five honest limits:**

1. It fires only where this plugin's hooks are installed and enabled in
   the environment running the committing agent, and only if a Python 3.7+
   interpreter answers to one of `python3`, `python` or `py -3`. Each hook
   command tries those three in order and then exits quietly; the fallbacks are
   what make Windows work, since the python.org installer ships `python.exe`
   and no `python3.exe`. With none of the three on PATH the gate silently
   vanishes. A different environment, or hooks disabled, means no gate.
2. It verifies the artifact exists and is well-formed (a non-empty
   `deliverable` saying what was reviewed, a valid `mode`, a non-empty
   `reviews` array, **a non-empty `lens` on every review**), that every
   `verdict` is exactly `PLEASED` with every `blocking` list empty **and
   `consolidated_blocking` empty**, and that it is bound to the commit it was
   reviewed against (`head_sha` must match current HEAD, so one artifact waives
   exactly one commit). It does
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
   commit aimed at a different, ungated repo (fail closed, see limit 5). It
   does not do that silently: the deny carries a line naming the repo the gate
   scoped itself to and saying the command's own target could not be resolved.
   Matcher evasion is a bad-faith route rather than
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

**What a deny actually looks like.** Nine lines, with real line breaks, in this
order: the headline, the specific problem, why this repo is gated at all, then
the three escape hatches above in priority order, with the artifact schema
printed **alone on its own line** so it can be selected and pasted without
re-typing. One extra line appears when `.delegation/` is staged but not
committed, saying so and giving `git restore --staged .delegation`; one more
appears when the gate had to fall back to the hook's own repo (limit 4). No
value read out of the artifact is ever echoed back into that message: findings
are reported positionally ("review #2 ..."), because hook output reaches the
model as privileged text and a cloned repo could otherwise speak through it.

Everything else (the always-pair-a-skeptic breadth, the reliability rules,
panel sizing) is skill guidance plus **reminder hooks**, which nudge and
never structurally enforce: a SubagentStop nudge ("attach a skeptic") and a
Stop nudge (uncommitted work with no all-PLEASED artifact at session stop),
both scoped by the same `.delegation/` opt-in marker, read through the same
HEAD-tree provenance rule, so they stay silent in unrelated repos and in repos
whose marker merely arrived with the clone. The Stop nudge asks the gate itself
whether the artifact would pass, rather than keeping a second opinion about it.
A hook cannot know an off-tree research deliverable went unreviewed.

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
agents/manager.md              the manager ROLE DEFINITION: read it and be the manager in your own top-level session; never spawn it as a subagent (nothing in this repo loads it)
agents/skeptic.md              the reusable adversarial reviewer of deliverables (spawnable)
agents/steward.md              the reusable adversarial reviewer of the MANAGER, a flat sibling the manager spawns (spawnable, standing)
skills/delegating/             the manager's loop: mechanics, the rules on top of them, the commit gate
skills/skeptical-review/       run a panel; lenses; swarm/deep/hybrid modes
skills/consolidating-review/   adjudicate BLOCKING findings (the fluff gate);
                               batch the survivors; drive convergence
commands/                      /delegate, /skeptic-review, /review-panel
hooks/hooks.json               reminder hooks; the commit gate
scripts/                       gate + validation scripts (portable Python)
docs/                          skill-referenced data (NOT auto-loaded):
                               operating-model, roles, lenses, rubric,
                               conflict-avoidance checklist, worked example,
                               compact standard
```

`docs/` and the rubric files are skill-referenced data: a skill points
at them by relative path and reads them on demand. They are not auto-loaded
plugin surfaces.

## Validation

Two mechanical checks and a test suite. The three are not the same kind of
thing, and only two of them do anything on a fresh clone:

```
python3 -m unittest discover test         # the commit gate, exercised
python3 scripts/validate-structure.py     # manifest, frontmatter, hooks, links
python3 scripts/check-domain-neutral.py   # denylist grep: no source-domain vocabulary
```

**The test suite is the only one that exercises behaviour.** It covers the
commit gate, which is the one structural slice: what it gates and what it
deliberately does not, repo resolution through `cd` chains and `git -C`, the
artifact-to-HEAD binding, malformed and hostile artifacts, the three marker
provenance states read from the HEAD tree, and that a repo which never opted in
stays silent. If you are deciding
whether to trust this thing, run that first. It needs no network, no fixtures
you have to build, and no `git` binary.

**`validate-structure.py` must be green**, here and on any vendored copy. It
checks the manifest, the frontmatter on every skill / agent / command, that
every script a hook references exists, that the required skill-referenced docs
are present, and that every relative markdown link in the tree resolves. It is
self-contained: it either passes or names exactly what is missing.

**`check-domain-neutral.py` checks nothing until you give it a list, and it
says so.** The denylist is deliberately not in this repository, because a
committed list of the words you scrubbed is itself the disclosure. The script
reads an untracked `.domain-tokens` file at the repo root (one term per line)
or the `DOMAIN_TOKENS` environment variable. With neither present, which is the
state of a fresh clone, it prints `DOMAIN-NEUTRALITY GATE: INERT (no token list
configured)` and exits 0 having checked nothing. That exit code is not a pass,
and the script refuses to describe it as one. A consumer that wants this check
supplies its own list:

```
printf 'acme\nwidgetco\ninternal_codename\n' > .domain-tokens
```

and keeps it gitignored. Even with a list loaded, the grep catches literal
token leaks only; domain-shaped *assumptions* phrased in none of the listed
words are policed by adversarial review, not by this script. Two distinct
mechanisms, not one.

Note: the design spec named the gate/check scripts as shell scripts (`.sh`);
they ship as portable Python (`.py`) so the same scripts run on Windows
and POSIX, a deliberate and flagged divergence with identical contracts. The
hook commands therefore require a Python 3.7+ interpreter, which they look for
as `python3`, then `python`, then `py -3` (limit 1 above).

## What green does NOT buy you

- Passing validation proves the machinery runs, not that any delegation
  was well-judged. Manager judgment remains human-owned.
- The commit gate is a wall against **forgetting** a review, not against a
  **fabricated** one, and only where hooks are installed and enabled, only
  in repos carrying the `.delegation/` opt-in marker, and with the residuals
  of limits 4 and 5 (unparsed paths now fall back and over-gate rather than
  mis-resolve silently; rare false positives).
- The published git history is short, and it is not a project record. This
  repo was rebuilt from a clean tree for public release rather than published
  in place, so neither the number of commits nor their timestamps say anything
  about how long the work took or how it evolved. Do not read the log as a
  timeline.
- Reminder hooks and the skeptic-pairing breadth are discipline, not
  structure: they reduce, but do not eliminate, the chance an off-tree
  deliverable ships unreviewed.
