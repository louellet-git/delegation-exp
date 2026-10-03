#!/usr/bin/env python3
"""Mechanical domain-neutrality gate.

A framework extracted from real work carries the vocabulary of the work it came
from. This script greps every text file against a **locally-configured** denylist
of terms (case-insensitive, word-boundary matched) and exits nonzero on any hit.

The token list is deliberately NOT in this repository. It lives in an untracked
file (default: `.domain-tokens` at the repo root, one term per line, `#` for
comments) or in the `DOMAIN_TOKENS` environment variable as a comma-separated
list, because a committed list of the words you scrubbed is itself the
disclosure.

Set your own list up like this:

    printf 'acme\\nwidgetco\\ninternal_codename\\n' > .domain-tokens

`.domain-tokens` is gitignored. Keep it that way.

**When no token list is configured this gate is INERT** — it checks nothing and
says so loudly on stdout. It does not fail closed, because a consumer of this
plugin has no list of ours and should not be blocked by one; and it does not
fail quietly, because a check that reports success while enforcing nothing is
the worst failure mode this framework has.

The grep catches the obvious leaks. Subtler domain-shaped *assumptions* can still
slip past a token match; adversarial review polices those. This script is only
the mechanical half.

Usage: python3 scripts/check-domain-neutral.py [repo-root]
Exit codes: 0 = clean (or inert), 1 = denylist hits found, 2 = usage/IO error.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

TOKENS_FILENAME = ".domain-tokens"
TOKENS_ENV_VAR = "DOMAIN_TOKENS"

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".delegation"}

TEXT_SUFFIXES = {
    ".md", ".json", ".py", ".txt", ".yml", ".yaml", ".toml", ".mjs", ".js",
    ".sh", ".cmd", ".ps1", ".gitignore", ".gitattributes",
}


def load_tokens(root: Path) -> list[str]:
    """Read the denylist from the environment or the untracked token file."""
    raw = os.environ.get(TOKENS_ENV_VAR)
    if raw:
        return [t.strip() for t in raw.split(",") if t.strip()]

    tokens_path = root / TOKENS_FILENAME
    if not tokens_path.is_file():
        return []
    try:
        lines = tokens_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"error: cannot read {TOKENS_FILENAME}: {exc}", file=sys.stderr)
        raise SystemExit(2)
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    # Extensionless files (hook scripts, LICENSE, etc.) are checked too.
    return path.suffix == ""


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    tokens = load_tokens(root)
    if not tokens:
        print("DOMAIN-NEUTRALITY GATE: INERT (no token list configured)")
        print(
            f"  No {TOKENS_FILENAME} at the repo root and no {TOKENS_ENV_VAR} set,\n"
            f"  so NOTHING WAS CHECKED. This is not a pass. See this script's\n"
            f"  docstring to configure your own list."
        )
        return 0

    denylist = re.compile(
        r"(?i)\b(" + "|".join(re.escape(t) for t in tokens) + r")\b"
    )

    hits: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.as_posix() == TOKENS_FILENAME:
            continue  # the list itself, which is untracked by design
        if not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable; token gate applies to text
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in denylist.finditer(line):
                hits.append(f"{rel.as_posix()}:{lineno}: '{match.group(0)}'")

    if hits:
        print("DOMAIN-NEUTRALITY GATE: FAILED")
        for hit in hits:
            print(f"  {hit}")
        print(f"\n{len(hits)} denylist hit(s). The tree must be domain-neutral.")
        return 1

    print(f"DOMAIN-NEUTRALITY GATE: PASSED ({len(tokens)} term(s) checked, no hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
