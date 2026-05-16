"""Resolve Aftertone install root (global ~/aftertone vs in-repo clone)."""

from __future__ import annotations

import os
from pathlib import Path

_INSTALL_DIR_FILE = Path.home() / ".cursor" / "hooks" / "aftertone-install-dir"
_MARKER = "py/speak_summary_prepare.py"


def _valid_root(path: Path) -> bool:
    return (path / _MARKER).is_file()


def resolve_repo_root(explicit: Path | None = None) -> Path:
    """Install root: env, ~/.cursor/hooks/aftertone-install-dir, or parent of py/."""
    if explicit is not None:
        root = explicit.expanduser().resolve()
        if _valid_root(root):
            return root
        raise FileNotFoundError(f"not an Aftertone install (missing {_MARKER}): {root}")

    for key in ("AFTERTONE_REPO", "SUPERTONIC_REPO", "AFTERTONE_INSTALL_DIR"):
        raw = os.environ.get(key, "").strip()
        if not raw:
            continue
        root = Path(raw).expanduser().resolve()
        if _valid_root(root):
            return root

    if _INSTALL_DIR_FILE.is_file():
        raw = _INSTALL_DIR_FILE.read_text(encoding="utf-8").strip()
        if raw:
            root = Path(raw).expanduser().resolve()
            if _valid_root(root):
                return root

    default = Path(__file__).resolve().parent.parent
    if _valid_root(default):
        return default

    raise FileNotFoundError(
        f"Aftertone install not found. Set AFTERTONE_INSTALL_DIR, run install.sh --global, "
        f"or open the install folder (expected {_MARKER})."
    )
