The delegation-framework plugin is installed, and its disciplines are binding
when they apply.

**Invoke the `delegation-framework:delegating` skill BEFORE dispatching any
agent** for a substantial, multi-part build. Invoke
`delegation-framework:skeptical-review` before trusting any deliverable, and
`delegation-framework:consolidating-review` once a panel has returned findings.
The `/delegate`, `/skeptic-review` and `/review-panel` commands run the same
roles.

**First, the trivial-edit gate, because it fires more often than the loop
does.** Do NOT delegate a trivial edit or a single-file fix — the overhead
exceeds the benefit, so just do it. The loop is for substantial multi-part
builds where independent review adds real safety. An orchestration that spawns
agents for work you could have done directly is the framework failing, not
succeeding.

**Six rules that hold whenever the loop is running:**

1. **Every work agent gets at least one skeptic.** No exceptions. A green
   checkmark, a passing suite and confident prose each prove nothing on their
   own. The skeptic reviews the deliverable against the end goal, not against
   the implementer's account of it.
2. **Spawning is one level deep.** Only the manager holds a spawn tool. Workers
   are flat siblings that coordinate laterally by messaging and ask the manager
   for any helper they need. A genuinely parallel deep team is a separate
   session with its own top-level manager.
3. **Write the end goal as a falsifiable claim before decomposing.** Not a topic
   but a claim whose non-movement could be caught. Every brief quotes it and
   every skeptic scores against it. If you cannot write one, get it from the
   owner before dispatching anything.
4. **Evidence before claims.** A deliverable is not done because an agent says
   it is done. Quote the command and its output. A test that was never run
   against the unfixed code has not been shown to fail, and a test that cannot
   fail is not a test.
5. **A BLOCKING finding gates only after it survives adjudication.** The
   manager runs every one through the fluff gate before any fix round: real
   defects enter it; fluff is demoted with a written reason the original
   reviewer gets exactly one round to rebut, and the adjudication record is
   written either way. No silent demotions.
6. **The commit gate reads the review artifact.** Do not commit on a panel that
   has not converged, and do not resolve a BLOCKING finding by restating it.

Fan out by **disjoint write sets** — two agents that can touch the same file
will conflict, and the conflict surfaces after both have finished. Reserve
shared index files, front-door docs and generated files to the manager.

Scout before cutting slices, and delegate the scouting: reconnaissance is
itself a slice, dispatched read-only, and its report cites the file every fact
came from.
