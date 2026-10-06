"""A002 contracts and NON_SCIENTIFIC_SYNTHETIC_ENGINE_INTEGRATION_TEST."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from malecns_sim.analysis.task008 import derive_task008_populations, prepare_network
from malecns_sim.application import ApplicationError, DatasetFiles, ErrorCode, EventJournal, EventType, ExperimentResult, ExperimentSpec, Lifecycle, State, read_result, run_experiment, validate_experiment, write_result
from malecns_sim.application.models import (
    Comparison, DatasetIdentity, InterventionSpec, ModelSpec, ObservablesSpec,
    RobustnessRequest, RobustnessVariant, SeedPolicy, SignPolicySpec,
    SpikeEvent, StimulusSpec, TargetSpec, TrialResult, RunIdentity,
)
from malecns_sim.application.service import ProductionEngine, _git_provenance, _trial
from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.dynamics.lif import _canonicalize_spike_events
from malecns_sim.homology import MaleCNSCandidate, population_fingerprint


def _candidate(body_id, side):
    return MaleCNSCandidate(body_id=str(body_id), type="LB3a", flywire_type="LB3", side=side, root_side=side, soma_side=None, superclass="cb_sensory", cell_class="gustatory", entry_nerve="MxLbN", consensus_nt="acetylcholine", resolved_nt="acetylcholine", task004_sign=1)


def _spec(*, population=None, graph="a" * 64, sign="Shiu2024SignPolicy", resolution="MaleCNSV1ConsensusThenPredictedThenCelltype"):
    population = population or derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False).sugar_left
    params = LIFParameters()
    return ExperimentSpec(
        "application-experiment-v1", "00000000-0000-0000-0000-000000000002",
        DatasetIdentity("MaleCNS-v1.0", "b" * 64, "c" * 64, "d" * 64, "e" * 64, graph, "f" * 64),
        "cpu_reference", SeedPolicy("explicit", (7,)), 5.0, 0.1, 1,
        StimulusSpec(population_fingerprint(population), tuple(int(i) for i in population.candidate_body_ids), "L", 100.0, 0.0, 5.0, 250.0, "reference-poisson-direct-voltage-v1"),
        TargetSpec(16949, "contralateral"), InterventionSpec("none", ()),
        ModelSpec(params, params.fingerprint), SignPolicySpec(sign, resolution),
        ObservablesSpec(True, (16949,), False, None), RobustnessRequest("none", (), None),
    )


def test_spec_validation_and_canonical_identity():
    spec = _spec()
    restored = ExperimentSpec.from_dict(json.loads(spec.canonical_bytes))
    assert restored.canonical_bytes == spec.canonical_bytes
    assert restored.digest == spec.digest
    assert replace(spec, seed_policy=SeedPolicy("explicit", (8,))).digest != spec.digest
    assert replace(spec, stimulus=replace(spec.stimulus, frequency_hz=150.0)).digest != spec.digest
    assert RunIdentity.create(spec, ("a" * 64,), "b" * 64) == RunIdentity.create(restored, ("a" * 64,), "b" * 64)
    with pytest.raises(ApplicationError):
        ExperimentSpec.from_dict({**spec.to_dict(), "unexpected": 1})


def _grid_trial(spike_steps, spike_ids=None):
    spec = _spec()
    projection = SimpleNamespace(neuron_ids=np.array([100, 16949]), unsigned_graph_fingerprint=spec.dataset.projection_fingerprint)
    prepared = SimpleNamespace(projection=projection)
    schedule = SimpleNamespace(fingerprint="a" * 64)
    spike_ids = [16949] * len(spike_steps) if spike_ids is None else spike_ids
    simulation = SimpleNamespace(duration_ms=spec.duration_ms, dt_ms=spec.dt_ms,
                                 parameter_fingerprint=spec.model.fingerprint,
                                 unsigned_graph_fingerprint=projection.unsigned_graph_fingerprint,
                                 sign_policy_fingerprint="signed", stimulus_fingerprint="a" * 64,
                                 spike_neuron_ids=np.array(spike_ids), spike_timesteps=np.array(spike_steps),
                                 spike_counts=np.array([spike_ids.count(100), spike_ids.count(16949)]), trace_v_mV=None, trace_g_mV=None,
                                 sparse_trace=None, spike_result_digest="b" * 64)
    projection.signed_policy_fingerprint = "signed"
    return spec, prepared, simulation, schedule


def test_final_grid_step_spike_is_valid():
    spec, prepared, simulation, schedule = _grid_trial([50])
    trial = _trial(spec, prepared, simulation, schedule, 0, 7)
    assert trial.target_spikes == 1
    assert trial.target_spike_timesteps == (50,)


@pytest.mark.parametrize("step", [0, -1, 51])
def test_spike_outside_engine_grid_is_rejected(step):
    spec, prepared, simulation, schedule = _grid_trial([step])
    with pytest.raises(ApplicationError) as error:
        _trial(spec, prepared, simulation, schedule, 0, 7)
    assert error.value.code == ErrorCode.RESULT_SERIALIZATION


@pytest.mark.parametrize("step", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_spike_step_is_rejected(step):
    spec, prepared, simulation, schedule = _grid_trial([step])
    with pytest.raises(ApplicationError) as error:
        _trial(spec, prepared, simulation, schedule, 0, 7)
    assert error.value.code == ErrorCode.RESULT_SERIALIZATION


def test_equal_timestep_spikes_have_deterministic_neuron_order():
    ids, steps = _canonicalize_spike_events(np.array([16949, 100, 16949]), np.array([50, 50, 1]))
    assert ids.tolist() == [16949, 100, 16949]
    assert steps.tolist() == [1, 50, 50]


@pytest.mark.parametrize("change", [
    {"experiment_schema_version": "wrong"}, {"duration_ms": 0.0}, {"dt_ms": 0.07},
    {"backend": "invented"},
])
def test_invalid_top_level(change):
    with pytest.raises((ApplicationError, ValueError)):
        replace(_spec(), **change)


def test_invalid_stimulus_and_finite_values():
    spec = _spec()
    for change in ({"side": "X"}, {"frequency_hz": 1.0}, {"frequency_hz": float("nan")}):
        with pytest.raises(ApplicationError):
            replace(spec.stimulus, **change)
    with pytest.raises(ApplicationError):
        replace(spec, duration_ms=float("inf"))


def test_state_events_and_no_fake_progress():
    lifecycle = Lifecycle("run", "inv")
    lifecycle.emit(EventType.RUN_STARTED)
    for state in (State.VALIDATING, State.LOADING_DATA, State.PREPARING_NETWORK, State.RUNNING):
        lifecycle.transition(state)
    event = lifecycle.emit(EventType.TRIAL_COMPLETED, {"completed_trials": 1, "total_trials": 1})
    assert json.loads(json.dumps(event.to_dict()))["payload"]["completed_trials"] == 1
    assert all("percent" not in e.payload for e in lifecycle.events)
    lifecycle.transition(State.CANCELLED)
    with pytest.raises(ApplicationError):
        lifecycle.transition(State.RUNNING)


def test_comparison_spikes_and_robustness_contract():
    assert Comparison.create(0, 4).relative_delta is None
    assert Comparison.create(0, 4).warning == "ZERO_BASELINE"
    with pytest.raises(ApplicationError):
        SpikeEvent(-1, 2)
    with pytest.raises(ApplicationError):
        TrialResult(0, 1, "a", "b", 0, 0, (), (SpikeEvent(2, 2), SpikeEvent(1, 1)), (), ())
    req = RobustnessRequest("explicit", (RobustnessVariant("R0", (), (1,)), RobustnessVariant("V1", (("tau_membrane_ms", 15.0),), (1,))), None)
    assert req.variants[1].parameter_overrides == (("tau_membrane_ms", 15.0),)
    spec = replace(_spec(), robustness=req)
    assert validate_experiment(spec) is spec


def test_optional_git_provenance(monkeypatch):
    import malecns_sim.application.service as service
    if os.environ.get("MALECNS_A019C_R2_FIREWALL") == "1":
        # Exercise production metadata parsing without admitting a Git process.
        root = Path(service.__file__).resolve().parents[3]
        commit = "0123456789abcdef0123456789abcdef01234567"
        calls = []

        def metadata_fixture(argv, **kwargs):
            calls.append((argv, kwargs["cwd"]))
            assert kwargs == dict(cwd=kwargs["cwd"], capture_output=True,
                                  text=True, timeout=2, check=True)
            expected = [
                (["git", "rev-parse", "--show-toplevel"], Path(service.__file__).resolve().parent, str(root)),
                (["git", "rev-parse", "HEAD"], str(root), commit),
                (["git", "status", "--porcelain"], str(root), " M synthetic-fixture"),
            ]
            command, cwd, stdout = expected[len(calls) - 1]
            assert argv == command and kwargs["cwd"] == cwd
            return subprocess.CompletedProcess(argv, 0, stdout=stdout + "\n")

        monkeypatch.setattr(service.subprocess, "run", metadata_fixture)
        assert _git_provenance() == {"git_commit": commit, "git_dirty": True}
        assert len(calls) == 3
    else:
        assert _git_provenance()["git_commit"]
    monkeypatch.setattr(service.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    assert _git_provenance() == {"git_commit": None, "git_dirty": None}


def test_cpu_only_import_and_cuda_unavailable(tmp_path):
    script = "import builtins; old=builtins.__import__; builtins.__import__=lambda name,*a,**k: (_ for _ in ()).throw(ImportError('CuPy forbidden')) if name.startswith('cupy') else old(name,*a,**k); import malecns_sim.application"
    assert subprocess.run([sys.executable, "-c", script], capture_output=True).returncode == 0
    spec = replace(_spec(), backend="cuda")
    class NoCuda:
        def cuda_available(self):
            return False
    events = []
    with pytest.raises(ApplicationError) as err:
        run_experiment(spec, DatasetFiles(tmp_path / "a", tmp_path / "b", tmp_path / "c", spec.dataset.manifest_digest, spec.dataset.mapping_fingerprint), engine=NoCuda(), event_sink=events.append)
    assert err.value.code == ErrorCode.GPU_UNAVAILABLE
    assert events[-1].event_type == EventType.RUN_FAILED


def test_non_scientific_synthetic_engine_integration(tmp_path):
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
    nt_rows = [{**{key: None for key in NT_COLUMNS}, "body": body, "consensus_nt": "acetylcholine"} for body in ids]
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

    events = []
    journal = EventJournal(tmp_path / "events.jsonl")
    def record(event):
        events.append(event)
        journal(event)
    result = run_experiment(spec, files, engine=SyntheticAdapter(), event_sink=record)
    assert result.status == "COMPLETED"
    assert result.trials[0].engine_digest
    assert result.identity.run_id == events[0].run_id == events[-1].run_id
    assert [e.sequence for e in events] == list(range(1, len(events) + 1))
    assert [json.loads(line)["sequence"] for line in journal.path.read_text().splitlines()] == list(range(1, len(events) + 1))
    assert all("percent" not in e.payload for e in events)
    assert [e.event_type for e in events].count(EventType.TRIAL_COMPLETED) == 1
    assert result.trials[0].seed == 7
    assert result.trials[0].target_spike_timesteps == tuple(s.timestep for s in result.trials[0].spikes if s.neuron_id == 16949)
    traced = run_experiment(replace(spec, observables=replace(spec.observables, delivery_trace=True)), files, engine=SyntheticAdapter())
    assert traced.status == "COMPLETED"
    right = derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False).sugar_right
    right_spec = replace(spec, stimulus=replace(spec.stimulus, population_fingerprint=population_fingerprint(right), member_ids=(200,), side="R"), target=TargetSpec(10331, "contralateral"), intervention=InterventionSpec("outgoing_silence", (200,)))
    right_result = run_experiment(right_spec, files, engine=SyntheticAdapter())
    assert right_result.intervention_summary["target_ids"] == (200,)
    assert right_result.stimulus_summary["side"] == "R"
    with pytest.raises(ApplicationError) as unsupported:
        run_experiment(replace(spec, robustness=RobustnessRequest("explicit", (RobustnessVariant("R0", (), (1,)),), None)), files, engine=SyntheticAdapter())
    assert unsupported.value.code == ErrorCode.UNSUPPORTED_OPERATION
    restored = ExperimentResult.from_dict(json.loads(json.dumps(result.to_dict())))
    assert restored.authoritative_digest == result.authoritative_digest
    destination = tmp_path / "result.json"
    file_hash = write_result(result, destination)
    assert read_result(destination, expected_sha256=file_hash).authoritative_digest == result.authoritative_digest
    with pytest.raises(ApplicationError):
        read_result(destination, expected_sha256="0" * 64)
    from malecns_sim.application.models import PopulationBins
    visual = PopulationBins(1.0, (0, 1), result.authoritative_digest, "bins-v1")
    visual_result = ExperimentResult.create(identity=result.identity, spec=spec, invocation_id=result.invocation_id, started_at=result.started_at, finished_at=result.finished_at, provenance=result.provenance, stimulus_summary=result.stimulus_summary, intervention_summary=result.intervention_summary, trials=result.trials, visualization=(visual,))
    assert visual_result.authoritative_digest == result.authoritative_digest
    assert visual_result.manifest_digest != result.manifest_digest
    changed = result.to_dict()
    changed["trials"][0]["target_spikes"] += 1
    with pytest.raises(ApplicationError):
        ExperimentResult.from_dict(changed)
    with pytest.raises(ApplicationError) as err:
        run_experiment(spec, files, engine=SyntheticAdapter(), cancel_requested=lambda: True)
    assert err.value.code == ErrorCode.CANCELLED
    assert err.value.partial_result.status == "CANCELLED"
    assert err.value.partial_result.trials == ()
    assert ExperimentResult.from_dict(err.value.partial_result.to_dict()).status == "CANCELLED"
    completed_flag = {"value": False}
    def note_completion(event):
        if event.event_type == EventType.TRIAL_COMPLETED:
            completed_flag["value"] = True
    with pytest.raises(ApplicationError) as after_trial:
        run_experiment(spec, files, engine=SyntheticAdapter(), event_sink=note_completion, cancel_requested=lambda: completed_flag["value"])
    assert after_trial.value.partial_result.status == "CANCELLED"
    assert len(after_trial.value.partial_result.trials) == 1
    with pytest.raises(ApplicationError) as bad_data:
        run_experiment(spec, replace(files, manifest_digest="0" * 64), engine=SyntheticAdapter())
    assert bad_data.value.code == ErrorCode.DATASET_PROVENANCE
    assert bad_data.value.partial_result.status == "FAILED"
