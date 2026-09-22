from __future__ import annotations

import json

import pytest

from malecns_sim.analysis.task017 import (
    BASELINE_CANDIDATE_ID,
    REFERENCE_VARIANT,
    TASK010_BASELINE,
    TASK010_INTERVENTION,
    ExecutionBudget,
    ExecutionBudgetExceeded,
    CheckpointError,
    CheckpointIdentityMismatch,
    CHECKPOINT_UNIT_PREFIX,
    DuplicateUnitExecution,
    StaleSidecar,
    Task017Checkpoint,
    Task017UnitKey,
    VARIANT_CONFIGURATIONS,
    _compatibility_score,
    _digest,
    _result_equal,
    _trace_equal,
    _synthetic_fixtures,
    _synthetic_projection,
    expected_task017_unit_keys,
    pending_task017_unit_keys,
    task016_specification_fingerprint,
    task017_scoring_allowed,
)
from malecns_sim.analysis.task008 import PreparedNetwork
from malecns_sim.analysis.task017 import FrozenSchedule, _run_or_reuse_series
from malecns_sim.dynamics import simulate_lif, simulate_lif_active
from malecns_sim.dynamics.cuda import cuda_available, simulate_cuda_batch, upload_graph


def test_task017_variant_matrix_is_literal_and_exact():
    assert tuple(item.variant_id for item in VARIANT_CONFIGURATIONS) == (
        "R0_REFERENCE_TASK005",
        "V1_TAU_MEMBRANE_FAST",
        "V2_TAU_MEMBRANE_SLOW",
        "V3_TAU_SYNAPSE_FAST",
        "V4_DELAY_SHORT",
        "V5_WEIGHT_LOW",
        "V6_THRESHOLD_HIGHER",
        "V7_CONSERVATIVE_SIGNS",
    )
    by_id = {item.variant_id: item for item in VARIANT_CONFIGURATIONS}
    assert by_id["R0_REFERENCE_TASK005"].parameters.v_threshold_mV == -45.0
    assert by_id["V1_TAU_MEMBRANE_FAST"].parameters.tau_membrane_ms == 10.0
    assert by_id["V2_TAU_MEMBRANE_SLOW"].parameters.tau_membrane_ms == 30.0
    assert by_id["V3_TAU_SYNAPSE_FAST"].parameters.tau_synapse_ms == 2.5
    assert by_id["V4_DELAY_SHORT"].parameters.synaptic_delay_ms == 1.0
    assert by_id["V4_DELAY_SHORT"].parameters.grid_steps(0.1)[0] == 10
    assert by_id["V5_WEIGHT_LOW"].parameters.synaptic_weight_per_anatomical_synapse_mV == 0.2
    assert by_id["V6_THRESHOLD_HIGHER"].parameters.v_threshold_mV == -44.0
    assert by_id["V7_CONSERVATIVE_SIGNS"].sign_policy_id == "ConservativeSignPolicy"
    assert REFERENCE_VARIANT.parameters.fingerprint == by_id["R0_REFERENCE_TASK005"].parameters.fingerprint


def test_task017_specification_fingerprint_is_deterministic():
    first = task016_specification_fingerprint()
    second = task016_specification_fingerprint()
    assert first == second
    assert len(first) == 64


def test_task017_mechanism_compatibility_preserves_direct_swap_rule():
    assert _compatibility_score("NETWORK_REDISTRIBUTION_COMPATIBLE", "MIXED") == 0.5
    assert _compatibility_score("SHORT_PATH_COMPATIBLE", "MIXED") == 0.5
    assert _compatibility_score("SHORT_PATH_COMPATIBLE", "NETWORK_REDISTRIBUTION_COMPATIBLE") == 0.0
    assert _compatibility_score("UNRESOLVED", "MIXED") == 0.0


def test_task017_expected_unit_keys_are_exact_and_deterministic():
    first = expected_task017_unit_keys()
    second = expected_task017_unit_keys()
    assert first == second
    assert len(first) == 3168
    assert first[0].variant_id == "R0_REFERENCE_TASK005"
    assert first[0].candidate_id == BASELINE_CANDIDATE_ID
    assert first[0].analysis_kind == TASK010_BASELINE
    assert {item.analysis_kind for item in first} == {
        TASK010_BASELINE,
        TASK010_INTERVENTION,
        "task011_baseline_trace",
        "task011_intervention_trace",
    }


def test_task017_checkpoint_resume_duplicate_and_fingerprint_rejection(tmp_path):
    identity = {"schema": "test", "specification_fingerprint": task016_specification_fingerprint()}
    path = tmp_path / "matrix.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    stimulus = _synthetic_fixtures(0.275)[0]
    result = simulate_lif(projection, duration_ms=10.0, stimulus=stimulus)
    key = Task017UnitKey("R0_REFERENCE_TASK005", BASELINE_CANDIDATE_ID, "LEFT", 0, TASK010_BASELINE)
    metadata = {
        "key": key.as_record(),
        "effective_model_parameters": REFERENCE_VARIANT.as_record(),
        "schedule_fingerprint": stimulus.fingerprint,
        "candidate_identity": BASELINE_CANDIDATE_ID,
        "stimulus_identity": "LEFT",
    }
    unit_fingerprint = _digest(CHECKPOINT_UNIT_PREFIX, metadata)
    checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
    resumed = Task017Checkpoint(path, identity)
    reused = resumed.get(key, unit_fingerprint)
    assert reused is not None
    assert _result_equal(result, reused)
    with pytest.raises(DuplicateUnitExecution):
        resumed.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
    assert resumed.duplicate_count == 1
    with pytest.raises(CheckpointIdentityMismatch):
        resumed.get(key, "unit-b")
    with pytest.raises(CheckpointIdentityMismatch):
        Task017Checkpoint(path, {"schema": "test", "specification_fingerprint": "different"})


def test_task017_checkpoint_merge_order_is_independent(tmp_path):
    identity = {"schema": "test-order"}
    path = tmp_path / "matrix.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    result = simulate_lif(projection, duration_ms=10.0, stimulus=_synthetic_fixtures(0.275)[0])
    keys = [
        Task017UnitKey("V1", "10135", "RIGHT", 2, TASK010_INTERVENTION),
        Task017UnitKey("R0", BASELINE_CANDIDATE_ID, "LEFT", 0, TASK010_BASELINE),
    ]
    for key in reversed(keys):
        metadata = {
            "key": key.as_record(),
            "effective_model_parameters": {"variant_id": key.variant_id},
            "schedule_fingerprint": "schedule",
            "candidate_identity": key.candidate_id,
            "stimulus_identity": key.stimulus_side,
        }
        checkpoint.put(key, unit_fingerprint=key.token, metadata=metadata, result=result)
    expected = sorted(keys, key=lambda item: (item.variant_id, item.stimulus_side, item.analysis_kind, item.trial_index, item.candidate_id))
    assert [item["key"] for item in checkpoint.records()] == [item.as_record() for item in expected]


def test_task017_checkpoint_preserves_trace_payloads(tmp_path):
    identity = {"schema": "test-trace"}
    path = tmp_path / "trace.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    stimulus = _synthetic_fixtures(0.275)[2]
    result = simulate_lif(
        projection,
        duration_ms=10.0,
        stimulus=stimulus,
        trace_neuron_ids=(1, 2, 3, 4),
        collect_sparse_trace=True,
    )
    key = Task017UnitKey("R0", "10135", "LEFT", 0, "task011_intervention_trace")
    metadata = {
        "key": key.as_record(),
        "effective_model_parameters": REFERENCE_VARIANT.as_record(),
        "schedule_fingerprint": stimulus.fingerprint,
        "candidate_identity": key.candidate_id,
        "stimulus_identity": key.stimulus_side,
    }
    unit_fingerprint = _digest(CHECKPOINT_UNIT_PREFIX, metadata)
    checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
    reused = Task017Checkpoint(path, identity).get(key, unit_fingerprint)
    assert reused is not None
    assert _trace_equal(result, reused)


def test_task017_incomplete_matrix_is_not_scoring_eligible():
    ledger = {
        "expected_unit_count": 3168,
        "completed_unit_count": 3167,
        "missing_unit_count": 1,
        "invalid_technical_unit_count": 0,
        "matrix_complete": False,
    }
    assert not task017_scoring_allowed(ledger)
    complete = dict(ledger, completed_unit_count=3168, missing_unit_count=0, matrix_complete=True)
    assert task017_scoring_allowed(complete)
    assert not task017_scoring_allowed(dict(complete, invalid_technical_unit_count=1))


def test_task017_bounded_budget_and_canonical_pending_resume(tmp_path):
    identity = {"schema": "bounded", "specification_fingerprint": task016_specification_fingerprint()}
    path = tmp_path / "bounded.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    result = simulate_lif(projection, duration_ms=10.0, stimulus=_synthetic_fixtures(0.275)[0])
    keys = expected_task017_unit_keys()[:2]
    for key in keys:
        metadata = {
            "key": key.as_record(),
            "effective_model_parameters": REFERENCE_VARIANT.as_record(),
            "schedule_fingerprint": "schedule",
            "candidate_identity": key.candidate_id,
            "stimulus_identity": key.stimulus_side,
        }
        checkpoint.put(key, unit_fingerprint=_digest(CHECKPOINT_UNIT_PREFIX, metadata), metadata=metadata, result=result)
    resumed = Task017Checkpoint(path, identity)
    pending = pending_task017_unit_keys(resumed)
    assert pending[0] == expected_task017_unit_keys()[2]
    budget = ExecutionBudget(max_units=2)
    assert budget.batch_limit(10) == 2
    budget.before_batch(2)
    budget.committed(2)
    with pytest.raises(ExecutionBudgetExceeded):
        budget.batch_limit(1)


def test_task017_incomplete_journal_tail_is_recovered(tmp_path):
    identity = {"schema": "tail"}
    path = tmp_path / "tail.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    result = simulate_lif(projection, duration_ms=10.0, stimulus=_synthetic_fixtures(0.275)[0])
    key = Task017UnitKey("R0", BASELINE_CANDIDATE_ID, "LEFT", 0, TASK010_BASELINE)
    metadata = {
        "key": key.as_record(),
        "effective_model_parameters": REFERENCE_VARIANT.as_record(),
        "schedule_fingerprint": "schedule",
        "candidate_identity": key.candidate_id,
        "stimulus_identity": key.stimulus_side,
    }
    unit_fingerprint = _digest(CHECKPOINT_UNIT_PREFIX, metadata)
    checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
    with path.open("ab") as handle:
        handle.write(b'{"kind":"completed_unit"')
    resumed = Task017Checkpoint(path, identity)
    assert resumed.get(key, unit_fingerprint) is not None
    assert path.read_bytes().endswith(b"\n")


def test_task017_bounded_execution_resume_matches_uninterrupted(tmp_path, monkeypatch):
    identity = {"schema": "execution-resume"}
    projection = _synthetic_projection(0.275)
    prepared = PreparedNetwork(
        projection=projection,
        signed_connectome=None,
        graph_name="synthetic",
        preparation_seconds=0.0,
        graph_loading_seconds=0.0,
        setup_seconds=0.0,
        memory_bytes=0,
        fingerprint=projection.fingerprint,
        cache_fingerprint="cache",
    )
    stimuli = _synthetic_fixtures(0.275)[:2]
    schedules = tuple(FrozenSchedule(index, index, stimulus, stimulus.fingerprint) for index, stimulus in enumerate(stimuli))

    def fake_run_batch(prepared_network, variant, batch_stimuli, **kwargs):
        return tuple(
            simulate_lif(
                prepared_network.projection,
                duration_ms=kwargs["duration_ms"],
                stimulus=stimulus,
                silenced_neuron_ids=kwargs.get("silenced_ids", ()),
            )
            for stimulus in batch_stimuli
        )

    monkeypatch.setattr("malecns_sim.analysis.task017._run_batch", fake_run_batch)

    resumable_path = tmp_path / "resumable.jsonl"
    first = Task017Checkpoint(resumable_path, identity)
    with pytest.raises(ExecutionBudgetExceeded):
        _run_or_reuse_series(
            first,
            REFERENCE_VARIANT,
            prepared,
            schedules,
            side="LEFT",
            candidate_id=BASELINE_CANDIDATE_ID,
            analysis_kind=TASK010_BASELINE,
            duration_ms=10.0,
            budget=ExecutionBudget(max_units=1),
        )
    resumed = Task017Checkpoint(resumable_path, identity)
    _run_or_reuse_series(
        resumed,
        REFERENCE_VARIANT,
        prepared,
        schedules,
        side="LEFT",
        candidate_id=BASELINE_CANDIDATE_ID,
        analysis_kind=TASK010_BASELINE,
        duration_ms=10.0,
        budget=ExecutionBudget(max_units=1),
    )

    uninterrupted = Task017Checkpoint(tmp_path / "uninterrupted.jsonl", identity)
    _run_or_reuse_series(
        uninterrupted,
        REFERENCE_VARIANT,
        prepared,
        schedules,
        side="LEFT",
        candidate_id=BASELINE_CANDIDATE_ID,
        analysis_kind=TASK010_BASELINE,
        duration_ms=10.0,
    )
    assert [item["result_digest"] for item in resumed.records()] == [item["result_digest"] for item in uninterrupted.records()]


def test_task017_effective_parameter_and_stale_sidecar_rejection(tmp_path):
    identity = {"schema": "reject"}
    path = tmp_path / "reject.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    result = simulate_lif(projection, duration_ms=10.0, stimulus=_synthetic_fixtures(0.275)[0])
    key = Task017UnitKey("R0", BASELINE_CANDIDATE_ID, "LEFT", 0, TASK010_BASELINE)
    metadata = {
        "key": key.as_record(),
        "effective_model_parameters": REFERENCE_VARIANT.as_record(),
        "schedule_fingerprint": "schedule",
        "candidate_identity": key.candidate_id,
        "stimulus_identity": key.stimulus_side,
    }
    unit_fingerprint = _digest(CHECKPOINT_UNIT_PREFIX, metadata)
    checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    records[1]["metadata"]["effective_model_parameters"] = {"variant_id": "MISMATCH"}
    path.write_text("\n".join(json.dumps(item, sort_keys=True) for item in records) + "\n", encoding="utf-8")
    with pytest.raises(CheckpointIdentityMismatch):
        Task017Checkpoint(path, identity)

    clean_path = tmp_path / "stale.jsonl"
    clean = Task017Checkpoint(clean_path, identity)
    clean.artifact_dir.mkdir()
    (clean.artifact_dir / "stale.npz").write_bytes(b"stale")
    with pytest.raises(StaleSidecar):
        Task017Checkpoint(clean_path, identity)


def test_task017_duplicate_journal_record_is_rejected(tmp_path):
    identity = {"schema": "duplicate-journal"}
    path = tmp_path / "duplicate.jsonl"
    checkpoint = Task017Checkpoint(path, identity)
    projection = _synthetic_projection(0.275)
    result = simulate_lif(projection, duration_ms=10.0, stimulus=_synthetic_fixtures(0.275)[0])
    key = Task017UnitKey("R0", BASELINE_CANDIDATE_ID, "LEFT", 0, TASK010_BASELINE)
    metadata = {
        "key": key.as_record(),
        "effective_model_parameters": REFERENCE_VARIANT.as_record(),
        "schedule_fingerprint": "schedule",
        "candidate_identity": key.candidate_id,
        "stimulus_identity": key.stimulus_side,
    }
    checkpoint.put(key, unit_fingerprint=_digest(CHECKPOINT_UNIT_PREFIX, metadata), metadata=metadata, result=result)
    record = path.read_text(encoding="utf-8").splitlines()[1]
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(record + "\n")
    with pytest.raises(CheckpointError):
        Task017Checkpoint(path, identity)


def test_task017_active_cpu_silencing_and_trace_invariance():
    projection = _synthetic_projection(0.275)
    stimulus = _synthetic_fixtures(0.275)[2]
    dense = simulate_lif(projection, duration_ms=10.0, stimulus=stimulus)
    active = simulate_lif_active(projection, duration_ms=10.0, stimulus=stimulus)
    assert _result_equal(dense, active)
    dense_silenced = simulate_lif(projection, duration_ms=10.0, stimulus=stimulus, silenced_neuron_ids=(1,))
    active_silenced = simulate_lif_active(projection, duration_ms=10.0, stimulus=stimulus, silenced_neuron_ids=(1,))
    assert _result_equal(dense_silenced, active_silenced)
    traced = simulate_lif(
        projection,
        duration_ms=10.0,
        stimulus=stimulus,
        trace_neuron_ids=(1, 2, 3, 4),
        collect_sparse_trace=True,
    )
    assert _result_equal(dense, traced)


@pytest.mark.skipif(not cuda_available(), reason="CUDA backend unavailable")
def test_task017_cuda_per_trial_silencing_matches_independent_runs():
    projection = _synthetic_projection(0.275)
    graph, _ = upload_graph(projection)
    stimuli = (_synthetic_fixtures(0.275)[0], _synthetic_fixtures(0.275)[2])
    batched = simulate_cuda_batch(
        projection,
        stimuli,
        duration_ms=10.0,
        silenced_neuron_ids_by_trial=((), (1,)),
        cuda_graph=graph,
    )
    independent = (
        simulate_cuda_batch(projection, (stimuli[0],), duration_ms=10.0, cuda_graph=graph)[0],
        simulate_cuda_batch(projection, (stimuli[1],), duration_ms=10.0, silenced_neuron_ids=(1,), cuda_graph=graph)[0],
    )
    assert all(_result_equal(left, right) for left, right in zip(batched, independent))
