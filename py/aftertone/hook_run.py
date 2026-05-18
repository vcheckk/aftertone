#!/usr/bin/env python3
"""Cursor hook: read stdin, POST to warm daemon /hook (or fallback prepare + /say)."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

_PY_ROOT = Path(__file__).resolve().parent.parent
if str(_PY_ROOT) not in sys.path:
    sys.path.insert(0, str(_PY_ROOT))

from aftertone.hook_json import decode_hook_bytes, loads_hook_json
from aftertone.paths import install_root, state_dir
from aftertone.pipeline_trace import (
    PipelineTracer,
    healthz_probe,
    probe_transcript,
    scan_cursor_envelope,
)


def _hook_log(repo: Path, msg: str) -> None:
    log_path = state_dir(repo) / "speak_summary-hook.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")


def _daemon_port(repo: Path) -> int:
    from aftertone.config import load_config

    cfg = load_config(repo)
    port = int(cfg.get("port", 8765))
    port_file = state_dir(repo) / "tts-daemon.port"
    if port_file.is_file():
        try:
            port = int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    return port


def _ensure_daemon(repo: Path, tr: PipelineTracer) -> None:
    port = _daemon_port(repo)
    tr.step("healthz_probe_start", port=port)
    ok, probe_ms = healthz_probe(port)
    tr.step("healthz_probe_done", port=port, ok=ok, probe_ms=probe_ms)
    if ok:
        tr.step("daemon_already_up", port=port)
        return
    tr.step("daemon_bootstrap_start", port=port)
    _hook_log(repo, f"daemon_bootstrap port={port}")
    py_root = repo / "py"
    vpy = py_root / ".venv" / "Scripts" / "python.exe"
    if not vpy.is_file():
        vpy = py_root / ".venv" / "bin" / "python"
    ctl = py_root / "tts_daemon_ctl.py"
    if vpy.is_file() and ctl.is_file():
        import subprocess

        log_path = state_dir(repo) / "tts-daemon-bootstrap.log"
        with open(log_path, "a", encoding="utf-8") as boot_log:
            subprocess.run(
                [str(vpy), str(ctl), "start", "--repo-root", str(repo)],
                cwd=str(py_root),
                stdout=boot_log,
                stderr=subprocess.STDOUT,
                timeout=120,
                check=False,
            )
    for i in range(120):
        ok, _ = healthz_probe(port)
        if ok:
            _hook_log(repo, "daemon_bootstrap_ok")
            tr.step("daemon_bootstrap_ok", port=port, wait_loops=i + 1)
            return
        time.sleep(0.5)
    _hook_log(repo, "daemon_bootstrap_failed")
    tr.step("daemon_bootstrap_failed", port=port)


def _post_hook(
    repo: Path, body: bytes, tr: PipelineTracer
) -> tuple[int, int, str | None]:
    port = _daemon_port(repo)
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/hook",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Aftertone-Trace": tr.trace_id,
            "X-Aftertone-Hook-T0-Ms": str(tr.hook_t0_ms),
        },
        method="POST",
    )
    tr.step("post_hook_start", port=port, body_bytes=len(body))
    last_exc: Exception | None = None
    job_id: str | None = None
    for attempt in range(3):
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                post_ms = int((time.perf_counter() - t0) * 1000)
                try:
                    raw = resp.read()
                    if raw:
                        data = json.loads(raw.decode("utf-8"))
                        job_id = data.get("id")
                except Exception:
                    pass
                tr.set_job_id(job_id)
                tr.step(
                    "post_hook_ack",
                    post_ms=post_ms,
                    http=resp.status,
                    attempt=attempt + 1,
                )
                return resp.status, post_ms, job_id
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                tr.step("post_hook_404", attempt=attempt + 1)
                return 404, 0, None
            last_exc = exc
            tr.step("post_hook_error", attempt=attempt + 1, error=str(exc)[:200])
        except Exception as exc:
            last_exc = exc
            tr.step("post_hook_error", attempt=attempt + 1, error=str(exc)[:200])
        time.sleep(0.15)
    raise last_exc or OSError("post /hook failed")


def _fallback_prepare_post(repo: Path, text: str, tr: PipelineTracer) -> tuple[int, int]:
    from aftertone.config import load_config
    from aftertone.prepare import post_say_payload, prepare_payload

    tr.step("fallback_prepare_start")
    hook = loads_hook_json(text)
    cfg = load_config(repo)
    out = prepare_payload(hook, cfg, repo)
    if out is None:
        tr.step("fallback_prepare_skip")
        return 0, 0
    tr.step("fallback_prepare_ok", payload_chars=len(out.get("text", "") or ""))
    tr.step("fallback_post_say_start")
    status, post_ms = post_say_payload(repo, out)
    tr.step("fallback_post_say_done", http=status, post_ms=post_ms)
    return status, post_ms


def main() -> int:
    hook_t0_ms = int(time.time() * 1000)
    trace_id = str(uuid.uuid4())
    t0 = time.perf_counter()

    if len(sys.argv) != 2 or sys.argv[1] != "--stdin":
        print("usage: python -m aftertone.hook_run --stdin", file=sys.stderr)
        return 2

    raw = sys.stdin.buffer.read()

    try:
        root = install_root()
    except FileNotFoundError as exc:
        print(f"{exc}", file=sys.stderr)
        print("{}")
        return 0

    tr = PipelineTracer(root, trace_id, hook_t0_ms)
    tr.step("hook_process_start")

    if not raw.strip():
        tr.step("stdin_empty")
        tr.finish_hook(http=0, hook_wall_ms=0)
        print("{}")
        return 0

    tr.step("stdin_read", bytes=len(raw))

    text = decode_hook_bytes(raw).lstrip("\ufeff")
    tr.step("stdin_decoded", text_chars=len(text))

    try:
        hook = loads_hook_json(text)
        tr.step("hook_json_parsed")
    except json.JSONDecodeError as exc:
        tr.step("hook_json_invalid", error=str(exc)[:120])
        tr.finish_hook(http=0, hook_wall_ms=int((time.perf_counter() - t0) * 1000), error="json")
        print("{}")
        return 0

    meta = scan_cursor_envelope(hook)
    tr.set_cursor_meta(meta)
    tr.step(
        "cursor_envelope",
        generation_id=meta.get("generation_id"),
        conversation_id=meta.get("conversation_id"),
        text_len=meta.get("text_len"),
        has_spoken_close=meta.get("has_spoken_summary_close"),
    )

    transcript_path = hook.get("transcript_path")
    if isinstance(transcript_path, str) and transcript_path.strip():
        probe = probe_transcript(transcript_path.strip(), hook_t0_ms)
        tr.set_transcript_probe(probe)
    else:
        tr.step("transcript_probe_skipped", reason="no_transcript_path")

    body = text.encode("utf-8")
    _hook_log(
        root,
        f"hook_invoked hook_json_bytes={len(body)} via=hook_run trace={trace_id}",
    )

    tr.step("install_root_ok", install=str(root))

    _ensure_daemon(root, tr)

    http_status = 0
    post_ms = 0
    job_id: str | None = None
    try:
        http_status, post_ms, job_id = _post_hook(root, body, tr)
    except Exception as exc:
        if http_status != 404:
            try:
                http_status, post_ms = _fallback_prepare_post(root, text, tr)
            except Exception as exc2:
                wall_ms = int((time.perf_counter() - t0) * 1000)
                tr.step("hook_failed", post_error=str(exc)[:120], fallback=str(exc2)[:120])
                tr.finish_hook(http=0, hook_wall_ms=wall_ms, error="post")
                _hook_log(
                    root,
                    f"hook_metrics post_ms=0 http=0 hook_wall_ms={wall_ms} "
                    f"post_error={exc}; fallback={exc2}",
                )
                print("{}")
                return 0

    if http_status == 404:
        try:
            http_status, post_ms = _fallback_prepare_post(root, text, tr)
        except Exception as exc:
            wall_ms = int((time.perf_counter() - t0) * 1000)
            tr.finish_hook(http=0, hook_wall_ms=wall_ms, error="404_fallback")
            _hook_log(
                root,
                f"hook_metrics post_ms=0 http=0 hook_wall_ms={wall_ms} post_error={exc}",
            )
            print("{}")
            return 0

    wall_ms = int((time.perf_counter() - t0) * 1000)
    tr.step("hook_process_done", hook_wall_ms=wall_ms, http=http_status, post_ms=post_ms)
    tr.finish_hook(http=http_status, hook_wall_ms=wall_ms)
    _hook_log(
        root,
        f"hook_metrics post_ms={post_ms} http={http_status} hook_wall_ms={wall_ms} "
        f"trace={trace_id} job_id={job_id or '-'}",
    )
    if http_status in (200, 202):
        _hook_log(root, f"post_say_done port={_daemon_port(root)} via=hook_run")
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
