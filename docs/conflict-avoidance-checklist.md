# Conflict-avoidance checklist: fill BEFORE you fan out

1. Copy the template into `.delegation/conflict-checklist.md`, a fresh copy per fan-out.
2. Fill every line.
3. Dispatch in parallel; an unfilled or partial checklist means serialize.

Write sets, not task independence, decide:
[delegating](../skills/delegating/SKILL.md#fan-out-disjoint-parallel-shared-sequential).

```markdown
# Conflict-avoidance checklist — <task name> — <date>

- [ ] **Write sets** pairwise disjoint (shared read-only inputs aside);
      overlapping agents run sequentially.
- [ ] **Reserved files** (ADR index, front-door docs, capability maps) listed
      below, reserved to the manager, forbidden in every brief.
- [ ] **Numbers** pre-assigned below and written into each brief's
      PRE-ASSIGNED NUMBERS slot; one never transmitted is one the agent picks.
- [ ] **Every brief** has a file-ownership allowlist and the exact test command.

| Agent | Slice | Allowlist | Test command | Numbers |
|-------|-------|-----------|--------------|---------|
| 1     |       |           |              |         |

Reserved to the manager: <index/routing files>
```
