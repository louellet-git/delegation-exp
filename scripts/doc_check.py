#!/usr/bin/env python3
"""Documentation-standard checker (rules: docs/DOC-STANDARD.md); soft, never a gate.

    python3 scripts/doc_check.py [--root DIR] check [paths...] | list
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

KEYS = ["id", "type", "item", "status", "date", "scope"]
TOOL_KEYS = ["name", "description", "tools", "model", "argument-hint", "allowed-tools", "disable-model-invocation"]
TYPES = ["description", "plan", "policy", "procedure", "report", "request", "specification", "record"]
STATUSES = ["draft", "current", "frozen", "superseded"]
TEXT = {".md", ".markdown", ".txt", ".rst", ".adoc"}
CRITIC_ONLY = {".docx", ".doc", ".odt", ".pptx", ".ppt", ".odp", ".pdf", ".html", ".htm"}
SKIP_DIRS = {".git", ".delegation", "node_modules", "__pycache__"}
MANIFEST = "vendor/delegation-framework/INSTALL.json"  # written by scripts/install-into.py
DATA_TXT = {"requirements.txt", "constraints.txt", "robots.txt", "license.txt", "copying.txt", "notice.txt"}  # data, legal
SEPARATOR = re.compile(r"[|:\s-]+")
# ISO/IEC/IEEE 15289:2019 clause 10 items 10.2..10.74, titles from the 2019 ToC (10.1 is "General")
ITEMS = dict(enumerate("""
Acceptance plan
Acceptance report
Acquisition plan
Capacity plan
Change request
Complaint procedure
Concept of operations
Configuration management plan
Configuration management procedure
Configuration status report
Contract
Customer satisfaction survey
Database design description
Design description
Development plan
Evaluation report
Implementation procedure
Improvement plan
Incident management procedure
Incident report
Information management plan
Information management procedure
Information security plan
Installation report
Integration and test report
Integration plan
Interface description
Life-cycle policy
Life-cycle procedure
Maintenance plan
Maintenance procedure
Measurement procedure
Monitoring and control report
Operational concept
Problem management procedure
Problem report
Process description
Process improvement report
Product need assessment
Progress report
Project management plan
Proposal
Quality management plan
Quality management policy
Quality management procedure
Release plan
Request for proposal (RFP)
Resource request
Review minutes
Risk action request
Risk management plan
Service catalog
Service continuity and availability plan
Service level agreement (SLA)
Service report
Supplier management procedure
System architecture description
System element description
System requirements specification
Test procedure
Test report
Training documentation
Training plan
Transition plan
Transition procedure
User documentation
User notification
Validation plan
Validation procedure
Validation report
Verification plan
Verification procedure
Verification report
""".split("\n")[1:-1], 2))


def _is_date(s):
    try:
        return len(s) == 10 and bool(datetime.strptime(s, "%Y-%m-%d"))
    except ValueError:
        return False


def _is_item(s):
    m = re.fullmatch(r"10\.([1-9]\d?) (.+)", s)
    return s == "9 record" or bool(m and ITEMS.get(int(m[1])) == m[2])


RULES = {"id": lambda s: re.fullmatch(r"DOC-[A-Z0-9-]+", s), "type": TYPES.__contains__, "item": _is_item,
         "status": STATUSES.__contains__, "date": _is_date}


def files(root):
    """Documentation files under root (relative paths): tracked or untracked-not-ignored in a git work tree,
    else an os.walk skipping SKIP_DIRS. Not vendor/, nor the installer's copies listed in its manifest."""
    try:
        git = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True)
    except OSError:
        git = None
    if git and git.returncode == 0:
        names = [n for n in git.stdout.decode().split("\0") if n]
    else:
        names = []
        for d, ds, fs in os.walk(root):
            ds[:] = [x for x in ds if x not in SKIP_DIRS]
            names += [Path(d, f).relative_to(root).as_posix() for f in fs]
    try:
        mine = set(json.loads(Path(root, MANIFEST).read_text())["files"])
    except (OSError, ValueError, KeyError, TypeError):
        mine = set()
    return [Path(n) for n in sorted(set(names)) if Path(root, n).is_file() and n not in mine
            and "vendor" not in Path(n).parts]


def governed(root):
    """Text documentation files: header and duplicate-line rules apply."""
    return [p for p in files(root) if p.suffix.lower() in TEXT and p.name.lower() not in DATA_TXT]


def critic_only(root):
    """Other documentation formats: a skeptic with lens doc-standard reviews them; this checker cannot read them."""
    return [p for p in files(root) if p.suffix.lower() in CRITIC_ONLY]


def header(text):
    """Front-matter key/value dict (indented continuation lines ignored), or None when there is no header."""
    m = re.match(r"---\r?\n(.*?\n)---\r?\n", text, re.S)
    if not m:
        return None
    return {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in m[1].splitlines()
            if ln.strip() and not ln[0].isspace())}


def _read(root, p):
    return Path(root, p).read_bytes().decode("utf-8-sig", errors="replace")


def _norm(s):
    return re.sub(r"[.,;:!?]+$", "", re.sub(r"\s+", " ", s.lower()))


def problems(root, paths=None):
    """Rule violations across the governed docs, one string each; only those touching `paths` (relative to
    root) when given. Duplicates are found over all docs and reported when any doc involved is in `paths`."""
    out, ids, lines, scopes = [], {}, {}, {}
    hit = lambda names: paths is None or any(n in paths for n in names)
    docs = governed(root)
    out += [f"{n}: not a governed file" for n in paths or [] if n not in {p.as_posix() for p in docs}
            and n not in {p.as_posix() for p in critic_only(root)}]
    for p in docs:
        name, mine = p.as_posix(), []
        text = _read(root, p)
        h = header(text)
        if h is None:
            mine.append(f"{name}: no header")
        else:
            mine += [f"{name}: missing key {k}" for k in KEYS if not h.get(k)]
            mine += [f"{name}: unknown key {k}" for k in h if k not in KEYS + TOOL_KEYS]
            mine += [f"{name}: bad {k} {h[k]}" for k, ok in RULES.items() if h.get(k) and not ok(h[k])]
            ids.setdefault(h.get("id"), []).append(name)
            if h.get("status") == "superseded":
                scopes[name] = h.get("scope", "")
        out += mine if hit([name]) else []
        frozen = h is not None and h.get("status") in ("frozen", "superseded")
        fenced = False
        for ln in ([] if frozen else text.splitlines()):
            s = ln.strip()
            fence = re.match(r"`{3,}|~{3,}", s)
            if fence:
                fenced = None if fenced == fence[0][0] else fenced or fence[0][0]
            elif not fenced and len(s) >= 60 and not SEPARATOR.fullmatch(s):
                lines.setdefault(_norm(s), (s, set()))[1].add(name)
    out += [f"{n}: superseded scope names no existing DOC id" for n, sc in scopes.items()
            if hit([n]) and not set(re.findall(r"DOC-[A-Z0-9-]+", sc)) & set(ids)]
    out += [f"duplicate id {i}: {', '.join(ns)}" for i, ns in ids.items() if i and len(ns) > 1 and hit(ns)]
    out += [f"duplicate line in {', '.join(sorted(ns))}: {s[:50]}" for s, ns in lines.values()
            if len(ns) > 1 and hit(ns)]
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("check").add_argument("paths", nargs="*")
    sub.add_parser("list")
    a = p.parse_args(argv)
    if a.cmd == "check":
        found = problems(a.root, [Path(x).as_posix() for x in a.paths] or None)
        print("\n".join(found) or "docs ok")
        return 1 if found else 0
    if a.cmd == "list":
        hs = [(header(_read(a.root, f)) or {}, f.as_posix()) for f in governed(a.root)]
        print("\n".join([" ".join([h.get(k, "-") for k in ("id", "type", "status")] + [f]) for h, f in hs]
                        + [f"critic-only {f.as_posix()}" for f in critic_only(a.root)]))
        return 0
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
