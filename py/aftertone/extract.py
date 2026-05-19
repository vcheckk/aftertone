"""Resolve assistant text from hook JSON and transcript files."""

from __future__ import annotations

import json
import os
from pathlib import Path

from aftertone.spoken_tag import parse_spoken_summary


def assistant_text_blocks(lines: list[str]) -> str:
    last_assistant: dict | None = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("role") != "assistant":
            continue
        last_assistant = obj
    if not last_assistant:
        return ""
    if isinstance(last_assistant.get("content"), str):
        return str(last_assistant["content"]).strip()
    msg = last_assistant.get("message")
    if isinstance(msg, str):
        return msg.strip()
    if not isinstance(msg, dict):
        return ""
    parts = msg.get("content")
    if isinstance(parts, str):
        return parts.strip()
    if not isinstance(parts, list):
        return ""
    texts: list[str] = []
    for p in parts:
        if isinstance(p, dict) and p.get("type") == "text":
            t = p.get("text")
            if isinstance(t, str) and t.strip():
                texts.append(t.strip())
    return "\n".join(texts)


def hook_inline_text(hook: dict) -> str:
    # Claude Code Stop / SubagentStop (https://code.claude.com/docs/en/hooks#stop)
    lam = hook.get("last_assistant_message")
    if isinstance(lam, str) and lam.strip():
        return lam.strip()
    for key in ("text", "response", "message", "content"):
        v = hook.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def transcript_assistant_text(hook: dict) -> str:
    transcript = hook.get("transcript_path") or os.environ.get("CURSOR_TRANSCRIPT_PATH")
    if not transcript or not os.path.isfile(transcript):
        return ""
    with open(transcript, encoding="utf-8", errors="replace") as f:
        return assistant_text_blocks(f.readlines())


def resolve_raw_text(hook: dict, event: str) -> str:
    if event in ("afterAgentResponse", "Stop", "SubagentStop"):
        inline = hook_inline_text(hook)
        if inline:
            if parse_spoken_summary(inline)[0]:
                return inline
            from_transcript = transcript_assistant_text(hook)
            if from_transcript and parse_spoken_summary(from_transcript)[0]:
                return from_transcript
            if event == "afterAgentResponse":
                return inline
        return transcript_assistant_text(hook)
    return transcript_assistant_text(hook)


def hook_event_name(hook: dict) -> str:
    return str(hook.get("hook_event_name") or hook.get("hookEventName") or "")
