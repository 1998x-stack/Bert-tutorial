"""Deterministic standard-library accounting for BERT fine-tuning deep dives 07-10.

These helpers only compute padding ledgers, optimizer-step counts and
word-to-subtoken label alignment. They do NOT train, evaluate or deploy any
model, and must never be reported as measured benchmark results.
"""
from __future__ import annotations

from collections.abc import Sequence


def padding_budget(lengths: Sequence[int], target: int) -> dict:
    """Token-slot ledger for one dynamically padded batch."""
    if not lengths or any(type(n) is not int or n < 0 for n in lengths):
        raise ValueError("lengths must be non-negative integers")
    if type(target) is not int or target < max(lengths):
        raise ValueError("target must cover the longest sample")
    slots = len(lengths) * target
    effective = sum(lengths)
    return {
        "slots": slots,
        "effective": effective,
        "empty": slots - effective,
        "empty_ratio": (slots - effective) / slots,
    }


def optimizer_steps(train_size: int, effective_batch: int, epochs: int) -> int:
    """Optimizer update steps: ceil per epoch times epochs (article 07 formula)."""
    for name, value in (("train_size", train_size), ("effective_batch", effective_batch), ("epochs", epochs)):
        if type(value) is not int or value <= 0:
            raise ValueError(name + " must be a positive integer")
    per_epoch = -(-train_size // effective_batch)
    return epochs * per_epoch


def align_word_labels(word_ids: Sequence[int | None], word_labels: Sequence[int], ignore: int = -100) -> list[int]:
    """Keep each word's label only on its first sub-token; others become ignore."""
    tokens = []
    previous = None
    for word_id in word_ids:
        if word_id is None:
            tokens.append(ignore)
        elif word_id != previous:
            if not 0 <= word_id < len(word_labels):
                raise ValueError("word_id out of range for word_labels")
            tokens.append(word_labels[word_id])
        else:
            tokens.append(ignore)
        previous = word_id
    return tokens


def tokens_per_update(batch: int, avg_length: int) -> int:
    """First-order tokens-per-update estimate, ignoring padding/packing (article 08)."""
    if type(batch) is not int or batch <= 0 or type(avg_length) is not int or avg_length <= 0:
        raise ValueError("batch and avg_length must be positive integers")
    return batch * avg_length


def jaccard(left: Sequence, right: Sequence) -> float:
    """Jaccard similarity |A∩B| / |A∪B| for two shingle collections (article 09)."""
    a, b = set(left), set(right)
    union = a | b
    if not union:
        raise ValueError("at least one set must be non-empty")
    return len(a & b) / len(union)


def mlm_replace_counts(selected: int) -> dict:
    """Floor 80/10/10 split of selected MLM positions; remainder stays original."""
    if type(selected) is not int or selected < 0:
        raise ValueError("selected must be a non-negative integer")
    mask = (selected * 80) // 100
    random_tokens = (selected * 10) // 100
    return {"mask": mask, "random": random_tokens, "keep": selected - mask - random_tokens}


def packing_utilization(lengths: Sequence[int], target: int) -> dict:
    """Token-slot utilisation when packing documents into target-length sequences."""
    if not lengths or any(type(n) is not int or n <= 0 for n in lengths):
        raise ValueError("lengths must be positive integers")
    if type(target) is not int or target <= 0:
        raise ValueError("target must be a positive integer")
    effective = sum(lengths)
    slots = target * -(-effective // target)
    return {"effective": effective, "slots": slots, "utilization": effective / slots}
