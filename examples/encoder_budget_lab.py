"""Small deterministic reference calculations for BERT deep dives 11–15.

These functions are *teaching mechanics*, not neural-network training or
benchmark reproduction. Only Python standard library is required.
"""
from __future__ import annotations

import math
from typing import Sequence


def token_exposures(schedule: Sequence[tuple[int, int]], batch_sequences: int) -> int:
    """Count sequence-token positions processed, before padding/packing corrections.

    schedule entries: (optimizer_updates, sequence_length), both integers.
    Returns positions processed, not unique corpus tokens.
    """
    if not isinstance(batch_sequences, int) or batch_sequences <= 0:
        raise ValueError("batch_sequences must be a positive integer")
    total = 0
    for updates, length in schedule:
        if not isinstance(updates, int) or not isinstance(length, int):
            raise ValueError("schedule entries must be integers")
        if updates < 0 or length <= 0:
            raise ValueError("updates cannot be negative and length must be positive")
        total += updates * batch_sequences * length
    return total


def language_sampling(raw_counts: Sequence[int], alpha: float = 0.7) -> list[float]:
    """Temperature-style smoothing: p_l = n_l**alpha / sum_j n_j**alpha."""
    if not raw_counts or any(not isinstance(n, int) or n <= 0 for n in raw_counts):
        raise ValueError("language counts must be positive integers")
    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError("alpha must be finite and non-negative")
    weights = [math.exp(alpha * math.log(n)) for n in raw_counts]
    denom = math.fsum(weights)
    if not math.isfinite(denom) or denom <= 0:
        raise ValueError("sampling weights overflow; rescale counts")
    return [w / denom for w in weights]


def rtd_is_replaced(original: Sequence[int],
                    corrupted: Sequence[int],
                    attention_mask: Sequence[int]) -> list[int | None]:
    """Token identity labels: 1 = replaced, 0 = original, None = padding.

    Selected MLM positions are deliberately not used: a sampled original token
    is an RTD-negative even if the position was selected for generator MLM.
    """
    if not (len(original) == len(corrupted) == len(attention_mask)):
        raise ValueError("all sequences must have the same length")
    if any(x not in (0, 1) for x in attention_mask):
        raise ValueError("attention_mask must be a 0/1 sequence")
    return [int(a != b) if m else None
            for a, b, m in zip(original, corrupted, attention_mask)]


def masked_softmax(scores: Sequence[float], allowed: Sequence[bool]) -> list[float]:
    """Stable softmax along allowed key positions only."""
    if len(scores) != len(allowed) or not scores:
        raise ValueError("scores and mask must have identical nonzero lengths")
    visible = [float(s) for s, ok in zip(scores, allowed) if ok]
    if not visible or any(not math.isfinite(s) for s in visible):
        raise ValueError("need at least one finite, visible key")
    maximum = max(visible)
    exp_scores = [math.exp(float(s) - maximum) if ok else 0.0
                  for s, ok in zip(scores, allowed)]
    normalizer = math.fsum(exp_scores)
    return [s / normalizer for s in exp_scores]


def flops_order(n_params: int, tokens_seen: int, factor: int = 6) -> int:
    """Order-of-magnitude training compute C ~= factor * N * D (article 11).

    This is a planning estimate only: it ignores attention terms, output heads,
    sequence-length details and engineering overhead, and must not be presented
    as a measured FLOP total.
    """
    if type(n_params) is not int or n_params <= 0:
        raise ValueError("n_params must be a positive integer")
    if type(tokens_seen) is not int or tokens_seen <= 0:
        raise ValueError("tokens_seen must be a positive integer")
    if type(factor) is not int or factor <= 0:
        raise ValueError("factor must be a positive integer")
    return factor * n_params * tokens_seen


def repeated_exposure(unique_tokens: int, epochs: int) -> dict:
    """Separate D_seen (repeated passes) from D_unique (distinct tokens)."""
    if type(unique_tokens) is not int or unique_tokens <= 0:
        raise ValueError("unique_tokens must be a positive integer")
    if type(epochs) is not int or epochs <= 0:
        raise ValueError("epochs must be a positive integer")
    return {"unique": unique_tokens, "seen": unique_tokens * epochs}


def param_memory_bytes(n_params: int, bytes_per_param: int) -> int:
    """Optimiser-state bytes = params x bytes_per_param (article 12; excludes activations)."""
    if type(n_params) is not int or n_params <= 0:
        raise ValueError("n_params must be a positive integer")
    if type(bytes_per_param) is not int or bytes_per_param <= 0:
        raise ValueError("bytes_per_param must be a positive integer")
    return n_params * bytes_per_param


def attention_matrix_elements(seq_len: int) -> int:
    """Dense score-matrix elements for one attention head = T**2 (article 12)."""
    if type(seq_len) is not int or seq_len <= 0:
        raise ValueError("seq_len must be a positive integer")
    return seq_len * seq_len


def scaled_gradient(grad: float, scale: float) -> float:
    """Multiply by the AMP loss-scale factor (article 12)."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    return grad * scale
