"""Exact cross-batch certification; synthetic files only."""
from functools import partial
from unittest.mock import patch
import weakref

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pytest

from test_application_a015 import a015, CASES
from malecns_sim.analysis.task008 import prepare_network
from malecns_sim.data.experimental_preparation import (
    experimental_load_batched_publication_numeric, retain_edge_batches,
)
from malecns_sim.data.feather_batches import edge_batches, feather_layout
from malecns_sim.dynamics.lif import PreparedRuntime


def proposed(files, size, **kwargs):
    with patch("malecns_sim.analysis.task008.load_male_cns_v1_numeric",
               partial(experimental_load_batched_publication_numeric, max_rows_per_batch=size)):
        return prepare_network(*files, **kwargs)


@pytest.mark.parametrize("rows", CASES + [[(1, 2, 1), (999, 2, 9)] * 8 + [(1, 1, 4)]])
@pytest.mark.parametrize("threshold", [0, 4, 5])
def test_boundaries_exact(tmp_path, rows, threshold):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    table = pa.table({name: pa.array([row[i] for row in rows], type=pa.int64())
                      for i, name in enumerate(("body_pre", "body_post", "weight"))})
    reference = None
    first = None
    for size in (1, 2, 3, 7, 65536):
        feather.write_feather(table, files[2], chunksize=size)
        reference = prepare_network(*files, min_synapses=threshold)
        result = proposed(files, size, min_synapses=threshold)
        a015.assert_exact(reference, result)
        if first is not None:
            a015.assert_exact(first, result)
        first = result
        a015.assert_exact(result, proposed(files, size, min_synapses=threshold))
        assert PreparedRuntime(reference.projection).identity == PreparedRuntime(result.projection).identity
        left, right = PreparedRuntime(reference.projection), PreparedRuntime(result.projection)
        assert left.parameters.grid_steps(left.dt_ms) == right.parameters.grid_steps(right.dt_ms)
        if all(row[0] >= 0 and row[1] >= 0 for row in rows):
            actual = retain_edge_batches(files[2], np.arange(1, 5, dtype=np.int64),
                                         ("body_pre", "body_post", "weight"), size)
            expected = [row for row in rows if 1 <= row[0] <= 4 and 1 <= row[1] <= 4]
            for i in range(3):
                np.testing.assert_array_equal(actual[i], [row[i] for row in expected])


@pytest.mark.parametrize("excluded", [False, True])
@pytest.mark.parametrize("column,value", [("body_pre", None), ("body_post", None), ("weight", -1)])
def test_invalid_boundary(tmp_path, excluded, column, value):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    columns = {"body_pre": [1, 999 if excluded else 1], "body_post": [2, 998 if excluded else 2], "weight": [1, 1]}
    columns[column][1] = value
    feather.write_feather(pa.table({name: pa.array(values, type=pa.int64()) for name, values in columns.items()}), files[2], chunksize=1)
    for run in (lambda: prepare_network(*files), lambda: proposed(files, 1)):
        with pytest.raises(ValueError):
            run()
    files[2].unlink()


def test_reader_projection_admission_lifetime(tmp_path):
    path = tmp_path / "edges.feather"
    feather.write_feather(pa.table({"body_pre": [1]*9, "body_post": [2]*9,
                                   "weight": [3]*9, "unused": ["x"]*9}), path, chunksize=4)
    assert feather_layout(path)["physical_rows"] == [4, 4, 1]
    with patch("pyarrow.feather.read_table", side_effect=AssertionError("full read forbidden")):
        with edge_batches(path, max_rows_per_batch=4) as batches:
            batch = next(batches)
            assert batch.column_names == ["body_pre", "body_post", "weight"]
            ref = weakref.ref(batch)
            array = batch["body_pre"].chunk(0)
            view = array.to_numpy(zero_copy_only=True)
            assert view.ctypes.data == array.buffers()[1].address
            del batch, array, view
            next(batches)
            assert ref() is None
    with patch("pyarrow.ipc.open_file", side_effect=AssertionError("payload reader forbidden")):
        with pytest.raises(ValueError, match="physical"):
            with edge_batches(path, max_rows_per_batch=3):
                pass
    with pytest.raises(RuntimeError):
        with edge_batches(path, max_rows_per_batch=4) as batches:
            next(batches)
            raise RuntimeError("interrupt")
    path.unlink()


def test_v1_rejected(tmp_path):
    path = tmp_path / "v1.feather"
    feather.write_feather(pa.table({"body_pre": [1], "body_post": [2], "weight": [3]}), path, version=1)
    with pytest.raises(ValueError, match="V2"):
        with edge_batches(path):
            pass


@pytest.mark.parametrize("rows", [10000, 100000, 2000000])
def test_scale_exact(tmp_path, rows):
    files = a015.synthetic_files(tmp_path, rows)
    a015.assert_exact(prepare_network(*files), proposed(files, 65536))


def test_masks_released_numeric_ownership(tmp_path):
    import malecns_sim.data.experimental_preparation as experimental
    path = tmp_path / "edges.feather"
    feather.write_feather(pa.table({"body_pre": [1,999,1], "body_post": [2,998,2],
                                   "weight": [1,7,3]}), path, chunksize=1)
    refs = []
    original = experimental.endpoint_membership
    def membership(*args):
        mask = original(*args)
        refs.append(weakref.ref(mask))
        return mask
    with patch.object(experimental, "endpoint_membership", membership):
        arrays = retain_edge_batches(path, np.array([1,2]), ("body_pre", "body_post", "weight"), 1)
    assert all(ref() is None for ref in refs)
    assert all(array.flags.owndata and array.dtype == np.int64 for array in arrays)
    np.testing.assert_array_equal(arrays[2], [1,3])


@pytest.mark.parametrize("kind", ["float", "dictionary"])
def test_noninteger_schema_rejected(tmp_path, kind):
    path = tmp_path / "invalid.feather"
    values = pa.array([1.0]) if kind == "float" else pa.array([1]).dictionary_encode()
    feather.write_feather(pa.table({"body_pre": values, "body_post": [2], "weight": [3]}), path)
    with pytest.raises(ValueError, match="integer"):
        with edge_batches(path):
            pass
