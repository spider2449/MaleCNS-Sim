"""Identity-checked comparison of two completed application runs."""

from __future__ import annotations

from hashlib import sha256
from dataclasses import asdict

from .models import Comparison, RESULT_SCHEMA, canonical_bytes
from .errors import ApplicationError
from .playback import build_playback, raster_order

SCHEMA = "application-comparison-v1"
METRIC_SET = "target-spikes-and-rate-v1"
MAX_COMPARISON_PLAYBACK_BYTES = 34_000_000


class PairingError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _require(equal: bool, code: str) -> None:
    if not equal:
        raise PairingError(code)


def verify_pair(baseline, intervention) -> dict:
    """Reject every uncontrolled difference, including realized input schedules."""
    _require(baseline is not None and intervention is not None and baseline.state == intervention.state == "COMPLETED", "RESULT_NOT_COMPLETE")
    a, b = baseline.result, intervention.result
    _require(a is not None and b is not None, "RESULT_NOT_COMPLETE")
    try:
        a.verify_integrity()
        b.verify_integrity()
    except ApplicationError as exc:
        raise PairingError("INCOMPATIBLE_RESULT") from exc
    _require(baseline.spec.digest == a.executed_spec.digest and intervention.spec.digest == b.executed_spec.digest, "RESULT_SPEC_MISMATCH")
    _require(a.result_schema_version == b.result_schema_version == RESULT_SCHEMA and len(a.trials) == len(b.trials) == 1, "INCOMPATIBLE_SCHEMA")
    sa, sb = a.executed_spec, b.executed_spec
    _require(sa.dataset == sb.dataset and a.provenance.get("dataset") == b.provenance.get("dataset") == sa.to_dict()["dataset"], "DIFFERENT_DATASET")
    _require(sa.stimulus.side == sb.stimulus.side, "DIFFERENT_SIDE")
    _require(sa.stimulus == sb.stimulus, "DIFFERENT_STIMULUS")
    _require(sa.duration_ms == sb.duration_ms, "DIFFERENT_DURATION")
    _require(sa.dt_ms == sb.dt_ms, "DIFFERENT_DT")
    _require(sa.seed_policy == sb.seed_policy and a.trials[0].seed == b.trials[0].seed, "DIFFERENT_SEED")
    _require(bool(a.trials[0].schedule_fingerprint) and a.trials[0].schedule_fingerprint == b.trials[0].schedule_fingerprint and a.identity.schedule_fingerprints == b.identity.schedule_fingerprints, "DIFFERENT_SCHEDULE")
    _require(sa.model == sb.model and sa.sign_policy == sb.sign_policy, "DIFFERENT_MODEL")
    _require(sa.target == sb.target, "DIFFERENT_TARGET")
    _require(sa.backend == sb.backend and a.backend == b.backend, "DIFFERENT_BACKEND")
    _require(sa.observables == sb.observables and sa.robustness == sb.robustness and sa.trial_count == sb.trial_count, "DIFFERENT_OBSERVABLES")
    _require(sa.intervention.kind == "none" and not sa.intervention.target_ids and sb.intervention.kind == "outgoing_silence" and sb.intervention.target_ids == (sb.target.neuron_id,), "NOT_INTERVENTION_PAIR")
    _require(a.identity.package_version == b.identity.package_version, "DIFFERENT_ENGINE_VERSION")
    _require(a.identity.graph_fingerprint == b.identity.graph_fingerprint == sa.dataset.projection_fingerprint, "DIFFERENT_BASE_GRAPH")
    _require(bool(a.provenance.get("graph_fingerprint")) and a.provenance.get("graph_fingerprint") == b.provenance.get("graph_fingerprint"), "DIFFERENT_PREPARED_GRAPH")
    _require(a.identity.run_id != b.identity.run_id, "SAME_RUN")
    return {"status": "PAIRED", "controlled_difference": "outgoing_silence", "realized_schedule_equal": True,
            "dataset_equal": True, "base_graph_equal": True, "prepared_graph_equal": True,
            "graph_rule": "Outgoing scheduling is suppressed during simulation; prepared topology and weights are unchanged."}


def _identity(record) -> dict:
    result = record.result
    return {"job_id": record.job_id, "run_id": result.identity.run_id, "spec_digest": record.spec.digest,
            "result_digest": result.authoritative_digest, "result_schema_version": result.result_schema_version,
            "dataset": record.spec.dataset, "schedule_fingerprint": result.trials[0].schedule_fingerprint,
            "base_graph_fingerprint": result.identity.graph_fingerprint,
            "prepared_graph_fingerprint": result.provenance["graph_fingerprint"], "backend": result.backend}


def build_comparison(baseline, intervention) -> dict:
    pairing = verify_pair(baseline, intervention)
    sa, sb = baseline.spec, intervention.spec
    spec = {"schema_version": SCHEMA, "baseline_run_id": baseline.result.identity.run_id,
            "intervention_run_id": intervention.result.identity.run_id, "target_neuron_id": sa.target.neuron_id,
            "comparison_metric_set": METRIC_SET}
    comparison_id = sha256(canonical_bytes({"domain": "malecns-comparison-id-v1", "spec": spec})).hexdigest()
    ta, tb = baseline.result.trials[0], intervention.result.trials[0]
    payload = {"schema_version": SCHEMA, "comparison_id": comparison_id, "spec": spec,
               "baseline": _identity(baseline), "intervention": _identity(intervention), "pairing": pairing,
               "intervention_state": {"kind": sb.intervention.kind, "neuron_ids": sb.intervention.target_ids,
                                      "backend": sb.backend, "semantics": "suppress outgoing scheduling only"},
               "target": {"neuron_id": sa.target.neuron_id,
                          "spike_count": asdict(Comparison.create(ta.target_spikes, tb.target_spikes)),
                          "firing_rate_hz": asdict(Comparison.create(ta.target_rate_hz, tb.target_rate_hz))},
               "playback": {"duration_ms": sa.duration_ms, "dt_ms": sa.dt_ms,
                            "baseline_engine_spike_digest": ta.engine_digest,
                            "intervention_engine_spike_digest": tb.engine_digest,
                            "synchronized": True},
               "graph": {"baseline_prepared_fingerprint": baseline.result.provenance["graph_fingerprint"],
                         "intervention_prepared_fingerprint": intervention.result.provenance["graph_fingerprint"],
                         "intervention_effect": "outgoing event scheduling suppressed; displayed edges remain structurally present"},
               "warnings": ["Simulation comparison; no biological causal verdict."]}
    payload["authoritative_digest"] = sha256(canonical_bytes({"domain": "malecns-comparison-result-v1", "payload": payload})).hexdigest()
    return payload


def build_comparison_playback(baseline, intervention, comparison: dict, baseline_view: dict, intervention_view: dict) -> dict:
    verify_pair(baseline, intervention)
    a, _ = build_playback(baseline.result, baseline.job_id, graph_fingerprint=baseline.result.provenance["graph_fingerprint"])
    b, _ = build_playback(intervention.result, intervention.job_id, graph_fingerprint=intervention.result.provenance["graph_fingerprint"])
    _require(a["run_id"] == comparison["baseline"]["run_id"] and b["run_id"] == comparison["intervention"]["run_id"], "PLAYBACK_IDENTITY_MISMATCH")
    _require(a["duration_ms"] == b["duration_ms"] and a["dt_ms"] == b["dt_ms"], "DIFFERENT_TIME_AXIS")
    ids = set(raster_order(baseline_view["nodes"])) | set(raster_order(intervention_view["nodes"]))
    roles = {n["neuron_id"]: n["roles"] for n in baseline_view["nodes"] + intervention_view["nodes"]}
    rows = raster_order([{"neuron_id": i, "roles": roles[i]} for i in ids])
    payload = {"schema_version": "application-comparison-playback-v1", "comparison_id": comparison["comparison_id"],
            "baseline": a, "intervention": b, "raster_rows": rows,
            "union_node_ids": rows, "baseline_view": baseline_view, "intervention_view": intervention_view,
            "display_semantics": "Union of both bounded display filters; absent nodes remain explicit."}
    _require(len(canonical_bytes(payload)) <= MAX_COMPARISON_PLAYBACK_BYTES, "COMPARISON_PLAYBACK_TOO_LARGE")
    return payload
