"""Deterministic mechanics checks for standalone deep dives 11–15."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from encoder_budget_lab import (token_exposures, language_sampling, rtd_is_replaced,
                                masked_softmax, flops_order, repeated_exposure,
                                param_memory_bytes, attention_matrix_elements, scaled_gradient)


class EncoderBudgetTests(unittest.TestCase):
    def test_token_exposures_short(self):
        self.assertEqual(token_exposures([(1_000_000, 128)], 256), 32_768_000_000)

    def test_token_exposures_original_length_schedule(self):
        self.assertEqual(token_exposures([(900_000, 128), (100_000, 512)], 256),
                         42_598_400_000)

    def test_length_quadruples_attention_matrix(self):
        self.assertEqual((1024 * 1024) // (512 * 512), 4)

    def test_flops_order_article_11(self):
        self.assertEqual(flops_order(110_000_000, 32_768_000_000), 21626880000000000000)
        self.assertEqual(flops_order(50_000_000, 20_000_000_000),
                         flops_order(200_000_000, 5_000_000_000))

    def test_repeated_exposure_article_11(self):
        ledger = repeated_exposure(10_000_000_000, 2)
        self.assertEqual(ledger["seen"], 20_000_000_000)
        self.assertEqual(ledger["unique"], 10_000_000_000)

    def test_param_memory_article_12(self):
        self.assertEqual(param_memory_bytes(110_000_000, 16), 1_760_000_000)
        self.assertEqual(param_memory_bytes(110_000_000, 16) / 1e9, 1.76)

    def test_attention_matrix_elements_quadruple(self):
        self.assertEqual(attention_matrix_elements(512), 262_144)
        self.assertEqual(attention_matrix_elements(1024), 1_048_576)
        self.assertEqual(attention_matrix_elements(2048), 4_194_304)
        self.assertEqual(attention_matrix_elements(1024) // attention_matrix_elements(512), 4)

    def test_scaled_gradient_roundtrip(self):
        scaled = scaled_gradient(1e-5, 65536)
        self.assertAlmostEqual(scaled, 0.65536, places=9)
        self.assertAlmostEqual(scaled / 65536, 1e-5, places=12)

    def test_invalid_batch_rejected(self):
        with self.assertRaises(ValueError):
            token_exposures([(1, 128)], 0)

    def test_language_smoothing(self):
        raw = language_sampling([100, 1], alpha=1.0)
        smooth = language_sampling([100, 1], alpha=0.7)
        self.assertAlmostEqual(raw[0] / raw[1], 100, places=6)
        self.assertAlmostEqual(smooth[0] / smooth[1], 100 ** 0.7, places=6)
        self.assertAlmostEqual(sum(smooth), 1.0, places=12)

    def test_flat_language_sampling(self):
        self.assertEqual(language_sampling([100, 1], alpha=0.0), [0.5, 0.5])

    def test_rtd_same_sample_is_original(self):
        # Token at position 2 was selected by generator, but sampled same ID.
        self.assertEqual(rtd_is_replaced([1, 2, 3, 0], [1, 2, 3, 0],
                                         [1, 1, 1, 0]), [0, 0, 0, None])

    def test_rtd_real_replacement(self):
        self.assertEqual(rtd_is_replaced([1, 2, 3, 0], [1, 2, 9, 0],
                                         [1, 1, 1, 0]), [0, 0, 1, None])

    def test_softmax_respects_mask(self):
        probabilities = masked_softmax([1.0, 1000.0, 0.0], [True, False, True])
        self.assertEqual(probabilities[1], 0.0)
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
        self.assertGreater(probabilities[0], probabilities[2])

    def test_all_keys_masked_raises(self):
        with self.assertRaises(ValueError):
            masked_softmax([1.0, 2.0], [False, False])


if __name__ == "__main__":
    unittest.main()
