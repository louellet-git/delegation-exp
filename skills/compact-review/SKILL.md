---
name: compact-review
description: Reviews a deliverable's docs and in-code docs for compactness. A skeptic loads it when its lens is compact; returns PLEASED | NOT PLEASED with a numbered BLOCKING list.
---

# Compact review

Input: one doc path or deliverable (any format you can read; else say so under UNCHECKED). Read it
all, every line; do not sample. Apply [compact.md](../../docs/compact.md).

1. Writer's duty (compact.md Docs): flag text that serves none of its three questions.
2. Docs and agent-read rules of compact.md, line by line: each finding cites a line and the rule,
   and gives the shorter text; one that adds text names the reader action it enables. Prefer cuts.
3. Restated facts: grep the doc's distinctive phrases across the repo's other docs; a copy, even
   re-wrapped or with a word changed, breaks state-once.
4. In-code docs (docstrings, comments) per compact.md.

Output the skeptic's verdict form ([rubric](../../docs/rubric.md#the-verdict-block)); doubts you
cannot verify go under UNCHECKED, never BLOCKING.

```
VERDICT: PLEASED | NOT PLEASED
BLOCKING:
1. <line, rule, fix>
UNCHECKED: <what you could not check>
COMPACT: <one line>
```
