#!/usr/bin/env python3
"""Start/stop/status for py/tts_daemon.py (Aftertone; PID + port under .cursor/hooks/state/)."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]


def _repo_root() -> Path:
    from aftertone_paths import resolve_repo_root

    return resolve_repo_root()


def _py_dir() -> Path:
    return Path(__file__).resolve().parent


def _state_dir(repo: Path) -> Path:
    d = repo / ".cursor" / "hooks" / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _pid_path(repo: Path) -> Path:
    return _state_dir(repo) / "tts-daemon.pid"


def _port_path(repo: Path) -> Path:
    return _state_dir(repo) / "tts-daemon.port"


def _hook_toml(repo: Path) -> Path:
    return repo / ".cursor" / "hooks" / "speak_summary.toml"


def _load_hook_config(repo: Path) -> dict:
    p = _hook_toml(repo)
    if not p.is_file():
        return {}
    with p.open("rb") as f:
        return tomllib.load(f)


def _voice_style_from_cfg(cfg: dict) -> str:
    """Explicit voice_style path, or ../assets/voice_styles/<voice_type>.json relative to py/."""
    vs = str(cfg.get("voice_style", "") or "").strip()
    if vs:
        return vs
    vt = str(cfg.get("voice_type", "M1") or "M1").strip() or "M1"
    if not vt.lower().endswith(".json"):
        vt = f"{vt}.json"
    return f"../assets/voice_styles/{vt}"


def _voice_style_abs(repo: Path, cfg: dict) -> Path:
    rel = _voice_style_from_cfg(cfg)
    p = Path(rel)
    if p.is_absolute():
        return p.resolve()
    return (_py_dir() / p).resolve()


def _listener_pid_on_port(port: int) -> int | None:
    """PID listening on 127.0.0.1:port (Linux ss), or None."""
    try:
        proc = subprocess.run(
            ["ss", "-tlnp", f"sport = :{port}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except FileNotFoundError:
        return None
    m = re.search(r"pid=(\d+)", proc.stdout or "")
    return int(m.group(1)) if m else None


def _kill_pid(pid: int, *, label: str = "tts_daemon") -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(50):
        time.sleep(0.1)
        if not _pid_alive(pid):
            print(f"{label}: stopped pid={pid}")
            return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    print(f"{label}: killed pid={pid} (SIGKILL)")


def _fetch_healthz(port: int) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _verify_daemon_ready(port: int, expected_voice: Path) -> tuple[bool, str, int | None]:
    """Return (ok, error_message, listener_pid)."""
    listener = _listener_pid_on_port(port)
    if listener is None:
        return False, f"nothing listening on port {port}", None
    data = _fetch_healthz(port)
    if not data:
        return False, "healthz unreachable", listener
    voice = str(data.get("voice", "") or "")
    if not voice:
        return False, "healthz missing voice field", listener
    try:
        if Path(voice).resolve() != expected_voice.resolve():
            return (
                False,
                f"healthz voice={voice!r} expected {expected_voice!r} "
                "(stale daemon on this port? run: tts_daemon_ctl.py restart)",
                listener,
            )
    except OSError:
        return False, f"healthz voice path invalid: {voice!r}", listener
    return True, "", listener


def _read_pid(repo: Path) -> int | None:
    pp = _pid_path(repo)
    if not pp.is_file():
        return None
    try:
        return int(pp.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def _read_port(repo: Path) -> int | None:
    pp = _port_path(repo)
    if not pp.is_file():
        return None
    try:
        return int(pp.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _uv_cmd(py_dir: Path, args: list[str]) -> list[str]:
    import shutil

    uv = shutil.which("uv")
    if uv:
        return [uv, "run", "--directory", str(py_dir), "python"] + args
    return [sys.executable] + args


def _print_hook_toml_summary(repo: Path) -> None:
    cfg = _load_hook_config(repo)
    p = _hook_toml(repo)
    if not p.is_file():
        print(f"speak_summary.toml: missing ({p})")
        return
    if not cfg:
        print(f"speak_summary.toml: empty or unreadable ({p})")
        return
    vs = _voice_style_from_cfg(cfg)
    vt = str(cfg.get("voice_type", "M1") or "M1").strip()
    try:
        from voice_presets import voice_display_name

        voice_hint = f"{voice_display_name(vt)} ({vt})"
    except ImportError:
        voice_hint = vt
    print(
        f"speak_summary.toml (disk): port={cfg.get('port', 8765)!r} "
        f"voice={voice_hint!r} voice_style={vs!r} lang={cfg.get('lang', 'en')!r} "
        f"speed={cfg.get('speed', 1.05)!r} use_gpu={cfg.get('use_gpu', False)!r}"
    )
    print(
        "toml hint: port / onnx_dir / voice / use_gpu → restart daemon to apply. "
        "speed / lang / total_step / max_chars / heuristics / enabled / quiet_hours → each hook, no restart."
    )


def cmd_status(repo: Path) -> int:
    _print_hook_toml_summary(repo)
    pid = _read_pid(repo)
    port = _read_port(repo)
    if pid is None or not _pid_alive(pid):
        print("tts_daemon: not running")
        return 1
    print(
        f"tts_daemon: running pid={pid} port={port} "
        "(POST /say uses this port file; if it disagrees with TOML, see port_mismatch in speak_summary-hook.log)"
    )
    if port:
        try:
            import urllib.request

            u = urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2)
            print(u.read().decode()[:500])
        except Exception as e:
            print(f"healthz: {e}")
    return 0


def cmd_stop(repo: Path) -> int:
    cfg = _load_hook_config(repo)
    port = int(cfg.get("port", 8765)) if cfg else 8765
    pid = _read_pid(repo)
    port_pid = _listener_pid_on_port(port)
    stopped_any = False

    if pid is not None and _pid_alive(pid):
        _kill_pid(pid)
        stopped_any = True
    elif pid is not None:
        _pid_path(repo).unlink(missing_ok=True)
        print("tts_daemon: stale pid file removed")

    if port_pid is not None and port_pid != pid:
        print(
            f"tts_daemon: freeing port {port} (foreign listener pid={port_pid})",
            file=sys.stderr,
        )
        _kill_pid(port_pid, label="tts_daemon (port)")
        stopped_any = True
        for _ in range(30):
            if _listener_pid_on_port(port) is None:
                break
            time.sleep(0.1)

    if not stopped_any and port_pid is None:
        print("tts_daemon: not running")
    elif stopped_any:
        print("tts_daemon: stopped")
    _pid_path(repo).unlink(missing_ok=True)
    return 0


def cmd_start(repo: Path, port_override: int | None) -> int:
    cfg = _load_hook_config(repo)
    port = port_override or int(cfg.get("port", 8765))
    expected_voice = _voice_style_abs(repo, cfg)
    pid = _read_pid(repo)
    if pid is not None and _pid_alive(pid):
        ok, err, _listener = _verify_daemon_ready(port, expected_voice)
        if ok:
            print(f"tts_daemon: already running pid={pid} voice={expected_voice.name}")
            return 0
        print(f"tts_daemon: running but wrong ({err}); restarting", file=sys.stderr)
        cmd_stop(repo)

    port_pid = _listener_pid_on_port(port)
    if port_pid is not None:
        print(
            f"tts_daemon: port {port} still in use by pid {port_pid}; stopping it first",
            file=sys.stderr,
        )
        _kill_pid(port_pid, label="tts_daemon (port)")
        for _ in range(30):
            if _listener_pid_on_port(port) is None:
                break
            time.sleep(0.1)

    use_gpu = bool(cfg.get("use_gpu", False))
    onnx_dir = str(cfg.get("onnx_dir", "../assets/onnx"))
    voice_style = _voice_style_from_cfg(cfg)
    lang = str(cfg.get("lang", "en"))

    py_dir = _py_dir()
    daemon_args = [
        str(py_dir / "tts_daemon.py"),
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--onnx-dir",
        onnx_dir,
        "--voice-style",
        voice_style,
        "--lang",
        lang,
        "--repo-root",
        str(repo),
    ]
    if use_gpu:
        daemon_args.append("--use-gpu")

    log_path = _state_dir(repo) / "tts-daemon.log"
    log_f = open(log_path, "a", encoding="utf-8")
    cmd = _uv_cmd(py_dir, daemon_args)
    proc = subprocess.Popen(
        cmd,
        cwd=str(py_dir),
        stdin=subprocess.DEVNULL,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _port_path(repo).write_text(str(port), encoding="utf-8")
    # Wait until something on :port reports the expected voice (uv run → child owns the port)
    deadline = time.monotonic() + 120.0
    ok = False
    last_err = "timeout"
    listener_pid: int | None = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            # uv wrapper exited; child may still be loading — keep polling healthz briefly
            if _listener_pid_on_port(port) is None:
                print(
                    f"tts_daemon: process exited early code={proc.poll()} log={log_path}"
                )
                _pid_path(repo).unlink(missing_ok=True)
                return 1
        ready, last_err, listener_pid = _verify_daemon_ready(port, expected_voice)
        if ready and listener_pid is not None:
            ok = True
            break
        time.sleep(0.3)
    if not ok:
        print(f"tts_daemon: not ready ({last_err}); check {log_path}", file=sys.stderr)
        _pid_path(repo).unlink(missing_ok=True)
        return 1
    _pid_path(repo).write_text(str(listener_pid), encoding="utf-8")
    try:
        from voice_presets import voice_display_name

        voice_msg = f"{voice_display_name(expected_voice.stem)} ({expected_voice.stem})"
    except ImportError:
        voice_msg = expected_voice.name
    print(f"tts_daemon: started pid={listener_pid} port={port} voice={voice_msg}")
    return 0


def cmd_restart(repo: Path, port: int | None) -> int:
    cmd_stop(repo)
    return cmd_start(repo, port)


def main() -> None:
    ap = argparse.ArgumentParser(description="Control Aftertone tts_daemon.")
    ap.add_argument("command", choices=("start", "stop", "status", "restart"))
    ap.add_argument("--repo-root", type=str, default="", help="Repo root (default: infer).")
    ap.add_argument("--port", type=int, default=0, help="Override port for start/restart.")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve() if args.repo_root else _repo_root()
    port = args.port or None
    if args.command == "status":
        raise SystemExit(cmd_status(repo))
    if args.command == "stop":
        raise SystemExit(cmd_stop(repo))
    if args.command == "start":
        raise SystemExit(cmd_start(repo, port))
    if args.command == "restart":
        raise SystemExit(cmd_restart(repo, port))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
