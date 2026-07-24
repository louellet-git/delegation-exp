#!/usr/bin/env python3
"""SessionStart discoverability check for delegation-framework's soft deps.

delegation-framework composes with other plugins by invoking their skills BY
NAME. Nothing machine-readable enforces any of those dependencies, so this hook
probes the standard plugin locations and WARNS (via SessionStart
additionalContext) when something named in a seam table is not discoverable.

Scope of this build: only `superpowers` is probed. The loop mechanics live
there; without it the `delegating` skill has no implement -> review -> fix loop
to route to.

Companion frameworks referenced elsewhere in this tree are NOT probed, because
none of them is public — probing for something a consumer cannot install would
open every session with a warning about a plugin that does not exist for them.
Their probes were removed rather than left to fail silently, which is the same
distinction this framework draws everywhere else: a check that reports nothing
because there is nothing to check should not look like a check that passed.

Honest framing: this is a WARNING, NEVER A BLOCK. The hook surface cannot
guarantee skill resolution and does not pretend to. Every path below returns 0
and a missing dependency degrades to text in `additionalContext` - it can never
deny, stop, or fail a session. The probe is also best-effort: a nonstandard
install location is not found and produces a soft "could not locate" line
rather than certainty either way.

Always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PINNED_VERSION_RANGE = "6.1.x"

PINNED_SKILLS = [
    "subagent-driven-development",
    "dispatching-parallel-agents",
    "requesting-code-review",
    "receiving-code-review",
    "test-driven-development",
    "verification-before-completion",
    "brainstorming",
    "writing-plans",
    "executing-plans",
    "finishing-a-development-branch",
]

# Companion-framework probes are intentionally empty in this build: none of the
# companions is public, so there is nothing a consumer could install. Keeping the
# machinery (rather than deleting it) means re-enabling is a data change, not a
# code change, if one is ever published.
SIBLING_PLUGINS: list[dict] = []
DOC_REVIEW = None

# Plugin-cache layouts, best-effort. `{name}` is the plugin directory name.
SEARCH_GLOBS = [
    # marketplace cache layout: cache/<marketplace>/<name>/<version>/skills
    "cache/*/{name}/*/skills",
    "cache/*/{name}/skills",
    # other layouts, best-effort
    "*/{name}/skills",
    "*/{name}/*/skills",
]


def read_version(skills_dir: Path) -> str | None:
    manifest = skills_dir.parent / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def version_tuple(version: str | None) -> tuple[int, ...]:
    if not version:
        return ()
    parts: list[int] = []
    for chunk in version.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def find_skills_dir(
    plugins_root: Path,
    plugin_name: str,
    pinned_skills: list[str],
    version_prefix: str,
) -> Path | None:
    """Pick the best install of `plugin_name`: most pinned skills present, then
    the pinned version range, then the newest version (a cache may hold
    several)."""
    if not plugins_root.is_dir():
        return None
    best: tuple[tuple[int, int, tuple[int, ...]], Path] | None = None
    seen: set[Path] = set()
    for pattern in SEARCH_GLOBS:
        try:
            candidates = list(plugins_root.glob(pattern.format(name=plugin_name)))
        except OSError:
            continue
        for candidate in candidates:
            if not candidate.is_dir() or candidate in seen:
                continue
            seen.add(candidate)
            found = sum(
                1 for s in pinned_skills if (candidate / s / "SKILL.md").is_file()
            )
            version = read_version(candidate)
            in_range = 1 if version and version.startswith(version_prefix) else 0
            score = (found, in_range, version_tuple(version))
            if best is None or score > best[0]:
                best = (score, candidate)
    return best[1] if best else None


def emit_warning(text: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": text,
                }
            }
        )
    )


def check_superpowers(plugins_root: Path) -> list[str]:
    """The REQUIRED dependency. Returns warning fragments."""
    skills_dir = find_skills_dir(plugins_root, "superpowers", PINNED_SKILLS, "6.1.")

    if skills_dir is None:
        return [
            "could not locate a superpowers installation under the standard "
            f"plugin locations (best-effort probe of {plugins_root}). "
            "delegation-framework composes with superpowers "
            f"{PINNED_VERSION_RANGE} by skill name - install superpowers or the "
            "loop mechanics (subagent-driven-development, "
            "dispatching-parallel-agents, code review, ...) will be missing."
        ]

    warnings: list[str] = []
    missing = [s for s in PINNED_SKILLS if not (skills_dir / s / "SKILL.md").is_file()]
    version = read_version(skills_dir)

    if missing:
        warnings.append(
            f"delegation-framework composes with superpowers {PINNED_VERSION_RANGE}; "
            "the following required skills are not discoverable: "
            + ", ".join(missing)
            + ". Install superpowers or the loop mechanics will be missing."
        )
    if not (version and version.startswith("6.1.")):
        warnings.append(
            f"delegation-framework is validated against superpowers "
            f"{PINNED_VERSION_RANGE}; found version "
            f"{version or 'unknown'} at {skills_dir}. Skill names may have "
            "drifted - verify the seam table in skills/delegating/SKILL.md."
        )
    return warnings


def check_siblings(plugins_root: Path) -> list[str]:
    """The OPTIONAL sibling frameworks. Returns note fragments (never errors).

    Absence is normal and is never a defect: a sibling is wanted only when its
    kind of deliverable is in play.
    """
    absent: list[str] = []
    drifted: list[str] = []

    for sibling in SIBLING_PLUGINS:
        name = sibling["plugin"]
        skills_dir = find_skills_dir(
            plugins_root, name, sibling["skills"], sibling["version_prefix"]
        )
        if skills_dir is None:
            absent.append(f"{name} (needed for: {sibling['seam']})")
            continue
        missing = [
            s for s in sibling["skills"] if not (skills_dir / s / "SKILL.md").is_file()
        ]
        if missing:
            drifted.append(
                f"{name}: skills not discoverable: {', '.join(missing)} "
                f"(at {skills_dir})"
            )
        version = read_version(skills_dir)
        if not (version and version.startswith(sibling["version_prefix"])):
            drifted.append(
                f"{name}: seam table is pinned to {sibling['version_range']}, "
                f"found {version or 'unknown'} at {skills_dir} - skill names may "
                "have drifted; verify the sibling seam table in "
                "skills/delegating/SKILL.md."
            )

    if DOC_REVIEW is not None and not doc_review_present():
        absent.append(
            f"{DOC_REVIEW['framework']} (needed for: {DOC_REVIEW['seam']}; "
            "ships no plugin manifest - vendored by hand, so this probe only "
            "sees it under .claude/agents/ and only if its agents were not "
            "renamed during vendoring, which its README invites)"
        )

    notes: list[str] = []
    if absent:
        notes.append(
            "OPTIONAL sibling frameworks not discoverable: "
            + "; ".join(absent)
            + ". These are soft, by-name references from the sibling seam table "
            "in skills/delegating/SKILL.md. Nothing auto-discovers them and "
            "nothing registers them - a manager reads the seam table and invokes "
            "by name. Absence blocks nothing and is expected when that kind of "
            "deliverable is not in play; install or vendor the sibling before "
            "routing work to its seam."
        )
    notes.extend(drifted)
    return notes


def doc_review_present() -> bool:
    """Best-effort, and weaker than the plugin probes - see module docstring."""
    if DOC_REVIEW is None:
        return True  # nothing to probe for; never report it as absent
    roots: list[Path] = []
    try:
        roots.append(Path.cwd() / ".claude" / "agents")
    except OSError:
        pass
    roots.append(Path.home() / ".claude" / "agents")
    for root in roots:
        try:
            if any((root / agent).is_file() for agent in DOC_REVIEW["agents"]):
                return True
        except OSError:
            continue
    return False


def main() -> int:
    plugins_root = Path.home() / ".claude" / "plugins"

    required = check_superpowers(plugins_root)
    optional = check_siblings(plugins_root)

    parts: list[str] = []
    if required:
        parts.append("WARNING (delegation-framework): " + " ".join(required))
    if optional:
        parts.append(
            "WARNING (delegation-framework, optional seams): " + " ".join(optional)
        )

    if parts:
        emit_warning("\n\n".join(parts))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a discoverability probe must never fail a session
        sys.exit(0)
