# delegation-framework

**Playbook, roles, and adversarial review machinery for a manager →
implementer → skeptic operating model, packaged as a Claude Code plugin.**

## Quickstart

```
/delegate add a CSV export endpoint to the reports service, with tests and a docs update
```

You become the manager: fresh implementers build scoped slices, a skeptic panel
reviews the integrated result, fix rounds run to convergence, and only then do
you commit.

- `PLEASED` / `NOT PLEASED`: a skeptic's only verdicts, none "with
  reservations"; all must be `PLEASED` before the commit
  ([rubric](docs/rubric.md)).
- `BLOCKING`: a numbered must-fix finding; nothing else gates. The fluff gate
  ([consolidating-review](skills/consolidating-review/SKILL.md)) keeps real
  defects and demotes fluff on the record after one rebuttal round.
- `swarm`, `deep`, `hybrid`: panel modes (many skimming, a few tracing deeply,
  or both), one per panel, recorded in the artifact.
- `lens`: one skeptic's adversarial angle; a panel diversifies them
  ([catalogue](docs/lenses.md)).

> ⚠️ **`/delegate` arms the repo:** it creates `.delegation/`, the opt-in
> marker, and from then on every commit, typo fixes included, needs an
> all-PLEASED review artifact
> ([enforcement](#enforcement-honestly-one-structural-slice-the-rest-is-discipline)).
> **Add `.delegation/` to `.gitignore` before committing anything:** `git add .`
> would sweep it in, and a marker the HEAD commit carries turns the gate OFF
> for you and every clone. To switch off:
> [un-arming](#when-not-to-delegate-and-how-to-un-arm-a-repo).

**Check the gate is live:** a broken install fails silently, since a hook that
cannot run must not block commits. In a repo you do not mind dirtying:

```
mkdir -p .delegation
grep -qxF '.delegation/' .gitignore 2>/dev/null || echo '.delegation/' >> .gitignore
git commit --allow-empty -m "gate check"
```

A deny printing the artifact schema means armed; silence, the hooks are not
running, whatever the install said; a warning, the marker is no opt-in (HEAD
carries it, or no git repo). Remove `.delegation/` afterwards.

**Read before your first `/delegate`:**
[`docs/example-run.md`](docs/example-run.md), one delegation end to end plus
two steward scorecards.

## Who this is for (read this before you install)

Flat-subscription accounts, a load-bearing assumption: where a seven-skeptic
panel costs what a two-skeptic one does, defaults maximise catches (panels of 5
to 7, dissenters re-reviewed, a standing steward). **Billed per token, that
costs real money:** scale panels down
([sizing](skills/skeptical-review/SKILL.md#panel-setup)) but keep the
always-pair-a-skeptic floor; the cost call is yours.

The owner-set **model ladder** (2026-09-02) is firm: the manager runs on Opus;
below it, tier is judgment recorded in the brief, never gated; a growing job
gets more agents, never a bigger one; panels stay large
([ladder](skills/delegating/SKILL.md#the-model-ladder-who-runs-on-what)).
Standing cost per project: an idle planner and an Opus manager session for the
run (the planner idles between turns, never polling), plus an idle Sonnet
watchdog and one hourly Routine firing, the platform floor
([watchdog](agents/manager.md#the-watchdog-a-third-seat-standing)).

## The roles at a glance (so any agent knows what they are)

The owner talks only to the **manager**
([`agents/manager.md`](agents/manager.md)), the single top-level orchestrator
and only spawner: it decomposes, spawns implementers and skeptics as flat
siblings one level deep, runs the panel, integrates and commits
([`docs/roles.md`](docs/roles.md)). **Never spawn the manager:** `/delegate`
makes your own top-level session adopt it
([how](agents/manager.md#how-to-use-this-file-do-not-spawn-it)). Implementers
build one slice each and skeptics ([`agents/skeptic.md`](agents/skeptic.md))
review every deliverable; neither can spawn, so a worker needing help asks the
manager. The manager also spawns the **steward**
([`agents/steward.md`](agents/steward.md)) to review itself, consulting it at
execution checkpoints by standing rule so the owner is never the reminder
([auto-consult](agents/manager.md#auto-consult-a-standing-binding-rule)).

The one-level rule holds only while the skeptic and steward `tools:` grant no
spawn tool (`Task`). Parallel deep teams are separate sessions with their own
managers, coordinated by the owner
([topology](agents/manager.md#the-spawn-topology-the-load-bearing-rule-of-this-framework)).

## What it owns

The loop ([`skills/delegating/SKILL.md`](skills/delegating/SKILL.md),
[`docs/operating-model.md`](docs/operating-model.md)): one scoped task per
fresh subagent, fan-out by disjoint write sets, test-first, evidence before
claims. `docs/` is read on demand, not auto-loaded. Claims are capabilities,
not guarantees: decomposition quality, whether a finding truly blocks, and the
commit go/no-go stay human (or the manager's).

## Install

### 1. Git-installable (the default, precedented path)

```
/plugin marketplace add louellet-git/delegation-framework-public
/plugin install delegation-framework@delegation-framework-source
```

[`marketplace.json`](.claude-plugin/marketplace.json) only enables this git
install; it is not a shared marketplace.

### 2. Vendoring: the frozen-snapshot escape hatch

Copy every path below, layout intact, into a subdirectory such as
`vendor/delegation-framework/` (at your root it silently overwrites your
`README.md`) and point the plugin loader there:

```
.claude-plugin/ agents/ skills/ commands/ hooks/ scripts/ docs/ test/ README.md LICENSE
```

Drop none: links are relative, hooks resolve
`${CLAUDE_PLUGIN_ROOT}/scripts/...`, other files cite `README.md`, and
`.claude-plugin/` and `test/` are the manifest and the suite. Check with
`python3 scripts/validate-structure.py <your-copy-root>`. A hand-vendored copy is
frozen: record its upstream commit in your README; to update it:

1. `git fetch` the upstream repo.
2. `git diff <vendored-commit>..<target-tag> -- .claude-plugin/ agents/ skills/ commands/ hooks/ scripts/ docs/ test/ README.md LICENSE`
3. Re-apply the diff to your copy.
4. Re-run `python3 scripts/validate-structure.py <your-copy-root>`.
5. Record the new commit in your README.

Marketplace propagation of version bumps is planned, not available: upgrades
are per consumer.

An installer-managed copy ([section 3](#3-project-vendored-cloud-sessions)) is
instead updated by re-running the installer from a newer clone.

### 3. Project-vendored (cloud sessions)

The owner's cloud sessions (observed 2026-10-25) do not run `/plugin install`.
From a clone of this repo, not a vendored copy, run:

```
python3 scripts/install-into.py /path/to/your/repo
```

It writes a [vendored](#2-vendoring-the-frozen-snapshot-escape-hatch) copy
under `vendor/delegation-framework/` with `INSTALL.json`, `skeptic`, `steward`,
the skills and the commands under `.claude/`, the hooks merged into
`.claude/settings.json`, and a `.delegation/` line in `.gitignore`. It refuses,
before writing anything, a file it wrote and you changed (delete it to accept
the new version) or a file or symlink it did not write (move or rename it). Commit the result.

It wires the commit gate but does not arm it; when the gate enforces is under
[Enforcement, honestly](#enforcement-honestly-one-structural-slice-the-rest-is-discipline).
Whether cloud sessions load the installed files is unverified.

## When not to delegate, and how to un-arm a repo

Skip the loop for a trivial edit or a single-file fix; `/delegate` says so and
stops. To un-arm, **run `git status` first**: if `.delegation/` holds tracked
files, removing it deletes a committed archive, in an ungated commit.

```
rm -rf .delegation                       # un-arm
mv .delegation .delegation.off           # or set it aside, keeping the history
```

The gate and both reminder hooks fall silent at once; re-arm by running the
loop or moving it back. An inherited marker is already off: delete it to
silence the warning.

## Dependencies

None: [`plugin.json`](.claude-plugin/plugin.json) declares no `dependencies`,
and no companion plugin or outside skill is needed. A soft seam exists by name
only: a sibling planning-framework planner may create this manager session
with a plan, and then
[plan intake](skills/delegating/SKILL.md#decompose-the-procedure) and the
[planner relay](skills/delegating/SKILL.md#the-planner-relay-questions-go-back-up-the-seam)
apply; nothing loads the sibling, and its absence fails nothing. The one
external requirement is Python 3.7+ (limit 1).

## Enforcement, honestly: one structural slice, the rest is discipline

The structural slice is **the commit gate**, a PreToolUse hook
([`scripts/commit-gate.py`](scripts/commit-gate.py)). It denies `git commit`,
`cherry-pick`, `revert` and `am`, `--continue` and `--amend` included, unless
`.delegation/review-artifact.json`
([format](skills/skeptical-review/SKILL.md)) is all-PLEASED and bound to the
current HEAD: one panel per commit. A command with `--abort`, `--skip`,
`--quit` or `--dry-run` outside quotes is never gated. Matching is anchored on
command position, so prose mentioning `git commit` passes.

**When the marker counts as an opt-in:** at the repo root, when the HEAD commit
does not carry it. The gate reads HEAD's tree, never the index:

| HEAD's tree at `.delegation` | Reading | Gate |
|---|---|---|
| A file directly inside, a submodule or a symlink | inherited | off, warns |
| Nothing, a plain file or only subdirectories (`history/`); or no refs yet (fresh `git init`) | local | **on** |
| HEAD unresolved (orphan branch, garbled HEAD), or its objects unreadable or unverifiable | unknown | off, warns |
| The marker is outside any git repo | nothing to bind to | off, warns |

A staged marker leaves the gate on but draws a warning even on allow, since
committing it would stand the gate down. Warnings repeat on every gated
command, by design: fix the cause.

**Claiming an inherited marker as your own opt-in** arms the gate (it does not
quiet it); the commit is ungated, since HEAD carries the marker until it lands:

```
git rm -r --cached .delegation      # stop tracking it
echo ".delegation/" >> .gitignore   # keep it local from now on
git commit -m "keep .delegation local"
```

**Not gated:** `pull`, `merge` and `rebase` (they replay commits gated when
authored); `reset`, `restore`, `push`, `add` and read-only commands (no
commit). **Residuals:** a `git merge --no-ff` merge commit has no artifact, and
branch commits made beyond the gate's reach (limits 1, 3, 4) are never
re-checked. `git reset --soft HEAD~1` re-freshens a spent artifact, so one
artifact can waive more than one commit; that stays open on purpose, as closing
it means gating `reset`, which authors no commit, and limit 4's `bash -c`
bypass is wider. A committed `.delegation/history/` does not disarm you but
gates every clone that has the plugin; accepted (keep the archive outside the
repo).

**Cost:** about 44ms on every `Bash` and `PowerShell` call, gated or not, 30ms
of it Python startup; the provenance read is about 0.36ms.

**Its five honest limits:**

1. It fires only where this plugin's hooks are installed and enabled for the
   committing agent and a Python 3.7+ answers to `python3`, `python` or
   `py -3`, tried in order (the fallbacks serve Windows, which ships no
   `python3.exe`); otherwise the gate silently vanishes.
2. It checks the artifact's form (non-empty `deliverable`, `reviews` and each
   review's `lens`; a valid `mode`), that every `verdict` is exactly `PLEASED`
   with every `blocking` list and `consolidated_blocking` empty, and that
   `head_sha` is the current HEAD. It cannot check rigor: a determined agent can
   fabricate an artifact. Skipping review takes that visible act, or removing
   the marker; the gate walls off forgetting, not bad faith.
3. It gates the local commit (the manager commits); agents that never touch
   this working tree are beyond it.
4. It sees only commits made through tool calls the PreToolUse matcher sees, as
   it parses them: a `git` alias, `bash -c "git commit"` or an IDE commit
   bypasses it (bad faith, but possible). A target repo it cannot resolve (say,
   via variables) falls back to the hook's own repo, gated there; the deny
   names that repo.
5. **Over-reach (the flip side).** Hooks are session-global, so the gate runs in
   every repo the session touches; the marker (none: silent allow) and anchored
   matching scope it, but a compound command, a quoted separator, a heredoc or
   the limit-4 fallback can deny wrongly. Escape hatches, in order: write the
   review artifact; remove `.delegation/`; disable the hook.

Everything else is discipline: skill guidance plus two reminder hooks,
SubagentStop ("attach a skeptic") and Stop (uncommitted work, no all-PLEASED
artifact), that nudge, never block. No hook can tell an off-tree research
deliverable went unreviewed.

## The do-not-modify rule — what it does and does not mean

One operating rule governs agents that run *under* this framework:

> **An agent pointed at this framework does not modify it.** It reads it, applies
> it, and operates by it. Changes require the owner's explicit authorization.
> There is no exception for "it would be an improvement," for a reviewer
> suggesting it, or for a run that seemed to need it. An agent's job is to operate
> by the rules, not to rewrite the rules it runs on. If an agent believes a change
> is warranted, it surfaces the change to the owner and stops.

**It does not bind you:** the code is MIT-licensed and "the owner" is you. The
rule exists because an agent able to rewrite its rules will rewrite an
inconvenient one mid-run and report success; only the instruction enforces it
([who authorizes what](docs/roles.md)).

## Validation

```
python3 -m unittest discover test
python3 scripts/validate-structure.py
python3 scripts/check-domain-neutral.py
```

Only the tests exercise behaviour: run them before trusting the gate (no
network, fixtures or `git` binary needed). The validator must be green, here
and on any vendored copy. The domain check is inert, its exit 0 no pass, until
you supply an untracked `.domain-tokens` list, one term per line:

```
printf 'acme\nwidgetco\ninternal_codename\n' > .domain-tokens
```

## The git history

Rebuilt from a clean tree for release: do not read the log as a timeline.
