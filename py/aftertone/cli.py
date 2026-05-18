#!/usr/bin/env python3
"""Cross-platform Aftertone v2 CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from aftertone.config import cfg_enabled, load_config, summary_mode
from aftertone.defaults import apply_install_defaults
from aftertone.doctor import run_doctor
from aftertone.paths import config_path, install_root, state_dir


def _repo(explicit: Path | None) -> Path:
    return install_root(explicit)


def _run_py_module(repo: Path, script: str, *args: str) -> int:
    py_dir = repo / "py"
    cmd = [sys.executable, str(py_dir / script), *args]
    return subprocess.call(cmd, cwd=str(py_dir))


def _run_uv(repo: Path, script: str, *args: str) -> int:
    py_dir = repo / "py"
    return subprocess.call(
        ["uv", "run", "python", script, *args],
        cwd=str(py_dir),
    )


def _invoke(repo: Path, script: str, *args: str) -> int:
    if (repo / "py" / ".venv").is_dir():
        return _run_uv(repo, script, *args)
    return _run_py_module(repo, script, *args)


def cmd_on(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "on")


def cmd_off(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "off")


def cmd_toggle(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "toggle")


def cmd_status(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    cfg = load_config(repo)
    port_file = state_dir(repo) / "tts-daemon.port"
    port = 8765
    if port_file.is_file():
        try:
            port = int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    daemon = "down"
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=0.5) as r:
            if r.status == 200:
                daemon = "up"
    except (urllib.error.URLError, OSError):
        pass
    print(
        json.dumps(
            {
                "tts_enabled": cfg_enabled(cfg),
                "summary_mode": summary_mode(cfg),
                "lang": cfg.get("lang", "en"),
                "voice_type": cfg.get("voice_type", ""),
                "daemon": daemon,
                "port": port,
                "install_root": str(repo),
            },
            indent=2,
        )
    )
    return 0


def cmd_restart(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    return _invoke(repo, "tts_daemon_ctl.py", "restart", "--repo-root", str(repo))


def cmd_repair(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    rc = _invoke(repo, "install_global_hooks.py", "--install-dir", str(repo))
    if rc != 0:
        return rc
    _invoke(repo, "speak_summary_toggle.py", "on")
    apply_install_defaults(config_path(repo))
    _invoke(repo, "sync_spoken_rule_lang.py")
    return cmd_restart(args)


def cmd_apply_defaults(args: argparse.Namespace) -> int:
    apply_install_defaults(config_path(_repo(args.repo_root)))
    return 0


def cmd_speak(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    cfg = load_config(repo)
    port = int(cfg.get("port", 8765))
    port_file = state_dir(repo) / "tts-daemon.port"
    if port_file.is_file():
        try:
            port = int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    payload = {
        "text": args.text,
        "totalStep": int(cfg.get("total_step", 8)),
        "speed": float(cfg.get("speed", 1.0)),
        "lang": str(cfg.get("lang", "en")),
        "mode": str(cfg.get("mode", "queue")).lower(),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/say",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.status)
            return 0
    except urllib.error.URLError as exc:
        print(f"speak failed: {exc}", file=sys.stderr)
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    return run_doctor(args.repo_root)


def cmd_prepare(args: argparse.Namespace) -> int:
    from aftertone.config import load_config
    from aftertone.hook_json import decode_hook_bytes, loads_hook_json
    from aftertone.prepare import prepare_payload

    path = Path(args.hook_json)
    hook = loads_hook_json(decode_hook_bytes(path.read_bytes()))
    repo = _repo(args.repo_root)
    out = prepare_payload(hook, load_config(repo), repo)
    if out:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("{}")
    return 0


def _config(repo: Path, *args: str) -> int:
    """Delegate to speak_summary_config.py (TOML edits; optional daemon restart)."""
    return _invoke(repo, "speak_summary_config.py", *args)


def cmd_set_lang(args: argparse.Namespace) -> int:
    return _config(_repo(args.repo_root), "set", "lang", args.code)


def cmd_set_speed(args: argparse.Namespace) -> int:
    return _config(_repo(args.repo_root), "set", "speed", args.value)


def cmd_set_mode(args: argparse.Namespace) -> int:
    return _config(_repo(args.repo_root), "set", "mode", args.mode)


def cmd_set_expression(args: argparse.Namespace) -> int:
    return _config(_repo(args.repo_root), "set", "expression", args.mode)


def cmd_set_voice(args: argparse.Namespace) -> int:
    extra: list[str] = []
    if args.restart:
        extra.append("--restart")
    if args.ensure:
        extra.append("--ensure")
    return _config(_repo(args.repo_root), "set", "voice", args.preset, *extra)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aftertone", description="Aftertone v2 CLI")
    parser.add_argument("--repo-root", type=Path, default=None, help="Install root")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, fn, help_text in (
        ("on", cmd_on, "Enable spoken TTS"),
        ("off", cmd_off, "Disable spoken TTS"),
        ("toggle", cmd_toggle, "Toggle spoken TTS"),
        ("status", cmd_status, "Show config and daemon status"),
        ("restart", cmd_restart, "Restart TTS daemon"),
        ("repair", cmd_repair, "Re-register hooks and set install defaults"),
        ("apply-defaults", cmd_apply_defaults, "Set tag_only + total_step 8 in speak_summary.toml"),
        ("doctor", cmd_doctor, "Diagnostics"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.set_defaults(func=fn)

    sp = sub.add_parser("speak", help="Speak text via daemon")
    sp.add_argument("text", help="Text to synthesize")
    sp.set_defaults(func=cmd_speak)

    pp = sub.add_parser("prepare", help="Prepare payload from hook JSON file")
    pp.add_argument("hook_json", help="Path to hook JSON")
    pp.set_defaults(func=cmd_prepare)

    pset = sub.add_parser("set", help="Update speak_summary.toml (no agent-side TOML edits)")
    set_sub = pset.add_subparsers(dest="setting", required=True)

    pl = set_sub.add_parser("lang", help="Set lang and sync spoken-summary rule")
    pl.add_argument("code", help="Language code (e.g. en, fr)")
    pl.set_defaults(func=cmd_set_lang)

    ps = set_sub.add_parser("speed", help="Set playback speed (no daemon restart)")
    ps.add_argument("value", help="Float 0.5–2.0")
    ps.set_defaults(func=cmd_set_speed)

    pm = set_sub.add_parser("mode", help="Set queue or interrupt (no daemon restart)")
    pm.add_argument("mode", choices=("queue", "interrupt"))
    pm.set_defaults(func=cmd_set_mode)

    pe = set_sub.add_parser("expression", help="Set expression_mode (no daemon restart)")
    pe.add_argument("mode", help="off, subtle, expressive, or passthrough")
    pe.set_defaults(func=cmd_set_expression)

    pv = set_sub.add_parser("voice", help="Set voice preset (restarts daemon by default)")
    pv.add_argument("preset", help="Preset id (F4, M1) or display name (Sara)")
    pv.add_argument(
        "--no-restart",
        action="store_true",
        help="Skip daemon restart (not recommended)",
    )
    pv.add_argument(
        "--ensure",
        action="store_true",
        help="Bootstrap voice assets if missing",
    )

    def cmd_set_voice_cli(ns: argparse.Namespace) -> int:
        ns.restart = not ns.no_restart
        return cmd_set_voice(ns)

    pv.set_defaults(func=cmd_set_voice_cli)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
