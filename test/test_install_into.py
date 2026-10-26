#!/usr/bin/env python3
"""Tests for scripts/install-into.py (project-vendored and --user installs). Stdlib only."""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install-into.py"
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
BARE_RE = re.compile(r"(?<!\])\(([^()\s`]+\.md)\)")
TICK_RE = re.compile(r"`([^`\s]+)`")
USER_HOOK = {"matcher": "Edit", "hooks": [{"type": "command", "command": "echo hi"}]}
STALE_HOOK = {"hooks": [{"type": "command", "command":
              'python3 "$CLAUDE_PROJECT_DIR/vendor/delegation-framework/scripts/subagent-reminder.py" || exit 0'}]}
VENDOR = "vendor/delegation-framework"


def install(target, script=SCRIPT):
    return subprocess.run([sys.executable, str(script), str(target)], capture_output=True, text=True)


def copy_src(dst):
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".delegation"))
    return dst


def commit_copy(src):
    copy_src(src)
    git = lambda *a: subprocess.run(["git", "-C", str(src), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)
    git("init", "-q")
    git("add", ".")
    git("commit", "-qm", "src")
    return git


def commands(cfg):
    return [h["command"] for groups in cfg["hooks"].values() for g in groups for h in g["hooks"]]


def snapshot(target):
    return {str(p.relative_to(target)): p.read_bytes() for p in sorted(target.rglob("*")) if p.is_file()}


class InstallInto(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.t = self.tmp / "repo"
        (self.t / ".claude").mkdir(parents=True)
        self.v = self.t / VENDOR
        self.settings = self.t / ".claude" / "settings.json"
        self.settings.write_text(json.dumps({"permissions": {"allow": ["X"]}, "hooks": {"PreToolUse": [USER_HOOK]}}))

    def test_merges_hooks_and_keeps_user_settings(self):
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = json.loads(self.settings.read_text())
        self.assertEqual(cfg["permissions"], {"allow": ["X"]})
        self.assertEqual(cfg["hooks"]["PreToolUse"][0], USER_HOOK)
        self.assertEqual(len(cfg["hooks"]["PreToolUse"]), 2)
        self.assertEqual(set(cfg["hooks"]), {"SessionStart", "SubagentStop", "Stop", "PreToolUse"})
        cmd = cfg["hooks"]["PreToolUse"][1]["hooks"][0]["command"]
        self.assertIn('"$CLAUDE_PROJECT_DIR/vendor/delegation-framework/scripts/commit-gate.py"', cmd)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", json.dumps(cfg))
        self.assertFalse([c for c in commands(cfg) if "\\" in c])

    def test_installs_agents_skills_commands(self):
        install(self.t)
        c = self.t / ".claude"
        for f in ("agents/skeptic.md", "agents/steward.md", "skills/delegating/SKILL.md",
                  "skills/skeptical-review/SKILL.md", "skills/consolidating-review/SKILL.md",
                  "commands/delegate.md", "commands/review-panel.md", "commands/skeptic-review.md"):
            self.assertTrue((c / f).is_file(), f)
        self.assertFalse((c / "agents" / "manager.md").exists())
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", (c / "commands" / "delegate.md").read_text())

    def test_installed_skill_names_are_plain(self):
        install(self.t)
        self.assertNotIn("delegation-framework:", (self.t / ".claude" / "commands" / "review-panel.md").read_text())

    def test_vendors_the_tree_unmodified_except_the_session_context(self):
        install(self.t)
        vendored = [f for f in self.v.rglob("*") if f.is_file() and f.name != "INSTALL.json"]
        self.assertGreater(len(vendored), 30)
        for f in vendored:
            rel = f.relative_to(self.v).as_posix()
            if rel != "hooks/session-start-context.md":
                self.assertEqual(f.read_bytes(), (ROOT / rel).read_bytes(), rel)
        self.assertNotIn(b"delegation-framework:", (self.v / "hooks" / "session-start-context.md").read_bytes())
        self.assertIn("source_commit", json.loads((self.v / "INSTALL.json").read_text()))

    def test_manifest_keys_are_posix(self):
        install(self.t)
        files = json.loads((self.v / "INSTALL.json").read_text())["files"]
        self.assertIn("vendor/delegation-framework/scripts/commit-gate.py", files)
        self.assertFalse([k for k in files if "\\" in k])

    def test_session_start_injects_plain_skill_names(self):
        install(self.t)
        r = subprocess.run([sys.executable, str(self.v / "scripts" / "session-start.py")], input="{}", capture_output=True, text=True)
        out = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("`delegating`", out)
        self.assertNotIn("delegation-framework:", out)

    def test_ignores_delegation_dir(self):
        install(self.t)
        self.assertIn(".delegation/", (self.t / ".gitignore").read_text().splitlines())

    def test_rerun_changes_nothing(self):
        install(self.t)
        before = snapshot(self.t)
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_rerun_from_a_clean_source_changes_nothing(self):
        src = self.tmp / "src"
        commit_copy(src)
        install(self.t, src / "scripts" / "install-into.py")
        before = snapshot(self.t)
        r = install(self.t, src / "scripts" / "install-into.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_rerun_from_a_newer_commit_changes_only_the_recorded_commit(self):
        src = self.tmp / "src"
        git = commit_copy(src)
        install(self.t, src / "scripts" / "install-into.py")
        before = snapshot(self.t)
        git("commit", "-q", "--allow-empty", "-m", "newer")
        install(self.t, src / "scripts" / "install-into.py")
        after = snapshot(self.t)
        self.assertEqual([k for k in after if after[k] != before[k]], [f"{VENDOR}/INSTALL.json"])

    def test_upgrade_replaces_vendored_and_installed_copies(self):
        src = copy_src(self.tmp / "src")
        install(self.t, src / "scripts" / "install-into.py")
        with open(src / "agents" / "skeptic.md", "a") as f:
            f.write("\nNEWER\n")
        r = install(self.t, src / "scripts" / "install-into.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NEWER", (self.v / "agents" / "skeptic.md").read_text())
        self.assertIn("NEWER", (self.t / ".claude" / "agents" / "skeptic.md").read_text())

    def test_upgrade_deletes_files_removed_upstream(self):
        src = copy_src(self.tmp / "src")
        install(self.t, src / "scripts" / "install-into.py")
        (src / "commands" / "review-panel.md").unlink()
        r = install(self.t, src / "scripts" / "install-into.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.v / "commands" / "review-panel.md").exists())
        self.assertFalse((self.t / ".claude" / "commands" / "review-panel.md").exists())

    def test_upgrade_keeps_a_locally_modified_file_removed_upstream(self):
        src = copy_src(self.tmp / "src")
        install(self.t, src / "scripts" / "install-into.py")
        (src / "docs" / "lenses.md").unlink()
        (self.v / "docs" / "lenses.md").write_text("my edit")
        r = install(self.t, src / "scripts" / "install-into.py")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("lenses.md", r.stderr)
        self.assertEqual((self.v / "docs" / "lenses.md").read_text(), "my edit")

    def test_refuses_a_source_missing_a_vendored_path(self):
        src = copy_src(self.tmp / "src")
        (src / "LICENSE").unlink()
        r = install(self.t, src / "scripts" / "install-into.py")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("LICENSE", r.stderr)
        self.assertFalse(self.v.exists())

    def test_refuses_foreign_agent(self):
        mine = self.t / ".claude" / "agents" / "skeptic.md"
        mine.parent.mkdir()
        mine.write_text("mine")
        before = snapshot(self.t)
        r = install(self.t)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("skeptic.md", r.stderr)
        self.assertIn("move or rename it, then re-run", r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_refuses_foreign_vendor_dir(self):
        self.v.mkdir(parents=True)
        (self.v / "mine.txt").write_text("mine")
        before = snapshot(self.t)
        r = install(self.t)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("partial install", r.stderr)
        self.assertIn("delete it if it holds only a copy of this framework", r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_refuses_modified_vendored_file(self):
        install(self.t)
        (self.v / "docs" / "compact.md").write_text("my edit")
        before = snapshot(self.t)
        r = install(self.t)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("compact.md", r.stderr)
        self.assertIn("modified since install", r.stderr)
        self.assertIn("delete it to accept the new version", r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_deleting_the_modified_file_accepts_the_new_version(self):
        install(self.t)
        (self.v / "docs" / "compact.md").write_text("my edit")
        self.assertNotEqual(install(self.t).returncode, 0)
        (self.v / "docs" / "compact.md").unlink()
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.v / "docs" / "compact.md").read_bytes(), (ROOT / "docs" / "compact.md").read_bytes())

    def test_refuses_the_vendored_dir_its_own_repo_and_anything_inside_it(self):
        install(self.t)
        before = snapshot(self.t)
        vendored = self.v / "scripts" / "install-into.py"
        for script, target in ((SCRIPT, self.v), (SCRIPT, self.v / "docs"),
                               (vendored, self.t), (vendored, self.v), (vendored, self.v / "docs")):
            r = install(target, script)
            self.assertNotEqual(r.returncode, 0, (script, target))
            self.assertIn("the target is inside, or contains, a vendored copy of this script, or is this script's own repo; run an upstream clone's script into another repo", r.stderr)
            self.assertEqual(snapshot(self.t), before, (script, target))
    def test_refuses_the_upstream_clone_and_anything_inside_it(self):
        src = copy_src(self.tmp / "src")
        before = snapshot(src)
        for target in (src, src / "docs"):
            r = install(target, src / "scripts" / "install-into.py")
            self.assertNotEqual(r.returncode, 0, target)
        self.assertEqual(snapshot(src), before)

    def downgraded_install(self):
        """Install from a source whose gate matcher is plain "Bash", ready to upgrade from the real one."""
        src = copy_src(self.tmp / "src")
        hooks = src / "hooks" / "hooks.json"
        hooks.write_text(hooks.read_text().replace("Bash|PowerShell", "Bash"))
        install(self.t, src / "scripts" / "install-into.py")
        self.assertEqual(json.loads(self.settings.read_text())["hooks"]["PreToolUse"][1]["matcher"], "Bash")

    def test_upgrade_takes_the_shipped_matcher(self):
        self.downgraded_install()
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        groups = json.loads(self.settings.read_text())["hooks"]["PreToolUse"]
        self.assertEqual([g["matcher"] for g in groups], ["Edit", "Bash|PowerShell"])

    def test_upgrade_moves_only_the_framework_hook_out_of_a_group_shared_with_a_user_hook(self):
        self.downgraded_install()
        cfg = json.loads(self.settings.read_text())
        mine = {"type": "command", "command": "echo mine"}
        cfg["hooks"]["PreToolUse"][1]["hooks"].append(mine)
        self.settings.write_text(json.dumps(cfg))
        install(self.t)
        groups = json.loads(self.settings.read_text())["hooks"]["PreToolUse"]
        self.assertEqual(groups[1], {"matcher": "Bash", "hooks": [mine]})
        self.assertEqual(groups[2]["matcher"], "Bash|PowerShell")
        self.assertIn("commit-gate.py", groups[2]["hooks"][0]["command"])
        self.assertEqual(len(groups), 3)

    def test_leaves_empty_user_groups_and_events_alone(self):
        empty = {"matcher": "X", "hooks": []}
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [USER_HOOK, empty], "Notification": []}}))
        install(self.t)
        hooks = json.loads(self.settings.read_text())["hooks"]
        self.assertEqual(hooks["Notification"], [])
        self.assertEqual(hooks["PreToolUse"][:2], [USER_HOOK, empty])

    def test_conflict_names_the_same_file_under_any_hash_seed(self):
        install(self.t)
        for name in ("compact.md", "lenses.md"):
            (self.v / "docs" / name).write_text("my edit")
        for seed in map(str, range(8)):
            r = subprocess.run([sys.executable, str(SCRIPT), str(self.t)], capture_output=True, text=True,
                               env={**os.environ, "PYTHONHASHSEED": seed})
            self.assertIn("compact.md", r.stderr, seed)
            self.assertNotIn("lenses.md", r.stderr, seed)

    def test_rerun_after_the_user_adds_a_hook_keeps_the_framework_groups_in_place(self):
        install(self.t)
        cfg = json.loads(self.settings.read_text())
        cfg["hooks"]["PreToolUse"].append({"matcher": "Write", "hooks": [{"type": "command", "command": "echo later"}]})
        self.settings.write_text(json.dumps(cfg, indent=2) + "\n")
        before = snapshot(self.t)
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(self.t), before)

    def test_a_user_hook_inside_the_framework_group_is_edited_around_in_place(self):
        install(self.t)
        cfg = json.loads(self.settings.read_text())
        group = cfg["hooks"]["PreToolUse"][1]["hooks"]
        gate = group[0]["command"]
        group.insert(0, {"type": "command", "command": "echo first"})
        group.append({"type": "command", "command": "echo last"})
        group[1]["timeout"] = 99
        self.settings.write_text(json.dumps(cfg, indent=2) + "\n")
        install(self.t)
        again = json.loads(self.settings.read_text())["hooks"]["PreToolUse"]
        self.assertEqual(len(again), 2)
        self.assertEqual([h["command"] for h in again[1]["hooks"]], ["echo first", gate, "echo last"])
        self.assertEqual(again[1]["hooks"][1]["timeout"], 10)
        before = snapshot(self.t)
        install(self.t)
        self.assertEqual(snapshot(self.t), before)

    def test_fresh_installs_write_the_same_settings_under_any_hash_seed(self):
        out = []
        for seed in ("1", "2", "3"):
            t = self.tmp / f"seed{seed}"
            t.mkdir()
            subprocess.run([sys.executable, str(SCRIPT), str(t)], check=True, capture_output=True,
                           env={**os.environ, "PYTHONHASHSEED": seed})
            out.append((t / ".claude" / "settings.json").read_bytes())
        self.assertEqual(out[0], out[1])
        self.assertEqual(out[1], out[2])

    def test_refuses_a_source_missing_hooks_json_or_the_session_context(self):
        for name in ("hooks.json", "session-start-context.md"):
            src = copy_src(self.tmp / name)
            (src / "hooks" / name).unlink()
            before = snapshot(self.t)
            r = install(self.t, src / "scripts" / "install-into.py")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(name, r.stderr)
            self.assertNotIn("Traceback", r.stderr)
            self.assertEqual(snapshot(self.t), before)

    def test_prunes_only_installer_hooks(self):
        own = {"hooks": [{"type": "command", "command": "echo vendor/delegation-framework"}]}
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [own, STALE_HOOK]}}))
        install(self.t)
        groups = json.loads(self.settings.read_text())["hooks"]["PreToolUse"]
        self.assertIn(own, groups)
        self.assertNotIn(STALE_HOOK, groups)

    def test_a_first_save_failure_names_the_manifest(self):
        spec = importlib.util.spec_from_file_location("install_into", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with mock.patch.object(Path, "write_text", side_effect=OSError(28, "No space left on device")), mock.patch.object(sys, "argv", ["x", str(self.t)]):
            with self.assertRaises(SystemExit) as cm:
                mod.main()
        self.assertIn("write failed on " + str(self.v / "INSTALL.json"), cm.exception.code)

    def test_write_failure_exits_cleanly_and_names_the_retry(self):
        (self.t / ".claude" / "agents").write_text("a file where a directory belongs")
        r = install(self.t)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn(f"write failed on {self.t / '.claude' / 'agents'}", r.stderr)
        self.assertIn("fix the cause above, then re-run", r.stderr)
        self.assertNotIn("delete vendor", r.stderr)

    def test_a_write_failure_names_the_destination(self):
        spec = importlib.util.spec_from_file_location("install_into", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        full = OSError(28, "No space left on device")
        with mock.patch.object(Path, "write_bytes", side_effect=full), mock.patch.object(sys, "argv", ["x", str(self.t)]):
            with self.assertRaises(SystemExit) as cm:
                mod.main()
        self.assertIsInstance(cm.exception.code, str)  # sys.exit(str) is exit status 1
        self.assertIn("write failed on", cm.exception.code)
        self.assertIn("No space left on device", cm.exception.code)

    def test_refuses_a_symlink_at_a_managed_path_before_writing(self):
        outside = self.tmp / "outside"
        c = self.t / ".claude"
        (c / "agents").mkdir()
        for name, link, to in (("agent to /dev/null", c / "agents" / "skeptic.md", "/dev/null"),
                               ("dangling agent", c / "agents" / "skeptic.md", outside),
                               ("settings to /dev/null", c / "settings.json", "/dev/null")):
            with self.subTest(name):
                if link == c / "settings.json":
                    self.settings.unlink()
                link.symlink_to(to)
                before = snapshot(self.t)
                r = install(self.t)
                link.unlink()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(f"{link} was not written by this installer; move or rename it, then re-run", r.stderr)
                self.assertEqual(snapshot(self.t), before)
                self.assertFalse(outside.exists())

    def test_upgrade_retry_after_a_write_failure_needs_no_vendor_delete(self):
        src = copy_src(self.tmp / "src")
        script = src / "scripts" / "install-into.py"
        install(self.t, script)
        for name in ("skeptic", "steward"):
            with open(src / "agents" / f"{name}.md", "a") as f:
                f.write("\nNEWER\n")
        blocker = self.t / ".claude" / "agents" / "skeptic.md"
        blocker.unlink()
        blocker.mkdir()
        r = install(self.t, script)
        self.assertEqual(r.returncode, 1)
        self.assertIn("fix the cause above, then re-run", r.stderr)
        blocker.rmdir()
        r = install(self.t, script)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NEWER", (self.t / ".claude" / "agents" / "steward.md").read_text())

    def test_a_failed_first_install_is_retryable(self):
        blocker = self.t / ".claude" / "agents"
        blocker.write_text("a file where a directory belongs")
        self.assertEqual(install(self.t).returncode, 1)
        blocker.unlink()
        r = install(self.t)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((blocker / "skeptic.md").is_file())

    def test_noop_rerun_does_not_rewrite_settings(self):
        install(self.t)
        self.settings.write_text(json.dumps(json.loads(self.settings.read_text()), indent=4) + "\n")
        before = self.settings.read_bytes()
        self.assertEqual(install(self.t).returncode, 0)
        self.assertEqual(self.settings.read_bytes(), before)

    def test_prunes_installer_hooks_in_events_the_framework_no_longer_uses(self):
        self.settings.write_text(json.dumps({"hooks": {"Notification": [STALE_HOOK], "PreToolUse": [USER_HOOK]}}))
        install(self.t)
        hooks = json.loads(self.settings.read_text())["hooks"]
        self.assertNotIn("Notification", hooks)
        self.assertEqual(hooks["PreToolUse"][0], USER_HOOK)

    def test_prunes_an_installer_hook_but_keeps_a_user_hook_in_its_group(self):
        mixed = {"hooks": [USER_HOOK["hooks"][0], STALE_HOOK["hooks"][0]]}
        self.settings.write_text(json.dumps({"hooks": {"Stop": [mixed]}}))
        install(self.t)
        groups = json.loads(self.settings.read_text())["hooks"]["Stop"]
        self.assertEqual(groups[0], {"hooks": [USER_HOOK["hooks"][0]]})
        self.assertNotIn("subagent-reminder.py", json.dumps(groups))

    def test_corrupt_manifest_fails_cleanly(self):
        install(self.t)
        (self.v / "INSTALL.json").write_text("{")
        r = install(self.t)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("INSTALL.json", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_refuses_non_directory(self):
        r = install(self.t / "missing")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not a directory", r.stderr)

    def test_installed_links_and_paths_resolve(self):
        install(self.t)
        for md in (self.t / ".claude").rglob("*.md"):
            text = md.read_text()
            for link in LINK_RE.findall(text) + BARE_RE.findall(text):
                path = link.split("#")[0]
                if path and not link.startswith(("http", "#", "mailto:")):
                    self.assertTrue((md.parent / path).exists(), f"{md.name}: {link}")
            for span in TICK_RE.findall(text):
                if span.startswith(VENDOR):
                    self.assertTrue((self.t / span).exists(), f"{md.name}: {span}")
                else:
                    self.assertFalse((self.v / span).exists(), f"{md.name}: bare {span}")

    def gate(self, command):  # sh-based
        cmd = json.loads(self.settings.read_text())["hooks"]["PreToolUse"][1]["hooks"][0]["command"]
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.t)})
        return subprocess.run(["sh", "-c", cmd], input=payload, capture_output=True, text=True,
                              cwd=self.t, env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.t)})

    @unittest.skipUnless(os.name == "posix", "runs the hook through sh")
    def test_installed_gate_denies_a_bare_commit_in_an_armed_repo(self):
        subprocess.run(["git", "init", "-q", str(self.t)], check=True)
        (self.t / ".delegation").mkdir()
        install(self.t)
        out = json.loads(self.gate("git commit -m x").stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("review-artifact.json", out["permissionDecisionReason"])
        self.assertIn("PLEASED", out["permissionDecisionReason"])

    @unittest.skipUnless(os.name == "posix", "runs the hook through sh")
    def test_installed_gate_is_silent_on_a_bare_commit_in_an_unarmed_repo(self):
        subprocess.run(["git", "init", "-q", str(self.t)], check=True)
        install(self.t)
        r = self.gate("git commit -m x")
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertFalse((self.t / ".delegation").exists())


class UserInstall(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.home = self.tmp / "home"
        self.cl = self.home / ".claude"
        self.cp = self.home / ".copilot"
        self.ag = self.home / ".agents"
        self.fw = self.cl / "delegation-framework"
        self.fwp = self.fw.resolve().as_posix()  # what the installer writes into commands and docs
        self.settings = self.cl / "settings.json"
        self.cl.mkdir(parents=True)

    def run_user(self, script=SCRIPT, **env):
        e = {k: v for k, v in os.environ.items() if k not in ("XDG_CONFIG_HOME", "COPILOT_HOME")}
        e.update(HOME=str(self.home), USERPROFILE=str(self.home), GIT_CONFIG_NOSYSTEM="1", **env)
        return subprocess.run([sys.executable, str(script), "--user"], capture_output=True, text=True, env=e, cwd=self.tmp)

    def ok(self, **env):
        r = self.run_user(**env)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_fresh_install_writes_every_target_with_absolute_paths(self):
        self.ok()
        self.assertEqual((self.fw / "docs" / "compact.md").read_bytes(), (ROOT / "docs" / "compact.md").read_bytes())
        self.assertIn("source_commit", json.loads((self.fw / "INSTALL.json").read_text()))
        for f in ("agents/skeptic.md", "agents/steward.md", "skills/delegating/SKILL.md", "commands/delegate.md"):
            self.assertTrue((self.cl / f).is_file(), f)
        self.assertFalse((self.cl / "agents" / "manager.md").exists())
        cfg = json.loads(self.settings.read_text())
        self.assertEqual(set(cfg["hooks"]), {"SessionStart", "SubagentStop", "Stop", "PreToolUse"})
        cmd = cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn(f'python3 "{self.fwp}/scripts/commit-gate.py"', cmd)
        self.assertFalse([c for c in commands(cfg) if "\\" in c])
        for bad in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT"):
            self.assertNotIn(bad, json.dumps(cfg))
        for name in ("delegating", "skeptical-review", "consolidating-review"):
            self.assertTrue((self.ag / "skills" / name / "SKILL.md").is_file(), name)
        self.assertFalse((self.cp / "skills").exists())
        self.assertNotIn("delegation-framework:", (self.ag / "skills" / "delegating" / "SKILL.md").read_text())
        for name in ("skeptic", "steward"):
            text = (self.cp / "agents" / f"{name}.agent.md").read_text()
            fm = text.split("---\n")[1]
            self.assertEqual(re.findall(r"^(\w+):", fm, re.M), ["name", "description"])
            self.assertIn(f"name: {name}\n", fm)
        hooks = json.loads((self.cp / "hooks" / "delegation-framework.json").read_text())
        shipped = json.loads((ROOT / "hooks" / "copilot-hooks.json").read_text())
        n = 0
        for groups in shipped["hooks"].values():
            for g in groups:
                for h in g["hooks"]:
                    h["env"] = {"PLUGIN_ROOT": self.fwp}
                    n += 1
        self.assertGreaterEqual(n, 4)
        self.assertEqual(hooks, shipped)

    def test_installed_links_and_paths_resolve(self):
        self.ok()
        for md in (*self.cl.glob("*/*.md"), *self.cl.glob("skills/*/SKILL.md"), *self.cp.rglob("*.md"), *self.ag.rglob("*.md")):
            if self.fw in md.parents:
                continue
            text = md.read_text()
            for link in LINK_RE.findall(text) + BARE_RE.findall(text):
                path = link.split("#")[0]
                if path and not link.startswith(("http", "#", "mailto:")):
                    self.assertTrue((md.parent / path).exists(), f"{md}: {link}")
            for span in TICK_RE.findall(text):
                if span.startswith(self.fwp):
                    self.assertTrue(Path(span).exists(), f"{md}: {span}")

    def test_a_user_hook_survives(self):
        self.settings.write_text(json.dumps({"permissions": {"allow": ["X"]}, "hooks": {"PreToolUse": [USER_HOOK]}}))
        self.ok()
        cfg = json.loads(self.settings.read_text())
        self.assertEqual(cfg["permissions"], {"allow": ["X"]})
        self.assertEqual(cfg["hooks"]["PreToolUse"][0], USER_HOOK)
        self.assertEqual(len(cfg["hooks"]["PreToolUse"]), 2)
        self.ok()
        self.assertEqual(json.loads(self.settings.read_text()), cfg)

    def test_a_user_hook_in_a_framework_looking_path_survives(self):
        mine = {"hooks": [{"type": "command", "command": 'python3 "/home/me/code/delegation-framework/scripts/my-check.py"'}]}
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [mine]}}))
        self.ok()
        self.assertIn(mine, json.loads(self.settings.read_text())["hooks"]["PreToolUse"])

    def test_rerun_changes_nothing(self):
        self.ok()
        before = snapshot(self.home)
        self.ok()
        self.assertEqual(snapshot(self.home), before)

    def test_windows_hooks_are_one_python_call(self):
        spec = importlib.util.spec_from_file_location("install_into", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        env = dict(HOME=str(self.home), USERPROFILE=str(self.home), GIT_CONFIG_NOSYSTEM="1",
                   XDG_CONFIG_HOME=str(self.home / ".config"), COPILOT_HOME=str(self.cp))
        with mock.patch.object(mod, "WINDOWS", True, create=True), mock.patch.dict(os.environ, env), mock.patch.object(sys, "argv", ["x", "--user"]):
            mod.main()
            before = snapshot(self.home)
            mod.main()
        self.assertEqual(snapshot(self.home), before)
        claude = commands(json.loads(self.settings.read_text()))
        self.assertEqual(len(claude), 4)
        for c in claude:
            self.assertRegex(c, rf'^python "{re.escape(self.fwp)}/scripts/[\w-]+\.py"$')
            self.assertTrue(mod.key({"command": c}), c)  # still the framework's on upgrade

    def test_refuses_a_modified_installed_file(self):
        self.ok()
        for f in (self.fw / "docs" / "compact.md", self.ag / "skills" / "delegating" / "SKILL.md"):
            f.write_text("my edit")
            before = snapshot(self.home)
            r = self.run_user()
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(f.name, r.stderr)
            self.assertIn("modified since install", r.stderr)
            self.assertEqual(snapshot(self.home), before)
            f.unlink()
            self.ok()

    def test_refuses_a_foreign_agent(self):
        mine = self.cl / "agents" / "skeptic.md"
        mine.parent.mkdir()
        mine.write_text("mine")
        before = snapshot(self.home)
        r = self.run_user()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("move or rename it, then re-run", r.stderr)
        self.assertEqual(snapshot(self.home), before)

    def test_refuses_to_install_over_its_own_copy(self):
        self.ok()
        before = snapshot(self.home)
        r = self.run_user(self.fw / "scripts" / "install-into.py")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(snapshot(self.home), before)

    def test_copilot_home_is_honoured(self):
        alt = self.tmp / "alt"
        self.ok(COPILOT_HOME=str(alt))
        self.assertFalse(self.cp.exists())
        self.assertFalse((alt / "skills").exists())
        self.assertTrue((self.ag / "skills" / "delegating" / "SKILL.md").is_file())
        self.assertTrue((alt / "agents" / "skeptic.agent.md").is_file())
        self.assertTrue((alt / "hooks" / "delegation-framework.json").is_file())
        before = snapshot(self.tmp)
        self.ok(COPILOT_HOME=str(alt))
        self.assertEqual(snapshot(self.tmp), before)

    def test_global_excludes_gets_the_dir_once(self):
        ign = self.home / ".config" / "git" / "ignore"
        ign.parent.mkdir(parents=True)
        ign.write_text("*.swp")
        self.ok()
        self.ok()
        self.assertEqual(ign.read_text().splitlines(), ["*.swp", ".delegation/"])

    def test_global_excludes_follows_xdg_then_git_config(self):
        self.ok(XDG_CONFIG_HOME=str(self.tmp / "xdg"))
        self.assertEqual((self.tmp / "xdg" / "git" / "ignore").read_text(), ".delegation/\n")
        self.assertFalse((self.home / ".config").exists())
        (self.home / ".gitconfig").write_text("[core]\n\texcludesFile = ~/my-ignore\n")
        self.ok(XDG_CONFIG_HOME=str(self.tmp / "xdg"))
        self.assertEqual((self.home / "my-ignore").read_text(), ".delegation/\n")

    def test_a_failed_first_install_is_retryable(self):
        (self.cl / "agents").write_text("a file where a directory belongs")
        r = self.run_user()
        self.assertEqual(r.returncode, 1)
        self.assertIn("fix the cause above, then re-run", r.stderr)
        (self.cl / "agents").unlink()
        self.ok()
        self.assertTrue((self.cl / "agents" / "skeptic.md").is_file())

    def test_hooks_rehomed_to_another_home_are_still_the_framework_s(self):
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [USER_HOOK]}}))
        self.ok()
        other = self.tmp / "other" / ".claude" / "delegation-framework"
        text = self.settings.read_text().replace(self.fwp, other.as_posix())
        self.settings.write_text(text)
        self.ok()
        cfg = json.loads(self.settings.read_text())
        self.assertNotIn(other.as_posix(), json.dumps(cfg))
        for event, groups in cfg["hooks"].items():
            ours = [h for g in groups for h in g["hooks"] if "delegation-framework/scripts/" in h["command"]]
            self.assertEqual(len(ours), 1, event)
        self.assertEqual(cfg["hooks"]["PreToolUse"][0], USER_HOOK)

    def test_upgrade_deletes_files_removed_upstream_from_every_copy(self):
        src = copy_src(self.tmp / "src")
        script = src / "scripts" / "install-into.py"
        self.assertEqual(self.run_user(script).returncode, 0)
        gone = (self.cl / "skills" / "skeptical-review" / "SKILL.md", self.ag / "skills" / "skeptical-review" / "SKILL.md",
                self.cl / "commands" / "review-panel.md")
        for f in gone:
            self.assertTrue(f.is_file(), f)
        shutil.rmtree(src / "skills" / "skeptical-review")
        (src / "commands" / "review-panel.md").unlink()
        with open(src / "agents" / "skeptic.md", "a") as f:
            f.write("\nNEWER\n")
        r = self.run_user(script)
        self.assertEqual(r.returncode, 0, r.stderr)
        for f in gone:
            self.assertFalse(f.exists(), f)
        self.assertIn("NEWER", (self.cp / "agents" / "skeptic.agent.md").read_text())

    def test_copilot_home_expands_a_tilde(self):
        self.ok(COPILOT_HOME="~/alt")
        self.assertTrue((self.home / "alt" / "agents" / "skeptic.agent.md").is_file())
        self.assertFalse((self.tmp / "~").exists())

    def test_refuses_a_foreign_agents_skill(self):
        mine = self.ag / "skills" / "delegating" / "SKILL.md"
        mine.parent.mkdir(parents=True)
        mine.write_text("mine")
        before = snapshot(self.home)
        r = self.run_user()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("move or rename it, then re-run", r.stderr)
        self.assertEqual(snapshot(self.home), before)

    def test_upgrade_from_the_copilot_skills_layout_moves_the_skills(self):
        self.ok()
        old = self.cp / "skills" / "delegating" / "SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_bytes((self.ag / "skills" / "delegating" / "SKILL.md").read_bytes())
        man = self.fw / "INSTALL.json"
        m = json.loads(man.read_text())
        m["files"][".copilot/skills/delegating/SKILL.md"] = hashlib.sha256(old.read_bytes()).hexdigest()
        man.write_text(json.dumps(m))
        self.ok()
        self.assertFalse(old.exists())
        self.assertTrue((self.ag / "skills" / "delegating" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
