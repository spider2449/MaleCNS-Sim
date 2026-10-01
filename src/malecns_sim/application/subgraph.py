"""Deterministic display filters over the graph used by the simulation."""

from __future__ import annotations

import hashlib
import json
import time

import numpy as np

SCHEMA = "application-subgraph-view-v1"
MODES = ("stimulus", "target", "combined")
NODE_CAPS = (80, 160)
EDGE_CAP = 1200


def _neighbors(projection, anchors: tuple[int, ...], direction: str) -> dict[int, float]:
    ids = projection.neuron_ids
    positions = np.searchsorted(ids, anchors)
    positions = positions[(positions < len(ids)) & (ids[np.minimum(positions, len(ids) - 1)] == np.asarray(anchors, dtype=np.int64))]
    edge_positions = projection.source_positions if direction == "outgoing" else projection.target_positions
    mask = np.isin(edge_positions, positions)
    opposite = projection.target_positions if direction == "outgoing" else projection.source_positions
    selected_ids = ids[opposite[mask]]
    selected_weights = np.abs(projection.effective_weights_mV[mask])
    scores: dict[int, float] = {}
    for neuron, weight in zip(selected_ids, selected_weights):
        key = int(neuron)
        scores[key] = max(scores.get(key, 0.0), float(weight))
    return scores


def build_subgraph(projection, spec, mode: str, cap: int, *, run_id: str | None = None, result=None) -> dict:
    """Return bounded, schematic topology with no inferred biological route."""
    if mode not in MODES or cap not in NODE_CAPS:
        raise ValueError("unsupported display filter")
    started = time.perf_counter()
    stimulus = tuple(int(i) for i in spec.stimulus.member_ids)
    target = int(spec.target.neuron_id)
    anchors = set(stimulus if mode != "target" else ()) | ({target} if mode != "stimulus" else set())
    outgoing = _neighbors(projection, stimulus, "outgoing") if mode != "target" else {}
    incoming = _neighbors(projection, (target,), "incoming") if mode != "stimulus" else {}
    scores = {key: max(outgoing.get(key, 0.0), incoming.get(key, 0.0)) for key in outgoing.keys() | incoming.keys()}
    candidates = anchors | scores.keys()
    selected = set(anchors)
    for neuron in sorted(candidates - anchors, key=lambda key: (-scores.get(key, 0.0), key))[:max(0, cap - len(anchors))]:
        selected.add(neuron)
    # Both allowed caps exceed the frozen stimulus anchor count.
    ids = projection.neuron_ids
    selected_positions = np.searchsorted(ids, np.asarray(sorted(selected), dtype=np.int64))
    mask = np.isin(projection.source_positions, selected_positions) & np.isin(projection.target_positions, selected_positions)
    indices = np.flatnonzero(mask)
    ranked = sorted(indices, key=lambda i: (-abs(float(projection.effective_weights_mV[i])), int(ids[projection.source_positions[i]]), int(ids[projection.target_positions[i]])))
    shown = ranked[:EDGE_CAP]
    trial = result.trials[0] if result is not None and result.status == "COMPLETED" and result.trials else None
    recorded = {}
    if trial is not None:
        for spike in trial.spikes:
            recorded[spike.neuron_id] = recorded.get(spike.neuron_id, 0) + 1
        recorded[target] = trial.target_spikes
    nodes = []
    for neuron in sorted(selected):
        roles = []
        if neuron in stimulus:
            roles.append("stimulus")
        if neuron == target:
            roles.append("target")
        if neuron in spec.intervention.target_ids:
            roles.append("intervention")
        if not roles:
            roles.append("context")
        if neuron in outgoing and neuron in incoming:
            roles.append("shared displayed context")
        activity = {"available": neuron in recorded, "spike_count": recorded.get(neuron) if neuron in recorded else None}
        if neuron == target and trial is not None:
            activity["firing_rate_hz"] = trial.target_rate_hz
        nodes.append({"neuron_id": neuron, "display_label": str(neuron), "roles": roles, "activity": activity})
    edges = []
    for i in shown:
        effective = float(projection.effective_weights_mV[i])
        edges.append({"source": int(ids[projection.source_positions[i]]), "target": int(ids[projection.target_positions[i]]),
                      "anatomical_weight": int(round(abs(effective) / projection.synaptic_weight_mV)),
                      "sign": "positive" if effective > 0 else "negative" if effective < 0 else "zero"})
    definition = {"mode": mode, "node_cap": cap, "edge_cap": EDGE_CAP,
                  "rule": "anchors plus strongest direct outgoing stimulus and/or incoming target connections; descending absolute effective weight, then neuron ID; induced edges ranked by absolute effective weight, source ID, target ID"}
    filter_identity = hashlib.sha256(json.dumps(definition, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    view = {"schema_version": SCHEMA, "dataset_identity": spec.dataset.manifest_digest,
            "graph_fingerprint": projection.fingerprint, "run_id": run_id, "spec_digest": spec.digest,
            "filter_definition": definition, "filter_identity": filter_identity,
            "truncated": len(candidates) > len(selected) or len(indices) > len(shown),
            "total_candidate_nodes": len(candidates), "total_candidate_edges": len(indices),
            "rendered_node_count": len(nodes), "rendered_edge_count": len(edges), "nodes": nodes, "edges": edges,
            "schematic_warning": "Schematic connectivity view — not anatomical position",
            "graph_source": "prepared simulation projection",
            "extraction_seconds": round(time.perf_counter() - started, 6)}
    view["serialized_bytes"] = len(json.dumps(view, separators=(",", ":")).encode())
    return view
