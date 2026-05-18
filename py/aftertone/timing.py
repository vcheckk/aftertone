"""Step-by-step latency lines in speak_summary-hook.log (ms since hook start → first sound)."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _log_path(repo_root: str | Path) -> Path:
    root = Path(repo_root)
    d = root / ".cursor" / "hooks" / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d / "speak_summary-hook.log"


def log_latency(
    repo_root: str | Path,
    step: str,
    *,
    trace_id: str | None = None,
    job_id: str | None = None,
    hook_t0_ms: int | None = None,
    **fields: Any,
) -> None:
    """Append one latency step. since_hook_ms is ms from hook_t0_ms to now (wall clock)."""
    now_ms = int(time.time() * 1000)
    parts: list[str] = [f"latency step={step}"]
    if trace_id:
        parts.append(f"trace={trace_id}")
    if job_id:
        parts.append(f"job_id={job_id}")
    if hook_t0_ms is not None and hook_t0_ms > 0:
        parts.append(f"since_hook_ms={now_ms - hook_t0_ms}")
    for key, val in fields.items():
        if val is None:
            continue
        parts.append(f"{key}={val}")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts} " + " ".join(parts) + "\n"
    with open(_log_path(repo_root), "a", encoding="utf-8") as f:
        f.write(line)


def log_latency_summary(
    repo_root: str | Path,
    *,
    trace_id: str | None,
    job_id: str,
    hook_t0_ms: int | None,
    first_sound_ms: int | None,
    **fields: Any,
) -> None:
    """One line after playback starts: end-to-end and per-phase breakdown."""
    parts: list[str] = [
        "latency_summary",
        f"job_id={job_id}",
        f"first_sound_since_hook_ms={first_sound_ms}",
    ]
    if trace_id:
        parts.append(f"trace={trace_id}")
    for key, val in fields.items():
        if val is None:
            continue
        parts.append(f"{key}={val}")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts} " + " ".join(parts) + "\n"
    with open(_log_path(repo_root), "a", encoding="utf-8") as f:
        f.write(line)
