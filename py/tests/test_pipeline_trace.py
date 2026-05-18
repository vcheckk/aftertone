"""Pipeline trace helpers."""

from __future__ import annotations

import json
import time

from aftertone.pipeline_trace import probe_transcript, scan_cursor_envelope


def test_scan_cursor_envelope():
    hook = {
        "hook_event_name": "afterAgentResponse",
        "text": "x\n<spoken_summary>Hi!!</spoken_summary>",
        "generation_id": "g1",
    }
    meta = scan_cursor_envelope(hook)
    assert meta["has_spoken_summary_close"] is True
    assert meta["generation_id"] == "g1"


def test_probe_transcript_mtime_gap(tmp_path):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(
        json.dumps({"role": "assistant", "content": "ok"}) + "\n",
        encoding="utf-8",
    )
    hook_t0 = int(time.time() * 1000)
    probe = probe_transcript(str(transcript), hook_t0)
    assert "transcript_mtime_ms" in probe
    assert "hook_minus_transcript_mtime_ms" in probe
    assert probe["hook_minus_transcript_mtime_ms"] >= 0
