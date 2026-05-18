"""Latency log line format."""

from __future__ import annotations

from aftertone.timing import log_latency


def test_log_latency_writes_step_line(tmp_path, monkeypatch):
    import time

    hook_t0 = int(time.time() * 1000) - 50
    log_latency(
        tmp_path,
        "stdin_read",
        trace_id="abc",
        hook_t0_ms=hook_t0,
        bytes=100,
    )
    log_file = tmp_path / ".cursor" / "hooks" / "state" / "speak_summary-hook.log"
    text = log_file.read_text(encoding="utf-8")
    assert "latency step=stdin_read" in text
    assert "trace=abc" in text
    assert "since_hook_ms=" in text
    assert "bytes=100" in text
