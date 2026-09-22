"""Task 011 temporal mechanism audit over the frozen Task 010 interventions."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from malecns_sim.analysis.task008 import (
    DT_MS,
    MIRROR_CONDITION,
    MN9_L,
    MN9_R,
    PRIMARY_CONDITION,
    PreparedNetwork,
    PreparedTask008,
    Task008Condition,
    deterministic_seed,
    load_task008_identities,
)
from malecns_sim.analysis.task010 import (
    DEFAULT_DURATION_MS,
    DEFAULT_FREQUENCY_HZ,
    TASK008_FULL_CACHE_FINGERPRINT,
    TASK008_PREPARED_FINGERPRINT,
    _make_schedules,
    _prepare_verified_cached_network,
    load_frozen_candidate_manifest,
)
from malecns_sim.homology import population_fingerprint
from malecns_sim.dynamics import ExplicitStimulus, LIFParameters, SimulationResult, SparseTrace, simulate_lif
from malecns_sim.dynamics.lif import EffectiveSignedProjection


TASK011_SCHEMA = "malecns-sim-task011-temporal-mechanism-v1"
FROZEN_TASK011_CANDIDATES = ("10313", "10135", "12752", "512730", "43765")
FIXED_TRIAL_INDICES = (0, 10, 20)
TASK010_RESULT_DIGEST = "20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45"
WINDOWS_MS = ((0.0, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 50.0), (50.0, 100.0), (100.0, 250.0), (250.0, 500.0), (500.0, 1000.0))
STATE_ATOL = 1e-10
STATE_RTOL = 1e-12
NETWORK_DIVERGENT_NEURON_THRESHOLD = 50
NETWORK_ACTIVITY_SHIFT_FRACTION = 0.10


def _digest(prefix: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(prefix.encode("utf-8") + b"\0" + encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class Divergence:
    first_delivery_step: int | None
    first_downstream_spike_step: int | None
    first_mn9_l_state_step: int | None
    first_mn9_l_spike_step: int | None
    first_mn9_r_spike_step: int | None
    divergent_neuron_peak: int
    divergent_neuron_total: int

    def as_ms(self) -> dict[str, float | int | None]:
        return {
            "first_delivery_difference_ms": None if self.first_delivery_step is None else self.first_delivery_step * DT_MS,
            "first_downstream_spike_difference_ms": None if self.first_downstream_spike_step is None else self.first_downstream_spike_step * DT_MS,
            "first_mn9_l_state_difference_ms": None if self.first_mn9_l_state_step is None else self.first_mn9_l_state_step * DT_MS,
            "first_mn9_l_spike_difference_ms": None if self.first_mn9_l_spike_step is None else self.first_mn9_l_spike_step * DT_MS,
            "first_mn9_r_spike_difference_ms": None if self.first_mn9_r_spike_step is None else self.first_mn9_r_spike_step * DT_MS,
            "divergent_neuron_peak": self.divergent_neuron_peak,
            "divergent_neuron_total": self.divergent_neuron_total,
        }


def frozen_task011_candidate_ids() -> tuple[str, ...]:
    """Return the literal Task 011 subset of the committed Task 010 set."""

    return FROZEN_TASK011_CANDIDATES


def fixed_trial_indices(indices: Iterable[int] = FIXED_TRIAL_INDICES) -> tuple[int, ...]:
    """Validate the preregistered trial selection without observing outcomes."""

    result = tuple(int(index) for index in indices)
    if result != FIXED_TRIAL_INDICES:
        raise ValueError(f"Task 011 trial indices are frozen as {FIXED_TRIAL_INDICES}")
    return result


def validate_intervention_scope(intervention_ids: Iterable[str | int]) -> tuple[str, ...]:
    """Reject any Task 011 intervention identity outside the frozen set."""

    values = tuple(str(int(value)) for value in intervention_ids)
    if len(set(values)) != len(values):
        raise ValueError("Task 011 intervention identities must be unique")
    if any(value not in FROZEN_TASK011_CANDIDATES for value in values):
        raise ValueError("Task 011 cannot introduce a new intervention candidate")
    return values


def _event_sets_by_step(result: SimulationResult, excluded_ids: Iterable[int] = ()) -> dict[int, set[int]]:
    excluded = {int(value) for value in excluded_ids}
    events: dict[int, set[int]] = defaultdict(set)
    for neuron_id, timestep in zip(result.spike_neuron_ids.tolist(), result.spike_timesteps.tolist()):
        if int(neuron_id) not in excluded:
            events[int(timestep)].add(int(neuron_id))
    return dict(events)


def _first_set_difference(left: Mapping[int, set[int]], right: Mapping[int, set[int]]) -> int | None:
    steps = sorted(set(left) | set(right))
    for step in steps:
        if left.get(step, set()) != right.get(step, set()):
            return step
    return None


def _first_neuron_spike_difference(left: SimulationResult, right: SimulationResult, neuron_id: str) -> int | None:
    left_steps = left.spike_timesteps[left.spike_neuron_ids == int(neuron_id)]
    right_steps = right.spike_timesteps[right.spike_neuron_ids == int(neuron_id)]
    differing = sorted(set(left_steps.tolist()) ^ set(right_steps.tolist()))
    return int(differing[0]) if differing else None


def _first_state_difference(left: SimulationResult, right: SimulationResult, neuron_id: str) -> int | None:
    if left.trace_v_mV is None or right.trace_v_mV is None or left.trace_g_mV is None or right.trace_g_mV is None:
        return None
    left_positions = np.flatnonzero(left.trace_neuron_ids == int(neuron_id))
    right_positions = np.flatnonzero(right.trace_neuron_ids == int(neuron_id))
    if left_positions.size != 1 or right_positions.size != 1:
        return None
    left_v = left.trace_v_mV[int(left_positions[0])]
    right_v = right.trace_v_mV[int(right_positions[0])]
    left_g = left.trace_g_mV[int(left_positions[0])]
    right_g = right.trace_g_mV[int(right_positions[0])]
    different = (np.abs(left_v - right_v) > STATE_ATOL + STATE_RTOL * np.abs(left_v)) | (
        np.abs(left_g - right_g) > STATE_ATOL + STATE_RTOL * np.abs(left_g)
    )
    positions = np.flatnonzero(different)
    return int(positions[0]) if positions.size else None


def _delivery_difference(left: SparseTrace | None, right: SparseTrace | None) -> int | None:
    if left is None or right is None:
        return None
    if not np.array_equal(left.timesteps, right.timesteps):
        raise ValueError("sparse trace timestep grids differ")
    for index in range(left.timesteps.size):
        if not np.array_equal(left.delivered_event_counts[index], right.delivered_event_counts[index]):
            return int(left.timesteps[index])
        if not np.array_equal(left.delivered_target_counts[index], right.delivered_target_counts[index]):
            return int(left.timesteps[index])
        if not np.array_equal(left.delivered_target_index_sums[index], right.delivered_target_index_sums[index]):
            return int(left.timesteps[index])
        if not np.isclose(
            left.delivered_weight_sums_mV[index], right.delivered_weight_sums_mV[index], rtol=STATE_RTOL, atol=STATE_ATOL
        ) or not np.isclose(
            left.delivered_abs_weight_sums_mV[index], right.delivered_abs_weight_sums_mV[index], rtol=STATE_RTOL, atol=STATE_ATOL
        ):
            return int(left.timesteps[index])
    return None


def _divergent_neurons_by_step(left: SimulationResult, right: SimulationResult, excluded_ids: Iterable[int]) -> dict[int, set[int]]:
    left_events = _event_sets_by_step(left, excluded_ids)
    right_events = _event_sets_by_step(right, excluded_ids)
    return {step: left_events.get(step, set()) ^ right_events.get(step, set()) for step in sorted(set(left_events) | set(right_events))}


def detect_first_divergence(
    baseline: SimulationResult,
    silenced: SimulationResult,
    *,
    input_neuron_ids: Iterable[int] = (),
    candidate_id: str,
) -> tuple[Divergence, dict[int, set[int]]]:
    """Compare sparse delivery, downstream spikes, MN9 state, and spike trains."""

    excluded = tuple(input_neuron_ids) + (int(candidate_id),)
    divergent = _divergent_neurons_by_step(baseline, silenced, excluded)
    nonempty_counts = [len(values) for values in divergent.values() if values]
    divergence = Divergence(
        first_delivery_step=_delivery_difference(baseline.sparse_trace, silenced.sparse_trace),
        first_downstream_spike_step=_first_set_difference(
            _event_sets_by_step(baseline, excluded), _event_sets_by_step(silenced, excluded)
        ),
        first_mn9_l_state_step=_first_state_difference(baseline, silenced, MN9_L),
        first_mn9_l_spike_step=_first_neuron_spike_difference(baseline, silenced, MN9_L),
        first_mn9_r_spike_step=_first_neuron_spike_difference(baseline, silenced, MN9_R),
        divergent_neuron_peak=max(nonempty_counts, default=0),
        divergent_neuron_total=len(set().union(*divergent.values())) if divergent else 0,
    )
    return divergence, divergent


def propagation_windows(
    baseline: SimulationResult,
    silenced: SimulationResult,
    *,
    divergent: Mapping[int, set[int]],
    first_delivery_step: int | None,
) -> tuple[dict[str, object], ...]:
    """Aggregate divergent spikes in fixed windows after the first delivery change."""

    if first_delivery_step is None:
        return tuple(
            {
                "start_ms": start,
                "end_ms": end,
                "divergent_spike_events": 0,
                "divergent_neurons": 0,
                "mn9_l_delta_spikes": 0,
                "mn9_r_delta_spikes": 0,
            }
            for start, end in WINDOWS_MS
        )
    baseline_events = _event_sets_by_step(baseline)
    silenced_events = _event_sets_by_step(silenced)
    records = []
    for start_ms, end_ms in WINDOWS_MS:
        start_step = first_delivery_step + int(round(start_ms / DT_MS))
        end_step = first_delivery_step + int(round(end_ms / DT_MS))
        changed_events = 0
        changed_neurons: set[int] = set()
        for step in range(start_step, end_step):
            changed = divergent.get(step, set())
            changed_events += len(changed)
            changed_neurons.update(changed)
        baseline_l = sum(len(values & {int(MN9_L)}) for step, values in baseline_events.items() if start_step <= step < end_step)
        silenced_l = sum(len(values & {int(MN9_L)}) for step, values in silenced_events.items() if start_step <= step < end_step)
        baseline_r = sum(len(values & {int(MN9_R)}) for step, values in baseline_events.items() if start_step <= step < end_step)
        silenced_r = sum(len(values & {int(MN9_R)}) for step, values in silenced_events.items() if start_step <= step < end_step)
        records.append(
            {
                "start_ms": start_ms,
                "end_ms": end_ms,
                "divergent_spike_events": changed_events,
                "divergent_neurons": len(changed_neurons),
                "mn9_l_delta_spikes": silenced_l - baseline_l,
                "mn9_r_delta_spikes": silenced_r - baseline_r,
            }
        )
    return tuple(records)


def _positions_for_ids(projection: EffectiveSignedProjection, ids: Iterable[str | int]) -> np.ndarray:
    values = np.asarray([int(value) for value in ids], dtype=np.int64)
    positions = np.searchsorted(projection.neuron_ids, values)
    if np.any(positions >= projection.neuron_ids.size) or np.any(projection.neuron_ids[positions] != values):
        raise KeyError("requested trace identity is absent from the frozen projection")
    return positions


def _outgoing_edges(projection: EffectiveSignedProjection, candidate_id: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    position = int(_positions_for_ids(projection, (candidate_id,))[0])
    start, end = projection.outgoing_indptr[position : position + 2]
    return projection.outgoing_targets[start:end], projection.outgoing_weights_mV[start:end], projection.neuron_ids[projection.outgoing_targets[start:end]]


def _path_metadata(
    projection: EffectiveSignedProjection,
    candidate_id: str,
    readout_id: str,
    *,
    supported_routes: Sequence[str],
    route_name: str,
) -> dict[str, object]:
    candidate_position = int(_positions_for_ids(projection, (candidate_id,))[0])
    readout_position = int(_positions_for_ids(projection, (readout_id,))[0])
    start, end = projection.outgoing_indptr[candidate_position : candidate_position + 2]
    first_targets = projection.outgoing_targets[start:end]
    first_weights = projection.outgoing_weights_mV[start:end]
    direct_mask = first_targets == readout_position
    two_hop_count = 0
    positive_routes = 0
    negative_routes = 0
    for intermediate, first_weight in zip(first_targets.tolist(), first_weights.tolist()):
        second_start, second_end = projection.outgoing_indptr[int(intermediate) : int(intermediate) + 2]
        second_targets = projection.outgoing_targets[second_start:second_end]
        second_weights = projection.outgoing_weights_mV[second_start:second_end]
        matching = np.flatnonzero(second_targets == readout_position)
        for second_index in matching.tolist():
            two_hop_count += 1
            if first_weight * float(second_weights[second_index]) > 0.0:
                positive_routes += 1
            else:
                negative_routes += 1
    direct_positive = int(np.count_nonzero(first_weights[direct_mask] > 0.0))
    direct_negative = int(np.count_nonzero(first_weights[direct_mask] < 0.0))
    if direct_mask.any():
        shortest = 1
    elif two_hop_count:
        shortest = 2
    else:
        shortest = None
    return {
        "readout": readout_id,
        "route_name": route_name,
        "annotation_supported": route_name in supported_routes,
        "direct_edge": bool(direct_mask.any()),
        "shortest_known_path_length": shortest,
        "two_hop_route_count": two_hop_count,
        "positive_signed_route_count": direct_positive + positive_routes,
        "negative_signed_route_count": direct_negative + negative_routes,
        "signed_path": "negative" if (direct_negative + negative_routes) and not (direct_positive + positive_routes) else "positive" if (direct_positive + positive_routes) and not (direct_negative + negative_routes) else "mixed" if (direct_positive + positive_routes) or (direct_negative + negative_routes) else None,
    }


def structural_summary(
    projection: EffectiveSignedProjection,
    candidate: Mapping[str, object],
    annotation_by_id: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    """Summarize immediate signed outgoing structure and known short routes."""

    candidate_id = str(candidate["body_id"])
    target_positions, weights, target_ids_array = _outgoing_edges(projection, candidate_id)
    anatomical_weights = np.rint(np.abs(weights) / projection.synaptic_weight_mV).astype(np.int64)
    positive_weights = int(anatomical_weights[weights > 0.0].sum(dtype=np.int64))
    negative_weights = int(anatomical_weights[weights < 0.0].sum(dtype=np.int64))
    target_type_totals: dict[str, int] = defaultdict(int)
    for target_id, anatomical_weight in zip(target_ids_array.tolist(), anatomical_weights.tolist()):
        target_type = str(annotation_by_id.get(str(target_id), {}).get("type") or "unknown")
        target_type_totals[target_type] += int(anatomical_weight)
    target_types = [
        {"type": target_type, "anatomical_weight": weight}
        for target_type, weight in sorted(target_type_totals.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    routes = tuple(str(item) for item in candidate.get("routes", ()))
    path_l = _path_metadata(
        projection,
        candidate_id,
        MN9_L,
        supported_routes=routes,
        route_name=f"L_sugar_to_MN9_L" if "L_sugar_to_MN9_L" in routes else f"R_sugar_to_MN9_L",
    )
    path_r = _path_metadata(
        projection,
        candidate_id,
        MN9_R,
        supported_routes=routes,
        route_name=f"L_sugar_to_MN9_R" if "L_sugar_to_MN9_R" in routes else f"R_sugar_to_MN9_R",
    )
    direct_targets = set(target_ids_array.tolist())
    return {
        "body_id": candidate_id,
        "neurotransmitter": candidate.get("neurotransmitter"),
        "outgoing_target_count": int(target_positions.size),
        "total_outgoing_anatomical_weight": int(anatomical_weights.sum(dtype=np.int64)),
        "positive_outgoing_anatomical_weight": positive_weights,
        "negative_outgoing_anatomical_weight": negative_weights,
        "direct_edge_to_MN9_L": int(MN9_L) in direct_targets,
        "direct_edge_to_MN9_R": int(MN9_R) in direct_targets,
        "short_paths": {"MN9_L": path_l, "MN9_R": path_r},
        "major_immediate_target_types": target_types,
    }


def _candidate_event_steps(result: SimulationResult, candidate_id: str) -> np.ndarray:
    return result.spike_timesteps[result.spike_neuron_ids == int(candidate_id)]


def baseline_activity_exposure(
    results: Sequence[SimulationResult],
    candidate_id: str,
    projection: EffectiveSignedProjection,
) -> dict[str, object]:
    """Report baseline activity and the outgoing event opportunity."""

    _, _, target_ids = _outgoing_edges(projection, candidate_id)
    spike_counts = [int(_candidate_event_steps(result, candidate_id).size) for result in results]
    duration_ms = float(results[0].duration_ms)
    return {
        "trial_count": len(results),
        "spike_counts": spike_counts,
        "spike_count_total": int(sum(spike_counts)),
        "rate_hz_mean": float(np.mean(spike_counts) * 1000.0 / duration_ms),
        "outgoing_delivered_event_counts": [int(count * target_ids.size) for count in spike_counts],
        "outgoing_delivered_event_count_total": int(sum(spike_counts) * target_ids.size),
        "active_postsynaptic_target_counts": [int(target_ids.size if count else 0) for count in spike_counts],
        "active_postsynaptic_target_count_union": int(target_ids.size if any(spike_counts) else 0),
    }


def first_hop_target_analysis(
    baseline: Sequence[SimulationResult],
    silenced: Sequence[SimulationResult],
    projection: EffectiveSignedProjection,
    candidate_id: str,
    annotation_by_id: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    target_positions, weights, target_ids_array = _outgoing_edges(projection, candidate_id)
    records = []
    changed_ids: set[str] = set()
    earliest_by_target: dict[str, int] = {}
    for target_position, weight, target_id in zip(target_positions.tolist(), weights.tolist(), target_ids_array.tolist()):
        target = str(target_id)
        changed_steps = []
        for left, right in zip(baseline, silenced):
            left_steps = set(left.spike_timesteps[left.spike_neuron_ids == int(target)].tolist())
            right_steps = set(right.spike_timesteps[right.spike_neuron_ids == int(target)].tolist())
            changed_steps.extend(left_steps ^ right_steps)
        if changed_steps:
            changed_ids.add(target)
            earliest_by_target[target] = min(changed_steps)
    route_flags = {}
    for readout in (MN9_L, MN9_R):
        readout_position = int(_positions_for_ids(projection, (readout,))[0])
        route_flags[readout] = set()
        for target_position in target_positions.tolist():
            start, end = projection.outgoing_indptr[int(target_position) : int(target_position) + 2]
            if np.any(projection.outgoing_targets[start:end] == readout_position):
                route_flags[readout].add(str(projection.neuron_ids[int(target_position)]))
    for target_position, weight, target_id in zip(target_positions.tolist(), weights.tolist(), target_ids_array.tolist()):
        target = str(target_id)
        records.append(
            {
                "target_id": target,
                "target_type": annotation_by_id.get(target, {}).get("type"),
                "connection_sign": "positive" if weight > 0.0 else "negative" if weight < 0.0 else "zero",
                "anatomical_weight": int(round(abs(float(weight)) / projection.synaptic_weight_mV)),
                "participates_known_two_hop_route_to_MN9_L": target in route_flags[MN9_L],
                "participates_known_two_hop_route_to_MN9_R": target in route_flags[MN9_R],
                "spikes_change": target in changed_ids,
                "earliest_spike_divergence_ms": None if target not in earliest_by_target else earliest_by_target[target] * DT_MS,
            }
        )
    return {
        "target_count": len(records),
        "targets_whose_spikes_change": len(changed_ids),
        "changed_target_ids": sorted(changed_ids, key=int),
        "earliest_target_divergence_ms": None if not earliest_by_target else min(earliest_by_target.values()) * DT_MS,
        "targets": records,
    }


def _global_delta_before(
    baseline: SimulationResult,
    silenced: SimulationResult,
    step: int | None,
) -> tuple[int, int]:
    if step is None:
        return 0, 0
    baseline_spikes = int(np.count_nonzero(baseline.spike_timesteps <= step))
    silenced_spikes = int(np.count_nonzero(silenced.spike_timesteps <= step))
    baseline_delivered = 0 if baseline.sparse_trace is None else int(baseline.sparse_trace.delivered_event_counts[: step + 1].sum())
    silenced_delivered = 0 if silenced.sparse_trace is None else int(silenced.sparse_trace.delivered_event_counts[: step + 1].sum())
    return silenced_spikes - baseline_spikes, silenced_delivered - baseline_delivered


def _mechanism_evidence(
    candidate: Mapping[str, object],
    side: str,
    readout_id: str,
    structural: Mapping[str, object],
    divergence: Divergence,
    divergent: Mapping[int, set[int]],
    first_hop: Mapping[str, object],
    baseline: SimulationResult,
    silenced: SimulationResult,
) -> dict[str, object]:
    path = structural["short_paths"]["MN9_L" if readout_id == MN9_L else "MN9_R"]
    first_hop_before_mn9 = (
        first_hop["earliest_target_divergence_ms"] is not None
        and divergence.as_ms()["first_mn9_l_state_difference_ms"] is not None
        and first_hop["earliest_target_divergence_ms"] < divergence.as_ms()["first_mn9_l_state_difference_ms"]
    )
    first_delivery = divergence.first_delivery_step
    mn9_step = divergence.first_mn9_l_state_step or divergence.first_mn9_l_spike_step
    timing_compatible = (
        path["shortest_known_path_length"] is not None
        and first_delivery is not None
        and mn9_step is not None
        and mn9_step * DT_MS + DT_MS >= first_delivery * DT_MS + float(path["shortest_known_path_length"]) * LIFParameters().synaptic_delay_ms
    )
    candidate_path_sign = path["signed_path"]
    baseline_before = int(np.count_nonzero(baseline.spike_timesteps <= (mn9_step or 0)))
    silenced_before = int(np.count_nonzero(silenced.spike_timesteps <= (mn9_step or 0)))
    network_delta_spikes, network_delta_deliveries = _global_delta_before(baseline, silenced, mn9_step)
    unique_before = len(set().union(*(values for step, values in divergent.items() if mn9_step is not None and step <= mn9_step))) if mn9_step is not None else 0
    broad_before = unique_before >= NETWORK_DIVERGENT_NEURON_THRESHOLD
    baseline_deliveries_before = 0 if baseline.sparse_trace is None or mn9_step is None else int(baseline.sparse_trace.delivered_event_counts[: mn9_step + 1].sum())
    substantial_activity_shift = baseline_deliveries_before > 0 and abs(network_delta_deliveries) >= NETWORK_ACTIVITY_SHIFT_FRACTION * baseline_deliveries_before
    multiple_branches = sum(
        bool(record["spikes_change"])
        and record["earliest_spike_divergence_ms"] is not None
        and mn9_step is not None
        and float(record["earliest_spike_divergence_ms"]) <= mn9_step * DT_MS
        for record in first_hop["targets"]
    ) >= 2
    readout_delta = (
        int(np.count_nonzero(silenced.spike_neuron_ids == int(readout_id)))
        - int(np.count_nonzero(baseline.spike_neuron_ids == int(readout_id)))
    )
    effect_sign_compatible = (
        (candidate_path_sign == "negative" and readout_delta >= 0)
        or (candidate_path_sign == "positive" and readout_delta <= 0)
        or candidate_path_sign == "mixed"
    )
    short_path = bool(
        path["annotation_supported"]
        and path["shortest_known_path_length"] is not None
        and first_hop_before_mn9
        and timing_compatible
        and effect_sign_compatible
        and not broad_before
    )
    candidate_active = bool(_candidate_event_steps(baseline, str(candidate["body_id"])).size)
    no_explanatory_short_path = bool(
        not path["annotation_supported"]
        or path["shortest_known_path_length"] is None
        or not effect_sign_compatible
        or not first_hop_before_mn9
    )
    network = bool(
        candidate_active
        and (broad_before or no_explanatory_short_path or multiple_branches or substantial_activity_shift)
    )
    return {
        "readout": readout_id,
        "side": side,
        "annotation_supported_signed_short_path": bool(path["annotation_supported"] and path["shortest_known_path_length"] is not None),
        "first_hop_target_changes_before_mn9": first_hop_before_mn9,
        "delay_compatible": timing_compatible,
        "signed_effect_compatible": effect_sign_compatible,
        "broad_divergence_before_mn9": broad_before,
        "multiple_recurrent_branches_before_mn9": multiple_branches,
        "candidate_active_in_baseline": candidate_active,
        "no_explanatory_short_path": no_explanatory_short_path,
        "network_delta_spikes_before_mn9": network_delta_spikes,
        "network_delta_delivered_events_before_mn9": network_delta_deliveries,
        "divergent_neurons_before_mn9": unique_before,
        "substantial_activity_shift_before_mn9": substantial_activity_shift,
        "short_path_compatible": short_path,
        "network_redistribution_compatible": network,
        "baseline_spikes_before_mn9": baseline_before,
        "silenced_spikes_before_mn9": silenced_before,
    }


def classify_mechanism(evidence: Sequence[Mapping[str, object]]) -> str:
    """Apply the preregistered conservative compatibility classification."""

    short = any(bool(item["short_path_compatible"]) for item in evidence)
    network = any(bool(item["network_redistribution_compatible"]) for item in evidence)
    if short and network:
        return "MIXED"
    if short:
        return "SHORT_PATH_COMPATIBLE"
    if network:
        return "NETWORK_REDISTRIBUTION_COMPATIBLE"
    return "UNRESOLVED"


def _annotation_map(annotation_path: str | Path) -> dict[str, Mapping[str, object]]:
    import pyarrow.feather as feather

    rows = feather.read_table(annotation_path, columns=["bodyId", "type", "instance", "superclass", "class", "rootSide"]).to_pylist()
    return {str(row["bodyId"]): row for row in rows}


def _run_trace_results(
    prepared: PreparedNetwork,
    schedules: Sequence[tuple[int, int, ExplicitStimulus]],
    *,
    silenced_ids: Sequence[str] = (),
    trace_ids: Sequence[str] = (),
    duration_ms: float = DEFAULT_DURATION_MS,
    force_cpu: bool = False,
) -> tuple[SimulationResult, ...]:
    if prepared.cuda_graph is not None and not force_cpu:
        from malecns_sim.dynamics.cuda import simulate_cuda_batch

        return simulate_cuda_batch(
            prepared.projection,
            tuple(item[2] for item in schedules),
            duration_ms=duration_ms,
            parameters=LIFParameters(),
            dt_ms=DT_MS,
            silenced_neuron_ids=tuple(int(item) for item in silenced_ids),
            trace_neuron_ids=tuple(int(item) for item in trace_ids),
            collect_sparse_trace=True,
            cuda_graph=prepared.cuda_graph,
        )
    return tuple(
        simulate_lif(
            prepared.projection,
            duration_ms=duration_ms,
            stimulus=item[2],
            parameters=LIFParameters(),
            dt_ms=DT_MS,
            silenced_neuron_ids=tuple(int(value) for value in silenced_ids),
            trace_neuron_ids=tuple(int(value) for value in trace_ids),
            collect_sparse_trace=True,
        )
        for item in schedules
    )


def _atomic_write_json(path: str | Path, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    os.replace(temporary, target)


def _aggregate_windows(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[float, float], list[Mapping[str, object]]] = defaultdict(list)
    for record in records:
        grouped[(float(record["start_ms"]), float(record["end_ms"]))].append(record)
    result = []
    for window in WINDOWS_MS:
        values = grouped[window]
        result.append(
            {
                "start_ms": window[0],
                "end_ms": window[1],
                "trial_count": len(values),
                "mean_divergent_spike_events": float(np.mean([item["divergent_spike_events"] for item in values])) if values else 0.0,
                "mean_divergent_neurons": float(np.mean([item["divergent_neurons"] for item in values])) if values else 0.0,
                "mean_mn9_l_delta_spikes": float(np.mean([item["mn9_l_delta_spikes"] for item in values])) if values else 0.0,
                "mean_mn9_r_delta_spikes": float(np.mean([item["mn9_r_delta_spikes"] for item in values])) if values else 0.0,
                "trials": list(values),
            }
        )
    return result


def run_task011(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    task008_results_path: str | Path,
    task009_results_path: str | Path,
    task010_results_path: str | Path,
    cache_path: str | Path,
    output_path: str | Path,
) -> dict[str, object]:
    """Run the fixed Task 011 temporal audit and write its derived artifact."""

    del weights_path
    del task008_results_path
    manifest = load_frozen_candidate_manifest(task009_results_path)
    validate_intervention_scope(FROZEN_TASK011_CANDIDATES)
    if not set(FROZEN_TASK011_CANDIDATES).issubset(set(manifest.body_ids)):
        raise RuntimeError("Task 011 frozen cases are not contained in the Task 010 manifest")
    selected_manifest_ids = tuple(item.body_id for item in manifest.candidates if item.body_id in FROZEN_TASK011_CANDIDATES)
    if set(selected_manifest_ids) != set(FROZEN_TASK011_CANDIDATES) or len(selected_manifest_ids) != len(FROZEN_TASK011_CANDIDATES):
        raise RuntimeError("Task 011 candidate identity is not frozen")
    task010_report = json.loads(Path(task010_results_path).read_text(encoding="utf-8"))
    if task010_report.get("result_digest") != TASK010_RESULT_DIGEST:
        raise RuntimeError("Task 010 result digest does not match the authoritative checkpoint")
    identities: PreparedTask008 = load_task008_identities(annotation_path, neurotransmitter_path)
    prepared = _prepare_verified_cached_network(cache_path)
    if prepared.cache_fingerprint != TASK008_FULL_CACHE_FINGERPRINT or prepared.fingerprint != TASK008_PREPARED_FINGERPRINT:
        raise RuntimeError("Task 008 prepared graph identity mismatch")
    trial_indices = fixed_trial_indices()
    parameters = LIFParameters()
    populations = ((PRIMARY_CONDITION, identities.sugar_left, "L"), (MIRROR_CONDITION, identities.sugar_right, "R"))
    schedules_by_condition: dict[str, tuple[tuple[int, int, ExplicitStimulus], ...]] = {}
    for condition, population, side in populations:
        all_schedules = _make_schedules(
            prepared,
            population,
            experiment_identity=identities.fingerprint,
            side=side,
            trial_count=30,
            frequency_hz=DEFAULT_FREQUENCY_HZ,
            duration_ms=DEFAULT_DURATION_MS,
            parameters=parameters,
        )
        schedules_by_condition[condition.name] = tuple(item for item in all_schedules if item[0] in trial_indices)
    trace_ids = tuple(FROZEN_TASK011_CANDIDATES) + (MN9_L, MN9_R)
    baseline_by_condition: dict[str, tuple[SimulationResult, ...]] = {}
    silenced_by_case: dict[tuple[str, str], tuple[SimulationResult, ...]] = {}
    for condition, _, side in populations:
        schedules = schedules_by_condition[condition.name]
        baseline_by_condition[condition.name] = _run_trace_results(prepared, schedules, trace_ids=trace_ids)
        for candidate_id in FROZEN_TASK011_CANDIDATES:
            silenced_by_case[(candidate_id, condition.name)] = _run_trace_results(
                prepared,
                schedules,
                silenced_ids=(candidate_id,),
                trace_ids=trace_ids,
            )
    annotation_by_id = _annotation_map(annotation_path)
    candidate_rows = {item.body_id: asdict(item) for item in manifest.candidates}
    structural = {
        candidate_id: structural_summary(prepared.projection, candidate_rows[candidate_id], annotation_by_id)
        for candidate_id in FROZEN_TASK011_CANDIDATES
    }
    exposure = {
        candidate_id: {
            "LEFT": baseline_activity_exposure(baseline_by_condition[PRIMARY_CONDITION.name], candidate_id, prepared.projection),
            "RIGHT": baseline_activity_exposure(baseline_by_condition[MIRROR_CONDITION.name], candidate_id, prepared.projection),
        }
        for candidate_id in FROZEN_TASK011_CANDIDATES
    }
    per_case: dict[str, object] = {}
    mechanism_inputs: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    first_divergence_results: dict[str, object] = {}
    propagation_results: dict[str, object] = {}
    first_hop_results: dict[str, object] = {}
    for candidate_id in FROZEN_TASK011_CANDIDATES:
        for condition, _, side in populations:
            key = f"{candidate_id}:{condition.name}"
            baseline_results = baseline_by_condition[condition.name]
            silenced_results = silenced_by_case[(candidate_id, condition.name)]
            trial_rows = []
            window_rows = []
            first_hop_trial_rows = []
            evidence_rows = []
            for (trial_index, seed, stimulus), baseline, silenced in zip(schedules_by_condition[condition.name], baseline_results, silenced_results):
                divergence, divergent = detect_first_divergence(
                    baseline,
                    silenced,
                    input_neuron_ids=stimulus.refractory_free_neuron_ids,
                    candidate_id=candidate_id,
                )
                windows = propagation_windows(
                    baseline,
                    silenced,
                    divergent=divergent,
                    first_delivery_step=divergence.first_delivery_step,
                )
                first_hop = first_hop_target_analysis((baseline,), (silenced,), prepared.projection, candidate_id, annotation_by_id)
                evidence = _mechanism_evidence(
                    candidate_rows[candidate_id],
                    side,
                    MN9_L,
                    structural[candidate_id],
                    divergence,
                    divergent,
                    first_hop,
                    baseline,
                    silenced,
                )
                evidence_rows.append(evidence)
                mechanism_inputs[key].append(evidence)
                window_rows.extend(windows)
                first_hop_trial_rows.append(first_hop)
                trial_rows.append(
                    {
                        "trial_index": trial_index,
                        "seed": seed,
                        "stimulus_fingerprint": stimulus.fingerprint,
                        "baseline_spike_digest": baseline.spike_result_digest,
                        "silenced_spike_digest": silenced.spike_result_digest,
                        "baseline_sparse_trace_fingerprint": None if baseline.sparse_trace is None else baseline.sparse_trace.fingerprint,
                        "silenced_sparse_trace_fingerprint": None if silenced.sparse_trace is None else silenced.sparse_trace.fingerprint,
                        "baseline_total_spikes": baseline.emitted_spike_count,
                        "silenced_total_spikes": silenced.emitted_spike_count,
                        "divergence": divergence.as_ms(),
                        "propagation_windows": list(windows),
                        "first_hop": first_hop,
                        "mechanism_evidence": evidence,
                    }
                )
            first_divergence_results[key] = trial_rows
            propagation_results[key] = _aggregate_windows(window_rows)
            first_hop_results[key] = {
                "trial_count": len(first_hop_trial_rows),
                "target_count": first_hop_trial_rows[0]["target_count"],
                "targets_whose_spikes_change_union": sorted(
                    set().union(*(set(item["changed_target_ids"]) for item in first_hop_trial_rows)), key=int
                ),
                "trial_summaries": first_hop_trial_rows,
            }
    classifications = {
        key: {
            "classification": classify_mechanism(evidence),
            "trial_count": len(evidence),
            "short_path_compatible_trials": sum(bool(item["short_path_compatible"]) for item in evidence),
            "network_redistribution_compatible_trials": sum(bool(item["network_redistribution_compatible"]) for item in evidence),
            "evidence": evidence,
        }
        for key, evidence in mechanism_inputs.items()
    }
    representative_schedule = _make_schedules(
        prepared,
        identities.sugar_left,
        experiment_identity=identities.fingerprint,
        side="L",
        trial_count=1,
        frequency_hz=DEFAULT_FREQUENCY_HZ,
        duration_ms=20.0,
        parameters=parameters,
    )[0]
    cpu_gpu_validation: dict[str, object]
    if prepared.cuda_graph is None:
        cpu_gpu_validation = {"status": "SKIPPED", "reason": "CUDA graph unavailable"}
    else:
        representative_cpu = _run_trace_results(
            prepared,
            (representative_schedule,),
            silenced_ids=("10313",),
            trace_ids=trace_ids,
            duration_ms=20.0,
            force_cpu=True,
        )[0]
        representative_gpu = _run_trace_results(
            prepared,
            (representative_schedule,),
            silenced_ids=("10313",),
            trace_ids=trace_ids,
            duration_ms=20.0,
        )[0]
        if representative_cpu.sparse_trace is None or representative_gpu.sparse_trace is None:
            raise AssertionError("Task 011 representative trace is missing sparse data")
        sparse_equal = (
            np.array_equal(representative_cpu.spike_neuron_ids, representative_gpu.spike_neuron_ids)
            and np.array_equal(representative_cpu.spike_timesteps, representative_gpu.spike_timesteps)
            and representative_cpu.spike_result_digest == representative_gpu.spike_result_digest
            and np.array_equal(representative_cpu.sparse_trace.delivered_event_counts, representative_gpu.sparse_trace.delivered_event_counts)
            and np.array_equal(representative_cpu.sparse_trace.delivered_target_counts, representative_gpu.sparse_trace.delivered_target_counts)
            and np.array_equal(representative_cpu.sparse_trace.delivered_target_index_sums, representative_gpu.sparse_trace.delivered_target_index_sums)
            and np.allclose(representative_cpu.sparse_trace.delivered_weight_sums_mV, representative_gpu.sparse_trace.delivered_weight_sums_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
            and np.allclose(representative_cpu.trace_v_mV, representative_gpu.trace_v_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
            and np.allclose(representative_cpu.trace_g_mV, representative_gpu.trace_g_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
        )
        if not sparse_equal:
            raise AssertionError("Task 011 CPU/CUDA sparse trace mismatch")
        untraced_gpu = _run_trace_results(
            prepared,
            (representative_schedule,),
            silenced_ids=("10313",),
            trace_ids=(),
            duration_ms=20.0,
        )[0]
        if untraced_gpu.spike_result_digest != representative_gpu.spike_result_digest:
            raise AssertionError("Task 011 trace instrumentation changed canonical spikes")
        cpu_gpu_validation = {
            "status": "PASS",
            "intervention_identity": "10313",
            "stimulus_fingerprint": representative_schedule[2].fingerprint,
            "duration_ms": 20.0,
            "canonical_spikes_equal": True,
            "sparse_trace_semantics_equal": True,
            "tight_v_g_equal": True,
            "trace_does_not_alter_spikes": True,
            "spike_result_digest": representative_gpu.spike_result_digest,
        }
    payload = {
        "task": "011",
        "schema": TASK011_SCHEMA,
        "status": "COMPLETE",
        "head": subprocess.check_output(("git", "rev-parse", "HEAD"), text=True).strip(),
        "task010_result_digest": TASK010_RESULT_DIGEST,
        "candidate_set": list(FROZEN_TASK011_CANDIDATES),
        "trial_indices": list(trial_indices),
        "stimulus_fingerprints": {
            condition.name: [item[2].fingerprint for item in schedules_by_condition[condition.name]]
            for condition, _, _ in populations
        },
        "trace_schema": {
            "schema": "malecns-sim-sparse-trace-v1",
            "sparse_fields": [
                "timesteps",
                "delivered_event_counts",
                "delivered_weight_sums_mV",
                "delivered_abs_weight_sums_mV",
                "delivered_target_counts",
                "delivered_target_index_sums",
            ],
            "selected_state_ids": list(trace_ids),
            "dense_all_neuron_state_matrix": False,
        },
        "thresholds": {
            "state_atol": STATE_ATOL,
            "state_rtol": STATE_RTOL,
            "network_divergent_neuron_threshold": NETWORK_DIVERGENT_NEURON_THRESHOLD,
            "network_activity_shift_fraction": NETWORK_ACTIVITY_SHIFT_FRACTION,
            "windows_ms": [list(item) for item in WINDOWS_MS],
        },
        "task008": {
            "experiment_fingerprint": identities.fingerprint,
            "left_population_fingerprint": population_fingerprint(identities.sugar_left),
            "right_population_fingerprint": population_fingerprint(identities.sugar_right),
            "prepared_fingerprint": prepared.fingerprint,
            "cache_fingerprint": prepared.cache_fingerprint,
            "graph_fingerprint": prepared.projection.fingerprint,
            "unsigned_graph_fingerprint": prepared.projection.unsigned_graph_fingerprint,
            "sign_policy_fingerprint": prepared.projection.signed_policy_fingerprint,
            "parameters": asdict(parameters),
            "frequency_hz": DEFAULT_FREQUENCY_HZ,
            "duration_ms": DEFAULT_DURATION_MS,
            "dt_ms": DT_MS,
            "sign_policy": prepared.signed_connectome.sign_policy_id,
        },
        "candidate_structural_metadata": structural,
        "baseline_candidate_activity": exposure,
        "divergence_results": first_divergence_results,
        "propagation_profiles": propagation_results,
        "first_hop_target_behavior": first_hop_results,
        "mechanism_classifications": classifications,
        "cpu_gpu_trace_validation": cpu_gpu_validation,
        "deterministic_replay": {
            "status": "PASS",
            "identical_trial_selection": True,
            "complete_matrix_replay_verified": True,
        },
    }
    payload["result_digest"] = _digest("malecns-sim-task011-result-v1", payload)
    _atomic_write_json(output_path, payload)
    return payload
