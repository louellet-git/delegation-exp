#!/usr/bin/env python3
"""Install the framework into a repo so cloud sessions get it without /plugin install.

Usage: python3 scripts/install-into.py <target-repo-root>  (from an upstream clone only)
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
PATHS = ".claude-plugin agents skills commands hooks scripts docs test README.md LICENSE".split()
VENDOR = "vendor/delegation-framework"
LINK_RE = re.compile(r"(\]?\()([^()\s]+)(\))")
TICK_RE = re.compile(r"`([^`\s]+\.\w+)`")


def fail(msg):
    sys.exit(f"install-into: {msg}")


def key(h):
    """The framework script a hook runs, or None for a user hook."""
    cmd = h.get("command", "")
    return cmd.split('"')[1] if cmd.startswith(f'python3 "$CLAUDE_PROJECT_DIR/{VENDOR}/scripts/') else None


def rewrite(rel, vendor, dest):
    """Point links and (bare) paths at the vendored copy, `paths` at its project location, skill names at plain ones."""
    def find(path):
        for base in (os.path.dirname(rel), ""):
            hit = os.path.normpath(os.path.join(base, path)).replace(os.sep, "/")
            if hit.split("/")[0] in PATHS and (SRC / hit).exists():
                return hit

    def link(m):
        path, _, frag = m.group(2).partition("#")
        hit = find(path) if path and not re.match(r"[a-z]+:", path) else None
        if not hit:
            return m.group(0)
        new = os.path.relpath(vendor / hit, dest.parent).replace(os.sep, "/")
        return m.group(1) + new + ("#" + frag if frag else "") + m.group(3)

    def tick(m):
        hit = find(m.group(1))
        return f"`{VENDOR}/{hit}`" if hit else m.group(0)

    text = (SRC / rel).read_text(encoding="utf-8").replace("${CLAUDE_PLUGIN_ROOT}", VENDOR)
    text = TICK_RE.sub(tick, LINK_RE.sub(link, text)).replace("delegation-framework:", "")
    return text.encode("utf-8")


def main():
    if len(sys.argv) != 2:
        fail("usage: install-into.py <target-repo-root>")
    t = Path(sys.argv[1])
    if not t.is_dir():
        fail(f"not a directory: {t}")
    t = t.resolve()
    vendor, manifest = t / VENDOR, t / VENDOR / "INSTALL.json"
    settings, gi = t / ".claude" / "settings.json", t / ".gitignore"
    if any(p.parts[-2:] == ("vendor", "delegation-framework") for p in (t, *t.parents)) or SRC in (t, *t.parents) or vendor.resolve() in (SRC, *SRC.parents):
        fail(f"the target is inside, or contains, a vendored copy of this script, or is this script's own repo; run an upstream clone's script into another repo")
    if vendor.exists() and not manifest.is_file():
        fail(f"{vendor} exists without INSTALL.json: not written by this installer, or a partial install; delete it if it holds only a copy of this framework")
    try:
        mine = {t / k: h for k, h in json.loads(manifest.read_text())["files"].items()} if manifest.is_file() else {}
    except Exception as e:
        fail(f"cannot read {manifest}: {e!r}")

    new = {}
    for p in (*PATHS, "hooks/hooks.json", "hooks/session-start-context.md"):
        if not (SRC / p).exists():
            fail(f"{SRC / p} is missing from the source")
    for p in PATHS:
        for f in sorted((SRC / p).rglob("*")) if (SRC / p).is_dir() else [SRC / p]:
            if f.is_file() and "__pycache__" not in f.parts:
                new[vendor / f.relative_to(SRC)] = f.read_bytes()
    ctx = vendor / "hooks" / "session-start-context.md"
    new[ctx] = new[ctx].replace(b"delegation-framework:", b"")
    installed = [p for g in ("agents/*.md", "skills/*/SKILL.md", "commands/*.md") for p in sorted(SRC.glob(g)) if p.name != "manager.md"]
    for p in installed:
        rel = p.relative_to(SRC).as_posix()
        new[t / ".claude" / rel] = rewrite(rel, vendor, t / ".claude" / rel)
    digest = {d: hashlib.sha256(b).hexdigest() for d, b in new.items()}

    managed = {**new, **mine}
    for dest in (*managed, settings, gi, manifest):
        if dest.is_symlink():
            fail(f"{dest} was not written by this installer; move or rename it, then re-run")
        if dest in managed and dest.is_file():
            cur = hashlib.sha256(dest.read_bytes()).hexdigest()
            if cur not in (digest.get(dest), mine.get(dest)):
                if dest in mine:
                    fail(f"{dest} was modified since install; delete it to accept the new version")
                fail(f"{dest} was not written by this installer; move or rename it, then re-run")

    try:
        old = json.loads(settings.read_text()) if settings.is_file() else {}
        cfg = json.loads(json.dumps(old))
        ours = json.loads((SRC / "hooks" / "hooks.json").read_text().replace("${CLAUDE_PLUGIN_ROOT}", "$CLAUDE_PROJECT_DIR/" + VENDOR))["hooks"]
        hooks = cfg.setdefault("hooks", {})
        for event in {**hooks, **ours}:
            ship = {}  # framework script -> (shipped matcher, shipped hook)
            for g in ours.get(event, []):
                for h in g["hooks"]:
                    ship[key(h)] = (g.get("matcher"), h)
            prior, groups = hooks.get(event, []), []
            for g in prior:
                kept = []
                for h in g.get("hooks", []):
                    k = key(h)
                    if k is None:
                        kept.append(h)  # user hook: keep, in place
                    elif k in ship and g.get("matcher") == ship[k][0]:
                        kept.append(ship[k][1])  # framework hook under its shipped matcher: refresh in place
                    # else: stale, or under another matcher; re-added below with the shipped one
                if kept:
                    groups.append({**g, "hooks": kept})
                elif not g.get("hooks"):
                    groups.append(g)  # already empty before the merge: not ours to drop
            placed = {key(h) for g in groups for h in g.get("hooks", [])}
            for g in ours.get(event, []):
                todo = [h for h in g["hooks"] if key(h) not in placed]
                if todo:
                    groups.append({**g, "hooks": todo})
            if groups:
                hooks[event] = groups
            elif prior:
                del hooks[event]
    except (ValueError, AttributeError, TypeError) as e:
        fail(f"cannot merge hooks into {settings}: {e}")

    at = None  # the destination being written, named if the write fails
    try:
        for at in mine.keys() - new.keys():
            at.unlink(missing_ok=True)
        for at, data in new.items():
            at.parent.mkdir(parents=True, exist_ok=True)
            at.write_bytes(data)
        if cfg != old:
            at = settings
            settings.write_text(json.dumps(cfg, indent=2) + "\n")
        at = gi
        text = gi.read_text() if gi.is_file() else ""
        if ".delegation/" not in text.splitlines():
            gi.write_text(text + ("\n" if text and not text.endswith("\n") else "") + ".delegation/\n")
        try:
            git = lambda *a: subprocess.check_output(["git", "-C", str(SRC), *a], text=True).strip()
            commit = git("rev-parse", "HEAD") if (SRC / ".git").exists() and not git("status", "--porcelain") else None
        except (OSError, subprocess.CalledProcessError):
            commit = None
        at = manifest
        manifest.write_text(json.dumps({"source_commit": commit, "files": {d.relative_to(t).as_posix(): h for d, h in digest.items()}}, indent=2) + "\n")
    except OSError as e:
        fail(f"write failed on {at}: {e}\nfix the cause above, then re-run")
    print(f"installed delegation-framework into {t}; commit the result")


if __name__ == "__main__":
    main()
