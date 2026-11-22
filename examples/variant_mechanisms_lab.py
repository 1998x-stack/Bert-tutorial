"""Deterministic Python teaching invariants, not model reproductions.

Run: python -m unittest discover -s tests -p "test_*.py" -v
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence


def permutation_visible(order: Sequence[int], target: int) -> tuple[int, ...]:
    """XLNet: previously exposed content positions; natural order is unchanged."""
    if not order or len(set(order)) != len(order) or target not in order:
        raise ValueError("target and a unique nonempty permutation are required")
    return tuple(order[:order.index(target)])


def mpnet_position_compensation(
    sequence_length: int, visible_positions: Iterable[int], target_positions: Iterable[int]
) -> dict[str, tuple[int, ...]]:
    """MPNet: position placeholders without exposing any target token IDs."""
    visible = tuple(visible_positions)
    targets = tuple(target_positions)
    if (sequence_length <= 0 or not targets
            or len(set(visible)) != len(visible)
            or len(set(targets)) != len(targets)
            or set(visible) & set(targets)
            or set(visible) | set(targets) != set(range(sequence_length))):
        raise ValueError("visible and target positions must be a disjoint full partition")
    return {
        "visible_content_positions": tuple(sorted(visible)),
        "masked_position_slots": tuple(sorted(targets)),
        "all_position_slots": tuple(range(sequence_length)),
    }


def albert_embedding_parameters(vocab_size: int, hidden_size: int, embedding_size: int) -> dict[str, int]:
    """Count only word-embedding and projection weights, not full-model parameters."""
    if min(vocab_size, hidden_size, embedding_size) <= 0:
        raise ValueError("all embedding dimensions must be positive")
    traditional = vocab_size * hidden_size
    factorized = vocab_size * embedding_size + embedding_size * hidden_size
    return {
        "traditional_word_weights": traditional,
        "factorized_word_and_projection_weights": factorized,
        "difference": traditional - factorized,
    }


def deberta_relative_index(query_position: int, key_position: int, max_relative_positions: int) -> int:
    """Signed i-j, clipped to [-k,k-1] then offset by k; P2C reverses arguments."""
    if not all(isinstance(x, int) for x in (query_position, key_position, max_relative_positions)):
        raise ValueError("positions and window must be integers")
    if query_position < 0 or key_position < 0 or max_relative_positions <= 0:
        raise ValueError("positions must be nonnegative; window must be positive")
    delta = query_position - key_position
    k = max_relative_positions
    return min(max(delta, -k), k - 1) + k


def whole_word_target_positions(
    word_group_ids: Sequence[int | None], selected_groups: Iterable[int]
) -> tuple[int, ...]:
    """Expand selected word groups to token targets; None marks specials or padding."""
    chosen = set(selected_groups)
    if any(not isinstance(x, int) or x < 0 for x in chosen):
        raise ValueError("invalid selected word group")
    if any(x is not None and (not isinstance(x, int) or x < 0) for x in word_group_ids):
        raise ValueError("group IDs must be nonnegative integers or None")
    available = {x for x in word_group_ids if x is not None}
    if not chosen.issubset(available):
        raise ValueError("selected group absent from token sequence")
    return tuple(i for i, group in enumerate(word_group_ids) if group is not None and group in chosen)


if __name__ == "__main__":
    print("XLNet previous content:", permutation_visible((3, 1, 4, 2), 2))
    print("MPNet position slots:", mpnet_position_compensation(5, (0, 1, 2), (3, 4)))
    print("ALBERT word weight count:", albert_embedding_parameters(30000, 768, 128))
    print("DeBERTa C2P and P2C:", deberta_relative_index(2, 4, 8), deberta_relative_index(4, 2, 8))
    print("WWM expanded targets:", whole_word_target_positions((0, 0, 1, 1, 1, 2, 2), (1,)))
