"""Load and interpret speak_summary.toml."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

from aftertone.paths import config_path

SummaryMode = Literal["auto", "tag_only", "heuristic"]


def load_config(root: Path | None = None) -> dict:
    path = config_path(root)
    if not path.is_file():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def cfg_bool(cfg: dict, key: str, default: bool) -> bool:
    v = cfg.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("0", "false", "no", "off"):
            return False
        if s in ("1", "true", "yes", "on"):
            return True
    return bool(v)


def cfg_enabled(cfg: dict) -> bool:
    return cfg_bool(cfg, "enabled", True)


def summary_mode(cfg: dict) -> SummaryMode:
    raw = str(cfg.get("summary_mode", "")).strip().lower()
    if raw in ("auto", "tag_only", "heuristic"):
        return raw  # type: ignore[return-value]
    if cfg_bool(cfg, "only_speak_spoken_summary", True):
        return "tag_only"
    return "tag_only"
