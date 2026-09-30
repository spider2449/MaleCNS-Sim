"""Frozen Task 018 integer partition of incoming MN9 synapse counts."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable


SCHEMA = "malecns-sim-task018-anatomical-asymmetry-v1"
LEFT = 10331
RIGHT = 16949
COMPONENTS = ("shared", "left_only", "right_only")
LABELS = {
    "shared": "SHARED_PARTNER_DIFFERENCE_LARGEST",
    "left_only": "LEFT_ONLY_INPUT_LARGEST",
    "right_only": "RIGHT_ONLY_OFFSET_LARGEST",
}


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def result_digest(value: dict[str, object]) -> str:
    return hashlib.sha256(canonical_json({key: item for key, item in value.items() if key != "result_digest"})).hexdigest()


def partition(edges: Iterable[tuple[int, int, int]], *, left: int = LEFT, right: int = RIGHT) -> dict[str, object]:
    """Aggregate directed pairs and partition partners by identical source body ID."""

    if left == right:
        return {"integrity_status": "FAIL", "classification": "INDETERMINATE", "error_reason": "identical_targets"}
    incoming: dict[int, dict[int, int]] = {left: {}, right: {}}
    try:
        for source, target, weight in edges:
            if not all(isinstance(value, int) and not isinstance(value, bool) for value in (source, target, weight)):
                raise ValueError("non_integer_edge")
            if weight <= 0:
                raise ValueError("nonpositive_edge_weight")
            if target in incoming:
                bucket = incoming[target]
                bucket[source] = bucket.get(source, 0) + weight
        l, r = incoming[left], incoming[right]
        pl, pr = set(l), set(r)
        shared, left_only, right_only = pl & pr, pl - pr, pr - pl
        if (shared | left_only) != pl or (shared | right_only) != pr or shared & left_only or shared & right_only or left_only & right_only:
            raise ValueError("partition_set_identity")
        wl, wr = sum(l.values()), sum(r.values())
        gap = wl - wr
        terms = {
            "shared": sum(l[p] - r[p] for p in sorted(shared)),
            "left_only": sum(l[p] for p in sorted(left_only)),
            "right_only": -sum(r[p] for p in sorted(right_only)),
        }
        if gap != sum(terms.values()):
            raise ValueError("partition_arithmetic_identity")
        if gap <= 0:
            classification, tied = "NO_LEFT_INCOMING_WEIGHT_EXCESS_IN_THIS_GRAPH", []
        else:
            largest = max(abs(value) for value in terms.values())
            tied = [key for key in COMPONENTS if abs(terms[key]) == largest]
            classification = LABELS[tied[0]] if len(tied) == 1 else "TIED_LARGEST_COMPONENTS"
        return {
            "integrity_status": "PASS",
            "left_total": wl,
            "right_total": wr,
            "gap": gap,
            "components": terms,
            "partner_counts": {"left": len(pl), "right": len(pr), "shared": len(shared), "left_only": len(left_only), "right_only": len(right_only)},
            "partition_identity_verified": True,
            "classification": classification,
            "tied_components": tied if len(tied) > 1 else [],
            "fractions": {key: terms[key] / gap for key in COMPONENTS} if gap > 0 else None,
            "fractions_null_reason": "zero_gap" if gap == 0 else "reversed_gap" if gap < 0 else None,
        }
    except ValueError as exc:
        return {"integrity_status": "FAIL", "classification": "INDETERMINATE", "error_reason": str(exc)}


def sensitivity(edges: Iterable[tuple[int, int, int]]) -> dict[str, object]:
    """Apply the frozen threshold after duplicate-pair aggregation."""

    pairs: dict[tuple[int, int], int] = {}
    for source, target, weight in edges:
        pairs[(source, target)] = pairs.get((source, target), 0) + weight
    result = partition((source, target, weight) for (source, target), weight in sorted(pairs.items()) if weight >= 5)
    result["label"] = "SENSITIVITY_MIN_SYNAPSES_5"
    return result
