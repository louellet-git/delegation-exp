# TODO

- **Engineering standard for the framework's docs** (owner, 2026-10-25). Apply ISO/IEC/IEEE
  15289:2019 (tailored) to every doc here, as FinancialAnalysis now does: header per item
  (id, type, item, status, date, scope), a Haiku doc-critic for conformance and compactness,
  and a checker run by hook and CI. Reference implementation: louellet-git/FinancialAnalysis
  `docs/DOC-STANDARD.md`, `scripts/doc_check.py`, `.claude/agents/doc-critic.md`. Lessons
  from that run:
  - Tell the critic to read every line; it samples otherwise and finds new nits each round.
  - Without elements-by-link, one-time audience and no glossary for standard terms, the
    critic demands sections that bloat docs against `docs/compact.md`.
  - Shell-parsing hooks never close; CI is the hard gate, the hook only an early warning.
