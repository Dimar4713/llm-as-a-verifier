import unittest

from llm_verifier.aimeton_guard import (
    DegenerateScoreDistributionError,
    MissingScoreEvidenceError,
    require_score_distribution_evidence,
    require_score_evidence,
    score_distribution_support,
    score_evidence_sources,
)


class AIMETONScoreEvidenceGuardTest(unittest.TestCase):
    def test_missing_signal_fails_closed_instead_of_accepting_fallback_half(self):
        with self.assertRaises(MissingScoreEvidenceError):
            require_score_evidence("", None, None)

    def test_literal_score_tags_are_valid_evidence_but_not_distribution(self):
        text = "analysis\n<score_A> J </score_A>\n<score_B> K </score_B>"
        sources = require_score_evidence(text, None, None)
        self.assertEqual(
            sources,
            {"<score_A>": "text", "<score_B>": "text"},
        )
        with self.assertRaises(DegenerateScoreDistributionError):
            require_score_distribution_evidence(None, None)

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
        support = require_score_distribution_evidence(tokens, position_logprobs)
        self.assertEqual(support, {"<score_A>": 2, "<score_B>": 2})

    def test_singleton_top_logprob_is_evidence_but_not_distribution(self):
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
            [("J", -0.1), (" ordinary-word", -0.2)],
            [("</score_A>", 0.0)],
            [("<score_B>", 0.0)],
            [("K", -0.1), (" other-token", -0.2)],
            [("</score_B>", 0.0)],
        ]
        sources = require_score_evidence("", tokens, position_logprobs)
        self.assertEqual(
            sources,
            {"<score_A>": "logprobs", "<score_B>": "logprobs"},
        )
        self.assertEqual(
            score_distribution_support(tokens, position_logprobs),
            {"<score_A>": 1, "<score_B>": 1},
        )
        with self.assertRaises(DegenerateScoreDistributionError):
            require_score_distribution_evidence(tokens, position_logprobs)

    def test_duplicate_case_variants_count_as_one_score_value(self):
        tokens = ["<score_A>", "J", "<score_B>", "K"]
        position_logprobs = [
            [("<score_A>", 0.0)],
            [("J", -0.1), ("j", -0.2)],
            [("<score_B>", 0.0)],
            [("K", -0.1), ("k", -0.2)],
        ]
        self.assertEqual(
            score_distribution_support(tokens, position_logprobs),
            {"<score_A>": 1, "<score_B>": 1},
        )
        with self.assertRaises(DegenerateScoreDistributionError):
            require_score_distribution_evidence(tokens, position_logprobs)

    def test_partial_signal_is_rejected(self):
        sources = score_evidence_sources(
            "<score_A> A </score_A>", None, None
        )
        self.assertEqual(sources, {"<score_A>": "text"})
        with self.assertRaises(MissingScoreEvidenceError):
            require_score_evidence("<score_A> A </score_A>", None, None)

    def test_distribution_floor_cannot_be_weakened_below_two(self):
        with self.assertRaises(ValueError):
            require_score_distribution_evidence(None, None, min_distinct_scores=1)


if __name__ == "__main__":
    unittest.main()
