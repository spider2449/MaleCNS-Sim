"""Local HTTP boundary and bounded manager checks without a full connectome run."""

from __future__ import annotations

import http.client
import json
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from malecns_sim.application.errors import ApplicationError, ErrorCode
from malecns_sim.application.models import ExperimentResult, RunIdentity
from malecns_sim.application.serialization import write_result
from malecns_sim.application.server import HISTORY_LIMIT, LocalServer, RunManager, RunRecord
from malecns_sim.application.workbench import DatasetCatalog


def _request(port: int, method: str, path: str, body=None, *, host=None, token=None, origin=None):
    connection = http.client.HTTPConnection("127.0.0.1", port)
    headers = {"Host": host or f"127.0.0.1:{port}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(body))
    if token:
        headers["X-Local-Session"] = token
    if origin:
        headers["Origin"] = origin
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    payload = response.read()
    connection.close()
    return response.status, json.loads(payload) if response.getheader("Content-Type", "").startswith("application/json") else payload


def test_loopback_catalog_security_and_ui(tmp_path: Path):
    catalog = DatasetCatalog(tmp_path / "missing", engine=None)
    server = LocalServer(0, catalog, tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_port
        assert server.server_address[0] == "127.0.0.1"
        assert _request(port, "GET", "/api/status")[0] == 200
        assert _request(port, "GET", "/api/datasets")[1]["datasets"][0]["status"] == "DATASET_UNAVAILABLE"
        assert _request(port, "GET", "/")[0] == 200
        assert _request(port, "GET", "/app.js")[0] == 200
        assert _request(port, "GET", "/style.css")[0] == 200
        assert _request(port, "GET", "/../server.py")[0] == 404
        assert _request(port, "GET", "/api/status", host="evil.example")[0] == 403
        assert _request(port, "GET", "/", host="evil.example")[0] == 403
        body = json.dumps({"unexpected": "path"})
        assert _request(port, "POST", "/api/runs")[0] == 403
        assert _request(port, "POST", "/api/experiments/validate", token="wrong", origin=f"http://127.0.0.1:{port}")[0] == 403
        assert _request(port, "POST", f"/api/experiments/validate?token={server.token}", origin=f"http://127.0.0.1:{port}")[0] == 403
        assert _request(port, "POST", "/api/experiments/validate", token=server.token, origin="http://evil.example")[0] == 403
        assert _request(port, "GET", "/api/runs")[0] == 403
        assert _request(port, "GET", "/api/runs", token="wrong")[0] == 403
        assert _request(port, "GET", "/api/runs", token=server.token)[0] == 200
        assert _request(port, "POST", "/api/runs", body, token=server.token, origin=f"http://127.0.0.1:{port}")[0] == 400
        assert _request(port, "GET", "/api/experiment/options")[0] == 503
        assert _request(port, "GET", "/api/runs/nope/result", token=server.token)[0] == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_previous_process_token_is_rejected(tmp_path: Path):
    first = LocalServer(0, DatasetCatalog(tmp_path / "missing", engine=None), tmp_path)
    old_token = first.token
    first.server_close()
    second = LocalServer(0, DatasetCatalog(tmp_path / "missing", engine=None), tmp_path)
    thread = threading.Thread(target=second.serve_forever, daemon=True)
    thread.start()
    try:
        assert second.token != old_token
        assert _request(second.server_port, "GET", "/")[0] == 200
        assert _request(second.server_port, "GET", "/api/runs", token=old_token)[0] == 403
        assert _request(second.server_port, "GET", "/api/runs", token=second.token)[0] == 200
    finally:
        second.shutdown()
        second.server_close()
        thread.join()


def test_history_limit_is_fixed(tmp_path: Path):
    manager = RunManager(DatasetCatalog(tmp_path, engine=None), tmp_path)
    assert HISTORY_LIMIT == 8
    assert manager.active is False


def test_selection_uses_stable_a002_digest_and_rejects_extra_fields():
    catalog = DatasetCatalog.local()
    if not catalog.available():
        pytest.skip("registered scientific dataset absent")
    selected = {"dataset_key": "male-cns-v1", "side": "L", "frequency_hz": 100, "mode": "none", "backend": "cpu_reference", "seed": 1555062870}
    first = catalog.spec(selected)
    assert first.digest == catalog.spec(selected).digest
    assert first.canonical_bytes == catalog.spec(selected).canonical_bytes
    assert first.target.neuron_id == 16949
    assert len(first.stimulus.member_ids) == 42
    right = catalog.spec({**selected, "side": "R"})
    assert right.target.neuron_id == 10331
    assert len(right.stimulus.member_ids) == 43
    with pytest.raises(ApplicationError) as extra:
        catalog.spec({**selected, "path": "C:/unexpected"})
    assert extra.value.code == ErrorCode.INVALID_SPEC
    with pytest.raises(ApplicationError) as mode:
        catalog.spec({**selected, "mode": "robustness"})
    assert mode.value.code == ErrorCode.UNSUPPORTED_OPERATION


def test_validate_and_run_requests_share_exact_spec_identity(tmp_path: Path):
    catalog = DatasetCatalog.local()
    if not catalog.available():
        pytest.skip("registered scientific dataset absent")
    selected = {"dataset_key": "male-cns-v1", "side": "L", "frequency_hz": 100, "mode": "none", "backend": "cpu_reference", "seed": 1555062870}
    observed = []
    server = LocalServer(0, catalog, tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps(selected)
        origin = f"http://127.0.0.1:{server.server_port}"
        with patch("malecns_sim.application.server.run_experiment", side_effect=lambda spec, *args, **kwargs: observed.append(spec) or (_ for _ in ()).throw(RuntimeError("synthetic stop"))):
            status, validated = _request(server.server_port, "POST", "/api/experiments/validate", body, token=server.token, origin=origin)
            assert status == 200
            status, created = _request(server.server_port, "POST", "/api/runs", body, token=server.token, origin=origin)
            assert status == 202
            for _ in range(100):
                if observed:
                    break
                time.sleep(0.01)
        assert len(observed) == 1
        validated_spec = catalog.spec(selected)
        assert validated_spec.to_dict() == validated["spec"]
        assert validated_spec.canonical_bytes == observed[0].canonical_bytes
        assert validated["spec_digest"] == created["spec_digest"] == observed[0].digest
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_manager_retains_safe_failure(tmp_path: Path):
    manager = RunManager(DatasetCatalog(tmp_path, engine=None), tmp_path)
    selected = object()
    with patch("malecns_sim.application.server.run_experiment", side_effect=RuntimeError("private detail")):
        record = manager.create(selected)
        for _ in range(100):
            if not manager.active:
                break
            time.sleep(0.01)
    assert record.state == "FAILED"
    assert record.error["code"] == "SIMULATION_FAILED"
    assert "private detail" not in record.error["message"]
    assert manager.get(record.job_id) is record


def test_manager_evicts_oldest_completed_job(tmp_path: Path):
    manager = RunManager(DatasetCatalog(tmp_path, engine=None), tmp_path)
    with patch("malecns_sim.application.server.run_experiment", side_effect=RuntimeError("synthetic failure")):
        jobs = []
        for _ in range(HISTORY_LIMIT + 1):
            record = manager.create(object())
            jobs.append(record.job_id)
            for _ in range(100):
                if not manager.active:
                    break
                time.sleep(0.01)
            assert not manager.active
    assert len(manager.records) == HISTORY_LIMIT
    assert manager.get(jobs[0]) is None
    assert manager.get(jobs[-1]) is not None


def test_result_events_and_backend_export_routes(tmp_path: Path):
    catalog = DatasetCatalog.local()
    if not catalog.available():
        pytest.skip("registered scientific dataset absent")
    selected = {"dataset_key": "male-cns-v1", "side": "L", "frequency_hz": 100, "mode": "none", "backend": "cpu_reference", "seed": 7}
    spec = catalog.spec(selected)
    identity = RunIdentity.create(spec, ("a" * 64,), spec.dataset.projection_fingerprint)
    result = ExperimentResult.create(identity=identity, spec=spec, invocation_id="synthetic-invocation",
                                     started_at="synthetic", finished_at="synthetic", provenance={"synthetic": True},
                                     stimulus_summary={}, intervention_summary={}, trials=())
    server = LocalServer(0, catalog, tmp_path)
    path = tmp_path / "synthetic.json"
    digest = write_result(result, path)
    record = RunRecord("synthetic", spec, "COMPLETED", [{"event_type": "RunCompleted", "phase": "COMPLETED"}], result, None, path, digest)
    server.manager.records[record.job_id] = record
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_port
        status, events = _request(port, "GET", "/api/runs/synthetic/events", token=server.token)
        assert status == 200 and events["events"][0]["event_type"] == "RunCompleted"
        status, response = _request(port, "GET", "/api/runs/synthetic/result", token=server.token)
        assert status == 200 and response["manifest_digest"] == result.manifest_digest
        status, exported = _request(port, "GET", "/api/runs/synthetic/export", token=server.token)
        assert status == 200 and exported == json.loads(path.read_bytes())
        assert _request(port, "GET", "/api/runs/synthetic", token=server.token)[1]["run_id"] == identity.run_id
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
