---
name: doc-review
description: Reviews documentation against docs/DOC-STANDARD.md. A skeptic loads it when its lens is doc-standard; returns PLEASED | NOT PLEASED with a numbered BLOCKING list.
id: DOC-SKILL-DOC-REVIEW
type: procedure
item: 10.73 Verification procedure
status: current
date: 2026-10-26
scope: Steps a skeptic with lens doc-standard follows to verify one documentation file against the documentation standard.
---

# Doc review

Input: one doc path (any format you can read; else say so under UNCHECKED). Read
[the standard](../../docs/DOC-STANDARD.md) and the doc, every line of both; do not sample.

1. Run `python3 scripts/doc_check.py check <path>` (`--root DIR` in a consumer project) and quote
   its output. It covers only the header rules, unique id, superseded scope and Compactness 4.
2. Header: the six keys present and valid; `item` is a clause-10 item that fits the doc's purpose.
3. Status: `frozen` must be an audited or binding record; `superseded`: the scope line names the
   newer `DOC-` id. Skip 4 to 6 for both.
4. Content: each element the standard requires for the doc's `type` is present in the body, met by
   header or reference, or tailored out.
5. Compactness: the compact.md Docs rules and rules 1-3 (rule 2 not for type record).
6. Cross-doc: grep the doc's distinctive phrases against the other governed docs
   (`python3 scripts/doc_check.py list`). A copy with a word changed or re-wrapped breaks state-once
   and Compactness 4, which the script misses.
7. In-code documentation (docstrings, comments) in the deliverable: judge it by the standard's
   In-code documentation section.

Each finding cites a line number and the rule it breaks, and gives the shorter or fixed text; a
finding that adds text names the reader action it enables. Prefer cuts.

Output the skeptic's verdict form ([rubric](../../docs/rubric.md#the-verdict-block)), plus the
slot below. Doubts you cannot verify go under UNCHECKED, never BLOCKING.

```
VERDICT: PLEASED | NOT PLEASED
BLOCKING:
1. <line, rule, fix>
UNCHECKED: <what you could not check>
COMPACT: <one line>
```
