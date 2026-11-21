"""Small, dependency-free reference implementations for the BERT tutorial.

These functions are teaching utilities, not a reproduction of Google's full BERT
tokenizer, TensorFlow model, or training pipeline. In particular,
wordpiece_tokenize expects a pre-tokenized word and an already-trained vocabulary.
"""
from __future__ import annotations

from math import exp, sqrt
from typing import Sequence


def wordpiece_tokenize(
    word: str,
    vocab: set[str],
    unk_token: str = "[UNK]",
    max_input_chars_per_word: int = 100,
) -> list[str]:
    """Greedy longest-match-first WordPiece for one pre-tokenized word.

    The caller is responsible for normalization and punctuation splitting.
    Continuation pieces are looked up with the ## prefix. If any suffix
    cannot be represented, the whole word falls back to unk_token.
    """
    if not word:
        return []
    if len(word) > max_input_chars_per_word:
        return [unk_token]

    pieces: list[str] = []
    start = 0
    while start < len(word):
        end = len(word)
        matched: str | None = None
        while end > start:
            candidate = word[start:end] if start == 0 else "##" + word[start:end]
            if candidate in vocab:
                matched = candidate
                break
            end -= 1
        if matched is None:
            return [unk_token]
        pieces.append(matched)
        start = end
    return pieces


def build_bert_inputs(
    tokens_a: Sequence[str],
    vocab: dict[str, int],
    tokens_b: Sequence[str] | None = None,
    *,
    max_length: int = 512,
    pad_to_max_length: bool = False,
) -> dict[str, list[int]]:
    """Build BERT-style IDs, token types, positions, and attention mask.

    tokens_a and tokens_b must already be tokenized. Truncation uses a simple
    longest-first policy. Padding is appended on the right.
    """
    required = ("[CLS]", "[SEP]", "[PAD]", "[UNK]")
    missing = [token for token in required if token not in vocab]
    if missing:
        raise ValueError(f"vocab is missing required special tokens: {missing}")

    pair = tokens_b is not None
    special_count = 3 if pair else 2
    if max_length < special_count:
        raise ValueError("max_length is too small for the required special tokens")

    a = list(tokens_a)
    b = list(tokens_b) if pair else []
    while len(a) + len(b) + special_count > max_length:
        if pair and len(a) > len(b):
            a.pop()
        elif pair:
            b.pop()
        elif a:
            a.pop()
        else:
            raise ValueError("cannot truncate sequence to requested max_length")

    tokens = ["[CLS]", *a, "[SEP]"]
    token_type_ids = [0] * len(tokens)
    if pair:
        tokens.extend([*b, "[SEP]"])
        token_type_ids.extend([1] * (len(b) + 1))

    unk_id = vocab["[UNK]"]
    input_ids = [vocab.get(token, unk_id) for token in tokens]
    attention_mask = [1] * len(input_ids)
    position_ids = list(range(len(input_ids)))

    if pad_to_max_length:
        pad_count = max_length - len(input_ids)
        input_ids.extend([vocab["[PAD]"]] * pad_count)
        token_type_ids.extend([0] * pad_count)
        attention_mask.extend([0] * pad_count)
        position_ids.extend([0] * pad_count)

    return {
        "input_ids": input_ids,
        "token_type_ids": token_type_ids,
        "position_ids": position_ids,
        "attention_mask": attention_mask,
    }


def scaled_dot_product_attention(
    q: Sequence[float],
    keys: Sequence[Sequence[float]],
    values: Sequence[Sequence[float]],
    allowed_mask: Sequence[bool] | None = None,
) -> tuple[list[float], list[float]]:
    """Compute one-query scaled dot-product attention using Python lists.

    allowed_mask[j] is True when key j may be attended to. This function
    demonstrates the math for a single query and one attention head.
    """
    if not q or not keys or not values:
        raise ValueError("q, keys, and values must be non-empty")
    if len(keys) != len(values):
        raise ValueError("keys and values must have the same sequence length")
    key_dim = len(q)
    value_dim = len(values[0])
    if any(len(key) != key_dim for key in keys):
        raise ValueError("all keys must have the same dimension as q")
    if any(len(value) != value_dim for value in values):
        raise ValueError("all values must have the same dimension")

    if allowed_mask is None:
        mask = [True] * len(keys)
    else:
        mask = list(allowed_mask)
        if len(mask) != len(keys):
            raise ValueError("allowed_mask length must equal key count")
        if not any(mask):
            raise ValueError("at least one key must remain visible")

    scores = []
    for key, allowed in zip(keys, mask):
        if not allowed:
            scores.append(float("-inf"))
        else:
            dot = sum(q_i * k_i for q_i, k_i in zip(q, key))
            scores.append(dot / sqrt(key_dim))

    maximum = max(score for score in scores if score != float("-inf"))
    exponentials = [0.0 if score == float("-inf") else exp(score - maximum) for score in scores]
    denominator = sum(exponentials)
    weights = [value / denominator for value in exponentials]
    output = [
        sum(weight * value[j] for weight, value in zip(weights, values))
        for j in range(value_dim)
    ]
    return output, weights


if __name__ == "__main__":
    toy_vocab = {
        "[CLS]": 101, "[SEP]": 102, "[PAD]": 0, "[UNK]": 100,
        "un": 200, "##believable": 201, "play": 202, "##ing": 203,
    }
    print(wordpiece_tokenize("unbelievable", {"un", "##believable"}))
    print(build_bert_inputs(["hello"], toy_vocab, ["world"], max_length=8, pad_to_max_length=True))
