"""Deterministic standard-library learning mechanics for BERT deep dives 21–25.

These functions verify adjacency masks, contrastive probabilities, distilled
distributions, INT8 rounding and LoRA algebra only. They do NOT train or
evaluate any real model, and must never be used as benchmark reproduction.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def sparse_attention_keys(length: int, query: int, radius: int,
                          global_positions: Sequence[int] = (),
                          random_positions: Sequence[int] = ()) -> list[int]:
    """Toy token-level window + global + random adjacency.

    Every global query sees all positions, and all queries see global keys.
    Actual BigBird uses a block-sparse algorithm with further constraints.
    """
    if any(type(v) is not int for v in (length, query, radius)) or length < 1 or radius < 0:
        raise ValueError("invalid length, query or radius")
    if not 0 <= query < length:
        raise ValueError("query outside sequence")
    targets = list(global_positions) + list(random_positions)
    if any(type(p) is not int or p not in range(length) for p in targets):
        raise ValueError("global/random positions must be valid")
    if query in global_positions:
        return list(range(length))
    return sorted(set(range(max(0, query - radius), min(length, query + radius + 1)))
                  | set(global_positions) | set(random_positions))


def attention_pair_budget(length: int, window: int, global_count: int) -> tuple[int, int]:
    """Dense pair count and T*(w+g) *approximation*, not exact sparse FLOPs."""
    if any(type(v) is not int for v in (length, window, global_count)):
        raise ValueError("integer arguments required")
    if length < 1 or window < 1 or global_count < 0 or global_count > length:
        raise ValueError("invalid sparse budget")
    return length * length, length * (window + global_count)


def softmax(scores: Sequence[float], temperature: float = 1.0) -> list[float]:
    """Stable softmax; output sums to one and has no NaNs."""
    if not scores or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("finite positive temperature and nonempty scores required")
    if any(not math.isfinite(s) for s in scores):
        raise ValueError("scores must be finite")
    scaled = [x / temperature for x in scores]
    offset = max(scaled)
    exps = [math.exp(x - offset) for x in scaled]
    total = math.fsum(exps)
    return [v / total for v in exps]


def contrastive_loss(similarities: Sequence[float], positive_index: int,
                     temperature: float = 1.0) -> float:
    """Single-anchor InfoNCE; batch negatives occupy all other indices."""
    if type(positive_index) is not int or positive_index not in range(len(similarities)):
        raise ValueError("positive_index is invalid")
    return -math.log(softmax(similarities, temperature)[positive_index])


def teacher_student_kl(teacher_logits: Sequence[float],
                       student_logits: Sequence[float],
                       temperature: float = 1.0,
                       scale_t_squared: bool = True) -> float:
    """KL(Pteacher||Pstudent) under optional T² scale, for one label vector."""
    if len(teacher_logits) != len(student_logits) or not teacher_logits:
        raise ValueError("teacher/student logits must have same nonempty shape")
    teacher = softmax(teacher_logits, temperature)
    student = softmax(student_logits, temperature)
    val = math.fsum(p * (math.log(p) - math.log(q)) for p, q in zip(teacher, student))
    return val * (temperature ** 2 if scale_t_squared else 1.0)


def bottleneck_projection_parameters(outer_width: int, inner_width: int) -> int:
    """Only two dense projection weight matrices, not a complete MobileBERT block."""
    if any(type(v) is not int or v <= 0 for v in (outer_width, inner_width)):
        raise ValueError("widths must be positive integers")
    return 2 * outer_width * inner_width


def quantize_symmetric_int8(value: float, scale: float) -> tuple[int, float]:
    """Simple symmetric signed INT8 demonstration with Python's tie-to-even round."""
    if not math.isfinite(value) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("finite value and positive scale required")
    q = max(-127, min(127, round(value / scale)))
    return q, q * scale


def lora_parameters(d_in: int, d_out: int, rank: int) -> tuple[int, int]:
    """Returns full weight elements and LoRA A/B weight elements."""
    if any(type(v) is not int or v < 1 for v in (d_in, d_out, rank)):
        raise ValueError("dimensions/rank must be positive integers")
    if rank > min(d_in, d_out):
        raise ValueError("rank cannot exceed smaller matrix dimension here")
    return d_in * d_out, rank * (d_in + d_out)


def lora_scalar_forward(w0: float, b: float, a: float,
                        x: float, alpha: float, rank: int) -> float:
    """One-dimensional symbolic W0+(alpha/r)BA sanity check, NOT a rank-r model."""
    if type(rank) is not int or rank <= 0 or any(
        not math.isfinite(v) for v in (w0, b, a, x, alpha)
    ):
        raise ValueError("invalid LoRA demonstration arguments")
    return (w0 + alpha / rank * b * a) * x


def rank_allocation(ranks: Sequence[int], target_budget: int) -> int:
    """Validate total rank while permitting uneven AdaLoRA-style allocations."""
    if type(target_budget) is not int or target_budget < 0:
        raise ValueError("invalid target budget")
    if not ranks or any(type(r) is not int or r < 0 for r in ranks):
        raise ValueError("invalid rank allocations")
    total = sum(ranks)
    if total != target_budget:
        raise ValueError("rank budget mismatch")
    return total
