"""Deterministic standard-library accounting for BERT deep dives 26–28.

These helpers compute padding/pair budgets, weight-bit memory, linear
quantization error and macro-F1 only. They do NOT train, benchmark or
deploy any model, and must never be reported as measured hardware results.
"""
from __future__ import annotations

from collections.abc import Sequence


def padding_budget(lengths: Sequence[int], target: int) -> dict:
    """Token-slot ledger for one padded batch versus packed token count."""
    if not lengths or any(type(n) is not int or n < 0 for n in lengths):
        raise ValueError("lengths must be non-negative integers")
    if type(target) is not int or target < max(lengths):
        raise ValueError("target must be an integer covering the longest sample")
    padded = len(lengths) * target
    effective = sum(lengths)
    return {
        "slots": padded,
        "effective": effective,
        "empty": padded - effective,
        "empty_ratio": (padded - effective) / padded,
    }


def attention_pair_budget(lengths: Sequence[int], target: int | None = None) -> dict:
    """Real token-pair count, and the dense count when padding to target."""
    if not lengths or any(type(n) is not int or n < 0 for n in lengths):
        raise ValueError("lengths must be non-negative integers")
    real = sum(n * n for n in lengths)
    if target is None:
        return {"real_pairs": real}
    if type(target) is not int or target < max(lengths):
        raise ValueError("target must cover the longest sample")
    dense = len(lengths) * target * target
    return {"real_pairs": real, "dense_pairs": dense, "kept_ratio": real / dense}


def weight_bytes(params: int, bits: int) -> float:
    """Ideal pure-weight storage in bytes (decimal), ignoring scales/metadata."""
    if type(params) is not int or params < 0 or bits <= 0:
        raise ValueError("params must be a non-negative int and bits positive")
    return params * bits / 8


def linear_quantize(values: Sequence[float], bits: int = 8):
    """Per-tensor symmetric affine quantization; returns (integers, scale)."""
    if not values or bits < 2:
        raise ValueError("need at least one value and bits >= 2")
    qmax = 2 ** (bits - 1) - 1
    amax = max(abs(v) for v in values)
    if amax == 0:
        return [0] * len(values), 0.0
    scale = amax / qmax
    clipped = [max(-qmax, min(qmax, round(v / scale))) for v in values]
    return clipped, scale


def dequantize(values: Sequence[int], scale: float) -> list:
    return [v * scale for v in values]


def macro_f1(confusion: Sequence[Sequence[int]]) -> float:
    """Mean per-class F1 from a confusion matrix indexed [true][pred].

    A class with no true and no predicted positives is defined as F1 = 0,
    matching the workshop convention used in article 28 rather than 1.
    """
    n = len(confusion)
    if n == 0 or any(len(row) != n for row in confusion):
        raise ValueError("confusion must be a non-empty square matrix")
    scores = []
    for c in range(n):
        tp = confusion[c][c]
        fp = sum(confusion[r][c] for r in range(n) if r != c)
        fn = sum(confusion[c][p] for p in range(n) if p != c)
        scores.append(0.0 if (tp + fp == 0 or tp + fn == 0) else 2 * tp / (2 * tp + fp + fn))
    return sum(scores) / n
