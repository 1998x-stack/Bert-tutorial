"""Standard-library regression tests for chapter 16–20 teaching mechanisms."""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("variant_mechanisms_lab", ROOT / "examples" / "variant_mechanisms_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class XLNetTests(unittest.TestCase):
    def test_last_target_sees_both_natural_sides(self):
        self.assertEqual(lab.permutation_visible((3, 1, 4, 2), 2), (3, 1, 4))

    def test_first_target_sees_nobody(self):
        self.assertEqual(lab.permutation_visible((2, 4, 1, 3), 2), ())

    def test_rejects_duplicate_or_missing_target(self):
        with self.assertRaises(ValueError):
            lab.permutation_visible((3, 3, 2), 2)
        with self.assertRaises(ValueError):
            lab.permutation_visible((3, 1), 2)


class MPNetTests(unittest.TestCase):
    def test_placeholders_preserve_all_slots_without_true_content(self):
        result = lab.mpnet_position_compensation(5, (0, 1, 2), (3, 4))
        self.assertEqual(result["masked_position_slots"], (3, 4))
        self.assertEqual(result["all_position_slots"], (0, 1, 2, 3, 4))
        self.assertNotIn("target_token_ids", result)

    def test_disjoint_full_partition_required(self):
        with self.assertRaises(ValueError):
            lab.mpnet_position_compensation(3, (0, 1), (1, 2))
        with self.assertRaises(ValueError):
            lab.mpnet_position_compensation(3, (0,), (1,))


class ALBERTTests(unittest.TestCase):
    def test_embedding_parameter_counts(self):
        count = lab.albert_embedding_parameters(30000, 768, 128)
        self.assertEqual(count["traditional_word_weights"], 23040000)
        self.assertEqual(count["factorized_word_and_projection_weights"], 3938304)
        self.assertEqual(count["difference"], 19101696)

    def test_factorization_is_not_always_smaller(self):
        count = lab.albert_embedding_parameters(8, 16, 16)
        self.assertGreater(count["factorized_word_and_projection_weights"], count["traditional_word_weights"])

    def test_positive_dimensions_only(self):
        with self.assertRaises(ValueError):
            lab.albert_embedding_parameters(30000, 0, 128)


class DeBERTaTests(unittest.TestCase):
    def test_c2p_and_p2c_use_opposite_signed_indices(self):
        self.assertEqual(lab.deberta_relative_index(2, 4, 8), 6)
        self.assertEqual(lab.deberta_relative_index(4, 2, 8), 10)

    def test_all_clipped_indices_are_in_table(self):
        for i in range(30):
            for j in range(30):
                self.assertIn(lab.deberta_relative_index(i, j, 8), range(16))

    def test_self_relative_index(self):
        self.assertEqual(lab.deberta_relative_index(2, 2, 8), 8)


class WWMTests(unittest.TestCase):
    def test_wwm_expands_group_without_selecting_special_tokens(self):
        self.assertEqual(lab.whole_word_target_positions((None, 0, 0, 1, 1, 1, 2, None), (1,)), (3, 4, 5))

    def test_different_word_boundaries_select_different_targets(self):
        self.assertEqual(lab.whole_word_target_positions((0, 0, 1, 1), (0,)), (0, 1))
        self.assertEqual(lab.whole_word_target_positions((0, 0, 0, 1), (0,)), (0, 1, 2))

    def test_invalid_word_id_rejected(self):
        with self.assertRaises(ValueError):
            lab.whole_word_target_positions((0, 1), (2,))

    def test_unselected_token_has_no_direct_label(self):
        self.assertEqual(lab.whole_word_target_positions((None, 0, 1, 1, 2, None), (1,)), (2, 3))


if __name__ == "__main__":
    unittest.main()
