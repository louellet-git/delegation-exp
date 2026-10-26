---
id: DOC-DOC-STANDARD
type: plan
item: 10.22 Information management plan
status: current
date: 2026-10-26
scope: How the framework's governed docs conform to ISO/IEC/IEEE 15289: header, content, compactness, review and enforcement.
---

# Documentation standard

## Conformance

Tailored conformance to ISO/IEC/IEEE 15289:2019 (normative references 12207:2017,
15288:2015); process claimed: information management. Clause-10 titles are verified against the
table of contents in ISO's sample preview of 15289:2019; clause 7 content is still the 2017 text
via GOST R 58609-2019. Staleness triggers: buying the 2019 text, or IEEE P15289 publishing.
Declaration (5.2(a)): "the contract" means the owner's rulings plus the PR merge.

## Governed set

Documentation of any kind, whatever its format: every such file in this repo, and in any project
the framework runs on, every one the run's agents create or change.

- Text formats (`.md`, `.markdown`, `.txt`, `.rst`, `.adoc`): the header is the leading
  front-matter block. Files with tool frontmatter (`agents/`, `skills/`, `commands/`) carry the
  six keys inside it, beside their tool keys. `hooks/session-start-context.md` carries a header;
  `scripts/session-start.py` strips it before injecting.
- Other formats (`.docx`, `.pptx`, `.pdf`, `.html` and the like): the same six fields as the
  document's first block, or its properties where the format has them. Only the reviewer checks
  them.
- Not governed: source code, data files, `vendor/`, the installer's copies (its `INSTALL.json`),
  and `.txt` files named exactly `requirements`, `constraints`, `robots`, `LICENSE`, `COPYING`,
  `NOTICE`.

One item per file.

## Header

Front matter between `---` lines, `key: value`; tool keys (`name`, `description`, `tools`,
`model`, `argument-hint`, `allowed-tools`, `disable-model-invocation`) may sit beside these:

| Key | Value |
|---|---|
| id | `DOC-<SLUG>`: A-Z, 0-9, hyphens; unique |
| type | description, plan, policy, procedure, report, request, specification, record |
| item | a clause-10 item exactly as listed (`10.<n> <title>`, n in 2..74; list in `scripts/doc_check.py`); or `9 record` |
| status | draft, current, frozen, superseded |
| date | YYYY-MM-DD, date of issue; frozen/superseded: date of the item's last commit |
| scope | one sentence: purpose and scope. Audience is always the owner and the framework's agents |

The registry of items is the headers: `python3 scripts/doc_check.py list`.

## Elements

The R column below says which are met by reference.

- Issuing organization: the project holding the doc.
- Change history: `git log -- <path>` plus the PR; without git, the doc's own record.
- Approval: the reviewer's PLEASED plus the owner's merge or acceptance.
- References: inline paths or links.
- Glossary: define a framework-coined term at first use or link its defining doc.

## Required content by type

Header: date, status, scope for every type. R = by reference; T = tailored out. Body: every other
element the doc has content for, present or linked. Never add a section only to state an element
is absent. The scope line is the summary unless the conclusions need more; notation only for
symbols defined neither at use nor in a linked source.

| Type | R | T | Body |
|---|---|---|---|
| description | issuer, references, history | glossary | context, notation, body, summary |
| plan | issuer, references, approval, history | glossary; schedule (standing), budget (none), resources (none), environment and safety (none), training (self-describing), completion (open-ended) | tasks, tools and methods, responsibilities, interfaces, risks, quality measures, review and reporting, other plans, change procedure |
| policy | issuer, references, approval, history | glossary | objectives, enforcers, effective date if not `date` |
| procedure | issuer, references, approval, history | glossary | related plans and procedures, inputs and outputs, ordered steps per participant, error resolution |
| report | issuer, references, history | glossary | participants, summary, context, methods, conclusions and recommendations |
| request | none | none | subject, originator, requested response, description with due date, rationale |
| specification | issuer, references, approval, history | glossary | body, assurance requirements, constraints, one unambiguous identified statement per requirement |
| record | issuer, references | none | subject or category, body; `id` is the record identifier |

## Status

- `frozen`: an audited or binding record. `superseded`: replaced by a newer item, whose `DOC-`
  id the scope line names. Both get the header check only, are never compacted, and are outside
  the duplicate-line rule. The header governs over any status line in the body.
- `draft` and `current`: full review.

## Compactness

[compact](compact.md) governs, its Docs rules first (state each fact once and link, no needless
words). Also:

1. No preamble; never restate the header.
2. No history narration in current docs (not type record, whose history is the body); git holds it.
3. The shortest form that keeps the meaning; a table or list over prose when shorter.
4. No 60+-character line appears in two docs (compared ignoring case, repeated whitespace and
   trailing punctuation; code fences and table separators excepted; frozen and superseded docs per
   Status). A re-wrapped or reworded copy escapes the check; the reviewer greps for it.

## In-code documentation

Docstrings and comments count, pragmatically: no header; Compactness applies. A docstring is a
one-line summary, then inputs, outputs and errors only where not obvious, in the language's
convention (e.g. PEP 257): the 10.28 Interface description shape. A comment says why, not what. A
module or file opens with a one-line purpose. The reviewer judges usefulness to the future
reader; the script does not check it.

## Review

A skeptic with [lens](lenses.md#doc-standard) `doc-standard` loads
[doc-review](../skills/doc-review/SKILL.md) on every doc deliverable; its verdict goes into the
review artifact like any skeptic's. NOT PLEASED: the author fixes, the same reviewer re-reviews.

## Enforcement

Soft: no CI, no hook. The implementer runs `python3 scripts/doc_check.py check <changed docs>`
(`--root DIR` in a consumer project; with or without git) before DONE and reports the output; the
reviewer may rerun it. It checks only the header rules, unique ids, a superseded scope naming an
existing id and Compactness 4: a doc can pass and still break this standard. The rest is the
reviewer's. `list` shows other-format docs as `critic-only`.

## Plan elements

- Tasks, tools and methods, quality measures, review and reporting: Review, Compactness,
  Enforcement. Responsibilities: Review, Approval. Interfaces: `scripts/doc_check.py`, the review
  artifact. Other plans: [operating model](operating-model.md). Risks: a skipped check; a
  reviewer miss. Change procedure: edit through a PR.
