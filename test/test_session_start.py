#!/usr/bin/env python3
"""Tests for scripts/session-start.py: the context file's front matter is stripped before injection."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "session-start.py"
spec = importlib.util.spec_from_file_location("session_start", SCRIPT)
session_start = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_start)


class SessionStart(unittest.TestCase):
    def run_hook(self, text, *argv):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "ctx.md")
            f.write_bytes(text.encode())
            out = io.StringIO()
            with mock.patch.object(session_start, "CONTEXT_PATH", f), mock.patch.object(sys, "argv", ["x", *argv]), \
                    mock.patch.object(sys, "stdin", io.StringIO("{}")), redirect_stdout(out):
                self.assertEqual(session_start.main(), 0)
        return json.loads(out.getvalue())

    def test_strips_front_matter_both_shapes(self):
        text = "---\nid: DOC-X\nscope: s\n---\nBODY LINE\n"
        claude = self.run_hook(text)["hookSpecificOutput"]
        self.assertEqual(claude["hookEventName"], "SessionStart")
        copilot = self.run_hook(text, "--copilot")
        for ctx in (claude["additionalContext"], copilot["additionalContext"]):
            self.assertIn("BODY LINE", ctx)
            self.assertNotIn("DOC-X", ctx)
            self.assertNotIn("---", ctx)

    def test_crlf_front_matter(self):
        ctx = self.run_hook("---\r\nid: DOC-X\r\n---\r\nBODY\r\n", "--copilot")["additionalContext"]
        self.assertIn("BODY", ctx)
        self.assertNotIn("DOC-X", ctx)

    def test_no_front_matter_unchanged(self):
        ctx = self.run_hook("Plain body\n---\nkept rule\n", "--copilot")["additionalContext"]
        self.assertIn("Plain body\n---\nkept rule", ctx)

    def test_header_only_stays_silent(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "ctx.md")
            f.write_text("---\nid: DOC-X\n---\n")
            out = io.StringIO()
            with mock.patch.object(session_start, "CONTEXT_PATH", f), mock.patch.object(sys, "stdin", io.StringIO("{}")), \
                    redirect_stdout(out):
                self.assertEqual(session_start.main(), 0)
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
