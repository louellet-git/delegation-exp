#!/usr/bin/env python3
"""Tests for the GitHub Copilot CLI wiring: hooks/copilot-hooks.json and --copilot output."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "hooks" / "copilot-hooks.json"
SCRIPT_RE = re.compile(r"scripts[/\\]([\w-]+\.py)")


def commands():
    for event, groups in json.loads(CONFIG.read_text(encoding="utf-8"))["hooks"].items():
        for group in groups:
            for hook in group["hooks"]:
                yield event, hook


class TestCopilotHooksFile(unittest.TestCase):
    def test_every_command_has_both_shells_and_names_a_script_with_the_flag(self):
        seen = 0
        for event, hook in commands():
            for key in ("bash", "powershell"):
                with self.subTest(event=event, key=key):
                    self.assertIn(key, hook)
                    cmd = hook[key]
                    names = SCRIPT_RE.findall(cmd)
                    self.assertTrue(names, cmd)
                    for name in names:
                        self.assertTrue((ROOT / "scripts" / name).is_file(), name)
                    self.assertIn("--copilot", cmd)
                    seen += 1
        self.assertGreater(seen, 0)


class TestSessionStartCopilot(unittest.TestCase):
    def run_script(self, *flags):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "session-start.py"), *flags],
            input="{}", capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_copilot_prints_top_level_additional_context(self):
        output = self.run_script("--copilot")
        self.assertEqual(set(output), {"additionalContext"})
        self.assertIn("EXTREMELY_IMPORTANT", output["additionalContext"])

    def test_default_keeps_hook_specific_output(self):
        output = self.run_script()
        self.assertEqual(set(output), {"hookSpecificOutput"})
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")


class TestCopilotManifest(unittest.TestCase):
    def test_manifest_matches_claude_plugin_and_points_at_copilot_hooks(self):
        copilot = json.loads((ROOT / ".github" / "plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        for key in ("name", "version"):
            self.assertEqual(copilot[key], claude[key])
        self.assertEqual(copilot["hooks"], "hooks/copilot-hooks.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
