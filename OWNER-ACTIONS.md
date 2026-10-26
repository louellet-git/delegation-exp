---
id: DOC-OWNER-ACTIONS
type: record
item: 9 record
status: current
date: 2026-10-26
scope: Append-only record of branch actions a seat could not perform, with why each is safe for the owner to run.
---

# Owner actions

One row per branch. Run a row's command locally; nothing else is needed.

| Date (UTC) | Repository | Branch | Why the seat could not | Safe because | Command |
|---|---|---|---|---|---|
| 2026-09-03 | delegation-framework-public | claude/planning-delegation-integration-88k9go | a direct-push landing, and the platform cuts `git push --delete` while the classifier denies the REST delete | tip f1ee8f3 is an ancestor of delegation-exp main at de3597f | `git push https://github.com/louellet-git/delegation-framework-public --delete claude/planning-delegation-integration-88k9go` |
