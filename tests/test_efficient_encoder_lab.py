"""Shape, numerical and graph tests for BERT chapters 21–25."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from efficient_encoder_lab import (
    sparse_attention_keys, attention_pair_budget, softmax, contrastive_loss,
    teacher_student_kl, bottleneck_projection_parameters,
    quantize_symmetric_int8, lora_parameters, lora_scalar_forward,
    rank_allocation,
)


class EfficientEncoderTests(unittest.TestCase):
    def test_longformer_local_plus_global(self):
        self.assertEqual(sparse_attention_keys(12, 6, 2, [0]),
                         [0, 4, 5, 6, 7, 8])

    def test_global_query_sees_everything(self):
        self.assertEqual(sparse_attention_keys(12, 0, 2, [0]),
                         list(range(12)))

    def test_bigbird_toy_random_edge_is_extra(self):
        self.assertEqual(sparse_attention_keys(12, 6, 2, [0], [10]),
                         [0, 4, 5, 6, 7, 8, 10])

    def test_sparse_edges_no_duplication(self):
        self.assertEqual(sparse_attention_keys(4, 1, 2, [1], [1]),
                         [0, 1, 2, 3])

    def test_pair_budget(self):
        self.assertEqual(attention_pair_budget(4096, 64, 1),
                         (16_777_216, 266_240))

    def test_simcse_softmax_stable(self):
        p = softmax([1001, 1000, 999])
        self.assertAlmostEqual(sum(p), 1.0, places=12)
        self.assertGreater(p[0], p[1])

    def test_simcse_positive_prob(self):
        self.assertAlmostEqual(contrastive_loss([2, 1, 0], 0),
                               -math.log(softmax([2, 1, 0])[0]))

    def test_simcse_lower_temperature_sharpens(self):
        self.assertGreater(softmax([2, 1, 0], 0.5)[0],
                           softmax([2, 1, 0], 2.0)[0])

    def test_negative_temperature_rejected(self):
        with self.assertRaises(ValueError):
            softmax([1, 2], 0)

    def test_distillation_kl_zero_equal_logits(self):
        self.assertAlmostEqual(teacher_student_kl([1, 2], [1, 2], 2.0), 0.0)

    def test_distillation_kl_nonnegative(self):
        self.assertGreater(teacher_student_kl([3, 1, 0], [0, 1, 3], 2), 0)

    def test_distillation_different_vocabulary_rejected(self):
        with self.assertRaises(ValueError):
            teacher_student_kl([1, 2], [1, 2, 3])

    def test_mobilebert_projection_count(self):
        self.assertEqual(bottleneck_projection_parameters(512, 128), 131_072)

    def test_int8_round_trip(self):
        self.assertEqual(quantize_symmetric_int8(0.37, .01), (37, .37))

    def test_int8_saturates(self):
        self.assertEqual(quantize_symmetric_int8(999, .01)[0], 127)

    def test_lora_parameter_budget(self):
        self.assertEqual(lora_parameters(768, 768, 8), (589_824, 12_288))

    def test_lora_forward_matches_merged_scalar(self):
        self.assertAlmostEqual(lora_scalar_forward(2, 3, 4, 5, 8, 4),
                               (2 + (8 / 4) * 3 * 4) * 5)

    def test_adalora_budget_equal_nonuniform(self):
        self.assertEqual(rank_allocation([2, 8, 2], 12), 12)

    def test_adalora_wrong_budget_rejected(self):
        with self.assertRaises(ValueError):
            rank_allocation([2, 8, 2], 11)


if __name__ == "__main__":
    unittest.main()
