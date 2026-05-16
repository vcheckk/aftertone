#!/usr/bin/env python3
"""
Sync the configured speak_summary `lang` into .cursor/rules/spoken-summary.mdc.

Cursor rules are static files; they do not read TOML when the model runs. This
script copies `lang` from speak_summary.toml into a marked block so the agent
prompt always shows the current code (e.g. fr, en) without manual copy-paste.

Run after changing lang in the TOML (from **repository root**, so paths resolve):

  uv run --directory py python sync_spoken_rule_lang.py

Optional: `--repo-root /abs/path/to/repo` if you run from another cwd.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

MARK_START = "<!-- autogen:spoken-lang:start -->\n"
MARK_END = "<!-- autogen:spoken-lang:end -->"


def _load_lang(toml_path: Path) -> str:
    with toml_path.open("rb") as f:
        data = tomllib.load(f)
    raw = data.get("lang", "en")
    lang = str(raw).strip() or "en"
    # single token for display / instruction
    return lang.replace("`", "").replace("\n", "")[:16]


def _blurb(lang: str) -> str:
    return (
        f"> **Active `lang` for `<spoken_summary>`:** `{lang}` "
        "(from [`.cursor/hooks/speak_summary.toml`](../hooks/speak_summary.toml)). "
        "Write **only** the inner tag text in the natural language for that code. "
        "After changing `lang` in the TOML, from the **repo root** run: "
        "`uv run --directory py python sync_spoken_rule_lang.py`\n"
    )


def sync_rule(repo: Path, *, check_only: bool) -> int:
    toml_path = repo / ".cursor" / "hooks" / "speak_summary.toml"
    mdc_path = repo / ".cursor" / "rules" / "spoken-summary.mdc"
    if not toml_path.is_file():
        print(f"error: missing {toml_path}", file=sys.stderr)
        return 2
    if not mdc_path.is_file():
        print(f"error: missing {mdc_path}", file=sys.stderr)
        return 2

    lang = _load_lang(toml_path)
    body = mdc_path.read_text(encoding="utf-8")
    if MARK_START not in body or MARK_END not in body:
        print(
            f"error: markers not found in {mdc_path} "
            f"(need {MARK_START.strip()} … {MARK_END})",
            file=sys.stderr,
        )
        return 2

    before, rest = body.split(MARK_START, 1)
    _mid, after = rest.split(MARK_END, 1)
    new_block = MARK_START + _blurb(lang) + MARK_END
    new_body = before + new_block + after

    if new_body == body:
        if check_only:
            print("ok: rule already matches TOML")
        else:
            print(f"ok: already synced (lang={lang})")
        return 0

    if check_only:
        print(
            f"error: rule out of sync with TOML (lang={lang}); run without --check",
            file=sys.stderr,
        )
        return 1

    mdc_path.write_text(new_body, encoding="utf-8")
    print(f"updated {mdc_path} (lang={lang})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of py/ containing this script)",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the rule file does not match TOML (CI / pre-commit).",
    )
    args = p.parse_args()
    from aftertone_paths import resolve_repo_root

    repo = resolve_repo_root(args.repo_root)
    return sync_rule(repo, check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
