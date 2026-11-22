"""Deterministic assertions for BERT deep dives 16–20."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from variant_mechanics_lab import (
    permutation_context, mpnet_information, embedding_parameter_counts,
    shared_block_parameter_counts, relative_directions, disentangled_raw_score,
    whole_word_target_positions,
)


class VariantMechanicsTests(unittest.TestCase):
    def test_xlnet_forward_target_sees_left(self):
        self.assertEqual(permutation_context(4, [0, 1, 2, 3], 1), [0])

    def test_xlnet_mixed_target_sees_both_sides(self):
        self.assertEqual(permutation_context(4, [2, 0, 3, 1], 1), [2, 0, 3])

    def test_xlnet_never_sees_target_itself(self):
        for target in range(4):
            self.assertNotIn(target, permutation_context(4, [2, 0, 3, 1], target))

    def test_invalid_permutation_rejected(self):
        with self.assertRaises(ValueError):
            permutation_context(4, [1, 1, 2, 3], 1)

    def test_mpnet_compensation_and_content(self):
        info = mpnet_information(6, [0, 2, 4, 3, 5, 1], 3, target=5)
        self.assertEqual(info["visible_real_positions"], [0, 2, 4, 3])
        self.assertEqual(info["mask_slot_positions"], [3, 5, 1])
        self.assertEqual(info["forbidden_real_positions"], [5, 1])
        self.assertNotIn(5, info["visible_real_positions"])

    def test_mpnet_cannot_predict_context_prefix(self):
        with self.assertRaises(ValueError):
            mpnet_information(4, [1, 3, 0, 2], 2, target=1)

    def test_albert_embedding_parameters_only(self):
        self.assertEqual(embedding_parameter_counts(30_000, 768, 128),
                         (23_040_000, 3_938_304))

    def test_albert_shared_weight_not_shared_execution(self):
        self.assertEqual(shared_block_parameter_counts(12, 1_000_000),
                         (1_000_000, 12_000_000))
        self.assertEqual(shared_block_parameter_counts(12, 1_000_000, 3),
                         (3_000_000, 12_000_000))

    def test_deberta_distance_reverses_sign(self):
        self.assertEqual(relative_directions(4, 2), (-2, 2))
        self.assertEqual(relative_directions(2, 4), (2, -2))

    def test_deberta_score_sum(self):
        self.assertAlmostEqual(disentangled_raw_score(0.8, 0.4, -0.1), 1.1)

    def test_deberta_nan_rejected(self):
        with self.assertRaises(ValueError):
            disentangled_raw_score(0.1, float("nan"), 0.3)

    def test_wwm_selects_whole_group(self):
        groups = [[0, 1, 2, 3], [4, 5], [6, 7]]
        self.assertEqual(whole_word_target_positions(groups, [0]), [0, 1, 2, 3])
        self.assertEqual(whole_word_target_positions(groups, [1, 2]), [4, 5, 6, 7])

    def test_wwm_rejects_overlapping_boundary(self):
        with self.assertRaises(ValueError):
            whole_word_target_positions([[0, 1], [1, 2]], [0])


if __name__ == "__main__":
    unittest.main()
