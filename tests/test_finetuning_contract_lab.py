"""Calculable-example tests for BERT fine-tuning chapters 07-10 helpers."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from finetuning_contract_lab import (
    padding_budget, optimizer_steps, align_word_labels, tokens_per_update,
    jaccard, mlm_replace_counts, packing_utilization,
    effective_batch, linear_warmup_lr, adamw_decay_factor,
)


class FinetuningContractTests(unittest.TestCase):
    def test_padding_budget_matches_article_07(self):
        ledger = padding_budget([8, 32, 96], 96)
        self.assertEqual(ledger["slots"], 288)
        self.assertEqual(ledger["effective"], 136)
        self.assertEqual(ledger["empty"], 152)
        self.assertAlmostEqual(ledger["empty_ratio"], 152 / 288, places=9)

    def test_optimizer_steps_match_article_07(self):
        self.assertEqual(optimizer_steps(3200, 16 * 1 * 2, 3), 300)

    def test_optimizer_steps_round_up_incomplete_batch(self):
        # 10 samples, batch 4, 1 epoch -> ceil(10/4) = 3 updates.
        self.assertEqual(optimizer_steps(10, 4, 1), 3)

    def test_align_word_labels_matches_article_07(self):
        word_ids = [None, 0, 1, 2, 2, None]
        labels = [0, 0, 3]  # O, O, B-LOC
        self.assertEqual(
            align_word_labels(word_ids, labels),
            [-100, 0, 0, 3, -100, -100],
        )

    def test_align_rejects_out_of_range_word_id(self):
        with self.assertRaises(ValueError):
            align_word_labels([7], [0])

    def test_tokens_per_update_batch_ratio(self):
        self.assertEqual(tokens_per_update(256, 512), 131072)
        self.assertEqual(tokens_per_update(8192, 512), 4194304)
        self.assertEqual(tokens_per_update(8192, 512) // tokens_per_update(256, 512), 32)

    def test_jaccard_article_09(self):
        self.assertAlmostEqual(jaccard([1, 2, 3, 4, 5], [3, 4, 5, 6, 7]), 3 / 7, places=9)
        self.assertEqual(jaccard([1, 2, 3], [1, 2, 3]), 1.0)

    def test_mlm_replace_counts_use_selected_denominator(self):
        self.assertEqual(mlm_replace_counts(100), {"mask": 80, "random": 10, "keep": 10})
        self.assertEqual(mlm_replace_counts(15), {"mask": 12, "random": 1, "keep": 2})

    def test_packing_utilization_article_09(self):
        ledger = packing_utilization([1000, 300], 1024)
        self.assertEqual(ledger["effective"], 1300)
        self.assertEqual(ledger["slots"], 2048)
        self.assertAlmostEqual(ledger["utilization"], 1300 / 2048, places=9)

    def test_effective_batch_article_10(self):
        self.assertEqual(effective_batch(8, 4, 4), 128)
        self.assertEqual(optimizer_steps(50000, effective_batch(8, 4, 4), 1), 391)

    def test_linear_warmup_lr_article_10(self):
        self.assertAlmostEqual(linear_warmup_lr(1e-4, 5000, 10000, 1000000), 5e-5, places=12)
        self.assertAlmostEqual(
            linear_warmup_lr(1e-4, 500000, 10000, 1000000),
            1e-4 * 500000 / 990000, places=12)

    def test_adamw_decay_factor_article_10(self):
        factor = adamw_decay_factor(1e-4, 0.01)
        self.assertAlmostEqual(factor, 0.999999, places=12)
        self.assertAlmostEqual(factor ** 100, 0.999900, places=5)

    def test_bad_inputs_raise(self):
        with self.assertRaises(ValueError):
            padding_budget([8, 32], 16)
        with self.assertRaises(ValueError):
            optimizer_steps(0, 32, 3)


if __name__ == "__main__":
    unittest.main()
