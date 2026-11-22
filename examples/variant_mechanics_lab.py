"""Deterministic teaching mechanics for BERT tutorial chapters 16–20.

This module demonstrates conditions, positions, and parameter counts. It does
not implement any pretrained neural network or reproduce published results.
Standard library only.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def permutation_context(n: int, permutation: Sequence[int], target: int) -> list[int]:
    """0-index original positions visible before target in the permutation."""
    if type(n) is not int or n <= 0:
        raise ValueError("n must be positive")
    if len(permutation) != n or set(permutation) != set(range(n)):
        raise ValueError("permutation must contain every position once")
    if type(target) is not int or target not in range(n):
        raise ValueError("target must be a valid original position")
    return list(permutation[:permutation.index(target)])


def mpnet_information(n: int, permutation: Sequence[int], context_size: int,
                      target: int) -> dict[str, list[int]]:
    """Paper-level condition sets, not the actual MPNet attention tensors."""
    permutation_context(n, permutation, target)
    if type(context_size) is not int or not 0 <= context_size < n:
        raise ValueError("context_size must be within [0, n)")
    index = permutation.index(target)
    if index < context_size:
        raise ValueError("target must belong to prediction suffix")
    return {
        "visible_real_positions": list(permutation[:index]),
        "mask_slot_positions": list(permutation[context_size:]),
        "forbidden_real_positions": list(permutation[index:]),
    }


def embedding_parameter_counts(vocabulary: int, hidden: int, embedding: int) -> tuple[int, int]:
    """BERT V*H versus ALBERT V*E+E*H, ignoring other parameters."""
    if any(type(v) is not int or v <= 0 for v in (vocabulary, hidden, embedding)):
        raise ValueError("dimensions must be positive integers")
    return vocabulary * hidden, vocabulary * embedding + embedding * hidden


def shared_block_parameter_counts(layers: int, per_block: int,
                                  parameter_groups: int = 1) -> tuple[int, int]:
    """Unique block weights and total block-weight uses (NOT FLOPs)."""
    if any(type(v) is not int or v <= 0 for v in (layers, per_block, parameter_groups)):
        raise ValueError("arguments must be positive integers")
    if parameter_groups > layers or layers % parameter_groups:
        raise ValueError("groups must evenly divide number of layers")
    return parameter_groups * per_block, layers * per_block


def relative_directions(query_index: int, key_index: int) -> tuple[int, int]:
    """δ(i,j)=j−i; c2p and reverse p2c relative directions."""
    if any(type(v) is not int or v < 0 for v in (query_index, key_index)):
        raise ValueError("positions must be nonnegative integers")
    return key_index - query_index, query_index - key_index


def disentangled_raw_score(c2c: float, c2p: float, p2c: float) -> float:
    """Sum three teaching terms before attention scaling/masking/softmax."""
    if not all(math.isfinite(v) for v in (c2c, c2p, p2c)):
        raise ValueError("score terms must be finite")
    return math.fsum([c2c, c2p, p2c])


def whole_word_target_positions(groups: Sequence[Sequence[int]],
                                selected_group_ids: Sequence[int]) -> list[int]:
    """Convert nonoverlapping token-position word groups to MLM target indices."""
    if not groups or any(not group for group in groups):
        raise ValueError("groups cannot be empty")
    positions = [idx for group in groups for idx in group]
    if any(type(idx) is not int or idx < 0 for idx in positions):
        raise ValueError("token positions must be nonnegative integers")
    if len(set(positions)) != len(positions):
        raise ValueError("word groups must be disjoint")
    selected = list(selected_group_ids)
    if len(set(selected)) != len(selected) or any(
        type(group_id) is not int or group_id not in range(len(groups))
        for group_id in selected
    ):
        raise ValueError("invalid or duplicated selected groups")
    return sorted(idx for group_id in selected for idx in groups[group_id])
