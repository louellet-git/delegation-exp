# Compact work

The framework's standard for compact code, docs, agent instructions and tests: the fewest elements that do the job and still read cold.
It governs the form of what agents write, not how many agents, skeptics or panels a task uses. Citations are tag plus source number: E empirical (arXiv conference papers: E7 ESEM 20, E33 AITest 26, E37 ICLR 26, E39 ICLR 26, E44 NeurIPS 25), G official guidance (vendor docs, style guides), B book, P practitioner (blogs and engineering write-ups).

## Code
- Build only what the current task needs: no speculative features, parameters, hooks or generality; YAGNI does not cover refactoring or tests, which keep code cheap to change. [P1 G2]
- Treat these as YAGNI smells and remove them unless they are a deliberate seam: a base class with one subclass, a flag or parameter that always has one value, a public member that could be private, code only tests run. [P3]
- Prefer duplication to the wrong abstraction [P4]; merge copies that encode the same knowledge [P5]; inline back a helper that has grown parameters and conditionals for its callers [P4].
- Prefer deep modules, a simple interface over real work; do not split code into helpers as complex as their bodies, and re-merge functions that must be read together (a contested design heuristic). [P6]
- Keep functions flat: nesting-weighted complexity tracks comprehension time, mixed for correctness [E7]; trust a complexity metric only once shown to beat plain size, since class-level OO metrics lost their link to faults once size was controlled [E8].
- Use a core language construct, then the standard library, before a new dependency, framework or wrapper layer. [G9]
- Delete unused code, parameters and flags in the same change, after searching for callers. [E10 B11]
- Use the plain form of constructs shown to be misread (increment inside an expression, logic used as control flow, type-conversion tricks), and meaningful names beyond tiny scopes, where `i`, `j`, `k` are fine. [E12 G13]
- Comment the why, the constraint and the non-obvious; never narrate the code; give public, nontrivial or non-obvious functions a docstring. [G13 G14]
- When agents write code, state the contract plainly with its exceptions: no unrequested features, files, docs or refactors, no handling for states that cannot occur, no one-use helpers; tendencies are model-specific, so check on the model in use. [G15 G16]

## Docs
- Omit needless words and sentences: make every word tell. [B17]
- Keep a small set of fresh docs: cut out-of-date, wrong and redundant text; in a cleanup delete what is certainly wrong and skip what is unclear. [G14]
- State each fact once and link to it, since copies drift; inline what a task needs within one hop, since over-splitting fragments docs. [P5 E18]

## Agent-read instructions
- Include only what the agent cannot infer from the repo or already knows; omit overviews the docs already give, file-by-file tours, self-evident advice and LLM-generated context files. [E20 G21 G19]
- Test each line with "would removing this cause a mistake?", judged by the weakest model that reads it. [G21 G19]
- Split loading by purpose: general reference knowledge in a compressed index that is always loaded; triggered action workflows on demand, one level deep, behind an explicit when-to-read trigger. In one vendor eval on Next.js 16 APIs absent from training (n=1), the index passed 100%, skills 79% with explicit instructions and 53% without (never invoked in 56% of cases). [G19 P22]
- Keep a SKILL.md body under 500 lines (a vendor heuristic) and rules that must survive auto-compaction in its first ~5,000 tokens, all Claude Code re-attaches. [G19 G23]
- Remove contradicting and outdated rules: of two that contradict, Claude may pick one arbitrarily. [G25]
- Write rules concrete enough to verify, in plain tone, one term per concept; give a non-obvious rule a one-clause reason, and a format one canonical example. [G25 G15 G19]
- Prune regularly: delete a rule the agent already follows, or turn it into a hook, script or validator with a specific error message; keep prose for judgment and for what to do when a check fails. [G21 G25 G19 E26]
- Move non-actionable background and examples out of the always-loaded body, on demand at most, and time-sensitive text into a collapsed old-patterns section. [E27 G19]
- Write agent and skill descriptions as what it does and when to use it, key use first, no feature lists; test them with should-trigger and should-not-trigger prompts. [G19 G23 E27]

## Tests
- Test behaviour through the public interface with real objects, then fakes, before mocks; a test that fails on a pure refactor is a smell to rewrite; keep implementation-level tests only for a named contract (call count, cache use, byte format). [B28 B29]
- Delete or rewrite change-detector tests, which restate the code (copied logic, call-order mocks); by extension, assert the fragments a reader acts on (path, command, field), not whole messages. [P30]
- Test one behaviour per test, named for it (action and expected outcome), not for a method or a fix ID. [B28]
- Write bodies straight-line by default, with literal inputs and expected outputs rather than loops, branches or computed expectations; never shorten a test by moving cause and effect into shared fixtures, external files or opaque helpers. [B28]
- Use a table or `subTest` only for cases sharing logic and setup; split when a row needs its own branch. [G31]
- Judge a test by whether it fails when behaviour breaks, not by coverage, which only finds untested code; on load-bearing paths, break the code and watch it fail (most agent test patches carry weak or no explicit oracle). [E32 E33]
- Prune only for a stated reason: a duplicate (same killed mutants), a change detector, a test of third-party behaviour, a pin on retired wording; never by count or coverage, since coverage-based cuts lost up to 20.5% of killed mutants and suite size tracks effectiveness. [E34 E32]
- Fix a flaky test at its root cause (concurrency, non-determinism, flaky third-party code, infrastructure); retry or quarantine only as a tracked mitigation: retries teach people to ignore flakiness, and quarantine can mask a real bug. [P35]
- Delete tests with the code they test, write none for cases that cannot happen, and hold test code to the production complexity bar. [P36 G21 G2]
- Treat tests as an agent's check, not its spec: the agent reports a wrong test instead of editing, deleting or special-casing around it; suite pruning is a separate owner-approved pass. [G15 E37]

## Process (for reviewers and whoever edits doctrine)
- Treat code as a liability, not an asset: every kept line costs upkeep, and removing it is work worth doing. [B11]
- Add a rule or doc line for an observed failure or a non-standard practice the agent cannot infer, then check that behaviour changed. [G19 E20]
- Test a doctrine cut as old-versus-new runs on the weakest model that reads it: 20-50 scenarios from real failures, several trials, grading what was produced; that size catches only large regressions. [P38 G19]
- Cut in one reviewed diff, category by category, and restore whatever a failing scenario proves needed: brevity bias drops domain insight and repeated LLM rewriting erodes detail. [E39 E27]
- Review agent diffs for deletable code and for guards wrapped around code that should be gone; where a change removes behaviour, add a check that fails if it remains. Prompts cut initial verbosity and erosion, not the degradation rate. [E40 E41]
- Have reviewers flag gaps against correctness and stated requirements, not style; chasing every finding adds layers, defensive code and tests for impossible cases. [G21]

## Where compact goes wrong
Compact, never cryptic. These limits win over every rule above.
- Compact means fewer elements, not fewer letters: no golfing, cryptic abbreviations or multi-clause comprehensions; concision ranks below clarity and simplicity. [G13 G9]
- Never cut what the reader lacks: the why, constraints, gotchas, exact commands for fragile steps; ambiguity, incompleteness and incorrectness are the severest API-doc problems. [P42 G19 E18]
- Minimal is not short: keep a brief's objective, output format, tools and sources, boundaries and fixed decisions, its stop, no-repeat and escalate conditions, and one canonical example per format. [P42 P43 E44 E27]
- Never cut or reword owner quotes, like those atop [delegating](../skills/delegating/SKILL.md) and [consolidating-review](../skills/consolidating-review/SKILL.md).

## Conflicts
- DRY vs DAMP: split by purpose; code merges same-knowledge copies, tests keep duplication that shows cause and effect. [P5 B28]
- Scope vs form: posture 5 MINIMAL bounds scope, posture 6 COMPACT bounds form; the merge, inline and delete rules above apply only to lines the change touches or orphans.
- Length vs adherence is open for agent config files. Realistic topical content around one single-line rule (25 to 500 lines, Claude Code headless) showed no detectable effect, BF10 0.05-0.10 [E26]; compressing skills (non-essential content moved on demand) raised quality 2.8% on generated, part LLM-judged tasks, more on long skills [E27]; at 500 keyword-inclusion constraints the best model scored 68%, though top models stayed near-perfect through 150+, on a task its authors say may not generalize [E45]; vendor guidance says length costs adherence but publishes no measurement [G21 G25].
- Contradicting rules: stacking up to 20 random constraints in one prompt cut following from ~96% to as low as 20% through pairwise conflicts, and one LLM rewrite (merge, precedence note, checklist) won back 11 points on the weakest model, none on the strongest [E24]; a contradicting adjacent config file showed no measured effect [E26].
- Rationale: E27 moves explanations and rationale out of the always-loaded body; G15 says the why helps Claude and G19 wants each constant justified. Keep one clause of why where a rule or value is non-obvious.

## Where the rule landed
Posture 6 of the brief template in [delegating](../skills/delegating/SKILL.md) and the closing reminder in [skeptic](../agents/skeptic.md); this memo holds no second copy.

## Sources
1. Fowler, Yagni: https://martinfowler.com/bliki/Yagni.html
2. Google eng-practices, What to look for in a code review: https://google.github.io/eng-practices/review/reviewer/looking-for.html
3. Google Testing Blog, Code Health: Eliminate YAGNI Smells: https://testing.googleblog.com/2017/08/code-health-eliminate-yagni-smells.html
4. Metz, The Wrong Abstraction: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
5. Thomas, Orthogonality and the DRY Principle: https://www.artima.com/articles/orthogonality-and-the-dry-principle
6. Ousterhout and Martin, aposd-vs-clean-code (a written debate): https://github.com/johnousterhout/aposd-vs-clean-code
7. Muñoz Barón, Wyrich, Wagner, Empirical Validation of Cognitive Complexity: https://arxiv.org/abs/2007.12520
8. El Emam et al., The Confounding Effect of Class Size on OO Metrics: https://neverworkintheory.org/2011/07/07/the-confounding-effect-of-class-size-on-the-validity-of-object-oriented-metrics.html
9. Google Go Style Guide: https://google.github.io/styleguide/go/guide.html
10. Romano et al., A Multi-Study Investigation into Dead Code: https://iris.unibas.it/handle/11563/141832
11. Software Engineering at Google, ch. 15 Deprecation: https://abseil.io/resources/swe-book/html/ch15.html
12. Gopstein et al., Understanding Misunderstandings in Source Code: https://pure.psu.edu/en/publications/understanding-misunderstandings-in-source-code/
13. Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
14. Google Style Guides, Documentation Best Practices: https://google.github.io/styleguide/docguide/best_practices.html
15. Anthropic, Claude prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
16. Anthropic, Prompting Claude Sonnet 5.5: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5
17. Strunk, The Elements of Style, rule 13: https://www.gutenberg.org/cache/epub/37134/pg37134-images.html
18. Uddin and Robillard, How API Documentation Fails: https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf
19. Anthropic, Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
20. Gloaguen et al., Evaluating AGENTS.md: https://arxiv.org/abs/2602.11988
21. Anthropic, Best practices for Claude Code: https://code.claude.com/docs/en/best-practices
22. Vercel, AGENTS.md outperforms skills in our agent evals: https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
23. Claude Code docs, Extend Claude with skills: https://code.claude.com/docs/en/skills
24. Anand and Chattaraj, Instruction Stacking Collapse: https://arxiv.org/html/2608.02639
25. Claude Code docs, How Claude remembers your project: https://code.claude.com/docs/en/memory
26. McMillan, Instruction Adherence in Coding Agent Configuration Files: https://arxiv.org/abs/2605.10039
27. SkillReducer: https://arxiv.org/abs/2603.29919
28. Software Engineering at Google, ch. 12 Unit Testing: https://abseil.io/resources/swe-book/html/ch12.html
29. Software Engineering at Google, ch. 13 Test Doubles: https://abseil.io/resources/swe-book/html/ch13.html
30. Google Testing Blog, Change-Detector Tests Considered Harmful: https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html
31. Google Go Style Decisions: https://google.github.io/styleguide/go/decisions
32. Inozemtseva and Holmes, Coverage Is Not Strongly Correlated with Test Suite Effectiveness: https://cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf
33. Banik et al., All Smoke, No Alarm: Oracle Signals in Agent-Authored Test Code: https://arxiv.org/abs/2606.18168
34. Shi et al., Balancing Trade-Offs in Test-Suite Reduction: https://mir.cs.illinois.edu/gyori/pubs/fse14reduction.pdf
35. Google Testing Blog, Flaky Tests at Google and How We Mitigate Them: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
36. Google Testing Blog, Sensenmann: Code Deletion at Scale: https://testing.googleblog.com/2023/04/sensenmann-code-deletion-at-scale.html
37. Zhong, Raghunathan, Carlini, ImpossibleBench: https://arxiv.org/abs/2510.20270
38. Anthropic, Demystifying evals for AI agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
39. Agentic Context Engineering: https://arxiv.org/abs/2510.04618
40. Orlanski et al., SlopCodeBench: https://arxiv.org/abs/2603.24755
41. Ebrahimi et al., To Add Is Machine, To Delete Is Human: https://arxiv.org/abs/2607.28887
42. Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
43. Anthropic, How we built our multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
44. Why Do Multi-Agent LLM Systems Fail?: https://arxiv.org/abs/2503.13657
45. Jaroslawicz et al., How Many Instructions Can LLMs Follow at Once? (IFScale): https://arxiv.org/abs/2507.11538
