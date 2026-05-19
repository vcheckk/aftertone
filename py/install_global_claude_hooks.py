#!/usr/bin/env python3
"""Register Aftertone user-level Claude Code hooks (~/.claude/settings.json)."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
import time
from pathlib import Path

_MARKER = "aftertone-claude-speak-on-stop"
_STOP_CMD = "bash __AFTERTONE_CLAUDE_STOP__"
_DOCTOR_CMD = "bash __AFTERTONE_CLAUDE_DOCTOR__"


def _strip_aftertone_entries(hooks: dict) -> dict:
    out: dict = {}
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            out[event] = entries
            continue
        kept_groups: list = []
        for group in entries:
            if not isinstance(group, dict):
                kept_groups.append(group)
                continue
            inner = group.get("hooks")
            if not isinstance(inner, list):
                kept_groups.append(group)
                continue
            filtered = [
                h
                for h in inner
                if isinstance(h, dict)
                and _MARKER not in (h.get("command") or "")
            ]
            if filtered:
                g = dict(group)
                g["hooks"] = filtered
                kept_groups.append(g)
        if kept_groups:
            out[event] = kept_groups
    return out


def _merge_hooks(existing: dict, fragment: dict) -> dict:
    out = dict(existing)
    hooks = _strip_aftertone_entries(dict(out.get("hooks") or {}))
    frag_hooks = fragment.get("hooks") or {}
    for event, entries in frag_hooks.items():
        cur = list(hooks.get(event) or [])
        seen_cmds: set[str] = set()
        for group in cur:
            if not isinstance(group, dict):
                continue
            for h in group.get("hooks") or []:
                if isinstance(h, dict) and h.get("command"):
                    seen_cmds.add(str(h["command"]))
        for group in entries:
            if not isinstance(group, dict):
                continue
            g = dict(group)
            inner = []
            for h in g.get("hooks") or []:
                if not isinstance(h, dict):
                    continue
                cmd = h.get("command")
                if cmd in seen_cmds:
                    continue
                inner.append(h)
                if cmd:
                    seen_cmds.add(str(cmd))
            if inner:
                g["hooks"] = inner
                cur.append(g)
        hooks[event] = cur
    out["hooks"] = hooks
    return out


_CLAUDE_WRAPPER_SCRIPTS: tuple[tuple[str, str], ...] = (
    ("activate-aftertone.sh", "aftertone-activate.sh"),
    ("aftertone-off.sh", "aftertone-off.sh"),
    ("aftertone-status.sh", "aftertone-status.sh"),
    ("aftertone-toggle.sh", "aftertone-toggle.sh"),
    ("aftertone-restart.sh", "aftertone-restart.sh"),
    ("aftertone-doctor.sh", "aftertone-doctor.sh"),
    ("aftertone-repair.sh", "aftertone-repair.sh"),
)

_AFTERTONE_BASH_ALLOW: tuple[str, ...] = tuple(
    f"Bash(bash ~/.cursor/hooks/{dest})" for _, dest in _CLAUDE_WRAPPER_SCRIPTS
)


def _merge_permissions(existing: dict) -> dict:
    """Pre-approve slash-command !`bash …` hooks (no prompt with disable-model-invocation)."""
    out = dict(existing)
    perms = dict(out.get("permissions") or {})
    allow = list(perms.get("allow") or [])
    seen = {str(x) for x in allow}
    for rule in _AFTERTONE_BASH_ALLOW:
        if rule not in seen:
            allow.append(rule)
            seen.add(rule)
    perms["allow"] = allow
    out["permissions"] = perms
    return out


def _substitute_commands(obj: object, stop: str, doctor: str) -> object:
    if isinstance(obj, dict):
        return {
            k: _substitute_commands(v, stop, doctor) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_substitute_commands(x, stop, doctor) for x in obj]
    if isinstance(obj, str):
        return (
            obj.replace(_STOP_CMD, stop)
            .replace(_DOCTOR_CMD, doctor)
            .replace("__AFTERTONE_CLAUDE_STOP__", stop)
            .replace("__AFTERTONE_CLAUDE_DOCTOR__", doctor)
        )
    return obj


def install_global_claude(*, install_dir: Path, dry_run: bool = False) -> None:
    install_dir = install_dir.expanduser().resolve()
    marker = install_dir / "py" / "speak_summary_prepare.py"
    if not marker.is_file():
        raise SystemExit(f"not an Aftertone install: {install_dir}")

    template_dir = install_dir / "scripts" / "claude-global"
    stop_src = template_dir / "aftertone-claude-speak-on-stop.sh"
    doctor_src = template_dir / "aftertone-claude-doctor-quiet.sh"
    common_src = template_dir / "_aftertone_common.sh"
    fragment_src = template_dir / "hooks.json"

    user_claude = Path.home() / ".claude"
    user_hooks = Path.home() / ".cursor" / "hooks"
    settings_json = user_claude / "settings.json"

    if not stop_src.is_file() or not fragment_src.is_file():
        raise SystemExit(f"missing templates under {template_dir}")

    dest_stop = user_hooks / "aftertone-claude-speak-on-stop.sh"
    dest_doctor = user_hooks / "aftertone-claude-doctor-quiet.sh"
    stop_cmd = f'bash "{dest_stop.resolve()}"'
    doctor_cmd = f'bash "{dest_doctor.resolve()}"'

    if dry_run:
        print(f"would copy hooks → {dest_stop}, {dest_doctor}")
        print(f"would merge {settings_json}")
        return

    user_hooks.mkdir(parents=True, exist_ok=True)
    for src, target in (
        (stop_src, dest_stop),
        (doctor_src, dest_doctor),
        (common_src, user_hooks / "_aftertone_common.sh"),
    ):
        if not src.is_file():
            continue
        shutil.copy2(src, target)
    for src_name, dest_name in _CLAUDE_WRAPPER_SCRIPTS:
        src = template_dir / src_name
        target = user_hooks / dest_name
        if not src.is_file():
            continue
        shutil.copy2(src, target)
        if sys.platform != "win32":
            target.chmod(
                target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )

    fragment = json.loads(fragment_src.read_text(encoding="utf-8-sig"))
    fragment = _substitute_commands(fragment, stop_cmd, doctor_cmd)

    if settings_json.is_file():
        existing = json.loads(settings_json.read_text(encoding="utf-8-sig"))
        backup = settings_json.with_suffix(f".json.bak.{int(time.time())}")
        shutil.copy2(settings_json, backup)
        merged = _merge_hooks(existing, fragment)
        print(f"backup: {backup}")
    else:
        user_claude.mkdir(parents=True, exist_ok=True)
        merged = fragment
    merged = _merge_permissions(merged)

    settings_json.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    skill_src = install_dir / "claude-plugin" / "aftertone" / "skills" / "spoken-summary" / "SKILL.md"
    if skill_src.is_file():
        skill_dest = user_claude / "skills" / "spoken-summary"
        skill_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_src, skill_dest / "SKILL.md")

    # Session rule (loaded every turn) — skills alone are optional and often skipped.
    rule_src = install_dir / "scripts" / "claude-global" / "spoken-summary.md"
    if rule_src.is_file():
        user_rule = user_claude / "rules" / "spoken-summary.md"
        user_rule.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rule_src, user_rule)
        project_rule = install_dir / ".claude" / "rules" / "spoken-summary.md"
        project_rule.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rule_src, project_rule)

    print(f"Global Claude Code hooks: {settings_json}")
    print(f"Install root: {install_dir}")
    print(
        "In Claude: `/aftertone_on`, `/aftertone_status`, `/aftertone_lang`, … "
        "(see docs/adapters/claude.md)."
    )


def main() -> None:
    p = argparse.ArgumentParser(
        description="Install Aftertone user-level Claude Code hooks."
    )
    p.add_argument("--install-dir", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    install_global_claude(install_dir=args.install_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
