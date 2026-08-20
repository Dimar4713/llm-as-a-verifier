"""AIMETON fail-closed guards for semantic verifier signal quality.

This module is intentionally separate from the upstream verifier API. It lets
AIMETON distinguish:

1. any recoverable score evidence (logprobs or literal score text), from
2. a genuinely non-degenerate probabilistic score distribution.

The distinction matters because upstream ``extract_score`` deliberately keeps
compatibility fallbacks: missing score evidence becomes ``0.5`` and a
logprob position containing only one valid A-T alternative is renormalized to
that singleton. Those behaviours are useful for a general-purpose library but
are not sufficient evidence for AIMETON's semantic-verifier lane.
"""

from __future__ import annotations

import re
from typing import Mapping, Optional, Sequence

from llm_verifier.fine_grained_reward import SCALE, _find_tag_logprobs


class MissingScoreEvidenceError(RuntimeError):
    """Raised when a verifier response contains no valid A-T score evidence."""


class DegenerateScoreDistributionError(RuntimeError):
    """Raised when score logprobs do not contain enough distinct A-T support."""


def _normalize_score_token(token: str) -> str:
    token = (token or "").strip()
    if token.startswith(">"):
        token = token[1:].strip()
    return token


def _score_logprob_support(tokens, position_logprobs, tag: str) -> set[float]:
    """Distinct scalar score values represented in a tag's top-logprobs."""
    tag_lp = _find_tag_logprobs(tokens, position_logprobs, tag)
    if not tag_lp:
        return set()
    valid_tokens = SCALE["valid_tokens"]
    support: set[float] = set()
    for token, _ in tag_lp:
        normalized = _normalize_score_token(token)
        if normalized in valid_tokens:
            support.add(valid_tokens[normalized])
    return support


def _logprob_has_score(tokens, position_logprobs, tag: str) -> bool:
    return bool(_score_logprob_support(tokens, position_logprobs, tag))


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
    This is an evidence-presence check, not a probabilistic-quality check.
    """
    sources = {}
    for tag in tags:
        if _logprob_has_score(tokens, position_logprobs, tag):
            sources[tag] = "logprobs"
        elif _text_has_score(text, tag):
            sources[tag] = "text"
    return sources


def score_distribution_support(
    tokens: Optional[Sequence[str]],
    position_logprobs,
    tags: Sequence[str] = ("<score_A>", "<score_B>"),
) -> Mapping[str, int]:
    """Return the number of distinct A-T score values visible per score tag.

    A literal score in response text intentionally does not count here: this
    function measures probability-distribution support only.
    """
    return {
        tag: len(_score_logprob_support(tokens, position_logprobs, tag))
        for tag in tags
    }


def require_score_evidence(
    text: str,
    tokens: Optional[Sequence[str]],
    position_logprobs,
    tags: Sequence[str] = ("<score_A>", "<score_B>"),
) -> Mapping[str, str]:
    """Fail closed unless every required score tag has valid score evidence.

    This guard prevents upstream ``extract_score(...)->0.5`` fallback from
    being mistaken for a genuine neutral measurement when no usable score
    signal was returned. Use ``require_score_distribution_evidence`` when the
    caller specifically needs a probabilistic semantic-verifier signal.
    """
    sources = score_evidence_sources(text, tokens, position_logprobs, tags)
    missing = [tag for tag in tags if tag not in sources]
    if missing:
        raise MissingScoreEvidenceError(
            "verifier returned no valid score evidence for: " + ", ".join(missing)
        )
    return sources


def require_score_distribution_evidence(
    tokens: Optional[Sequence[str]],
    position_logprobs,
    tags: Sequence[str] = ("<score_A>", "<score_B>"),
    *,
    min_distinct_scores: int = 2,
) -> Mapping[str, int]:
    """Fail closed unless every score tag has non-degenerate A-T support.

    ``min_distinct_scores=2`` is AIMETON's P0 scientific floor: a singleton
    A-T token in ``top_logprobs`` is a point estimate after renormalization,
    not evidence of a useful score distribution. This guard intentionally
    rejects such responses instead of weakening the measurement gate or
    silently converting them to 0.5.
    """
    if min_distinct_scores < 2:
        raise ValueError("min_distinct_scores must be >= 2")

    support = score_distribution_support(tokens, position_logprobs, tags)
    insufficient = {
        tag: count for tag, count in support.items()
        if count < min_distinct_scores
    }
    if insufficient:
        detail = ", ".join(
            f"{tag}={count}" for tag, count in insufficient.items()
        )
        raise DegenerateScoreDistributionError(
            "verifier score distribution support below scientific floor "
            f"({min_distinct_scores} distinct A-T scores required): {detail}"
        )
    return support
