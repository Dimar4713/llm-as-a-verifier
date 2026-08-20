import unittest
from unittest.mock import patch

import llm_verifier


class SelectWithoutCacheRegressionTest(unittest.TestCase):
    """Regression for upstream issue #14: ring-pass scores must survive phase B."""

    def test_ring_pass_scores_are_preserved_without_cache(self):
        call_index = 0

        def fake_score_directed_pairs(
            _lazy,
            _tasks,
            needed_pairs,
            criteria,
            _note,
            n_reps,
            *_args,
            **_kwargs,
        ):
            nonlocal call_index
            self.assertEqual(n_reps, 1)
            pairs = list(needed_pairs["task"])
            criterion_id = criteria[0]["id"]
            scores = {}

            # seed=0, N=3 ring is [(0, 2), (2, 1), (1, 0)]. Make candidate 2
            # the clear ring leader. The pivot phase is deliberately neutral.
            ring_rewards = {
                (0, 2): (0.0, 1.0),
                (2, 1): (1.0, 0.0),
                (1, 0): (0.5, 0.5),
            }

            for a, b in pairs:
                if call_index == 0:
                    ra, rb = ring_rewards[(a, b)]
                else:
                    ra, rb = 0.5, 0.5
                key = f"{criterion_id}|task|{a},{b}|0"
                scores[key] = {"score_A": ra, "score_B": rb}

            call_index += 1
            return scores

        with patch(
            "llm_verifier.score_directed_pairs",
            side_effect=fake_score_directed_pairs,
        ):
            result = llm_verifier.select(
                "Choose the best candidate",
                ["candidate-0", "candidate-1", "candidate-2"],
                criteria={"Quality": "Prefer the objectively better candidate."},
                n_evaluations=1,
                pivots=1,
                seed=0,
                cache=None,
                progress=False,
                client=object(),
            )

        self.assertEqual(call_index, 2)
        self.assertEqual(result.index, 2)
        self.assertEqual(result.ranking[0], 2)


if __name__ == "__main__":
    unittest.main()
