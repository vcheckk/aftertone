"""Build speakable line from assistant text (v2 summary router)."""

from __future__ import annotations

from aftertone.config import SummaryMode
from aftertone.spoken_tag import parse_spoken_summary, without_spoken_block
from aftertone.text_utils import (
    clamp,
    code_fence_fraction,
    demote_code_fences,
    effective_heuristic_cap,
    effective_plain_cap,
    effective_tag_cap,
    heuristic_spoken,
    plain_excerpt,
    spoken_tag_to_speakable,
)


def build_speakable_text(
    raw_text: str,
    cfg: dict,
    mode: SummaryMode,
    *,
    min_chars: int,
    max_chars: int,
    h_max: int,
    h_code_max: int,
    fence_thr: float,
    apply_expression_fn,
) -> tuple[str, str]:
    """
    Return (speakable_text, source) where source is tag | heuristic | excerpt | empty.
    """
    spoken, flow_state = parse_spoken_summary(raw_text)

    if mode == "tag_only" and not spoken:
        return "", "empty"

    base = without_spoken_block(raw_text)
    code_heavy = code_fence_fraction(raw_text) >= fence_thr
    eff_sentences = h_code_max if code_heavy else h_max
    hcap = effective_heuristic_cap(cfg, max_chars)

    if spoken:
        try:
            tag_max_sent = int(cfg.get("spoken_summary_max_sentences", 0))
        except (TypeError, ValueError):
            tag_max_sent = 0
        text = spoken_tag_to_speakable(
            spoken,
            effective_tag_cap(cfg, max_chars),
            max_sentences=max(0, tag_max_sent),
        )
        text = apply_expression_fn(text, flow_state, cfg.get("expression_mode", "off"))
        return text.strip(), "tag"

    if mode == "tag_only":
        return "", "empty"

    text = heuristic_spoken(base, hcap, eff_sentences)
    if len(text) < min_chars:
        text = heuristic_spoken(demote_code_fences(base), hcap, eff_sentences)
    if len(text) < min_chars:
        text = plain_excerpt(raw_text, effective_plain_cap(cfg, max_chars))
        source = "excerpt"
    else:
        source = "heuristic"

    text = text.strip()
    if not text:
        return "", "empty"
    if len(text) < min_chars:
        return "", "empty"
    return text, source
