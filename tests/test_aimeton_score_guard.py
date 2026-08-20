import unittest

from llm_verifier.aimeton_guard import (
    MissingScoreEvidenceError,
    require_score_evidence,
    score_evidence_sources,
)


class AIMETONScoreEvidenceGuardTest(unittest.TestCase):
    def test_missing_signal_fails_closed_instead_of_accepting_fallback_half(self):
        with self.assertRaises(MissingScoreEvidenceError):
            require_score_evidence("", None, None)

    def test_literal_score_tags_are_valid_evidence(self):
        text = "analysis\n<score_A> J </score_A>\n<score_B> K </score_B>"
        sources = require_score_evidence(text, None, None)
        self.assertEqual(
            sources,
            {"<score_A>": "text", "<score_B>": "text"},
        )

    def test_logprob_score_distribution_is_valid_evidence(self):
        tokens = [
            "<score_A>",
            "J",
            "</score_A>",
            "<score_B>",
            "K",
            "</score_B>",
        ]
        position_logprobs = [
            [("<score_A>", 0.0)],
            [("J", -0.1), ("K", -2.0)],
            [("</score_A>", 0.0)],
            [("<score_B>", 0.0)],
            [("K", -0.2), ("J", -1.8)],
            [("</score_B>", 0.0)],
        ]
        sources = require_score_evidence("", tokens, position_logprobs)
        self.assertEqual(
            sources,
            {"<score_A>": "logprobs", "<score_B>": "logprobs"},
        )

    def test_partial_signal_is_rejected(self):
        sources = score_evidence_sources(
            "<score_A> A </score_A>", None, None
        )
        self.assertEqual(sources, {"<score_A>": "text"})
        with self.assertRaises(MissingScoreEvidenceError):
            require_score_evidence("<score_A> A </score_A>", None, None)


if __name__ == "__main__":
    unittest.main()
