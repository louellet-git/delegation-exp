#!/usr/bin/env python3
"""Structural validation gate for the delegation-framework plugin repo.

Checks (all must pass):
  1. .claude-plugin/plugin.json is valid JSON with name/version/description,
     and name == "delegation-framework".
  2. The three skills exist and each SKILL.md has YAML frontmatter with
     name + description.
  3. agents/manager.md, agents/steward.md and agents/skeptic.md each exist
     with frontmatter (name, description, tools); agents/implementation-agent.md
     must NOT exist (implementers are briefed inline, one per slice, rather
     than defined as a reusable agent file); agents/director.md must NOT exist
     (the Director role was removed, the manager is the sole top-level
     orchestrator/spawner).
  4. The three command files exist with frontmatter carrying a description.
  5. hooks/hooks.json is valid JSON with a non-empty "hooks" object, and
     every script referenced via ${CLAUDE_PLUGIN_ROOT}/... exists in-repo.
  6. The required skill-referenced docs exist.
  7. Every relative markdown link in the tree resolves to an existing file.

Usage: python3 scripts/validate-structure.py [repo-root]
Exit codes: 0 = green, 1 = failures listed, 2 = usage/IO error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PLUGIN_ROOT_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\\\s]+)")

EXPECTED_SKILLS = ["delegating", "skeptical-review", "consolidating-review"]
EXPECTED_COMMANDS = ["delegate.md", "skeptic-review.md", "review-panel.md"]
EXPECTED_DOCS = [
    "operating-model.md",
    "roles.md",
    "lenses.md",
    "rubric.md",
    "conflict-avoidance-checklist.md",
    "example-run.md",
]

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def frontmatter_fields(path: Path) -> dict[str, str] | None:
    """Parse simple `key: value` frontmatter. Returns None if no frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fields: dict[str, str] = {}
    current_key = None
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            current_key = kv.group(1)
            fields[current_key] = kv.group(2).strip()
        elif current_key and line.startswith((" ", "\t")):
            # folded/continued scalar (e.g. `description: >-`)
            fields[current_key] = (fields[current_key] + " " + line.strip()).strip()
    return fields


def require_frontmatter(path: Path, required: list[str], label: str) -> None:
    fm = frontmatter_fields(path)
    if fm is None:
        err(f"{label}: missing YAML frontmatter block")
        return
    for field in required:
        if not fm.get(field):
            err(f"{label}: frontmatter missing or empty '{field}'")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    # 1. Manifest
    manifest = root / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        err("missing .claude-plugin/plugin.json")
    else:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            err(f".claude-plugin/plugin.json: invalid JSON ({exc})")
        else:
            for field in ("name", "version", "description"):
                if not data.get(field):
                    err(f".claude-plugin/plugin.json: missing or empty '{field}'")
            if data.get("name") not in (None, "delegation-framework"):
                err(".claude-plugin/plugin.json: name must be 'delegation-framework'")

    # 2. Skills
    for skill in EXPECTED_SKILLS:
        path = root / "skills" / skill / "SKILL.md"
        if not path.is_file():
            err(f"missing skills/{skill}/SKILL.md")
            continue
        require_frontmatter(path, ["name", "description"], f"skills/{skill}/SKILL.md")

    # 3. Agents
    skeptic = root / "agents" / "skeptic.md"
    if not skeptic.is_file():
        err("missing agents/skeptic.md")
    else:
        require_frontmatter(skeptic, ["name", "description", "tools"], "agents/skeptic.md")
    steward = root / "agents" / "steward.md"
    if not steward.is_file():
        err("missing agents/steward.md")
    else:
        require_frontmatter(steward, ["name", "description", "tools"], "agents/steward.md")
    manager = root / "agents" / "manager.md"
    if not manager.is_file():
        err("missing agents/manager.md")
    else:
        require_frontmatter(manager, ["name", "description", "tools"], "agents/manager.md")
    if (root / "agents" / "implementation-agent.md").exists():
        err(
            "agents/implementation-agent.md must not exist "
            "(implementers are briefed inline, one per slice, not defined as a "
            "reusable agent file)"
        )
    if (root / "agents" / "director.md").exists():
        err(
            "agents/director.md must not exist "
            "(the Director role was removed; the manager is the sole spawner)"
        )

    # 4. Commands
    for command in EXPECTED_COMMANDS:
        path = root / "commands" / command
        if not path.is_file():
            err(f"missing commands/{command}")
            continue
        require_frontmatter(path, ["description"], f"commands/{command}")

    # 5. Hooks
    hooks_file = root / "hooks" / "hooks.json"
    if not hooks_file.is_file():
        err("missing hooks/hooks.json")
    else:
        raw = hooks_file.read_text(encoding="utf-8")
        try:
            hooks_data = json.loads(raw)
        except json.JSONDecodeError as exc:
            err(f"hooks/hooks.json: invalid JSON ({exc})")
        else:
            if not isinstance(hooks_data.get("hooks"), dict) or not hooks_data["hooks"]:
                err("hooks/hooks.json: missing or empty 'hooks' object")
        for ref in PLUGIN_ROOT_REF_RE.finditer(raw):
            target = root / ref.group(1)
            if not target.is_file():
                err(f"hooks/hooks.json: referenced script does not exist: {ref.group(1)}")

    # 6. Skill-referenced docs
    for doc in EXPECTED_DOCS:
        if not (root / "docs" / doc).is_file():
            err(f"missing docs/{doc}")

    # 7. Relative markdown links resolve
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if any(part in {".git", "node_modules", "__pycache__"} for part in rel.parts):
            continue
        in_fence = False
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_RE.finditer(line):
                target = match.group(1)
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                if not (md.parent / path_part).exists():
                    err(f"{rel.as_posix()}: broken relative link -> {target}")

    if errors:
        print("STRUCTURAL VALIDATION: FAILED")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(errors)} failure(s).")
        return 1

    print("STRUCTURAL VALIDATION: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
