"""A007A bounded NON_SCIENTIFIC_SYNTHETIC integration and identity regressions."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from malecns_sim.analysis.task008 import derive_task008_populations, prepare_network
from malecns_sim.application.models import ExperimentSpec, ExperimentResult, RunIdentity, InterventionSpec, LIFParameters
from malecns_sim.application.preparation import (
    PRESET_ID, PRESET_DIGEST, OVERRIDES, REFERENCE_CONFIG, PreparationConfig,
    VariantExperimentSpec, decode_variant_request, resolve_variant,
)
from malecns_sim.application.errors import ApplicationError
from malecns_sim.application.service import DatasetFiles, ProductionEngine, run_experiment, _schedule
from malecns_sim.application.comparisons import verify_pair, PairingError, build_comparison
from malecns_sim.application.retention import ParentResultStore, MAX_PARENTS, MAX_PARENT_BYTES
from malecns_sim.application.server import RunManager, HISTORY_LIMIT
from test_application_a002 import _spec, _candidate
from test_application_a006 import record


@pytest.fixture
def synthetic(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather
    from malecns_sim.analysis.task007 import MALE_CNS_ANNOTATION_COLUMNS, NT_COLUMNS

    annotation = tmp_path / "annotation.feather"
    neurotransmitter = tmp_path / "nt.feather"
    weights = tmp_path / "weights.feather"
    ids = [100, 200, 10331, 16949]
    rows = []
    for body, side, flywire in ((100, "L", "LB3"), (200, "R", "LB3"), (10331, "L", "CB0701"), (16949, "R", "CB0701")):
        row = {key: None for key in MALE_CNS_ANNOTATION_COLUMNS}
        row.update(bodyId=body, flywireType=flywire, type="LB3a" if flywire == "LB3" else "MN9", rootSide=side, somaSide=side, superclass="cb_sensory" if flywire == "LB3" else "motor", **{"class": "gustatory" if flywire == "LB3" else "motor"}, entryNerve="MxLbN")
        rows.append(row)
    feather.write_feather(pa.Table.from_pylist(rows), annotation)
    nt_rows = [{**{key: None for key in NT_COLUMNS}, "body": body, "consensus_nt": "glutamate" if body == 200 else "acetylcholine"} for body in ids]
    feather.write_feather(pa.Table.from_pylist(nt_rows), neurotransmitter)
    feather.write_feather(pa.table({"body_pre": [100, 200], "body_post": [16949, 10331], "weight": [5, 5]}), weights)
    prepared = prepare_network(annotation, neurotransmitter, weights)
    population = derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False).sugar_left
    spec = _spec(population=population, graph=prepared.projection.unsigned_graph_fingerprint, sign=prepared.projection.sign_policy_id, resolution=prepared.projection.resolution_policy_id)
    spec = replace(spec, dataset=replace(spec.dataset, annotation_sha256=hashlib.sha256(annotation.read_bytes()).hexdigest(), neurotransmitter_sha256=hashlib.sha256(neurotransmitter.read_bytes()).hexdigest(), weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest()))
    files = DatasetFiles(annotation, neurotransmitter, weights, spec.dataset.manifest_digest, spec.dataset.mapping_fingerprint)

    class SyntheticAdapter(ProductionEngine):
        def identities(self, files):
            return derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False)

        def simulate(self, prepared, spec, stimulus):
            self.executed_input_amplitude = stimulus.weight_mV
            self.executed_parameters = spec.model.parameters
            return super().simulate(prepared, spec, stimulus)
    return spec, files, SyntheticAdapter()


def envelope(spec, variant):
    return decode_variant_request(spec, {"preset_id": PRESET_ID, "variant_id": variant})


@pytest.mark.parametrize("variant,overrides", OVERRIDES)
def test_exact_variant_contract(variant, overrides):
    value = resolve_variant(PRESET_ID, variant)
    assert value.overrides == overrides
    assert value == resolve_variant(PRESET_ID, variant)
    assert value.canonical_bytes == resolve_variant(PRESET_ID, variant).canonical_bytes
    assert value.digest == resolve_variant(PRESET_ID, variant).digest
    assert len(value.digest) == 64
    config = value.resolved_config
    expected = dict(overrides)
    sign = expected.pop("sign_policy_id", "Shiu2024SignPolicy")
    assert config.parameters == replace(LIFParameters(), **expected)
    assert config.sign_policy_id == sign
    with pytest.raises(ApplicationError):
        replace(value, overrides=overrides + (("v_reset_mV", -50.0),))
    with pytest.raises(ApplicationError):
        replace(value, resolved_config=replace(config, parameters=replace(config.parameters, v_reset_mV=-50.0)))


def test_reference_and_weight_coupling():
    assert REFERENCE_CONFIG.parameters == LIFParameters()
    assert REFERENCE_CONFIG.direct_input_amplitude_mv == 68.75
    v5 = resolve_variant(PRESET_ID, "V5").resolved_config
    assert v5.parameters.synaptic_weight_per_anatomical_synapse_mV == .200
    assert v5.direct_input_amplitude_mv == 50.0
    assert v5.direct_input_amplitude_mv != REFERENCE_CONFIG.direct_input_amplitude_mv
    assert v5.direct_input_rule == "derived-anatomical-weight-times-factor-v1"
    assert len({resolve_variant(PRESET_ID, v).digest for v, _ in OVERRIDES}) == 8
    assert len({resolve_variant(PRESET_ID, v).resolved_config.digest for v, _ in OVERRIDES}) == 8


@pytest.mark.parametrize("sign", ["Shiu2024SignPolicy", "ConservativeSignPolicy"])
def test_allowlisted_sign_policy(sign):
    assert PreparationConfig(sign_policy_id=sign).sign_policy.policy_id == sign


@pytest.mark.parametrize("change", [
    {"sign_policy_id": "os.system"}, {"direct_input_weight_factor": float("nan")},
    {"direct_input_weight_factor": float("inf")}, {"direct_input_weight_factor": True},
    {"resolution_policy_id": "unknown"}, {"parameters": {}},
])
def test_invalid_preparation(change):
    with pytest.raises(ApplicationError):
        PreparationConfig(**change)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True])
def test_nonfinite_parameters(value):
    with pytest.raises((TypeError, ValueError)):
        PreparationConfig(parameters=LIFParameters(tau_membrane_ms=value))


@pytest.mark.parametrize("raw", [
    {"preset_id": PRESET_ID, "variant_id": "V8"},
    {"preset_id": PRESET_ID, "variant_id": []},
    {"preset_id": "unknown", "variant_id": "R0"},
    {"preset_id": PRESET_ID, "variant_id": "V5", "overrides": {"weight": .2}},
    {"preset_id": PRESET_ID, "variant_id": "V7", "sign_policy": "arbitrary"},
])
def test_reject_unbounded_client_input(raw):
    with pytest.raises(ApplicationError):
        decode_variant_request(_spec(), raw)


@pytest.mark.parametrize("variant", [v for v, _ in OVERRIDES])
def test_true_preparation_and_execution(synthetic, variant):
    spec, files, engine = synthetic
    source = envelope(spec, variant)
    prepared = []
    result = run_experiment(source, files, engine=engine, prepared_sink=prepared.append)
    assert result.status == "COMPLETED"
    result.verify_integrity()
    restored = ExperimentResult.from_dict(json.loads(json.dumps(result.to_dict())))
    assert restored.authoritative_digest == result.authoritative_digest
    assert result.provenance["variant_digest"] == source.variant.digest
    assert result.provenance["preparation_config_digest"] == source.variant.resolved_config.digest
    assert result.provenance["preparation_variant"] == source.variant.to_dict()
    assert prepared[0].projection.synaptic_weight_mV == source.model.parameters.synaptic_weight_per_anatomical_synapse_mV
    assert prepared[0].projection.sign_policy_id == source.sign_policy.policy_id
    assert engine.executed_input_amplitude == source.variant.resolved_config.direct_input_amplitude_mv
    assert engine.executed_parameters == source.variant.resolved_config.parameters
    assert result.trials[0].engine_digest
    assert result.identity.run_id != RunIdentity.create(spec, result.identity.schedule_fingerprints, spec.dataset.projection_fingerprint).run_id
    if variant == "V5":
        assert _schedule(source, 7).weight_mV == 50.0
        assert _schedule(spec, 7).weight_mV == 68.75
        assert list(prepared[0].projection.effective_weights_mV) == [1.0, -1.0]
    if variant == "V7":
        reference = engine.prepare(files, spec.backend)
        assert len(reference.projection.source_positions) == 2
        assert len(prepared[0].projection.source_positions) == 1
        assert prepared[0].projection.fingerprint != reference.projection.fingerprint
        assert result.provenance["graph_fingerprint"] == prepared[0].projection.fingerprint
    changed = json.loads(json.dumps(result.to_dict()))
    changed["executed_spec"]["variant"]["resolved_config"]["parameters"]["v_threshold_mV"] = -40
    with pytest.raises(ApplicationError):
        ExperimentResult.from_dict(changed)


def test_ordinary_reference_bytes_and_known_certified_identities():
    fixture = Path(__file__).parent / "fixtures"
    raw = (fixture / "application-a003r-reference-spec.json").read_bytes().rstrip(b"\r\n")
    spec = ExperimentSpec.from_dict(json.loads(raw))
    assert spec.canonical_bytes == raw
    assert spec.digest == "5d5e5d95d38b457d0fcc20d7351d3d79e95fc9321b5fb252697763fbdedb9d38"
    schedule = ("3e3ddb63ad75a568227a857b2e0ae432bfc12b894c43e5e63ccf9285a6b93b32",)
    assert RunIdentity.create(spec, schedule, spec.dataset.projection_fingerprint, "0.3.0").run_id == "4827ec1ebd407566b4254d80f59eaceecc01f9364d903f54a4843683a88920ce"
    intervention = ExperimentSpec.from_dict(json.loads((fixture / "application-a006-intervention-spec.json").read_bytes()))
    assert intervention.digest == "6bbc6aa1433fd363d8fd8edd3de3401a92a4435be39fe4ac3e97a9d3590a9787"
    assert verify_pair(record(spec, schedule=schedule[0]), record(intervention, schedule=schedule[0]))["status"] == "PAIRED"


@pytest.mark.parametrize("variant", [v for v, _ in OVERRIDES])
def test_same_variant_pairing(synthetic, variant):
    spec, files, engine = synthetic
    baseline = envelope(spec, variant)
    intervention = envelope(replace(spec, intervention=InterventionSpec("outgoing_silence", (16949,))), variant)
    a, b = [SimpleNamespace(spec=s, state="COMPLETED", result=run_experiment(s, files, engine=engine), job_id=str(i)) for i, s in enumerate((baseline, intervention))]
    assert verify_pair(a, b)["status"] == "PAIRED"
    assert build_comparison(a, b)["pairing"]["status"] == "PAIRED"


def test_cross_variant_rejected(synthetic):
    spec, files, engine = synthetic
    a = envelope(spec, "V1")
    b = envelope(replace(spec, intervention=InterventionSpec("outgoing_silence", (16949,))), "V2")
    records = [SimpleNamespace(spec=s, state="COMPLETED", result=run_experiment(s, files, engine=engine)) for s in (a,b)]
    with pytest.raises(PairingError) as error:
        verify_pair(*records)
    assert error.value.code == "DIFFERENT_PREPARATION_VARIANT"


def test_sixteen_children_survive_recent_eviction(synthetic, tmp_path, monkeypatch):
    spec, files, engine = synthetic
    store = ParentResultStore("session-a")
    parent = store.create("session-a")
    expected = {}
    for variant, _ in OVERRIDES:
        for intervention in (False, True):
            base = replace(spec, intervention=InterventionSpec("outgoing_silence", (16949,))) if intervention else spec
            result = run_experiment(envelope(base, variant), files, engine=engine)
            child = store.retain("session-a", parent, result)
            expected[child] = result.authoritative_digest
    assert len(expected) == 16
    manager = RunManager(SimpleNamespace(), tmp_path)
    def execute(record):
        manager.active = False
    monkeypatch.setattr(manager, "_execute", execute)
    class ImmediateThread:
        def __init__(self, target, args, **kwargs): self.target, self.args = target, args
        def start(self): self.target(*self.args)
    monkeypatch.setattr("malecns_sim.application.server.threading.Thread", ImmediateThread)
    for _ in range(24):
        manager.create(spec)
    assert HISTORY_LIMIT == len(manager.records) == 8
    assert store.children("session-a", parent) == tuple(expected)
    for child, digest_value in expected.items():
        assert store.get("session-a", parent, child).authoritative_digest == digest_value
    second = store.create("session-a")
    for token, owner, child in (("session-b", parent, next(iter(expected))), ("session-a", second, next(iter(expected))), ("session-a", "../escape", "../../result.json")):
        with pytest.raises(ApplicationError): store.get(token, owner, child)
    with pytest.raises(ApplicationError): store.create("session-a")
    store.release("session-a", parent)
    with pytest.raises(ApplicationError): store.get("session-a", parent, next(iter(expected)))
    store.close()
    with pytest.raises(ApplicationError): store.children("session-a", second)


def test_parent_byte_limit_and_snapshot(synthetic, monkeypatch):
    spec, files, engine = synthetic
    result = run_experiment(envelope(spec, "R0"), files, engine=engine)
    store = ParentResultStore("session")
    parent = store.create("session")
    monkeypatch.setattr("malecns_sim.application.retention.MAX_PARENT_BYTES", 1)
    with pytest.raises(ApplicationError): store.retain("session", parent, result)
    monkeypatch.setattr("malecns_sim.application.retention.MAX_PARENT_BYTES", MAX_PARENT_BYTES)
    child = store.retain("session", parent, result)
    store.get("session", parent, child).provenance["variant_digest"] = "tampered"
    assert store.get("session", parent, child).provenance["variant_digest"] == result.provenance["variant_digest"]


def test_no_historical_runner_dependency():
    import ast
    application = Path(__file__).parents[1] / "src/malecns_sim/application"
    for path in application.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "task017" not in (node.module or "")
            elif isinstance(node, ast.Import):
                assert all("task017" not in alias.name for alias in node.names)


def test_cuda_receives_equivalent_configuration(synthetic, monkeypatch):
    import sys
    spec, files, engine = synthetic
    calls = []
    def simulate_cuda(projection, **kwargs):
        calls.append((projection, kwargs))
        return "synthetic-dispatch-only"
    monkeypatch.setitem(sys.modules, "malecns_sim.dynamics.cuda", SimpleNamespace(simulate_cuda=simulate_cuda))
    source = envelope(replace(spec, backend="cuda"), "V5")
    prepared = engine.prepare(files, "cpu_reference", source.variant.resolved_config)
    prepared = SimpleNamespace(projection=prepared.projection, cuda_graph="synthetic-uploaded-graph")
    assert engine.simulate(prepared, source, _schedule(source, 7)) == "synthetic-dispatch-only"
    assert calls[0][1]["parameters"] == source.variant.resolved_config.parameters
    assert calls[0][1]["stimulus"].weight_mV == 50.0
    assert calls[0][1]["cuda_graph"] == "synthetic-uploaded-graph"


def test_variant_cuda_unavailable_is_explicit(synthetic):
    spec, files, engine = synthetic
    engine.cuda_available = lambda: False
    with pytest.raises(ApplicationError) as error:
        run_experiment(envelope(replace(spec, backend="cuda"), "V7"), files, engine=engine)
    assert error.value.code.value == "GPU_UNAVAILABLE"
    error.value.partial_result.verify_integrity()


def test_closed_session_cannot_admit_parent():
    store = ParentResultStore("session")
    store.close()
    with pytest.raises(ApplicationError):
        store.create("session")


def test_frozen_preset_digest():
    assert PRESET_DIGEST == "34de3189f0630c159fabe140892362ec65228487984224ef880702eb3fd8f139"
    assert resolve_variant(PRESET_ID, "V5").digest == "efc8220ba209e7a6e92d129ae1e3f82678befcb376462b2c450747a2cb86cc61"


def test_parent_child_capacity(synthetic):
    spec, files, engine = synthetic
    store = ParentResultStore("session")
    parent = store.create("session")
    from malecns_sim.application.models import SeedPolicy
    for seed in range(16):
        base = replace(spec, seed_policy=SeedPolicy("explicit", (seed,)))
        store.retain("session", parent, run_experiment(envelope(base, "R0"), files, engine=engine))
    base = replace(spec, seed_policy=SeedPolicy("explicit", (16,)))
    with pytest.raises(ApplicationError):
        store.retain("session", parent, run_experiment(envelope(base, "R0"), files, engine=engine))
    assert len(store.children("session", parent)) == 16


def test_derived_input_must_remain_finite():
    with pytest.raises(ApplicationError):
        PreparationConfig(parameters=LIFParameters(synaptic_weight_per_anatomical_synapse_mV=1e308))
