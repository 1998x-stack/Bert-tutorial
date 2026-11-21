import unittest

from examples.bert_mechanics import (
    build_bert_inputs,
    scaled_dot_product_attention,
    wordpiece_tokenize,
)


class WordPieceTests(unittest.TestCase):
    def test_longest_match_first(self):
        vocab = {"un", "##believable", "play", "##ing"}
        self.assertEqual(wordpiece_tokenize("unbelievable", vocab), ["un", "##believable"])
        self.assertEqual(wordpiece_tokenize("playing", vocab), ["play", "##ing"])

    def test_unknown_falls_back_for_the_whole_word(self):
        self.assertEqual(wordpiece_tokenize("unseen", {"un", "##known"}), ["[UNK]"])

    def test_empty_word_has_no_pieces(self):
        self.assertEqual(wordpiece_tokenize("", {"a"}), [])


class InputConstructionTests(unittest.TestCase):
    def setUp(self):
        self.vocab = {
            "[PAD]": 0, "[UNK]": 100, "[CLS]": 101, "[SEP]": 102,
            "a": 10, "b": 11, "c": 12, "d": 13,
        }

    def test_single_sequence_layout(self):
        result = build_bert_inputs(["a", "b"], self.vocab)
        self.assertEqual(result["input_ids"], [101, 10, 11, 102])
        self.assertEqual(result["token_type_ids"], [0, 0, 0, 0])
        self.assertEqual(result["attention_mask"], [1, 1, 1, 1])
        self.assertEqual(result["position_ids"], [0, 1, 2, 3])

    def test_pair_sequence_marks_second_segment(self):
        result = build_bert_inputs(["a"], self.vocab, ["b", "c"])
        self.assertEqual(result["input_ids"], [101, 10, 102, 11, 12, 102])
        self.assertEqual(result["token_type_ids"], [0, 0, 0, 1, 1, 1])

    def test_longest_first_truncation_respects_max_length(self):
        result = build_bert_inputs(
            ["a", "b", "c"], self.vocab, ["d", "a"],
            max_length=7,
        )
        self.assertEqual(len(result["input_ids"]), 7)
        self.assertEqual(result["input_ids"], [101, 10, 11, 102, 13, 10, 102])

    def test_padding_aligns_all_fields(self):
        result = build_bert_inputs(["a"], self.vocab, max_length=6, pad_to_max_length=True)
        self.assertEqual(result["input_ids"], [101, 10, 102, 0, 0, 0])
        self.assertEqual(result["attention_mask"], [1, 1, 1, 0, 0, 0])
        self.assertEqual(result["token_type_ids"], [0, 0, 0, 0, 0, 0])
        self.assertEqual(result["position_ids"], [0, 1, 2, 0, 0, 0])

    def test_missing_special_token_is_rejected(self):
        with self.assertRaises(ValueError):
            build_bert_inputs(["a"], {"[CLS]": 1})


class AttentionTests(unittest.TestCase):
    def test_masked_key_gets_zero_weight(self):
        output, weights = scaled_dot_product_attention(
            [1.0, 0.0],
            [[1.0, 0.0], [0.0, 1.0]],
            [[2.0, 3.0], [90.0, 90.0]],
            [True, False],
        )
        self.assertEqual(weights, [1.0, 0.0])
        self.assertEqual(output, [2.0, 3.0])

    def test_weights_sum_to_one(self):
        _, weights = scaled_dot_product_attention(
            [1.0, 0.0],
            [[1.0, 0.0], [0.0, 1.0]],
            [[1.0], [2.0]],
        )
        self.assertAlmostEqual(sum(weights), 1.0, places=12)

    def test_all_masked_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            scaled_dot_product_attention([1.0], [[1.0]], [[1.0]], [False])

    def test_dimension_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            scaled_dot_product_attention([1.0, 0.0], [[1.0]], [[1.0]])


if __name__ == "__main__":
    unittest.main()
