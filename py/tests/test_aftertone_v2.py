"""Aftertone v2 package tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aftertone.config import summary_mode
from aftertone.hook_json import decode_hook_bytes, loads_hook_json
from aftertone.prepare import prepare_payload
from aftertone.summary import build_speakable_text
from aftertone.text_utils import heuristic_spoken


def test_summary_mode_tag_only_default():
    assert summary_mode({}) == "tag_only"
    assert summary_mode({"only_speak_spoken_summary": False}) == "tag_only"
    assert summary_mode({"summary_mode": "auto"}) == "auto"
    assert summary_mode({"summary_mode": "heuristic"}) == "heuristic"


def test_windows_path_json_escape():
    raw = r'{"text":"ok","transcript_path":"c:\Users\pc\file.jsonl"}'
    d = loads_hook_json(raw)
    assert "Users" in d["transcript_path"]


def test_utf16_hook_decode():
    payload = '{"text":"hello"}'
    utf16 = payload.encode("utf-16-le")
    assert loads_hook_json(decode_hook_bytes(utf16))["text"] == "hello"


def test_auto_summary_without_tag():
    cfg = {
        "enabled": True,
        "summary_mode": "auto",
        "min_chars": 5,
        "max_chars": 2000,
        "heuristic_max_sentences": 2,
        "heuristic_max_sentences_code_heavy": 1,
        "heuristic_code_fence_fraction": 0.35,
        "expression_mode": "off",
    }
    raw = "Sure. The daemon is running and tests passed."
    text, source = build_speakable_text(
        raw,
        cfg,
        "auto",
        min_chars=5,
        max_chars=2000,
        h_max=2,
        h_code_max=1,
        fence_thr=0.35,
        apply_expression_fn=lambda t, _s, _m: t,
    )
    assert source in ("heuristic", "excerpt")
    assert "daemon" in text.lower() or "tests" in text.lower()


def test_tag_only_silent_without_tag():
    cfg = {"summary_mode": "tag_only", "expression_mode": "off"}
    text, source = build_speakable_text(
        "No tag here, just prose.",
        cfg,
        "tag_only",
        min_chars=5,
        max_chars=2000,
        h_max=2,
        h_code_max=1,
        fence_thr=0.35,
        apply_expression_fn=lambda t, _s, _m: t,
    )
    assert source == "empty"
    assert text == ""


def test_prepare_payload_after_agent_response():
    hook = {
        "hook_event_name": "afterAgentResponse",
        "text": "Implemented v2. The hook now auto-summarizes when tags are missing.",
        "generation_id": "g1",
    }
    cfg = {
        "enabled": True,
        "summary_mode": "auto",
        "min_chars": 5,
        "max_chars": 2000,
        "total_step": 4,
        "speed": 1.0,
        "lang": "en",
        "mode": "queue",
        "heuristic_max_sentences": 2,
        "heuristic_max_sentences_code_heavy": 1,
        "heuristic_code_fence_fraction": 0.35,
        "expression_mode": "off",
    }
    out = prepare_payload(hook, cfg)
    assert out is not None
    assert "text" in out
    assert len(out["text"]) >= 5


def test_prepare_skips_non_after_agent():
    hook = {"hook_event_name": "stop", "text": "done"}
    cfg = {"enabled": True, "summary_mode": "auto"}
    assert prepare_payload(hook, cfg) is None
