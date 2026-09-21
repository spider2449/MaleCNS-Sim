import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from malecns_sim.analysis.shiu_v630 import (
    compare_summaries,
    summarize_reference_parquet,
    summarize_simulation_results,
)
from malecns_sim.data.shiu_v630 import (
    MN9_FLYWIRE_ID,
    SHIU_SUGAR_NEURON_IDS,
    ShiuV630Reference,
    ShiuV630ReferenceError,
    ShiuV630Schema,
    load_shiu_v630,
    parse_sugar_ids_from_notebook,
    prepare_shiu_v630_projection,
    verify_reference_neurons,
)
from malecns_sim.data.provenance import read_manifest
from malecns_sim.dynamics import ExplicitStimulus, PoissonStimulus, SpikeSchedule, simulate_lif


def _reference(ids=(101, 102, 103, 104)):
    return ShiuV630Reference(
        neuron_ids=np.asarray(ids, dtype=np.int64),
        source_positions=np.asarray([0, 1, 2], dtype=np.int64),
        target_positions=np.asarray([1, 2, 3], dtype=np.int64),
        connectivity_counts=np.asarray([2, 3, 4], dtype=np.int64),
        excitatory_signs=np.asarray([1, -1, 1], dtype=np.int64),
        signed_connectivity_counts=np.asarray([2, -3, 4], dtype=np.int64),
        schema=ShiuV630Schema(
            completeness_id_column="CSV index",
            completeness_neuron_count=len(ids),
            connectivity_columns=(
                "Presynaptic_ID",
                "Postsynaptic_ID",
                "Presynaptic_Index",
                "Postsynaptic_Index",
                "Connectivity",
                "Excitatory",
                "Excitatory x Connectivity",
            ),
        ),
    )


def _exact_reference():
    ids = np.asarray(sorted(set(SHIU_SUGAR_NEURON_IDS + (MN9_FLYWIRE_ID,))), dtype=np.int64)
    return ShiuV630Reference(
        neuron_ids=ids,
        source_positions=np.asarray([0, 1], dtype=np.int64),
        target_positions=np.asarray([1, 2], dtype=np.int64),
        connectivity_counts=np.asarray([2, 3], dtype=np.int64),
        excitatory_signs=np.asarray([1, -1], dtype=np.int64),
        signed_connectivity_counts=np.asarray([2, -3], dtype=np.int64),
        schema=ShiuV630Schema("CSV index", len(ids), ("Excitatory x Connectivity",)),
    )


def test_v630_loader_records_schema_and_original_index_mapping(tmp_path):
    ids = [101, 102, 103]
    pd.DataFrame({"Completed": [True, True, True]}, index=ids).to_csv(tmp_path / "comp.csv")
    pd.DataFrame(
        {
            "Presynaptic_ID": [101, 102],
            "Postsynaptic_ID": [102, 103],
            "Presynaptic_Index": [0, 1],
            "Postsynaptic_Index": [1, 2],
            "Connectivity": [2, 3],
            "Excitatory": [1, -1],
            "Excitatory x Connectivity": [2, -3],
        }
    ).to_parquet(tmp_path / "connectivity.parquet")
    reference = load_shiu_v630(tmp_path / "comp.csv", tmp_path / "connectivity.parquet")
    assert reference.neuron_ids.tolist() == ids
    assert reference.source_positions.tolist() == [0, 1]
    assert reference.target_positions.tolist() == [1, 2]
    assert reference.signed_connectivity_counts.tolist() == [2, -3]
    assert reference.schema.presynaptic_index_column == "Presynaptic_Index"
    assert reference.schema.signed_connectivity_column == "Excitatory x Connectivity"


def test_original_signed_connectivity_is_used_without_male_cns_resolution():
    projection = prepare_shiu_v630_projection(_reference())
    assert projection.effective_weights_mV.tolist() == [pytest.approx(0.55), pytest.approx(-0.825), pytest.approx(1.1)]
    assert projection.sign_policy_id == "shiu-v630-original-signed-connectivity-v1"
    assert projection.included_anatomical_weight == 9


def test_ordered_sugar_reference_is_parsed_and_mn9_is_indexed(tmp_path):
    notebook = {"cells": [{"cell_type": "code", "source": [f"neu_sugar = {list(SHIU_SUGAR_NEURON_IDS)!r}\n"]}]}
    path = tmp_path / "example.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    parsed = parse_sugar_ids_from_notebook(path)
    assert parsed == SHIU_SUGAR_NEURON_IDS
    verified = verify_reference_neurons(_exact_reference(), parsed)
    assert verified.sugar_ids == SHIU_SUGAR_NEURON_IDS
    assert verified.mn9_id == MN9_FLYWIRE_ID
    assert verified.mn9_position == int(np.searchsorted(_exact_reference().neuron_ids, MN9_FLYWIRE_ID))


def test_missing_reference_neuron_fails_closed():
    reference = _reference()
    with pytest.raises(ShiuV630ReferenceError, match="missing"):
        reference.positions_for_ids((999,))
    with pytest.raises(ShiuV630ReferenceError, match="missing"):
        verify_reference_neurons(reference, SHIU_SUGAR_NEURON_IDS)


def test_graph_is_reused_and_trial_state_resets_without_mutation():
    projection = prepare_shiu_v630_projection(_reference())
    before = tuple(array.copy() for array in (projection.outgoing_indptr, projection.outgoing_targets, projection.outgoing_weights_mV))
    stimulus = ExplicitStimulus((SpikeSchedule(101, (0.0,)),), weight_mV=10.0)
    first = simulate_lif(projection, duration_ms=2.0, stimulus=stimulus)
    second = simulate_lif(projection, duration_ms=2.0, stimulus=stimulus)
    assert first.spike_result_digest == second.spike_result_digest
    assert first.simulation_fingerprint == second.simulation_fingerprint
    assert projection.fingerprint == projection.fingerprint
    for actual, expected in zip((projection.outgoing_indptr, projection.outgoing_targets, projection.outgoing_weights_mV), before):
        assert np.array_equal(actual, expected)


def test_seeded_trial_generation_is_deterministic():
    first = PoissonStimulus((101, 102), rate_hz=100.0, seed=7).generate(10.0, 0.1, 0.275)
    second = PoissonStimulus((101, 102), rate_hz=100.0, seed=7).generate(10.0, 0.1, 0.275)
    assert first.fingerprint == second.fingerprint
    assert [item.spike_times_ms for item in first.schedules] == [item.spike_times_ms for item in second.schedules]


def test_summary_firing_rate_reference_parquet_and_comparison(tmp_path):
    frame = pd.DataFrame(
        {
            "t": [0.1, 0.2, 0.3, 0.4],
            "trial": [0, 0, 1, 1],
            "flywire_id": [MN9_FLYWIRE_ID, 101, MN9_FLYWIRE_ID, 102],
            "exp_name": ["sugarR_100Hz"] * 4,
        }
    )
    path = tmp_path / "reference.parquet"
    frame.to_parquet(path)
    reference = summarize_reference_parquet(path, mn9_id=MN9_FLYWIRE_ID, duration_seconds=1.0)
    assert reference.mn9_spike_counts.tolist() == [1, 1]
    assert reference.mn9_mean_firing_rate_hz == pytest.approx(1.0)
    assert reference.mn9_active_trial_fraction == 1.0
    local = summarize_simulation_results(
        [
            simulate_lif(prepare_shiu_v630_projection(_reference()), duration_ms=1000.0),
            simulate_lif(prepare_shiu_v630_projection(_reference()), duration_ms=1000.0),
        ],
        condition="local",
        mn9_id=MN9_FLYWIRE_ID,
        duration_seconds=1.0,
        input_spike_counts=[3, 4],
    )
    assert local.input_spike_counts.tolist() == [3, 4]
    comparisons = compare_summaries(reference, local)
    assert comparisons[0].metric == "mn9_mean_firing_rate_hz"
    assert comparisons[0].absolute_difference == pytest.approx(-1.0)


def test_reference_provenance_manifest_is_pinned():
    manifest = read_manifest(Path(__file__).parents[1] / "data" / "provenance" / "shiu-2024-v630.json")
    assert manifest.release == "main@91bdd1e7dcf193f3e7ca5a8933497fcef63b7960"
    assert len(manifest.files) == 5
    assert all(len(item.sha256) == 64 and item.byte_size > 0 for item in manifest.files)
