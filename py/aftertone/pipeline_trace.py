"""Full pipeline trace: every step from hook stdin → first sound (+ Cursor gap hints)."""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aftertone.timing import log_latency, log_latency_summary

_TRACE_JSONL = "pipeline_trace.jsonl"


def _trace_jsonl_path(repo_root: str | Path) -> Path:
    d = Path(repo_root) / ".cursor" / "hooks" / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d / _TRACE_JSONL


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _since_hook(hook_t0_ms: int) -> int:
    return int(time.time() * 1000) - hook_t0_ms


def _find_timestamp_fields(obj: Any, prefix: str = "", out: dict[str, Any] | None = None) -> dict[str, Any]:
    """Collect numeric / ISO fields that may indicate when Cursor finished."""
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (int, float)) and v > 1_000_000_000:
                out[key] = v
            elif isinstance(v, str) and len(v) >= 10 and ("T" in v or v[:4].isdigit()):
                if any(t in k.lower() for t in ("time", "ts", "date", "at", "ms")):
                    out[key] = v
            elif isinstance(v, (dict, list)):
                _find_timestamp_fields(v, key, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:20]):
            _find_timestamp_fields(item, f"{prefix}[{i}]", out)
    return out


def scan_cursor_envelope(hook: dict[str, Any]) -> dict[str, Any]:
    text = hook.get("text")
    text_s = text if isinstance(text, str) else ""
    tag = "<spoken_summary>" in text_s.lower()
    close = "</spoken_summary>" in text_s.lower()
    return {
        "hook_event_name": hook.get("hook_event_name") or hook.get("hookEventName"),
        "generation_id": hook.get("generation_id") or hook.get("generationId"),
        "conversation_id": hook.get("conversation_id") or hook.get("conversationId"),
        "model": hook.get("model"),
        "cursor_version": hook.get("cursor_version"),
        "has_transcript_path": bool(hook.get("transcript_path")),
        "transcript_path_len": len(str(hook.get("transcript_path") or "")),
        "text_len": len(text_s),
        "has_spoken_summary_open": tag,
        "has_spoken_summary_close": close,
        "top_keys": sorted(hook.keys())[:40],
        "timestamp_fields": _find_timestamp_fields(hook),
    }


def probe_transcript(transcript_path: str | None, hook_t0_ms: int) -> dict[str, Any]:
    """Transcript mtime vs hook start ≈ delay after last disk write (proxy for Cursor gap)."""
    out: dict[str, Any] = {}
    if not transcript_path:
        return out
    p = Path(transcript_path)
    if not p.is_file():
        out["transcript_missing"] = True
        return out
    try:
        st = p.stat()
        mtime_ms = int(st.st_mtime * 1000)
        out["transcript_mtime_ms"] = mtime_ms
        out["transcript_size_bytes"] = st.st_size
        out["hook_minus_transcript_mtime_ms"] = hook_t0_ms - mtime_ms
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        out["transcript_lines"] = len(lines)
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("role") != "assistant":
                continue
            out["last_assistant_keys"] = sorted(obj.keys())[:30]
            for k in obj:
                kl = k.lower()
                if any(t in kl for t in ("time", "ts", "date", "ms", "at")):
                    out[f"assistant_{k}"] = obj[k]
            content = obj.get("content") or obj.get("message")
            if isinstance(content, str):
                out["last_assistant_has_spoken_close"] = "</spoken_summary>" in content.lower()
                out["last_assistant_len"] = len(content)
            break
    except OSError as exc:
        out["transcript_error"] = str(exc)
    return out


class PipelineTracer:
    def __init__(self, repo_root: str | Path, trace_id: str, hook_t0_ms: int) -> None:
        self.repo_root = Path(repo_root)
        self.trace_id = trace_id
        self.hook_t0_ms = hook_t0_ms
        self.job_id: str | None = None
        self._record: dict[str, Any] = {
            "trace_id": trace_id,
            "hook_t0_ms": hook_t0_ms,
            "hook_t0_utc": datetime.fromtimestamp(
                hook_t0_ms / 1000.0, tz=timezone.utc
            ).isoformat(),
            "steps": [],
        }

    def step(self, name: str, **fields: Any) -> None:
        entry: dict[str, Any] = {
            "step": name,
            "t_utc": _iso_now(),
            "since_hook_ms": _since_hook(self.hook_t0_ms),
        }
        entry.update({k: v for k, v in fields.items() if v is not None})
        self._record["steps"].append(entry)
        log_latency(
            self.repo_root,
            name,
            trace_id=self.trace_id,
            job_id=self.job_id,
            hook_t0_ms=self.hook_t0_ms,
            **{k: v for k, v in fields.items() if k not in ("t_utc",)},
        )

    def set_job_id(self, job_id: str | None) -> None:
        self.job_id = job_id
        if job_id:
            self._record["job_id"] = job_id

    def set_cursor_meta(self, meta: dict[str, Any]) -> None:
        self._record["cursor"] = meta

    def set_transcript_probe(self, probe: dict[str, Any]) -> None:
        self._record["transcript_probe"] = probe
        gap = probe.get("hook_minus_transcript_mtime_ms")
        if isinstance(gap, int):
            self.step(
                "cursor_gap_hint_transcript_mtime",
                hook_minus_transcript_mtime_ms=gap,
                note="ms from last transcript file write to hook start; large value suggests Cursor delayed calling the hook after the reply was saved",
            )

    def finish_hook(self, *, http: int, hook_wall_ms: int, error: str | None = None) -> None:
        self._record["phase"] = "hook"
        self._record["hook_finished"] = {
            "http": http,
            "hook_wall_ms": hook_wall_ms,
            "error": error,
        }
        self._flush()

    def finish_sound(
        self,
        *,
        job_id: str,
        first_sound_since_hook_ms: int | None,
        **metrics: Any,
    ) -> None:
        self.set_job_id(job_id)
        self._record["phase"] = "sound"
        self._record["first_sound_since_hook_ms"] = first_sound_since_hook_ms
        self._record["sound_metrics"] = metrics
        log_latency_summary(
            self.repo_root,
            trace_id=self.trace_id,
            job_id=job_id,
            hook_t0_ms=self.hook_t0_ms,
            first_sound_ms=first_sound_since_hook_ms,
            **metrics,
        )
        gap = (self._record.get("transcript_probe") or {}).get(
            "hook_minus_transcript_mtime_ms"
        )
        if isinstance(gap, int) and first_sound_since_hook_ms is not None:
            self.step(
                "estimated_ui_to_sound_ms",
                transcript_mtime_gap_ms=gap,
                aftertone_first_sound_ms=first_sound_since_hook_ms,
                estimated_total_ms=gap + first_sound_since_hook_ms,
                note="transcript_mtime_gap + first_sound; proxy if tag was written when transcript last saved",
            )
        self._flush()

    def _flush(self) -> None:
        path = _trace_jsonl_path(self.repo_root)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(self._record, ensure_ascii=False) + "\n")


def healthz_probe(port: int, timeout: float = 0.4) -> tuple[bool, int]:
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/healthz", timeout=timeout
        ) as resp:
            ok = resp.status == 200
    except Exception:
        ok = False
    return ok, int((time.perf_counter() - t0) * 1000)
