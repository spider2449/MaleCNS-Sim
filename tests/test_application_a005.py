"""Authoritative playback timing, identity and bounded transport checks."""

from hashlib import sha256
from types import SimpleNamespace
import http.client
import json
import threading

import pytest

from malecns_sim.application.models import SpikeEvent, canonical_bytes
from malecns_sim.application.errors import ApplicationError
from malecns_sim.application.playback import MAX_PLAYBACK_BYTES, build_playback, raster_order, spike_time_ms
from malecns_sim.application.server import LocalServer, RunRecord
from malecns_sim.application.workbench import DatasetCatalog


def sample_result(spikes=(SpikeEvent(1, 1), SpikeEvent(1000, 3))):
    stimulus = SimpleNamespace(member_ids=(1, 2), start_ms=0.0, end_ms=100.0, frequency_hz=100)
    spec = SimpleNamespace(digest="spec", duration_ms=100.0, dt_ms=0.1, stimulus=stimulus, target=SimpleNamespace(neuron_id=3))
    trial = SimpleNamespace(spikes=spikes, selected_traces=(), engine_digest="engine", schedule_fingerprint="schedule")
    return SimpleNamespace(status="COMPLETED", trials=(trial,), executed_spec=spec,
                           identity=SimpleNamespace(run_id="run", spec_digest="spec"),
                           provenance={"graph_fingerprint": "graph"}, authoritative_digest="result")


def test_post_update_spike_time_grid():
    assert spike_time_ms(1, .1, 100) == .1
    assert spike_time_ms(1000, .1, 100) == 100
    for invalid in (0, -1, 1001, 1.5, True):
        with pytest.raises(ValueError):
            spike_time_ms(invalid, .1, 100)


def test_sparse_payload_identity_digest_and_no_fabricated_events():
    result = sample_result()
    payload, body = build_playback(result, "job", graph_fingerprint="graph")
    assert payload["sparse_spikes"] == [{"timestep": 1, "neuron_id": 1}, {"timestep": 1000, "neuron_id": 3}]
    assert payload["stimulus"]["realized_events"] is None
    assert payload["stimulus"]["requested_frequency_hz"] == 100
    assert payload["population_bins"] is None
    assert payload["recording_policy"].startswith("all prepared neurons")
    assert len(body) <= MAX_PLAYBACK_BYTES
    assert build_playback(result, "job", graph_fingerprint="graph")[1] == body
    without_digest = dict(payload)
    del without_digest["playback_payload_digest"]
    assert payload["playback_payload_digest"] == sha256(canonical_bytes(without_digest)).hexdigest()
    assert payload["authoritative_result_digest"] == "result"
    with pytest.raises(ValueError, match="identity"):
        build_playback(result, "job", graph_fingerprint="wrong")
    with pytest.raises(ValueError, match="timestep"):
        build_playback(sample_result((SpikeEvent(1001, 1),)), "job", graph_fingerprint="graph")


def test_deterministic_raster_order():
    nodes = [{"neuron_id": 4, "roles": ["target"]}, {"neuron_id": 3, "roles": ["context"]},
             {"neuron_id": 2, "roles": ["stimulus"]}, {"neuron_id": 1, "roles": ["stimulus"]}]
    assert raster_order(nodes) == [1, 2, 3, 4]


def test_payload_rejects_nonfinite_trace_and_size_cap(monkeypatch):
    result = sample_result()
    result.trials[0].selected_traces = (SimpleNamespace(neuron_id=1, v_mV=(float("nan"),), g_mV=(0.0,)),)
    with pytest.raises(ApplicationError, match="nonfinite"):
        build_playback(result, "job", graph_fingerprint="graph")
    result.trials[0].selected_traces = ()
    monkeypatch.setattr("malecns_sim.application.playback.MAX_PLAYBACK_BYTES", 10)
    with pytest.raises(ValueError, match="cap"):
        build_playback(result, "job", graph_fingerprint="graph")


def test_playback_endpoint_session_and_completion_gate(tmp_path):
    server = LocalServer(0, DatasetCatalog(tmp_path / "missing", engine=None), tmp_path)
    spec = SimpleNamespace(digest="spec")
    record = RunRecord("job", spec)
    server.manager.records["job"] = record
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def get(token=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/api/runs/job/playback", headers={"X-Local-Session": token} if token else {})
        response = connection.getresponse()
        output = response.status, json.loads(response.read())
        connection.close()
        return output
    try:
        assert get()[0] == 403
        assert get(server.token)[0] == 409
        record.state = "FAILED"
        assert get(server.token)[1]["error"]["message"] == "No completed playback result."
        record.state = "COMPLETED"
        record.result = sample_result()
        status, payload = get(server.token)
        assert status == 200 and payload["run_id"] == "run"
    finally:
        server.shutdown(); server.server_close(); thread.join()
