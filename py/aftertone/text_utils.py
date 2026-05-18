"""Markdown stripping, sentence heuristics, and caps for speakable text."""

from __future__ import annotations

import re
from datetime import datetime, time as dtime

from aftertone.spoken_tag import without_spoken_block


def parse_hhmm(s: str) -> dtime | None:
    s = s.strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        return None
    return dtime(h, mi)


def in_quiet_hours(now_local: datetime, spec: str) -> bool:
    spec = (spec or "").strip()
    if not spec or spec.lower() in ("none", "off", "false"):
        return False
    m = re.match(r"^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$", spec)
    if not m:
        return False
    a = parse_hhmm(m.group(1))
    b = parse_hhmm(m.group(2))
    if a is None or b is None:
        return False
    t = now_local.time().replace(tzinfo=None)
    if a <= b:
        return a <= t < b
    return t >= a or t < b


def demote_code_fences(raw: str) -> str:
    return re.sub(r"```[\s\S]*?```", " code example ", raw)


def strip_markdownish(s: str) -> str:
    s = re.sub(r"```[\s\S]*?```", " ", s)
    s = re.sub(r"`[^`]+`", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[#*_~`]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


_OUTCOME_HINT = re.compile(
    r"\b("
    r"updated|changed|fixed|added|removed|commit|push|pulled|merged|amended|amend|"
    r"created|edited|replaced|implemented|refactor|installed|ran|wrote|saved|sent|built|"
    r"passed|failed|hook|daemon|branch|script|readme|docs|config|test|deploy|rewrite|"
    r"reword|moved|deleted|renamed|install|upgrade|downgrade|patch|issue|pull request"
    r")\b",
    re.I,
)

_LOW_SUBSTANCE_HEAD = re.compile(
    r"^("
    r"here\'?s|here is|i\'ll|i will|let me|"
    r"sure[,!]?|certainly[,!]?|absolutely[,!]?|"
    r"great question|good question|makes sense|sounds good|"
    r"you\'re (not )?wrong|you are (not )?wrong|you\'re right|you are right|"
    r"i (get|understand)( it)?|okay|ok"
    r")[\s,.:;]",
    re.I,
)


def is_low_substance_sentence(s: str) -> bool:
    t = s.strip()
    if not t:
        return True
    if _OUTCOME_HINT.search(t):
        return False
    if len(t) >= 120:
        return False
    tl = t.lower().strip(" '\"")
    if re.match(r"^(done|all set)\.?!?\s*$", tl):
        return True
    if _LOW_SUBSTANCE_HEAD.match(t):
        return True
    return False


def split_sentences(s: str) -> list[str]:
    s = strip_markdownish(s)
    if not s:
        return []
    chunks = re.split(r"(?<=[.!?])\s+", s)
    return [c.strip() for c in chunks if c.strip()]


def code_fence_fraction(raw: str) -> float:
    raw = raw or ""
    if not raw.strip():
        return 0.0
    total = len(raw)
    covered = sum(len(m.group(0)) for m in re.finditer(r"```[\s\S]*?```", raw))
    return covered / max(total, 1)


def clamp(s: str, max_chars: int) -> str:
    s = s.strip()
    if max_chars <= 0 or len(s) <= max_chars:
        return s
    return s[: max_chars - 3].rsplit(" ", 1)[0] + "..."


def heuristic_spoken(base: str, max_chars: int, max_sentences: int) -> str:
    ms = max(1, min(3, int(max_sentences)))
    parts = split_sentences(base)
    if not parts:
        return ""
    i = 0
    while i < len(parts) and is_low_substance_sentence(parts[i]):
        i += 1
    if i >= len(parts):
        k = min(ms, len(parts))
        tail = " ".join(parts[-k:]).strip() if k else parts[-1].strip()
        return clamp(tail, max_chars) if tail else ""
    picked = parts[i : i + ms]
    text = " ".join(picked).strip()
    return clamp(text, max_chars) if text else ""


def plain_excerpt(raw: str, max_chars: int) -> str:
    s = strip_markdownish(demote_code_fences(without_spoken_block(raw)))
    return clamp(s, max_chars) if s else ""


def spoken_tag_to_speakable(
    raw_inner: str, cap: int, *, max_sentences: int = 0
) -> str:
    s = strip_markdownish(raw_inner.replace("\n", " "))
    if not s:
        return ""
    if cap <= 0:
        return s.strip()
    parts = split_sentences(s)
    if not parts:
        return clamp(s, cap)
    out: list[str] = []
    for p in parts:
        if max_sentences > 0 and len(out) >= max_sentences:
            break
        trial = " ".join(out + [p]).strip() if out else p.strip()
        if len(trial) <= cap:
            out.append(p)
        else:
            break
    if not out:
        return clamp(parts[0], cap)
    joined = " ".join(out).strip()
    return clamp(joined, cap) if len(joined) > cap else joined


def effective_tag_cap(cfg: dict, max_chars: int) -> int:
    try:
        sc = int(cfg.get("spoken_summary_max_chars", 360))
    except (TypeError, ValueError):
        sc = 360
    if sc <= 0:
        return max_chars if max_chars > 0 else 10**9
    if max_chars <= 0:
        return sc
    return min(max_chars, sc)


def effective_plain_cap(cfg: dict, max_chars: int) -> int:
    try:
        pe = int(cfg.get("plain_excerpt_max_chars", 420))
    except (TypeError, ValueError):
        pe = 420
    if pe <= 0:
        return max_chars if max_chars > 0 else 10**9
    if max_chars <= 0:
        return pe
    return min(max_chars, pe)


def effective_heuristic_cap(cfg: dict, max_chars: int) -> int:
    try:
        h = int(cfg.get("heuristic_max_chars", 480))
    except (TypeError, ValueError):
        h = 480
    if h <= 0:
        return max_chars if max_chars > 0 else 10**9
    if max_chars <= 0:
        return h
    return min(max_chars, h)


def cfg_int_bounded(cfg: dict, key: str, default: int, lo: int, hi: int) -> int:
    try:
        v = int(cfg.get(key, default))
    except (TypeError, ValueError):
        v = default
    return max(lo, min(hi, v))


def cfg_float_bounded(cfg: dict, key: str, default: float, lo: float, hi: float) -> float:
    try:
        v = float(cfg.get(key, default))
    except (TypeError, ValueError):
        v = default
    return max(lo, min(hi, v))
