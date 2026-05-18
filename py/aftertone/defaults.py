"""Install-time defaults for speak_summary.toml."""

from __future__ import annotations

import re
from pathlib import Path


def apply_install_defaults(toml_path: Path) -> None:
    """Fresh installs: tag_only, total_step 8, full spoken_summary tag (no sentence cap)."""
    if not toml_path.is_file():
        return
    text = toml_path.read_text(encoding="utf-8")

    if re.search(r"^\s*summary_mode\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^(\s*)summary_mode\s*=\s*\S+.*$",
            r'\1summary_mode = "tag_only"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = text.rstrip() + '\n\nsummary_mode = "tag_only"\n'

    if re.search(r"^\s*total_step\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^(\s*)total_step\s*=\s*\d+.*$",
            r"\1total_step = 8",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = text.rstrip() + "\ntotal_step = 8\n"

    if re.search(r"^\s*only_speak_spoken_summary\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^(\s*)only_speak_spoken_summary\s*=\s*\S+.*$",
            r"\1only_speak_spoken_summary = true",
            text,
            count=1,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    else:
        text = text.rstrip() + "\nonly_speak_spoken_summary = true\n"

    if re.search(r"^\s*spoken_summary_max_sentences\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^(\s*)spoken_summary_max_sentences\s*=\s*\d+.*$",
            r"\1spoken_summary_max_sentences = 0",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = text.rstrip() + "\nspoken_summary_max_sentences = 0\n"

    toml_path.write_text(text, encoding="utf-8")
