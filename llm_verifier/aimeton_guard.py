"""AIMETON fail-closed guards for semantic verifier signal quality.

This module is intentionally separate from the upstream verifier API.  It lets
AIMETON distinguish a real verifier score from the upstream fallback value
0.5 that is returned when no usable score-token evidence can be recovered.
"""

from __future__ import annotations

import re
from typing import Mapping, Optional, Sequence

from llm_verifier.fine_grained_reward import SCALE, _find_tag_logprobs


class MissingScoreEvidenceError(RuntimeError):
    """Raised when a verifier response contains no valid A-T score evidence."""


def _normalize_score_token(token: str) -> str:
    token = (token or "").strip()
    if token.startswith(">"):
        token = token[1:].strip()
    return token


def _logprob_has_score(tokens, position_logprobs, tag: str) -> bool:
    tag_lp = _find_tag_logprobs(tokens, position_logprobs, tag)
    if not tag_lp:
        return False
    valid_tokens = SCALE["valid_tokens"]
    return any(_normalize_score_token(tok) in valid_tokens for tok, _ in tag_lp)


def _text_has_score(text: str, tag: str) -> bool:
    tag_name = tag.strip("<>")
    pattern = rf"<{re.escape(tag_name)}>\s*(.+?)\s*</{re.escape(tag_name)}>"
    matches = list(re.finditer(pattern, text or "", re.IGNORECASE))
    if not matches:
        return False
    token = matches[-1].group(1).strip()
    return token.upper() in {chr(65 + i) for i in range(20)}


def score_evidence_sources(
    text: str,
    tokens: Optional[Sequence[str]],
    position_logprobs,
    tags: Sequence[str] = ("<score_A>", "<score_B>"),
) -> Mapping[str, str]:
    """Return the evidence source for each score tag that can be validated.

    Values are ``"logprobs"`` or ``"text"``. Missing tags are omitted.
    """
    sources = {}
    for tag in tags:
        if _logprob_has_score(tokens, position_logprobs, tag):
            sources[tag] = "logprobs"
        elif _text_has_score(text, tag):
            sources[tag] = "text"
    return sources


def require_score_evidence(
    text: str,
    tokens: Optional[Sequence[str]],
    position_logprobs,
    tags: Sequence[str] = ("<score_A>", "<score_B>"),
) -> Mapping[str, str]:
    """Fail closed unless every required score tag has valid score evidence.

    This guard is meant to run before AIMETON accepts semantic-verifier output.
    It prevents the upstream ``extract_score(...)->0.5`` fallback from being
    mistaken for a genuine neutral measurement when the backend returned no
    usable score-token signal.
    """
    sources = score_evidence_sources(text, tokens, position_logprobs, tags)
    missing = [tag for tag in tags if tag not in sources]
    if missing:
        raise MissingScoreEvidenceError(
            "verifier returned no valid score evidence for: " + ", ".join(missing)
        )
    return sources
