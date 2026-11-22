"""Calculable-example tests for BERT chapters 26–28 accounting helpers."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from modern_encoder_lab import (
    padding_budget, attention_pair_budget, weight_bytes,
    linear_quantize, dequantize, macro_f1,
)


class ModernEncoderAccountingTests(unittest.TestCase):
    def test_padding_budget_matches_article_26(self):
        ledger = padding_budget([16, 64, 128], 128)
        self.assertEqual(ledger["slots"], 384)
        self.assertEqual(ledger["effective"], 208)
        self.assertEqual(ledger["empty"], 176)
        self.assertAlmostEqual(ledger["empty_ratio"], 176 / 384, places=9)

    def test_attention_pair_budget_differs_from_slot_savings(self):
        ledger = attention_pair_budget([16, 64, 128], 128)
        self.assertEqual(ledger["real_pairs"], 20736)
        self.assertEqual(ledger["dense_pairs"], 49152)
        self.assertAlmostEqual(ledger["kept_ratio"], 0.421875, places=9)
        self.assertNotAlmostEqual(ledger["kept_ratio"], 1 - 176 / 384, places=3)

    def test_padding_budget_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            padding_budget([16, 64], 32)
        with self.assertRaises(ValueError):
            attention_pair_budget([16, -1], 32)

    def test_weight_bytes_ledger_article_27(self):
        self.assertEqual(weight_bytes(100_000_000, 32), 400_000_000.0)
        self.assertEqual(weight_bytes(100_000_000, 8), 100_000_000.0)
        self.assertEqual(
            weight_bytes(100_000_000, 32) / weight_bytes(100_000_000, 8), 4.0)

    def test_linear_quantization_error_is_bounded_by_half_scale(self):
        values = [0.0, 0.5, -0.5, 1.0]
        integers, scale = linear_quantize(values, bits=8)
        self.assertEqual(scale, 1.0 / 127)
        restored = dequantize(integers, scale)
        for original, approx in zip(values, restored):
            self.assertLessEqual(abs(original - approx), scale / 2 + 1e-12)

    def test_macro_f1_treats_empty_class_as_zero(self):
        confusion = [[5, 1, 0], [2, 6, 0], [0, 0, 0]]
        expected = (10 / 13 + 12 / 15 + 0.0) / 3
        self.assertAlmostEqual(macro_f1(confusion), expected, places=9)


if __name__ == "__main__":
    unittest.main()
