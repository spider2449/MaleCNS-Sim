"""A007B synthetic orchestration, ownership and evidence certification."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest
import numpy as np

from test_application_a007a import synthetic
from malecns_sim.application.errors import ApplicationError
from malecns_sim.application.models import SeedPolicy, canonical_bytes
from malecns_sim.application.preparation import PRESET_DIGEST, PRESET_ID, digest
from malecns_sim.application.retention import ParentResultStore
from malecns_sim.application.robustness import (
    DOMAIN, SCHEMA, VARIANTS, RobustnessSpec, RobustnessResult, RobustnessManager,
    event_schedule_evidence, decode_request,
)
from malecns_sim.application.server import RunManager, LocalServer, HISTORY_LIMIT


@pytest.fixture
def scenario_synthetic(synthetic):
    """Test-engine observables deliberately cover arithmetic, without biological meaning.

    Preparation, input generation and LIF dispatch still use actual A007A
    configuration. This adapter replaces target observations with known test
    counts; these are synthetic contract evidence, not LIF model conclusions.
    """
    spec, files, engine = synthetic
    original = engine.simulate
    def simulate(prepared, child, stimulus):
        result = original(prepared, child, stimulus)
        variant = child.variant.variant_id
        baseline = child.intervention.kind == "none"
        count = 0 if variant == "R0" else (1 if baseline else 2) if variant == "V1" else 1
        keep = result.spike_neuron_ids != child.target.neuron_id
        ids = np.concatenate((result.spike_neuron_ids[keep], np.full(count, child.target.neuron_id, dtype=np.int64)))
        steps = np.concatenate((result.spike_timesteps[keep], np.arange(1, count + 1, dtype=np.int64)))
        order = np.lexsort((ids, steps))
        ids, steps = ids[order], steps[order]
        counts = np.asarray([np.count_nonzero(ids == i) for i in prepared.projection.neuron_ids], dtype=np.int64)
        spike_digest = hashlib.sha256(b"malecns-sim-spike-result-v1" + ids.tobytes() + steps.tobytes() + counts.tobytes()).hexdigest()
        return replace(result, spike_neuron_ids=ids, spike_timesteps=steps, spike_counts=counts,
                       spike_result_digest=spike_digest, emitted_spike_count=len(ids), active_neuron_count=int(np.count_nonzero(counts)))
    engine.simulate = simulate
    return spec, files, engine


def manager_for(synthetic, tmp_path):
    spec, files, engine = synthetic
    catalog = SimpleNamespace(files=files, engine=engine)
    runs = RunManager(catalog, tmp_path)
    manager = RobustnessManager(runs, ParentResultStore("session"), "session")
    return spec, engine, manager


def run(manager, spec, variants=VARIANTS, **kwargs):
    return manager.create(RobustnessSpec(spec, variants, **kwargs), background=False)


def test_spec_serialization_identity_and_no_verdict(synthetic):
    spec, _, _ = synthetic
    value = RobustnessSpec(spec)
    restored = RobustnessSpec.from_dict(json.loads(value.canonical_bytes))
    assert restored == value
    assert restored.robustness_id == value.robustness_id
    assert value.robustness_id == digest(DOMAIN, value.to_dict())
    assert value.preset_digest == PRESET_DIGEST == "34de3189f0630c159fabe140892362ec65228487984224ef880702eb3fd8f139"
    assert value.variant_ids == ("R0", "V1", "V2", "V3", "V4", "V5", "V6", "V7")
    changed = [replace(value, variant_ids=tuple(reversed(VARIANTS))), replace(value, variant_ids=("R0",)),
               replace(value, reuse_policy="EXECUTE_ONLY"),
               replace(value, base_spec=replace(spec, seed_policy=SeedPolicy("explicit", (8,)))),
               replace(value, base_spec=replace(spec, dataset=replace(spec.dataset, manifest_digest="a" * 64))),
               replace(value, base_spec=replace(spec, backend="cuda"))]
    assert len({v.robustness_id for v in [value, *changed]}) == len(changed) + 1
    assert all("timestamp" not in key for key in value.to_dict())
    with pytest.raises(ApplicationError):
        RobustnessSpec.from_dict({**value.to_dict(), "path": "../escape"})
    with pytest.raises(ApplicationError):
        replace(value, preset_digest="0" * 64)
    with pytest.raises(ApplicationError):
        replace(value, aggregate_rule="TASK017")
    payload = {"aggregate_rule": "NO_AGGREGATE_RULE", "aggregate_result": None}
    result = RobustnessResult.create(payload)
    assert result.to_dict()["aggregate_result"] is None
    with pytest.raises(ApplicationError):
        replace(result, authoritative_digest="0" * 64).to_dict()


@pytest.mark.parametrize("variants", [("V8",), (), ("R0", "R0"), ("../path",), (True,)])
def test_invalid_variant_allowlist(synthetic, variants):
    with pytest.raises(ApplicationError):
        RobustnessSpec(synthetic[0], variants)


def test_cross_variant_event_schedule(synthetic):
    spec, _, _ = synthetic
    value = RobustnessSpec(spec)
    evidence = [event_schedule_evidence(value.child_spec(v, r)) for v in VARIANTS for r in ("baseline", "intervention")]
    assert len({v["schedule_fingerprint"] for v in evidence}) == 1
    assert evidence[0]["stimulus_fingerprints"] != evidence[10]["stimulus_fingerprints"]
    assert evidence[10]["input_amplitudes_mv"] == [50.0]
    for i in range(0, 16, 2):
        assert evidence[i] == evidence[i + 1]


def test_full_sweep_and_retention_stress(scenario_synthetic, tmp_path, monkeypatch):
    spec, engine, manager = manager_for(scenario_synthetic, tmp_path)
    calls = []
    original = engine.simulate
    def simulate(prepared, child, stimulus):
        calls.append((child.variant.variant_id, child.intervention.kind))
        assert manager.runs.active
        with pytest.raises(ApplicationError):
            manager.runs.create(spec)
        return original(prepared, child, stimulus)
    engine.simulate = simulate
    started = time.perf_counter()
    identity = run(manager, spec)
    sweep_seconds = time.perf_counter() - started
    snapshot = manager.get(identity)
    assert snapshot["result"]["overall_state"] == "COMPLETE", snapshot
    assert calls == [(v, role) for v in VARIANTS for role in ("none", "outgoing_silence")]
    assert len(calls) == 16
    assert len(manager.store.children("session", manager.sweeps[identity].parent)) == 16
    assert snapshot["result"]["aggregate_rule"] == "NO_AGGREGATE_RULE"
    assert snapshot["result"]["aggregate_result"] is None
    assert snapshot["progress"]["completed_variants"] == snapshot["progress"]["total_variants"] == 8
    assert "percentage" not in json.dumps(snapshot).lower()
    assert "eta" not in snapshot["progress"]
    assert any(e["variant_id"] == "V3" and e["role"] == "baseline" and e["phase"] == "PREPARING_NETWORK" for e in snapshot["events"])
    assert all(v["state"] == "COMPLETE" for v in snapshot["result"]["variants"])
    assert all(v[r]["provenance"] == "EXECUTED" for v in snapshot["result"]["variants"] for r in ("baseline", "intervention"))
    numeric = [v["comparison"]["target"]["spike_count"] for v in snapshot["result"]["variants"]]
    assert numeric[0]["relative_delta"] is None and numeric[0]["warning"] == "ZERO_BASELINE"
    assert numeric[1]["absolute_delta"] == 1
    assert numeric[2]["absolute_delta"] == 0
    # Actual RunManager admission/eviction, without additional scientific execution.
    monkeypatch.setattr(manager.runs, "_execute", lambda record: setattr(manager.runs, "active", False))
    class ImmediateThread:
        def __init__(self, target, args, **kwargs): self.target, self.args = target, args
        def start(self): self.target(*self.args)
    monkeypatch.setattr("malecns_sim.application.server.threading.Thread", ImmediateThread)
    for _ in range(24):
        manager.runs.create(spec)
    assert len(manager.runs.records) == HISTORY_LIMIT == 8
    metrics = {"full_sweep_seconds": sweep_seconds,
               "cross_variant_schedule_fingerprint": snapshot["result"]["schedule_fingerprint"]}
    for variant in VARIANTS:
        for kind in ("comparison", "playback", "subgraph"):
            started = time.perf_counter()
            payload = manager.evidence(identity, variant, kind)
            metrics.setdefault(kind + "_seconds", []).append(time.perf_counter() - started)
            assert payload
            if kind == "comparison":
                assert payload["pairing"]["realized_schedule_equal"]
                assert payload["baseline"]["result_digest"] == manager.variant(identity, variant)["baseline"]["result_digest"]
            elif kind == "playback":
                assert payload["baseline"]["run_id"] == manager.variant(identity, variant)["baseline"]["run_id"]
            else:
                assert payload["shared_node_ids"] == payload["union_node_ids"]
    assert len(calls) == 16
    started = time.perf_counter()
    export = manager.export(identity)
    metrics["export_seconds"] = time.perf_counter() - started
    assert canonical_bytes(export) == canonical_bytes(manager.export(identity))
    authoritative = export.pop("authoritative_digest")
    assert authoritative == digest(DOMAIN + "-export", export)
    metrics["export_bytes"] = len(canonical_bytes(export))
    metrics["retained_bytes"] = manager.store.retained_bytes("session", manager.sweeps[identity].parent)
    started = time.perf_counter()
    manager.sweeps[identity].result()
    metrics["result_construction_seconds"] = time.perf_counter() - started
    print("A007B_SYNTHETIC_MEASUREMENTS=" + json.dumps(metrics, sort_keys=True))


def test_exact_reuse_and_mixed_provenance(synthetic, tmp_path):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    calls = []
    original = engine.simulate
    engine.simulate = lambda *args: (calls.append(args[1].variant.variant_id), original(*args))[1]
    first = run(manager, spec, ("R0", "V1"))
    assert len(calls) == 4
    second = run(manager, spec, ("V1", "R0", "V2"))
    assert len(calls) == 6
    variants = manager.get(second)["result"]["variants"]
    assert [v["state"] for v in variants] == ["REUSED", "REUSED", "COMPLETE"]
    assert all(v[r]["provenance"] == "REUSED" for v in variants[:2] for r in ("baseline", "intervention"))
    assert variants[2]["baseline"]["reuse_lookup"]["rejected"]
    assert manager.evidence(second, "R0", "comparison") == manager.evidence(first, "R0", "comparison")
    with pytest.raises(ApplicationError):
        run(manager, replace(spec, seed_policy=SeedPolicy("explicit", (9,))), ("R0",))
    manager.release(first)
    changed = run(manager, replace(spec, seed_policy=SeedPolicy("explicit", (9,))), ("R0",))
    assert len(calls) == 8
    assert manager.variant(changed, "R0")["baseline"]["provenance"] == "EXECUTED"
    assert all(v["reason"] == "EXACT_SPEC_MISMATCH" for v in manager.variant(changed, "R0")["baseline"]["reuse_lookup"]["rejected"])


@pytest.mark.parametrize("boundary", ["between_children", "between_variants"])
def test_cancel_preserves_completed_evidence(synthetic, tmp_path, boundary):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    original = manager._event
    def event(sweep, phase, **payload):
        original(sweep, phase, **payload)
        if ((boundary == "between_variants" and phase == "VARIANT_COMPLETE" and sweep.current_variant == "R0")
                or (boundary == "between_children" and phase == "CHILD_RETAINED" and sweep.current_variant == "V1" and sweep.current_role == "baseline")):
            manager.cancel(sweep.spec.robustness_id)
    manager._event = event
    identity = run(manager, spec)
    snapshot = manager.get(identity)
    assert snapshot["result"]["overall_state"] == "CANCELLED"
    assert snapshot["result"]["variants"][0]["state"] == "COMPLETE"
    assert manager.evidence(identity, "R0", "comparison")
    assert manager.evidence(identity, "R0", "playback")
    assert manager.evidence(identity, "R0", "subgraph")
    assert snapshot["progress"]["completed_variants"] == 1
    if boundary == "between_children":
        v1 = snapshot["result"]["variants"][1]
        assert v1["baseline"] and not v1["intervention"]
        assert v1["state"] == "CANCELLED"
        assert manager.evidence(identity, "V1", "playback", "baseline")
        assert manager.evidence(identity, "V1", "subgraph", "baseline")
    assert not manager.runs.active


def test_stop_on_failure(synthetic, tmp_path):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    original = engine.simulate
    calls = []
    def simulate(prepared, child, stimulus):
        calls.append(child.variant.variant_id)
        if child.variant.variant_id == "V2":
            raise RuntimeError("injected synthetic failure")
        return original(prepared, child, stimulus)
    engine.simulate = simulate
    identity = run(manager, spec)
    snapshot = manager.get(identity)
    assert snapshot["result"]["overall_state"] == "PARTIAL"
    assert [v["state"] for v in snapshot["result"]["variants"]] == ["COMPLETE", "COMPLETE", "FAILED", *(["PENDING"] * 5)]
    assert calls == ["R0", "R0", "V1", "V1", "V2"]
    for kind in ("comparison", "playback", "subgraph"):
        assert manager.evidence(identity, "V1", kind)


def test_mixed_child_reuse_after_cancellation(synthetic, tmp_path):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    original = manager._event
    def event(sweep, phase, **payload):
        original(sweep, phase, **payload)
        if phase == "CHILD_RETAINED" and sweep.current_role == "baseline":
            manager.cancel(sweep.spec.robustness_id)
    manager._event = event
    first = run(manager, spec, ("R0",))
    assert manager.get(first)["result"]["overall_state"] == "CANCELLED"
    manager._event = original
    second = run(manager, spec, ("R0", "V1"))
    variant = manager.variant(second, "R0")
    assert variant["state"] == "COMPLETE"
    assert variant["baseline"]["provenance"] == "REUSED"
    assert variant["intervention"]["provenance"] == "EXECUTED"


def test_parent_byte_bound_preserves_earlier_evidence(synthetic, tmp_path, monkeypatch):
    spec, _, manager = manager_for(synthetic, tmp_path)
    import malecns_sim.application.retention as retention
    original = manager._event
    def event(sweep, phase, **payload):
        original(sweep, phase, **payload)
        if phase == "VARIANT_COMPLETE" and sweep.current_variant == "R0":
            monkeypatch.setattr(retention, "MAX_PARENT_BYTES", manager.store.retained_bytes("session", sweep.parent))
    manager._event = event
    identity = run(manager, spec)
    assert manager.get(identity)["result"]["overall_state"] == "PARTIAL"
    assert manager.evidence(identity, "R0", "playback")
    assert len(manager.store.children("session", manager.sweeps[identity].parent)) == 2


def test_identity_and_graph_mismatch_rejected(synthetic, tmp_path):
    spec, _, manager = manager_for(synthetic, tmp_path)
    identity = run(manager, spec, ("R0",))
    parent = manager.sweeps[identity].parent
    variant = manager.variant(identity, "R0")
    child = variant["baseline"]["run_id"]
    value = manager.store.evidence("session", parent, "graph:" + child)
    value["view"]["run_id"] = "0" * 64
    manager.store.retain_evidence("session", parent, "graph:" + child, value)
    with pytest.raises(ApplicationError):
        manager.evidence(identity, "R0", "playback")
    with pytest.raises(ApplicationError):
        manager.get("../result.json")
    with pytest.raises(ApplicationError):
        manager.variant(identity, "V8")
    with pytest.raises(ApplicationError):
        manager.store.get("wrong-session", parent, child)


def test_session_host_origin_and_synthetic_api(synthetic, tmp_path):
    spec, files, engine = synthetic
    catalog = SimpleNamespace(files=files, engine=engine, spec=lambda selection: spec)
    server = LocalServer(0, catalog=catalog, result_root=tmp_path)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    headers = {"X-Local-Session": server.token, "Origin": base, "Content-Type": "application/json"}
    body = {"selection": {}, "preset_id": PRESET_ID, "variant_ids": list(VARIANTS),
            "reuse_policy": "EXACT_REUSE_OR_EXECUTE", "aggregate_rule": "NO_AGGREGATE_RULE"}
    def request(path, data=None, extra=None):
        req = Request(base + path, data=canonical_bytes(data) if data is not None else None, headers=headers if extra is None else extra)
        try:
            with urlopen(req, timeout=20) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            return exc.code, json.load(exc)
    try:
        assert request("/api/robustness", extra={})[0] == 403
        assert request("/api/robustness", extra={**headers, "Host": "evil.invalid"})[0] == 403
        assert request("/api/robustness", extra={**headers, "Origin": "http://evil.invalid"})[0] == 403
        with pytest.raises(HTTPError) as denied:
            urlopen(Request(base + "/api/robustness", data=b"", headers={"X-Local-Session": server.token}), timeout=5)
        assert denied.value.code == 403
        assert request("/api/robustness", {**body, "path": "../escape"})[0] == 400
        assert request("/api/robustness", {**body, "parameters": {"tau_m": 4}})[0] == 400
        status, response = request("/api/robustness", body)
        assert status == 202
        identity = response["robustness_id"]
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            snapshot = request("/api/robustness/" + identity)[1]
            if snapshot["result"]["overall_state"] in ("COMPLETE", "FAILED", "PARTIAL"):
                break
            time.sleep(.02)
        assert snapshot["result"]["overall_state"] == "COMPLETE", snapshot
        for suffix in ("", "/events", "/export", "/variants/R0", "/variants/R0/comparison", "/variants/R0/playback", "/variants/R0/subgraph"):
            assert request("/api/robustness/" + identity + suffix)[0] == 200
            assert request("/api/robustness/" + identity + suffix, extra={})[0] == 403
        assert request("/api/robustness/" + identity + "/variants/V8")[0] == 409
        assert request("/api/robustness/" + identity + "/variants/R0/subgraph?path=escape")[0] == 409
        assert request("/api/robustness/" + identity + "/release", {})[0] == 200
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_cpu_startup_cuda_lazy():
    result = subprocess.run([sys.executable, "-c", "import sys; from malecns_sim.application.server import LocalServer; s=LocalServer(0); assert 'cupy' not in sys.modules; assert 'malecns_sim.dynamics.cuda' not in sys.modules; s.server_close()"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_schedule_gap_stops_before_execution(synthetic, tmp_path, monkeypatch):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    import malecns_sim.application.robustness as robustness
    original = robustness.event_schedule_evidence
    def evidence(child):
        value = original(child)
        if child.variant.variant_id == "V5":
            value["schedule_fingerprint"] = "0" * 64
        return value
    monkeypatch.setattr(robustness, "event_schedule_evidence", evidence)
    engine.simulate = lambda *args: pytest.fail("uncontrolled schedule must not execute")
    identity = run(manager, spec)
    snapshot = manager.get(identity)
    assert snapshot["result"]["overall_state"] == "FAILED"
    assert "A007B-SCHEDULE-CONTRACT-GAP" in str(snapshot["result"]["warnings"])


def test_all_children_reused_without_execution(synthetic, tmp_path):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    first = run(manager, spec)
    engine.simulate = lambda *args: pytest.fail("exact reuse must not execute")
    second = run(manager, spec, tuple(reversed(VARIANTS)))
    assert manager.get(second)["result"]["overall_state"] == "COMPLETE"
    assert all(v["state"] == "REUSED" for v in manager.get(second)["result"]["variants"])
    manager.release(first)
    for variant in VARIANTS:
        assert manager.evidence(second, variant, "comparison")
        assert manager.evidence(second, variant, "playback")
        assert manager.evidence(second, variant, "subgraph")


def test_cancel_before_first_child(synthetic, tmp_path):
    spec, engine, manager = manager_for(synthetic, tmp_path)
    original = manager._event
    def event(sweep, phase, **payload):
        original(sweep, phase, **payload)
        if phase == "VALIDATING":
            manager.cancel(sweep.spec.robustness_id)
    manager._event = event
    engine.simulate = lambda *args: pytest.fail("cancelled sweep must not execute")
    identity = run(manager, spec)
    assert manager.get(identity)["result"]["overall_state"] == "CANCELLED"
    assert not manager.store.children("session", manager.sweeps[identity].parent)


def test_child_capacity_and_parent_limits(synthetic, tmp_path, monkeypatch):
    spec, _, manager = manager_for(synthetic, tmp_path)
    import malecns_sim.application.retention as retention
    assert retention.MAX_PARENTS == 2
    assert retention.MAX_CHILDREN == 16
    assert retention.MAX_PARENT_BYTES == 64_000_000
    monkeypatch.setattr(retention, "MAX_CHILDREN", 1)
    identity = run(manager, spec, ("R0",))
    assert manager.get(identity)["result"]["overall_state"] == "FAILED"
    assert len(manager.store.children("session", manager.sweeps[identity].parent)) == 1
    assert manager.evidence(identity, "R0", "playback", "baseline")
    run(manager, spec, ("V1",))
    with pytest.raises(ApplicationError):
        run(manager, spec, ("V2",))


def test_strict_request_contract(synthetic):
    spec, _, _ = synthetic
    catalog = SimpleNamespace(spec=lambda selection: spec)
    raw = {"selection": {}, "preset_id": PRESET_ID, "variant_ids": ["R0"],
           "reuse_policy": "EXECUTE_ONLY", "aggregate_rule": "NO_AGGREGATE_RULE"}
    assert decode_request(catalog, raw).variant_ids == ("R0",)
    for change in ({"variant_ids": "R0"}, {"variant_ids": [[]]}, {"preset_id": "unknown"},
                   {"reuse_policy": "APPROXIMATE"}, {"aggregate_rule": "6/7"}):
        with pytest.raises(ApplicationError):
            decode_request(catalog, {**raw, **change})
    for extra in ("path", "parameters", "checkpoint", "sign_policy"):
        with pytest.raises(ApplicationError):
            decode_request(catalog, {**raw, extra: "arbitrary"})
