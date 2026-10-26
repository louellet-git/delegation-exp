#!/usr/bin/env python3
"""Tests for scripts/doc_check.py: governed set (walk and git), header rules, paths, duplicates. Stdlib only."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "doc_check.py"
spec = importlib.util.spec_from_file_location("doc_check", SCRIPT)
doc_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc_check)

HEAD = dict(id="DOC-A", type="plan", item="10.22 Information management plan",
            status="current", date="2026-10-25", scope="Test scope.")
LONG = "A rule that is long enough to count as a stated rule, stated here once only."


def put(root, rel, raw=None, body="Body.\n", **over):
    """Write a doc; a None override drops that key."""
    f = {k: v for k, v in {**HEAD, **over}.items() if v is not None}
    p = Path(root, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raw if raw is not None else "---\n" + "".join(f"{k}: {v}\n" for k, v in f.items()) + "---\n" + body)


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class Base(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root = Path(d.name)

    def problems(self, *paths):
        return doc_check.problems(self.root, paths or None)


class Walk(Base):
    """A temp dir without git."""

    def test_ok_and_skipped_dirs(self):
        put(self.root, "a.md")
        for d in (".git", ".delegation", "vendor", "node_modules", "__pycache__"):
            put(self.root, f"{d}/x.md", raw="no header\n")
        put(self.root, "sub/b.md", id="DOC-B")
        self.assertEqual(self.problems(), [])
        self.assertEqual([p.as_posix() for p in doc_check.governed(self.root)], ["a.md", "sub/b.md"])

    def test_every_md_is_governed(self):
        put(self.root, "agents/x.md", raw="no header\n")
        put(self.root, "test/y.md", raw="no header\n")
        self.assertEqual(sorted(p.split(":")[0] for p in self.problems()), ["agents/x.md", "test/y.md"])

    def test_text_formats_and_critic_only(self):
        put(self.root, "a.txt")
        put(self.root, "b.rst", id="DOC-B")
        put(self.root, "c.adoc", raw="no header\n")
        for f in ("d.docx", "e.pdf", "f.html", "src.py", "data.json"):
            Path(self.root, f).write_bytes(b"x")
        self.assertEqual(self.problems(), ["c.adoc: no header"])
        self.assertEqual([p.as_posix() for p in doc_check.critic_only(self.root)], ["d.docx", "e.pdf", "f.html"])
        self.assertEqual(self.problems("d.docx"), [])
        out = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "list"],
                             capture_output=True, text=True).stdout
        self.assertEqual(out.splitlines()[-3:], ["critic-only d.docx", "critic-only e.pdf", "critic-only f.html"])
        self.assertNotIn("src.py", out)

    def test_data_and_legal_txt_exact_names_only(self):
        for f in ("requirements.txt", "constraints.txt", "robots.txt", "LICENSE.txt", "COPYING.txt", "notice.TXT",
                  "sub/Requirements.txt"):
            put(self.root, f, raw="x\n")
        for f in ("license-plan.txt", "requirements-dev.txt", "notes.txt"):
            put(self.root, f, raw="x\n")
        self.assertEqual(self.problems(), [f"{f}: no header" for f in ("license-plan.txt", "notes.txt", "requirements-dev.txt")])

    def test_consumer_skips_vendor_and_installed_copies(self):
        man = {"source_commit": None, "files": {".claude/skills/doc-review/SKILL.md": "h", ".claude/agents/skeptic.md": "h"}}
        for use_git in (False, True):
            with self.subTest(git=use_git), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                if use_git:
                    git(root, "init", "-q")
                put(root, "own.md")
                put(root, "vendor/delegation-framework/docs/x.md", raw="no header\n")
                put(root, "vendor/other/y.md", raw="no header\n")
                put(root, ".claude/skills/doc-review/SKILL.md", raw="no header\n")
                put(root, ".claude/agents/skeptic.md", raw="no header\n")
                put(root, "vendor/delegation-framework/INSTALL.json", raw=json.dumps(man))
                self.assertEqual(doc_check.problems(root), [])
                put(root, ".claude/agents/mine.md", raw="no header\n")
                self.assertEqual(doc_check.problems(root), [".claude/agents/mine.md: no header"])

    def test_cli_without_git(self):
        put(self.root, "a.md")
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *a],
                                        capture_output=True, text=True)
        r = run("check")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "docs ok"))
        put(self.root, "b.md", raw="x\n")
        r = run("check")
        self.assertEqual((r.returncode, r.stdout.strip()), (1, "b.md: no header"))
        self.assertEqual(run("list").stdout.strip(), "DOC-A plan current a.md\n- - - b.md")


class Git(Base):
    def test_tracked_untracked_not_ignored(self):
        git(self.root, "init", "-q")
        put(self.root, "a.md")
        put(self.root, "new.md", id="DOC-N")
        put(self.root, "gone/x.md", raw="no header\n")
        put(self.root, ".delegation/y.md", raw="no header\n")
        Path(self.root, ".gitignore").write_text("gone/\n.delegation/\n")
        git(self.root, "add", "a.md", ".gitignore")
        self.assertEqual([p.as_posix() for p in doc_check.governed(self.root)], ["a.md", "new.md"])
        self.assertEqual(self.problems(), [])

    def test_subdir_of_repo(self):
        git(self.root, "init", "-q")
        put(self.root, "p/a.md")
        put(self.root, "other.md", raw="no header\n")
        self.assertEqual([p.as_posix() for p in doc_check.governed(self.root / "p")], ["a.md"])


class Header(Base):
    def one(self, **over):
        put(self.root, "a.md", **over)
        return self.problems()

    def test_valid_items(self):
        for item in ("9 record", "10.2 Acceptance plan", "10.48 Request for proposal (RFP)",
                     "10.74 Verification report"):
            self.assertEqual(self.one(item=item), [], item)

    def test_bad_item(self):
        for item in ("10.22 Information security plan", "10.99 Plan", "10.1 General", "10.22", "10.022 Plan",
                     "9 plan", "10.22 information management plan"):
            self.assertEqual(self.one(item=item), [f"a.md: bad item {item}"], item)

    def test_clause_10_list(self):
        self.assertEqual(sorted(doc_check.ITEMS), list(range(2, 75)))
        self.assertEqual(doc_check.ITEMS[36], "Problem management procedure")

    def test_missing_unknown_and_bad_values(self):
        self.assertEqual(self.one(scope=None), ["a.md: missing key scope"])
        self.assertEqual(self.one(owner="x"), ["a.md: unknown key owner"])
        self.assertEqual(self.one(id="doc-a"), ["a.md: bad id doc-a"])
        self.assertEqual(self.one(type="memo"), ["a.md: bad type memo"])
        self.assertEqual(self.one(status="old"), ["a.md: bad status old"])
        self.assertEqual(self.one(date="2026-13-01"), ["a.md: bad date 2026-13-01"])

    def test_no_header(self):
        put(self.root, "a.md", raw="Body.\n")
        self.assertEqual(self.problems(), ["a.md: no header"])

    def test_tool_keys_and_continuation_lines(self):
        raw = ("---\nname: x\ndescription: >-\n  folded text: with colon\n  more\ntools: Read, Grep\nmodel: haiku\n"
               "argument-hint: a\nallowed-tools: Bash\ndisable-model-invocation: true\n"
               + "".join(f"{k}: {v}\n" for k, v in HEAD.items()) + "---\nBody.\n")
        put(self.root, "agents/x.md", raw=raw)
        self.assertEqual(self.problems(), [])

    def test_continuation_lines_do_not_hide_missing_keys(self):
        put(self.root, "a.md", raw="---\nname: x\ndescription: >-\n  id: DOC-X\n---\nBody.\n")
        self.assertIn("a.md: missing key id", self.problems())

    def test_bom(self):
        put(self.root, "a.md")
        p = self.root / "a.md"
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
        self.assertEqual(self.problems(), [])

    def test_superseded_names_existing_doc(self):
        put(self.root, "old.md", id="DOC-OLD", status="superseded", scope="Replaced by DOC-NEW.")
        self.assertEqual(self.problems(), ["old.md: superseded scope names no existing DOC id"])
        put(self.root, "new.md", id="DOC-NEW")
        self.assertEqual(self.problems(), [])
        put(self.root, "old.md", id="DOC-OLD", status="superseded", scope="Replaced by nothing.")
        self.assertEqual(self.problems(), ["old.md: superseded scope names no existing DOC id"])
        put(self.root, "old.md", id="DOC-OLD", status="frozen", scope="Audited record.")
        self.assertEqual(self.problems(), [])

    def test_crlf(self):
        put(self.root, "a.md", raw="---\r\n" + "".join(f"{k}: {v}\r\n" for k, v in HEAD.items()) + "---\r\nBody.\r\n")
        self.assertEqual(self.problems(), [])


class Cross(Base):
    def test_duplicate_id(self):
        put(self.root, "a.md")
        put(self.root, "b.md")
        self.assertEqual(self.problems(), ["duplicate id DOC-A: a.md, b.md"])

    def test_duplicate_line(self):
        put(self.root, "a.md", body=LONG + "\n")
        put(self.root, "b.md", id="DOC-B", body=LONG + "\n")
        self.assertEqual(self.problems(), [f"duplicate line in a.md, b.md: {LONG[:50]}"])

    def test_duplicate_line_normalised(self):
        put(self.root, "a.md", body="A rule that is long enough to count as a stated rule, stated here once only.\n")
        put(self.root, "b.md", id="DOC-B", body="  a RULE that is long enough to count  as a stated rule, stated here once only!\n")
        self.assertEqual(len(self.problems()), 1)

    def test_tilde_fences(self):
        put(self.root, "a.md", body=f"~~~\n{LONG}\n~~~\n")
        put(self.root, "b.md", id="DOC-B", body=f"~~~\n{LONG}\n~~~\n")
        put(self.root, "c.md", id="DOC-C", body=f"```\n~~~\n{LONG}\n```\n")
        put(self.root, "d.md", id="DOC-D", body=f"```\n~~~\n{LONG}\n```\n")
        self.assertEqual(self.problems(), [])
        put(self.root, "e.md", id="DOC-E", body=f"~~~\n~~~\n{LONG}\n")
        put(self.root, "f.md", id="DOC-F", body=f"{LONG}\n")
        self.assertEqual(len(self.problems()), 1)

    def test_duplicate_line_exceptions(self):
        short, fence = "Short line.", "```\n" + LONG + "\n```\n"
        put(self.root, "a.md", body=f"{short}\n{fence}|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        put(self.root, "b.md", id="DOC-B", body=f"{short}\n{fence}|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        put(self.root, "c.md", id="DOC-C", status="frozen", body=LONG + "\n")
        put(self.root, "d.md", id="DOC-D", body=LONG + "\n")
        self.assertEqual(self.problems(), [])

    def test_paths(self):
        put(self.root, "a.md", raw="x\n")
        put(self.root, "b.md", raw="y\n")
        put(self.root, "c.md", id="DOC-C", body=LONG + "\n")
        put(self.root, "d.md", id="DOC-D", body=LONG + "\n")
        self.assertEqual(self.problems("b.md"), ["b.md: no header"])
        self.assertEqual(self.problems("c.md"), [f"duplicate line in c.md, d.md: {LONG[:50]}"])
        self.assertEqual(self.problems("a.md", "b.md"), ["a.md: no header", "b.md: no header"])
        self.assertEqual(self.problems("nope.md"), ["nope.md: not a governed file"])

    def test_cli_paths(self):
        put(self.root, "a.md", raw="x\n")
        put(self.root, "b.md")
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "check", "b.md"],
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "docs ok"))


if __name__ == "__main__":
    unittest.main()
