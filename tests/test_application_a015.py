"""Adversarial exact equivalence against unchanged production preparation."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from malecns_sim.analysis.task008 import prepare_network
from malecns_sim.data.experimental_preparation import endpoint_membership
from malecns_sim.dynamics.lif import PreparedRuntime

spec = importlib.util.spec_from_file_location("a015", Path(__file__).resolve().parents[1] / "scripts/certify_application_a015.py")
a015 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a015)

CASES = [
    [(1, 2, 5)], [(101, 2, 5)], [(1, 101, 5)], [(101, 102, 5)],
    [(1, 2, 2), (1, 2, 3)], [(1, 2, 1)] * 5,
    [(1, 2, 2), (1, 2, 2)], [(1, 1, 5)], [(999, 2, 5)],
    [(2, 1, 5), (1, 2, 5), (3, 2, 5), (4, 2, 5)],
    [(3, 1, 5), (1, 3, 5), (2, 1, 0), (1, 1, 1)],
    [(1, 2, 0), (1, 2, 1)],
    [(101 + i, 2, 5) for i in range(1000)] + [(1, 2, 5)],
    [(1, 2, 1), (101, 2, 9), (1, 2, 3), (1, 2, 2)],
    [(2**40, 1, 1), (1, 2, 5)],
    [],
    [(-1, 2, 5), (1, 2, 5)],
]


@pytest.mark.parametrize("rows", CASES, ids=[f"fixture-{i+1}" for i in range(len(CASES))])
@pytest.mark.parametrize("threshold", [0, 4, 5])
def test_exact_adversarial(tmp_path, rows, threshold):
    import pyarrow as pa
    import pyarrow.feather as feather
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    nt = pa.table({"body": [1, 2, 3, 4], "consensus_nt": ["acetylcholine", "gaba", None, "histamine"]})
    feather.write_feather(nt, files[1])
    feather.write_feather(pa.table({name: pa.array([row[i] for row in rows], type=pa.int64())
                                    for i, name in enumerate(("body_pre", "body_post", "weight"))}), files[2])
    reference = prepare_network(*files, min_synapses=threshold)
    candidate = a015.proposed(files, min_synapses=threshold)
    a015.assert_exact(reference, candidate)
    a015.assert_exact(candidate, a015.proposed(files, min_synapses=threshold))
    left, right = PreparedRuntime(reference.projection), PreparedRuntime(candidate.projection)
    assert left.identity == right.identity
    assert left.parameters.grid_steps(left.dt_ms) == right.parameters.grid_steps(right.dt_ms)


@pytest.mark.parametrize("rows", [10000, 100000, 1000000])
def test_high_exclusion_scale(tmp_path, rows):
    files = a015.synthetic_files(tmp_path, rows)
    a015.assert_exact(prepare_network(*files), a015.proposed(files))


def test_membership_exact():
    universe = np.array([1, 3, 2**40], dtype=np.int64)
    values = np.array([-1, 0, 1, 2, 3, 2**40, 2**40+1], dtype=np.int64)
    np.testing.assert_array_equal(endpoint_membership(values, universe), np.isin(values, universe))
    assert not endpoint_membership(values, universe[:0]).any()


def test_authoritative_membership_and_no_identity_collapse(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    table = feather.read_table(files[0]).to_pydict()
    table["superclass"] = [" neuron ", "neuron", " ", None]
    table["status"] = ["Glia", None, "Traced", "Traced"]
    # A shared cell type does not map distinct raw body IDs into one identity.
    table["type"] = ["same"] * 4
    feather.write_feather(pa.table(table), files[0])
    feather.write_feather(pa.table({"body_pre": [1, 3, 2, 1], "body_post": [2, 2, 1, 1],
                                    "weight": [2, 100, 3, 4]}), files[2])
    reference = prepare_network(*files)
    a015.assert_exact(reference, a015.proposed(files))
    np.testing.assert_array_equal(reference.projection.neuron_ids, [1, 2])
    np.testing.assert_array_equal(reference.signed_connectome.connectome.synapse_counts, [4, 2, 3])


@pytest.mark.parametrize("column,value", [("body_pre", None), ("body_post", None), ("weight", -1)])
def test_invalid_excluded_rows_rejected(tmp_path, column, value):
    import pyarrow as pa
    import pyarrow.feather as feather
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    columns = {"body_pre": [999], "body_post": [998], "weight": [1]}
    columns[column] = [value]
    feather.write_feather(pa.table({name: pa.array(values, type=pa.int64()) for name, values in columns.items()}), files[2])
    for run in (lambda: prepare_network(*files), lambda: a015.proposed(files)):
        with pytest.raises(ValueError):
            run()
