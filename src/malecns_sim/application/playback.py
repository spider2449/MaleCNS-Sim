"""Bounded playback projection of a completed authoritative result."""

from __future__ import annotations

from hashlib import sha256

from .models import canonical_bytes

SCHEMA = "application-playback-v1"
MAX_PLAYBACK_BYTES = 16_000_000


def spike_time_ms(timestep: int, dt_ms: float, duration_ms: float) -> float:
    """Engine step k is the post-update time k * dt, with k in 1..N."""
    if type(timestep) is not int or not 1 <= timestep <= round(duration_ms / dt_ms):
        raise ValueError("spike timestep outside completed simulation grid")
    return round(timestep * dt_ms, 10)


def raster_order(nodes: list[dict]) -> list[int]:
    def key(node):
        roles = node["roles"]
        rank = 0 if "stimulus" in roles else 3 if "target" in roles else 2 if "intervention" in roles else 1
        return rank, node["neuron_id"]
    return [node["neuron_id"] for node in sorted(nodes, key=key)]


def build_playback(result, job_id: str, *, graph_fingerprint: str) -> tuple[dict, bytes]:
    if result.status != "COMPLETED" or len(result.trials) != 1:
        raise ValueError("completed single-trial result required")
    spec = result.executed_spec
    identity = result.identity
    if identity.spec_digest != spec.digest or result.provenance["graph_fingerprint"] != graph_fingerprint:
        raise ValueError("playback result identity mismatch")
    trial = result.trials[0]
    for spike in trial.spikes:
        spike_time_ms(spike.timestep, spec.dt_ms, spec.duration_ms)
    payload = {
        "schema_version": SCHEMA,
        "job_id": job_id,
        "run_id": identity.run_id,
        "spec_digest": spec.digest,
        "graph_fingerprint": graph_fingerprint,
        "authoritative_result_digest": result.authoritative_digest,
        "engine_spike_digest": trial.engine_digest,
        "duration_ms": spec.duration_ms,
        "dt_ms": spec.dt_ms,
        "recording_policy": "all prepared neurons: sparse engine spikes; selected traces only when explicitly requested",
        "sparse_spikes": [{"timestep": s.timestep, "neuron_id": s.neuron_id} for s in trial.spikes],
        "selected_traces": [{"neuron_id": t.neuron_id, "v_mV": t.v_mV, "g_mV": t.g_mV} for t in trial.selected_traces],
        "stimulus": {"member_ids": spec.stimulus.member_ids, "configured_start_ms": spec.stimulus.start_ms,
                     "configured_end_ms": spec.stimulus.end_ms, "requested_frequency_hz": spec.stimulus.frequency_hz,
                     "realized_events": None, "schedule_fingerprint": trial.schedule_fingerprint},
        "target_neuron_id": spec.target.neuron_id,
        "population_bins": None,
        "derived_visualization": {"display_window_ms": 2.0, "binning": "client-only"},
    }
    body = canonical_bytes(payload)
    if len(body) > MAX_PLAYBACK_BYTES:
        raise ValueError("playback JSON exceeds bounded transport cap")
    payload["playback_payload_digest"] = sha256(body).hexdigest()
    encoded = canonical_bytes(payload)
    return payload, encoded
