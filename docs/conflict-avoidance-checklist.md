# Conflict-avoidance checklist: fill BEFORE you fan out

Parallel agents that write the same files clobber each other. This checklist
is a **forced artifact**: the `delegating` skill requires the manager to copy
this template into the working repo (suggested path:
`.delegation/conflict-checklist.md`), fill in every line, and only then
dispatch agents in parallel. An unfilled or partially filled checklist means
serialize instead.

(Creating the `.delegation/` directory for this copy is also what **opts the
repo in** to the commit gate and reminder hooks, the marker they check
before acting. Add `.delegation/` to that repo's `.gitignore` in the same
step. A committed marker arrives in every clone and blocks contributors who
never opted in, and a committed all-PLEASED artifact would waive review for
all of them.)

Rationale and the hard-won rules behind each item:
[`operating-model.md`](operating-model.md#conflict-avoidance-hard-won).

## The checklist (copy from here down)

```markdown
# Conflict-avoidance checklist — <task name> — <date>

- [ ] **Disjoint directories.** The per-agent write sets are listed below and
      are pairwise disjoint. Any two agents whose sets overlap are
      re-planned to run sequentially.
- [ ] **Reserved index files.** Shared index/routing files (ADR index,
      front-door docs, capability maps) are listed below, reserved to the
      manager, and every agent brief forbids touching them.
- [ ] **Pre-assigned numbers.** ADR / doc numbers each agent will create are
      assigned below, so parallel agents cannot collide on the same number.
- [ ] **File-ownership allowlists.** Every agent brief contains an explicit
      allowlist of the files/directories it may create or modify.
- [ ] **Exact test command.** Every agent brief contains the exact test
      command for its slice.

## Per-agent write sets

| Agent | Slice | Allowed paths (allowlist) | Test command |
|-------|-------|---------------------------|--------------|
| 1     |       |                           |              |
| 2     |       |                           |              |

## Reserved to the manager (no agent touches these)

- <index/routing files here>

## Pre-assigned ADR / doc numbers

- Agent 1: <number(s)>
- Agent 2: <number(s)>
```

## Notes

- The checklist is per fan-out, not per project; a new parallel dispatch
  gets a fresh copy.
- "Disjoint" means disjoint write sets; shared read-only inputs are fine.
- If filling the table honestly shows overlap you cannot remove, that is the
  checklist working: run those slices sequentially.
