"""Task 009 structural-only MN9 bilateral asymmetry analysis.

This module deliberately depends on the data, graph, and Task 004 sign layers
only. It does not import or execute the LIF implementation. The structural
proxy values returned here are diagnostics, not dynamical quantities.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from malecns_sim.analysis.task007 import load_male_cns_candidates
from malecns_sim.data.male_cns_v1 import (
    official_v1_mapping,
    load_male_cns_v1_numeric,
    project_numeric_connectome,
    select_publication_neuron_ids,
    threshold_curated_projection,
)
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterResolutionPolicy,
    load_male_cns_v1_neurotransmitter_evidence,
)
from malecns_sim.graph.signed import SignedAnatomicalConnectome, signed_graph_fingerprint
from malecns_sim.sign import Shiu2024SignPolicy
from malecns_sim.homology import derive_sugar_population, population_fingerprint


MN9_L = "10331"
MN9_R = "16949"
LEFT_SUGAR_FINGERPRINT = "8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7"
RIGHT_SUGAR_FINGERPRINT = "2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b"
ANALYSIS_SCHEMA = "malecns-sim-task009-structural-v1"
UNRESOLVED_SIGN = 2


@dataclass(frozen=True, slots=True)
class NodeMetadata:
    """Annotation and Task 004 metadata retained for reported nodes."""

    body_id: str
    type: str | None = None
    instance: str | None = None
    side: str | None = None
    superclass: str | None = None
    cell_class: str | None = None
    neurotransmitter: str | None = None
    dimorphism: str | None = None


@dataclass(frozen=True, slots=True)
class StructuralGraph:
    """Sparse directed edges with anatomical weights and independent signs."""

    neuron_ids: np.ndarray
    source_ids: np.ndarray
    target_ids: np.ndarray
    anatomical_weights: np.ndarray
    edge_signs: np.ndarray
    threshold: int
    unsigned_fingerprint: str
    signed_fingerprint: str

    def __post_init__(self) -> None:
        arrays = (
            self.neuron_ids,
            self.source_ids,
            self.target_ids,
            self.anatomical_weights,
            self.edge_signs,
        )
        if len({array.size for array in arrays[1:]}) != 1:
            raise ValueError("structural graph edge arrays must have equal lengths")
        if self.neuron_ids.ndim != 1:
            raise ValueError("structural graph neuron IDs must be one-dimensional")
        for array in arrays:
            array.flags.writeable = False


@dataclass(frozen=True, slots=True)
class MetricSummary:
    edge_count: int
    anatomical_weight: int
    positive_weight: int
    negative_weight: int
    unresolved_weight: int
    contributing_source_count: int
    resolved_source_count: int
    unresolved_source_count: int


@dataclass(frozen=True, slots=True)
class DirectRoute:
    source_side: str
    target_id: str
    summary: MetricSummary


@dataclass(frozen=True, slots=True)
class IncomingNeighborhood:
    target_id: str
    total_presynaptic_neuron_count: int
    total_input_edge_count: int
    total_anatomical_weight: int
    resolved_sign_presynaptic_count: int
    resolved_sign_input_edge_count: int
    resolved_sign_anatomical_weight: int
    excitatory_presynaptic_count: int
    inhibitory_presynaptic_count: int
    excitatory_anatomical_weight: int
    inhibitory_anatomical_weight: int
    unresolved_presynaptic_count: int
    unresolved_input_edge_count: int
    unresolved_anatomical_weight: int
    neutral_presynaptic_count: int
    neurotransmitter_composition: tuple[tuple[str, int, int], ...]
    top_input_types: tuple[tuple[str, int, int], ...]
    normalized_fractions: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class FirstHopMetrics:
    side: str
    target_category: str
    target_count: int
    resolved_target_count: int
    edge_count: int
    anatomical_weight: int
    positive_weight: int
    negative_weight: int
    unresolved_weight: int


@dataclass(frozen=True, slots=True)
class FirstHopPartition:
    shared: FirstHopMetrics
    left_only: FirstHopMetrics
    right_only: FirstHopMetrics


@dataclass(frozen=True, slots=True)
class IntermediateAggregate:
    route: str
    source_side: str
    target_id: str
    intermediate_id: str
    contributing_sugar_count: int
    sugar_edge_count: int
    sugar_anatomical_weight: int
    sugar_positive_edge_count: int
    sugar_negative_edge_count: int
    sugar_unresolved_edge_count: int
    sugar_positive_weight: int
    sugar_negative_weight: int
    outgoing_edge_count: int
    outgoing_anatomical_weight: int
    outgoing_positive_weight: int
    outgoing_negative_weight: int
    outgoing_unresolved_weight: int
    path_count: int
    resolved_path_count: int
    unresolved_path_count: int
    positive_path_count: int
    negative_path_count: int
    ee_path_count: int
    ei_path_count: int
    ie_path_count: int
    ii_path_count: int
    bottleneck_proxy: int
    multiplicative_anatomical_proxy: int
    signed_multiplicative_proxy: int


@dataclass(frozen=True, slots=True)
class RouteAnalysis:
    route: str
    source_side: str
    target_id: str
    source_population_count: int
    source_outgoing_anatomical_weight: int
    intermediate_count: int
    path_count: int
    resolved_path_count: int
    unresolved_path_count: int
    positive_path_count: int
    negative_path_count: int
    ee_path_count: int
    ei_path_count: int
    ie_path_count: int
    ii_path_count: int
    bottleneck_proxy: int
    multiplicative_anatomical_proxy: int
    signed_multiplicative_proxy: int
    net_positive_signed_proxy: int
    net_negative_signed_proxy: int
    normalized_proxies: tuple[tuple[str, float], ...]
    intermediates: tuple[IntermediateAggregate, ...]


@dataclass(frozen=True, slots=True)
class HomologPairComparison:
    basis: str
    type: str | None
    instance_base: str
    left_id: str
    right_id: str
    left_sugar_to_left_weight: int
    right_sugar_to_right_weight: int
    left_sugar_to_left_signed_weight: int
    right_sugar_to_right_signed_weight: int
    left_to_mn9_l_weight: int
    right_to_mn9_l_weight: int
    left_to_mn9_r_weight: int
    right_to_mn9_r_weight: int
    left_to_mn9_l_signs: tuple[int, ...]
    right_to_mn9_l_signs: tuple[int, ...]
    left_to_mn9_r_signs: tuple[int, ...]
    right_to_mn9_r_signs: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CandidateIntervention:
    body_id: str
    reasons: tuple[str, ...]
    routes: tuple[str, ...]
    signed_proxy_values: tuple[tuple[str, int], ...]


def _id(value: int | str) -> str:
    return str(int(value))


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _digest(prefix: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(prefix.encode() + b"\0" + encoded).hexdigest()


def graph_from_signed_connectome(
    signed: SignedAnatomicalConnectome, *, threshold: int
) -> StructuralGraph:
    """Make an immutable structural view without importing the dynamics layer."""

    graph = signed.connectome
    return StructuralGraph(
        neuron_ids=np.asarray(graph.neuron_ids, dtype=np.int64).copy(),
        source_ids=np.asarray(graph.source_ids, dtype=np.int64).copy(),
        target_ids=np.asarray(graph.target_ids, dtype=np.int64).copy(),
        anatomical_weights=np.asarray(graph.synapse_counts, dtype=np.int64).copy(),
        edge_signs=np.asarray(signed.presynaptic_signs, dtype=np.int8).copy(),
        threshold=threshold,
        unsigned_fingerprint=signed.unsigned_graph_fingerprint,
        signed_fingerprint=signed_graph_fingerprint(signed),
    )


def metadata_from_annotations(
    rows: Iterable[Mapping[str, object]],
    resolved_neurotransmitters: Mapping[str, str | None],
    curated_ids: Iterable[int | str],
) -> dict[str, NodeMetadata]:
    """Build metadata only for the curated neuron IDs in deterministic order."""

    allowed = {_id(value) for value in curated_ids}
    result: dict[str, NodeMetadata] = {}
    for row in rows:
        body_id = _id(row["bodyId"])
        if body_id not in allowed:
            continue
        result[body_id] = NodeMetadata(
            body_id=body_id,
            type=_clean(row.get("type")),
            instance=_clean(row.get("instance")),
            side=_clean(row.get("rootSide")) or _clean(row.get("somaSide")),
            superclass=_clean(row.get("superclass")),
            cell_class=_clean(row.get("class")),
            neurotransmitter=resolved_neurotransmitters.get(body_id),
            dimorphism=_clean(row.get("dimorphism")),
        )
    missing = allowed - result.keys()
    if missing:
        raise ValueError(f"curated metadata is missing body IDs: {sorted(missing, key=int)!r}")
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def _edge_summary(graph: StructuralGraph, indices: np.ndarray) -> MetricSummary:
    if indices.size == 0:
        return MetricSummary(0, 0, 0, 0, 0, 0, 0, 0)
    weights = graph.anatomical_weights[indices]
    signs = graph.edge_signs[indices]
    sources = graph.source_ids[indices]
    unique_sources, inverse = np.unique(sources, return_inverse=True)
    source_signs = np.full(unique_sources.size, UNRESOLVED_SIGN, dtype=np.int8)
    for position in range(unique_sources.size):
        source_signs[position] = signs[inverse == position][0]
    resolved_sources = source_signs != UNRESOLVED_SIGN
    return MetricSummary(
        edge_count=int(indices.size),
        anatomical_weight=int(weights.sum(dtype=np.int64)),
        positive_weight=int(weights[signs == 1].sum(dtype=np.int64)),
        negative_weight=int(weights[signs == -1].sum(dtype=np.int64)),
        unresolved_weight=int(weights[signs == UNRESOLVED_SIGN].sum(dtype=np.int64)),
        contributing_source_count=int(unique_sources.size),
        resolved_source_count=int(resolved_sources.sum()),
        unresolved_source_count=int((~resolved_sources).sum()),
    )


def direct_connectivity(
    graph: StructuralGraph,
    sugar_ids_by_side: Mapping[str, Sequence[int | str]],
    readout_ids: Sequence[int | str],
) -> tuple[DirectRoute, ...]:
    """Measure all unsigned and signed direct sugar-to-readout edges."""

    result: list[DirectRoute] = []
    for side in ("L", "R"):
        sugar = np.asarray(sorted({_id(value) for value in sugar_ids_by_side[side]}, key=int), dtype=np.int64)
        for target_id in sorted((_id(value) for value in readout_ids), key=int):
            mask = np.isin(graph.source_ids, sugar) & (graph.target_ids == int(target_id))
            result.append(DirectRoute(side, target_id, _edge_summary(graph, np.flatnonzero(mask))))
    return tuple(result)


def _source_indices(graph: StructuralGraph, source_ids: Sequence[int | str]) -> np.ndarray:
    return np.flatnonzero(np.isin(graph.source_ids, np.asarray(sorted({_id(value) for value in source_ids}, key=int), dtype=np.int64)))


def first_hop_metrics(
    graph: StructuralGraph,
    sugar_ids: Sequence[int | str],
    target_ids: set[int],
    category: str,
    side: str,
) -> FirstHopMetrics:
    indices = _source_indices(graph, sugar_ids)
    if target_ids:
        indices = indices[np.isin(graph.target_ids[indices], np.asarray(sorted(target_ids), dtype=np.int64))]
    summary = _edge_summary(graph, indices)
    resolved_target_count = int(
        np.unique(graph.target_ids[indices][graph.edge_signs[indices] != UNRESOLVED_SIGN]).size
    )
    return FirstHopMetrics(
        side=side,
        target_category=category,
        target_count=len(target_ids),
        resolved_target_count=resolved_target_count,
        edge_count=summary.edge_count,
        anatomical_weight=summary.anatomical_weight,
        positive_weight=summary.positive_weight,
        negative_weight=summary.negative_weight,
        unresolved_weight=summary.unresolved_weight,
    )


def first_hop_partition(
    graph: StructuralGraph,
    left_sugar_ids: Sequence[int | str],
    right_sugar_ids: Sequence[int | str],
) -> tuple[FirstHopPartition, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Partition first-hop targets and retain separate L/R weights."""

    left_indices = _source_indices(graph, left_sugar_ids)
    right_indices = _source_indices(graph, right_sugar_ids)
    left_targets = set(graph.target_ids[left_indices].tolist())
    right_targets = set(graph.target_ids[right_indices].tolist())
    categories = (
        ("shared", left_targets & right_targets),
        ("left_only", left_targets - right_targets),
        ("right_only", right_targets - left_targets),
    )
    records: dict[str, FirstHopMetrics] = {}
    for category, targets in categories:
        records[f"L:{category}"] = first_hop_metrics(graph, left_sugar_ids, targets, category, "L")
        records[f"R:{category}"] = first_hop_metrics(graph, right_sugar_ids, targets, category, "R")
    partition = FirstHopPartition(
        shared=records["L:shared"],
        left_only=records["L:left_only"],
        right_only=records["R:right_only"],
    )
    return (
        partition,
        tuple(_id(value) for value in sorted(left_targets & right_targets)),
        tuple(_id(value) for value in sorted(left_targets - right_targets)),
        tuple(_id(value) for value in sorted(right_targets - left_targets)),
    )


def first_hop_partition_records(
    graph: StructuralGraph,
    left_sugar_ids: Sequence[int | str],
    right_sugar_ids: Sequence[int | str],
) -> tuple[FirstHopMetrics, ...]:
    """Return both side records for each first-hop partition."""

    _, shared, left_only, right_only = first_hop_partition(graph, left_sugar_ids, right_sugar_ids)
    records = []
    left_targets = set(int(value) for value in shared) | set(int(value) for value in left_only)
    right_targets = set(int(value) for value in shared) | set(int(value) for value in right_only)
    for category, targets in (
        ("shared", set(int(value) for value in shared)),
        ("left_only", set(int(value) for value in left_only)),
        ("right_only", set(int(value) for value in right_only)),
    ):
        records.append(first_hop_metrics(graph, left_sugar_ids, targets, category, "L"))
        records.append(first_hop_metrics(graph, right_sugar_ids, targets, category, "R"))
    if left_targets | right_targets != left_targets | right_targets:
        raise AssertionError("first-hop partition bookkeeping failed")
    return tuple(records)


def _path_class_counts(sign1: np.ndarray, sign2: np.ndarray) -> tuple[int, int, int, int, int, int]:
    resolved1 = sign1 != UNRESOLVED_SIGN
    resolved2 = sign2 != UNRESOLVED_SIGN
    ee = int(np.count_nonzero((sign1[:, None] == 1) & (sign2[None, :] == 1)))
    ei = int(np.count_nonzero((sign1[:, None] == 1) & (sign2[None, :] == -1)))
    ie = int(np.count_nonzero((sign1[:, None] == -1) & (sign2[None, :] == 1)))
    ii = int(np.count_nonzero((sign1[:, None] == -1) & (sign2[None, :] == -1)))
    resolved = int(np.count_nonzero(resolved1[:, None] & resolved2[None, :]))
    total = int(sign1.size * sign2.size)
    return total, resolved, total - resolved, ee, ei, ie + ii


def _sum_pairwise_minimum(left: np.ndarray, right: np.ndarray) -> int:
    """Sum pairwise minima without materializing an outer-product matrix."""

    ordered = np.sort(np.asarray(left, dtype=np.int64))
    other = np.sort(np.asarray(right, dtype=np.int64))
    prefix = np.cumsum(ordered, dtype=np.int64)
    positions = np.searchsorted(ordered, other, side="right")
    below = np.where(positions, prefix[positions - 1], 0)
    above = (ordered.size - positions).astype(np.int64) * other
    return int((below + above).sum(dtype=np.int64))


def _aggregate_intermediate(
    graph: StructuralGraph,
    incoming_indices: np.ndarray,
    outgoing_indices: np.ndarray,
    *,
    route: str,
    source_side: str,
    target_id: str,
    intermediate_id: str,
) -> IntermediateAggregate:
    first_weights = graph.anatomical_weights[incoming_indices]
    second_weights = graph.anatomical_weights[outgoing_indices]
    first_signs = graph.edge_signs[incoming_indices]
    second_signs = graph.edge_signs[outgoing_indices]
    path_count, resolved_count, unresolved_count, ee, ei, ii_plus_ie = _path_class_counts(first_signs, second_signs)
    ie = int(np.count_nonzero((first_signs[:, None] == -1) & (second_signs[None, :] == 1)))
    ii = int(np.count_nonzero((first_signs[:, None] == -1) & (second_signs[None, :] == -1)))
    products = first_signs[:, None].astype(np.int16) * second_signs[None, :].astype(np.int16)
    resolved_products = products[(first_signs[:, None] != UNRESOLVED_SIGN) & (second_signs[None, :] != UNRESOLVED_SIGN)]
    source_ids = graph.source_ids[incoming_indices]
    return IntermediateAggregate(
        route=route,
        source_side=source_side,
        target_id=target_id,
        intermediate_id=intermediate_id,
        contributing_sugar_count=int(np.unique(source_ids).size),
        sugar_edge_count=int(incoming_indices.size),
        sugar_anatomical_weight=int(first_weights.sum(dtype=np.int64)),
        sugar_positive_edge_count=int(np.count_nonzero(first_signs == 1)),
        sugar_negative_edge_count=int(np.count_nonzero(first_signs == -1)),
        sugar_unresolved_edge_count=int(np.count_nonzero(first_signs == UNRESOLVED_SIGN)),
        sugar_positive_weight=int(first_weights[first_signs == 1].sum(dtype=np.int64)),
        sugar_negative_weight=int(first_weights[first_signs == -1].sum(dtype=np.int64)),
        outgoing_edge_count=int(outgoing_indices.size),
        outgoing_anatomical_weight=int(second_weights.sum(dtype=np.int64)),
        outgoing_positive_weight=int(second_weights[second_signs == 1].sum(dtype=np.int64)),
        outgoing_negative_weight=int(second_weights[second_signs == -1].sum(dtype=np.int64)),
        outgoing_unresolved_weight=int(second_weights[second_signs == UNRESOLVED_SIGN].sum(dtype=np.int64)),
        path_count=path_count,
        resolved_path_count=resolved_count,
        unresolved_path_count=unresolved_count,
        positive_path_count=int(np.count_nonzero(resolved_products > 0)),
        negative_path_count=int(np.count_nonzero(resolved_products < 0)),
        ee_path_count=ee,
        ei_path_count=ei,
        ie_path_count=ie,
        ii_path_count=ii,
        bottleneck_proxy=_sum_pairwise_minimum(first_weights, second_weights),
        multiplicative_anatomical_proxy=int(first_weights.sum(dtype=np.int64) * second_weights.sum(dtype=np.int64)),
        signed_multiplicative_proxy=int(
            (first_weights[first_signs != UNRESOLVED_SIGN] * first_signs[first_signs != UNRESOLVED_SIGN]).sum(dtype=np.int64)
            * (second_weights[second_signs != UNRESOLVED_SIGN] * second_signs[second_signs != UNRESOLVED_SIGN]).sum(dtype=np.int64)
        ),
    )


def two_hop_route(
    graph: StructuralGraph,
    sugar_ids: Sequence[int | str],
    target_id: int | str,
    *,
    source_side: str,
    metadata: Mapping[str, NodeMetadata] | None = None,
) -> RouteAnalysis:
    """Aggregate exact sugar -> intermediate -> target paths by intermediate."""

    target_text = _id(target_id)
    route = f"{source_side}_sugar_to_MN9_{'L' if target_text == MN9_L else 'R'}"
    first_indices = _source_indices(graph, sugar_ids)
    second_indices = np.flatnonzero(graph.target_ids == int(target_text))
    first_targets = graph.target_ids[first_indices]
    second_sources = graph.source_ids[second_indices]
    intermediates = np.intersect1d(first_targets, second_sources, assume_unique=False)
    aggregate: list[IntermediateAggregate] = []
    for intermediate in intermediates.tolist():
        incoming = first_indices[first_targets == intermediate]
        outgoing = second_indices[second_sources == intermediate]
        aggregate.append(
            _aggregate_intermediate(
                graph,
                incoming,
                outgoing,
                route=route,
                source_side=source_side,
                target_id=target_text,
                intermediate_id=_id(intermediate),
            )
        )
    aggregate.sort(key=lambda item: int(item.intermediate_id))
    source_summary = _edge_summary(graph, first_indices)
    sums = {
        "path_count": sum(item.path_count for item in aggregate),
        "resolved_path_count": sum(item.resolved_path_count for item in aggregate),
        "unresolved_path_count": sum(item.unresolved_path_count for item in aggregate),
        "positive_path_count": sum(item.positive_path_count for item in aggregate),
        "negative_path_count": sum(item.negative_path_count for item in aggregate),
        "ee_path_count": sum(item.ee_path_count for item in aggregate),
        "ei_path_count": sum(item.ei_path_count for item in aggregate),
        "ie_path_count": sum(item.ie_path_count for item in aggregate),
        "ii_path_count": sum(item.ii_path_count for item in aggregate),
        "bottleneck_proxy": sum(item.bottleneck_proxy for item in aggregate),
        "multiplicative_anatomical_proxy": sum(item.multiplicative_anatomical_proxy for item in aggregate),
        "signed_multiplicative_proxy": sum(item.signed_multiplicative_proxy for item in aggregate),
    }
    source_count = len(tuple(sugar_ids))
    normalizers = {
        "per_sugar_neuron": float(source_count),
        "per_unit_sugar_outgoing_anatomical_weight": float(source_summary.anatomical_weight),
    }
    normalized = tuple(
        (f"{name}:{metric}", float(sums[metric]) / value if value else 0.0)
        for name, value in normalizers.items()
        for metric in ("bottleneck_proxy", "multiplicative_anatomical_proxy", "signed_multiplicative_proxy")
    )
    return RouteAnalysis(
        route=route,
        source_side=source_side,
        target_id=target_text,
        source_population_count=source_count,
        source_outgoing_anatomical_weight=source_summary.anatomical_weight,
        intermediate_count=len(aggregate),
        **sums,
        net_positive_signed_proxy=max(sums["signed_multiplicative_proxy"], 0),
        net_negative_signed_proxy=min(sums["signed_multiplicative_proxy"], 0),
        normalized_proxies=normalized,
        intermediates=tuple(aggregate),
    )


def rank_intermediates(
    route: RouteAnalysis, metric: str, *, limit: int = 10
) -> tuple[IntermediateAggregate, ...]:
    """Rank one transparent metric with body-ID tie breaking."""

    allowed = {
        "sugar_anatomical_weight",
        "outgoing_anatomical_weight",
        "bottleneck_proxy",
        "signed_multiplicative_proxy",
    }
    if metric not in allowed:
        raise ValueError(f"unsupported Task 009 ranking metric: {metric!r}")
    return tuple(
        sorted(
            route.intermediates,
            key=lambda item: (-abs(getattr(item, metric)) if metric == "signed_multiplicative_proxy" else -getattr(item, metric), int(item.intermediate_id)),
        )[:limit]
    )


def _edge_indices_between(graph: StructuralGraph, sources: Sequence[int | str], targets: Sequence[int | str]) -> np.ndarray:
    return np.flatnonzero(
        np.isin(graph.source_ids, np.asarray(sorted({_id(value) for value in sources}, key=int), dtype=np.int64))
        & np.isin(graph.target_ids, np.asarray(sorted({_id(value) for value in targets}, key=int), dtype=np.int64))
    )


def _edge_weight_and_signs(graph: StructuralGraph, indices: np.ndarray) -> tuple[int, int, tuple[int, ...]]:
    signs = tuple(sorted(set(int(value) for value in graph.edge_signs[indices].tolist())))
    weights = graph.anatomical_weights[indices]
    signed = graph.edge_signs[indices]
    return int(weights.sum(dtype=np.int64)), int((weights[signed != UNRESOLVED_SIGN] * signed[signed != UNRESOLVED_SIGN]).sum(dtype=np.int64)), signs


def identify_homolog_pairs(metadata: Mapping[str, NodeMetadata]) -> tuple[tuple[str, str, str | None, str], ...]:
    """Identify only explicit same-type `_L`/`_R` instance pairs."""

    grouped: dict[tuple[str | None, str | None, str | None, str], dict[str, list[str]]] = defaultdict(lambda: {"L": [], "R": []})
    for item in metadata.values():
        if not item.instance or not item.instance.endswith(("_L", "_R")):
            continue
        side = item.instance[-1]
        base = item.instance[:-2]
        key = (item.type, item.superclass, item.cell_class, base)
        grouped[key][side].append(item.body_id)
    pairs = []
    for (cell_type, _, _, base), sides in grouped.items():
        if len(sides["L"]) == 1 and len(sides["R"]) == 1:
            pairs.append((sides["L"][0], sides["R"][0], cell_type, base))
    return tuple(sorted(pairs, key=lambda item: (int(item[0]), int(item[1]))))


def homolog_pair_comparisons(
    graph: StructuralGraph,
    metadata: Mapping[str, NodeMetadata],
    left_sugar_ids: Sequence[int | str],
    right_sugar_ids: Sequence[int | str],
) -> tuple[HomologPairComparison, ...]:
    pairs = identify_homolog_pairs(metadata)
    sugar_edge_indices = np.concatenate(
        (_source_indices(graph, left_sugar_ids), _source_indices(graph, right_sugar_ids))
    )
    target_edge_indices = np.flatnonzero(np.isin(graph.target_ids, np.asarray([int(MN9_L), int(MN9_R)], dtype=np.int64)))
    relevant_intermediates = set(graph.target_ids[sugar_edge_indices].tolist()) & set(graph.source_ids[target_edge_indices].tolist())
    pairs = tuple(
        pair for pair in pairs
        if int(pair[0]) in relevant_intermediates or int(pair[1]) in relevant_intermediates
    )
    pair_ids = np.asarray(
        sorted({int(value) for pair in pairs for value in pair[:2]}), dtype=np.int64
    )
    left_sugar_edge_indices = _source_indices(graph, left_sugar_ids)
    right_sugar_edge_indices = _source_indices(graph, right_sugar_ids)
    left_inputs = left_sugar_edge_indices[np.isin(graph.target_ids[left_sugar_edge_indices], pair_ids)]
    right_inputs = right_sugar_edge_indices[np.isin(graph.target_ids[right_sugar_edge_indices], pair_ids)]
    output_indices = np.flatnonzero(
        np.isin(graph.source_ids, pair_ids)
        & np.isin(graph.target_ids, np.asarray([int(MN9_L), int(MN9_R)], dtype=np.int64))
    )
    left_input_by_target: dict[int, np.ndarray] = {}
    right_input_by_target: dict[int, np.ndarray] = {}
    output_by_source_target: dict[tuple[int, int], np.ndarray] = {}
    for target in pair_ids.tolist():
        left_input_by_target[target] = left_inputs[graph.target_ids[left_inputs] == target]
        right_input_by_target[target] = right_inputs[graph.target_ids[right_inputs] == target]
    for source in pair_ids.tolist():
        for target in (int(MN9_L), int(MN9_R)):
            output_by_source_target[(source, target)] = output_indices[
                (graph.source_ids[output_indices] == source)
                & (graph.target_ids[output_indices] == target)
            ]
    result = []
    for left_id, right_id, cell_type, base in pairs:
        left_input = left_input_by_target[int(left_id)]
        right_input = right_input_by_target[int(right_id)]
        ll = output_by_source_target[(int(left_id), int(MN9_L))]
        rl = output_by_source_target[(int(right_id), int(MN9_L))]
        lr = output_by_source_target[(int(left_id), int(MN9_R))]
        rr = output_by_source_target[(int(right_id), int(MN9_R))]
        li_unsigned, li_signed, _ = _edge_weight_and_signs(graph, left_input)
        ri_unsigned, ri_signed, _ = _edge_weight_and_signs(graph, right_input)
        ll_unsigned, _, ll_signs = _edge_weight_and_signs(graph, ll)
        rl_unsigned, _, rl_signs = _edge_weight_and_signs(graph, rl)
        lr_unsigned, _, lr_signs = _edge_weight_and_signs(graph, lr)
        rr_unsigned, _, rr_signs = _edge_weight_and_signs(graph, rr)
        result.append(
            HomologPairComparison(
                basis="same type, superclass, class, and unique instance _L/_R suffix",
                type=cell_type,
                instance_base=base,
                left_id=left_id,
                right_id=right_id,
                left_sugar_to_left_weight=li_unsigned,
                right_sugar_to_right_weight=ri_unsigned,
                left_sugar_to_left_signed_weight=li_signed,
                right_sugar_to_right_signed_weight=ri_signed,
                left_to_mn9_l_weight=ll_unsigned,
                right_to_mn9_l_weight=rl_unsigned,
                left_to_mn9_r_weight=lr_unsigned,
                right_to_mn9_r_weight=rr_unsigned,
                left_to_mn9_l_signs=ll_signs,
                right_to_mn9_l_signs=rl_signs,
                left_to_mn9_r_signs=lr_signs,
                right_to_mn9_r_signs=rr_signs,
            )
        )
    return tuple(result)


def classify_dimorphism(value: str | None) -> str:
    normalized = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return "unresolved"
    if "male" in normalized and "specific" in normalized:
        return "male-specific"
    if "dimorph" in normalized:
        return "dimorphic"
    if "isomorph" in normalized:
        return "isomorphic"
    return "unresolved"


def dimorphism_summary(
    routes: Sequence[RouteAnalysis], metadata: Mapping[str, NodeMetadata]
) -> tuple[tuple[str, tuple[tuple[str, int], ...], tuple[str, ...]], ...]:
    """Summarize official local dimorphism metadata for important types."""

    important_ids = {
        item.intermediate_id
        for route in routes
        for item in rank_intermediates(route, "signed_multiplicative_proxy", limit=10)
    }
    by_type: dict[str, list[NodeMetadata]] = defaultdict(list)
    for body_id in important_ids:
        item = metadata[body_id]
        by_type[item.type or "<missing>"].append(item)
    result = []
    for cell_type, items in sorted(by_type.items()):
        counts = Counter(classify_dimorphism(item.dimorphism) for item in items)
        result.append((cell_type, tuple(sorted(counts.items())), tuple(sorted((item.body_id for item in items), key=int))))
    return tuple(result)


def freeze_candidate_list(routes: Sequence[RouteAnalysis], *, support_limit: int = 5, inhibition_limit: int = 5) -> tuple[CandidateIntervention, ...]:
    """Freeze a small structural-only Task 010 list before perturbation work."""

    by_id: dict[str, dict[str, object]] = {}
    left_routes = [route for route in routes if route.target_id == MN9_L]
    support: dict[str, tuple[int, int, str]] = {}
    for route in left_routes:
        for item in route.intermediates:
            key = item.intermediate_id
            candidate = (abs(item.signed_multiplicative_proxy), item.bottleneck_proxy, key)
            if key not in support or candidate[:2] > support[key][:2]:
                support[key] = candidate
    support_ids = [item[2] for item in sorted(support.values(), key=lambda value: (-value[0], -value[1], int(value[2])))[:support_limit]]
    for body_id in support_ids:
        by_id.setdefault(body_id, {"reasons": [], "routes": set(), "values": {}})["reasons"].append("top absolute signed multiplicative support for MN9_L")
    inhibitory: list[tuple[int, int, str, str, int]] = []
    for route in routes:
        if route.target_id != MN9_R:
            continue
        for item in route.intermediates:
            if item.signed_multiplicative_proxy < 0:
                inhibitory.append((abs(item.signed_multiplicative_proxy), item.bottleneck_proxy, item.intermediate_id, route.route, item.signed_multiplicative_proxy))
    for _, _, body_id, route, value in sorted(inhibitory, key=lambda row: (-row[0], -row[1], int(row[2]), row[3]))[:inhibition_limit]:
        entry = by_id.setdefault(body_id, {"reasons": [], "routes": set(), "values": {}})
        entry["reasons"].append("top negative signed multiplicative route proxy for MN9_R")
    for route in routes:
        for item in route.intermediates:
            if item.intermediate_id in by_id:
                entry = by_id[item.intermediate_id]
                entry["routes"].add(route.route)
                entry["values"][route.route] = item.signed_multiplicative_proxy
    result = []
    for body_id in sorted(by_id, key=int):
        entry = by_id[body_id]
        result.append(
            CandidateIntervention(
                body_id=body_id,
                reasons=tuple(sorted(set(entry["reasons"]))),
                routes=tuple(sorted(entry["routes"])),
                signed_proxy_values=tuple(sorted((key, int(value)) for key, value in entry["values"].items())),
            )
        )
    return tuple(result)


def source_normalization(route: RouteAnalysis) -> tuple[tuple[str, float], ...]:
    """Return descriptive controls; these do not alter the input population."""

    return route.normalized_proxies


def table_fingerprint(rows: Iterable[object], prefix: str = "malecns-sim-task009-table-v1") -> str:
    return _digest(prefix, [asdict(row) if hasattr(row, "__dataclass_fields__") else row for row in rows])


def _node_type_weight_summary(
    graph: StructuralGraph,
    indices: np.ndarray,
    metadata: Mapping[str, NodeMetadata],
) -> tuple[tuple[str, int, int], ...]:
    weights: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    for source, weight in zip(graph.source_ids[indices].tolist(), graph.anatomical_weights[indices].tolist()):
        item = metadata.get(_id(source))
        label = item.type if item and item.type else "<missing>"
        weights[label] += int(weight)
        counts[label] += 1
    return tuple(sorted(((label, counts[label], weights[label]) for label in weights), key=lambda row: (-row[2], row[0])))


def incoming_neighborhood(
    graph: StructuralGraph,
    target_id: int | str,
    metadata: Mapping[str, NodeMetadata],
) -> IncomingNeighborhood:
    target_text = _id(target_id)
    indices = np.flatnonzero(graph.target_ids == int(target_text))
    summary = _edge_summary(graph, indices)
    source_ids = graph.source_ids[indices]
    source_signs = graph.edge_signs[indices]
    unique_sources, first_positions = np.unique(source_ids, return_index=True)
    unique_signs = source_signs[first_positions]
    weights = graph.anatomical_weights[indices]
    nt_weights: dict[str, int] = defaultdict(int)
    nt_counts: dict[str, int] = defaultdict(int)
    for source, weight in zip(source_ids.tolist(), weights.tolist()):
        item = metadata.get(_id(source))
        label = item.neurotransmitter if item and item.neurotransmitter else "<unresolved>"
        nt_weights[label] += int(weight)
        nt_counts[label] += 1
    total = summary.anatomical_weight
    fractions = (
        ("resolved_sign_weight", summary.anatomical_weight - summary.unresolved_weight),
        ("excitatory_weight", summary.positive_weight),
        ("inhibitory_weight", summary.negative_weight),
        ("unresolved_weight", summary.unresolved_weight),
    )
    return IncomingNeighborhood(
        target_id=target_text,
        total_presynaptic_neuron_count=int(unique_sources.size),
        total_input_edge_count=summary.edge_count,
        total_anatomical_weight=total,
        resolved_sign_presynaptic_count=int(np.count_nonzero(unique_signs != UNRESOLVED_SIGN)),
        resolved_sign_input_edge_count=int(np.count_nonzero(graph.edge_signs[indices] != UNRESOLVED_SIGN)),
        resolved_sign_anatomical_weight=total - summary.unresolved_weight,
        excitatory_presynaptic_count=int(np.count_nonzero(unique_signs == 1)),
        inhibitory_presynaptic_count=int(np.count_nonzero(unique_signs == -1)),
        excitatory_anatomical_weight=summary.positive_weight,
        inhibitory_anatomical_weight=summary.negative_weight,
        unresolved_presynaptic_count=int(np.count_nonzero(unique_signs == UNRESOLVED_SIGN)),
        unresolved_input_edge_count=int(np.count_nonzero(graph.edge_signs[indices] == UNRESOLVED_SIGN)),
        unresolved_anatomical_weight=summary.unresolved_weight,
        neutral_presynaptic_count=int(np.count_nonzero(unique_signs == 0)),
        neurotransmitter_composition=tuple(sorted(((label, nt_counts[label], nt_weights[label]) for label in nt_weights), key=lambda row: (-row[2], row[0]))),
        top_input_types=_node_type_weight_summary(graph, indices, metadata)[:10],
        normalized_fractions=tuple((name, float(value) / total if total else 0.0) for name, value in fractions),
    )


def build_run_metadata(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
) -> tuple[StructuralGraph, StructuralGraph, dict[str, NodeMetadata], tuple[str, ...], tuple[str, ...]]:
    """Load the primary and thresholded graph representations once."""

    import pyarrow.feather as feather

    candidates = load_male_cns_candidates(annotation_path, neurotransmitter_path)
    sugar_candidates = tuple(item for item in candidates if item.flywire_type == "LB3")
    left = derive_sugar_population(sugar_candidates, side="L", side_field="root_side")
    right = derive_sugar_population(sugar_candidates, side="R", side_field="root_side")
    if len(left.candidate_body_ids) != 42 or len(right.candidate_body_ids) != 43:
        raise ValueError("Task 009 frozen sugar populations do not have the Task 008a counts")
    if population_fingerprint(left) != LEFT_SUGAR_FINGERPRINT or population_fingerprint(right) != RIGHT_SUGAR_FINGERPRINT:
        raise ValueError("Task 009 frozen sugar population fingerprint mismatch")
    mapping = official_v1_mapping()
    numeric = load_male_cns_v1_numeric(annotation_path, neurotransmitter_path, weights_path, mapping)
    annotation_table = feather.read_table(annotation_path)
    annotation_rows = annotation_table.to_pylist()
    selection = select_publication_neuron_ids(annotation_rows)
    projection = project_numeric_connectome(numeric, selection.neuron_ids)
    evidence = load_male_cns_v1_neurotransmitter_evidence(
        annotation_path, neurotransmitter_path, mapping, curated_only=True
    )
    signed = SignedAnatomicalConnectome.from_projection(
        projection, evidence, NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy()
    )
    nt_by_id = {
        _id(item.evidence.neuron_id): item.identity for item in signed.resolved_neurotransmitters
    }
    metadata = metadata_from_annotations(annotation_rows, nt_by_id, selection.neuron_ids)
    threshold_projection = threshold_curated_projection(projection, min_synapses=5)
    threshold_signed = SignedAnatomicalConnectome.from_projection(
        threshold_projection, evidence, NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy()
    )
    return (
        graph_from_signed_connectome(signed, threshold=0),
        graph_from_signed_connectome(threshold_signed, threshold=5),
        metadata,
        left.candidate_body_ids,
        right.candidate_body_ids,
    )


def analyze_graph(
    graph: StructuralGraph,
    metadata: Mapping[str, NodeMetadata],
    left_sugar_ids: Sequence[int | str],
    right_sugar_ids: Sequence[int | str],
) -> dict[str, object]:
    sugar_by_side = {"L": left_sugar_ids, "R": right_sugar_ids}
    readouts = (MN9_L, MN9_R)
    direct = direct_connectivity(graph, sugar_by_side, readouts)
    incoming = tuple(incoming_neighborhood(graph, target, metadata) for target in readouts)
    partition, shared, left_only, right_only = first_hop_partition(graph, left_sugar_ids, right_sugar_ids)
    partition_records = first_hop_partition_records(graph, left_sugar_ids, right_sugar_ids)
    routes = tuple(
        two_hop_route(graph, sugar_by_side[side], target, source_side=side, metadata=metadata)
        for side in ("L", "R")
        for target in readouts
    )
    homologs = homolog_pair_comparisons(graph, metadata, left_sugar_ids, right_sugar_ids)
    ranks = {
        route.route: {
            metric: tuple(item.intermediate_id for item in rank_intermediates(route, metric))
            for metric in ("sugar_anatomical_weight", "outgoing_anatomical_weight", "bottleneck_proxy", "signed_multiplicative_proxy")
        }
        for route in routes
    }
    top_details = {
        route.route: {
            metric: tuple(
                {"metadata": asdict(metadata[item.intermediate_id]), "aggregate": asdict(item)}
                for item in rank_intermediates(route, metric)
            )
            for metric in ("sugar_anatomical_weight", "outgoing_anatomical_weight", "bottleneck_proxy", "signed_multiplicative_proxy")
        }
        for route in routes
    }
    return {
        "threshold": graph.threshold,
        "unsigned_graph_fingerprint": graph.unsigned_fingerprint,
        "signed_graph_fingerprint": graph.signed_fingerprint,
        "direct": direct,
        "incoming": incoming,
        "first_hop_partition": partition,
        "first_hop_partition_records": partition_records,
        "first_hop_target_ids": {"shared": shared, "left_only": left_only, "right_only": right_only},
        "routes": routes,
        "rankings": ranks,
        "top_intermediates": top_details,
        "homolog_pairs": homologs,
        "dimorphism": dimorphism_summary(routes, metadata),
    }


def run_task009(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
) -> dict[str, object]:
    """Run Task 009 twice in one immutable load and require equal fingerprints."""

    full_graph, threshold_graph, metadata, left, right = build_run_metadata(
        annotation_path, neurotransmitter_path, weights_path
    )
    full = analyze_graph(full_graph, metadata, left, right)
    threshold = analyze_graph(threshold_graph, metadata, left, right)
    candidates = freeze_candidate_list(full["routes"])
    config = {
        "schema": ANALYSIS_SCHEMA,
        "primary_graph": "full_curated",
        "sensitivity_graph": "min_synapses=5",
        "sign_policy": "Shiu2024SignPolicy",
        "unresolved_sign": "excluded from signed metrics; retained in anatomical metrics",
        "readouts": {"MN9_L": MN9_L, "MN9_R": MN9_R},
        "dynamics_used": False,
    }
    populations = {
        "left": {"count": len(left), "body_ids": tuple(left), "fingerprint": LEFT_SUGAR_FINGERPRINT},
        "right": {"count": len(right), "body_ids": tuple(right), "fingerprint": RIGHT_SUGAR_FINGERPRINT},
    }
    readouts = {"MN9_L": MN9_L, "MN9_R": MN9_R}
    aggregate_rows = [item for route in full["routes"] for item in route.intermediates]
    fingerprints = {
        "analysis_configuration": _digest("malecns-sim-task009-config-v1", config),
        "frozen_sugar_populations": _digest("malecns-sim-task009-populations-v1", populations),
        "mn9_readouts": _digest("malecns-sim-task009-readouts-v1", readouts),
        "two_hop_aggregate_table": table_fingerprint(aggregate_rows),
        "candidate_task010_intervention_list": table_fingerprint(candidates, "malecns-sim-task009-candidates-v1"),
    }
    repeat_full = analyze_graph(full_graph, metadata, left, right)
    repeat_threshold = analyze_graph(threshold_graph, metadata, left, right)
    repeat_candidates = freeze_candidate_list(repeat_full["routes"])
    repeat_fingerprints = {
        "two_hop_aggregate_table": table_fingerprint([item for route in repeat_full["routes"] for item in route.intermediates]),
        "candidate_task010_intervention_list": table_fingerprint(repeat_candidates, "malecns-sim-task009-candidates-v1"),
        "full_report": _digest("malecns-sim-task009-full-report-v1", full),
        "threshold_report": _digest("malecns-sim-task009-threshold-report-v1", threshold),
    }
    repeat_fingerprints_expected = {
        "two_hop_aggregate_table": fingerprints["two_hop_aggregate_table"],
        "candidate_task010_intervention_list": fingerprints["candidate_task010_intervention_list"],
        "full_report": _digest("malecns-sim-task009-full-report-v1", repeat_full),
        "threshold_report": _digest("malecns-sim-task009-threshold-report-v1", repeat_threshold),
    }
    if repeat_fingerprints != repeat_fingerprints_expected:
        raise RuntimeError("Task 009 deterministic repeat fingerprint mismatch")
    return {
        "task": "009",
        "status": "COMPLETE",
        "config": config,
        "populations": populations,
        "readouts": readouts,
        "full": full,
        "min_synapses_5": threshold,
        "candidate_task010_intervention_list": candidates,
        "fingerprints": fingerprints,
        "repeat": {"identical": True, "fingerprints": repeat_fingerprints},
    }
