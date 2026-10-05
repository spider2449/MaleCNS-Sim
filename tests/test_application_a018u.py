"""Exact synthetic downstream profiling against the unchanged scientific oracle."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from test_application_a015 import a015
from malecns_sim.graph.sparse import SparseDirectedGraph

spec = importlib.util.spec_from_file_location('a018u', Path(__file__).resolve().parents[1] / 'scripts/certify_application_a018u.py')
a018u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a018u)


@pytest.mark.parametrize('shape', a018u.SHAPES)
@pytest.mark.parametrize('neurons,edges', [(10, 0), (10, 1), (100, 1000), (2000, 100000)])
@pytest.mark.parametrize('threshold,conservative', [(0, False), (5, False), (0, True)])
def test_instrumented_oracle_exact(tmp_path, shape, neurons, edges, threshold, conservative):
    files, numeric = a018u.fixture(tmp_path, neurons, edges, shape)
    reference, identity, delay, _ = a018u.run(files, numeric, threshold=threshold, conservative=conservative)
    probe = a018u.Probe()
    try:
        actual, actual_identity, actual_delay, _ = a018u.run(files, numeric, probe=probe,
            threshold=threshold, conservative=conservative)
    finally:
        probe.close()
    a015.assert_exact(reference, actual)
    repeated, repeat_identity, repeat_delay, _ = a018u.run(files, numeric,
        threshold=threshold, conservative=conservative)
    a015.assert_exact(reference, repeated)
    assert identity == actual_identity == repeat_identity
    assert delay == actual_delay == repeat_delay
    for name in reference.projection.__dataclass_fields__:
        left, right = getattr(reference.projection, name), getattr(actual.projection, name)
        if isinstance(left, np.ndarray):
            assert left.dtype == right.dtype and left.tobytes() == right.tobytes()
    assert reference.signed_connectome.sign_policy_id == actual.signed_connectome.sign_policy_id
    assert reference.signed_connectome.resolution_policy_id == actual.signed_connectome.resolution_policy_id
    assert reference.signed_connectome.connectome.provenance == actual.signed_connectome.connectome.provenance
    for result in (reference, actual):
        matrix = SparseDirectedGraph.from_numeric_connectome(result.signed_connectome.connectome).matrix
        # Incoming CSR is a derived test view, not a production preparation owner.
        incoming = matrix.T.tocsr()
        if result is reference:
            expected = incoming
        else:
            for name in ('indptr', 'indices', 'data'):
                assert getattr(expected, name).tobytes() == getattr(incoming, name).tobytes()
    assert probe.rows and all(row['seconds'] >= 0 for row in probe.rows)
    assert all(row['temporary_peak_bytes'] is None for row in probe.rows)


def test_missing_metadata_and_policy_contract(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather
    files, numeric = a018u.fixture(tmp_path, 10, 80, 'sorted')
    feather.write_feather(pa.table({'body': [1, 2, 3, 4],
        'consensus_nt': ['acetylcholine', 'gaba', 'unknown', 'glutamate']}), files[1])
    for conservative in (False, True):
        expected, _, _, _ = a018u.run(files, numeric, conservative=conservative)
        probe = a018u.Probe()
        try:
            actual, _, _, _ = a018u.run(files, numeric, probe=probe, conservative=conservative)
        finally:
            probe.close()
        a015.assert_exact(expected, actual)
        results = expected.signed_connectome.neuron_signs
        assert results[0].sign == 1 and results[1].sign == -1
        assert expected.signed_connectome.sign_policy_id == actual.signed_connectome.sign_policy_id


@pytest.mark.parametrize('shape', ['random', 'all_exc'])
def test_large_safe_exact(tmp_path, shape):
    test_instrumented_oracle_exact(tmp_path, shape, 20000, 1000000, 0, False)


def test_large_integer_identity(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather
    from dataclasses import replace
    files, numeric = a018u.fixture(tmp_path, 100, 1000, 'mixed')
    offset = 2**60
    for path, field in ((files[0], 'bodyId'), (files[1], 'body')):
        table = feather.read_table(path).to_pydict()
        table[field] = [value + offset for value in table[field]]
        feather.write_feather(pa.table(table), path)
    numeric = replace(numeric, neuron_ids=numeric.neuron_ids + offset,
                      source_ids=numeric.source_ids + offset, target_ids=numeric.target_ids + offset)
    expected, identity, delay, _ = a018u.run(files, numeric)
    probe = a018u.Probe()
    try:
        actual, actual_identity, actual_delay, _ = a018u.run(files, numeric, probe=probe)
    finally:
        probe.close()
    a015.assert_exact(expected, actual)
    assert identity == actual_identity and delay == actual_delay


def test_default_has_no_probe(tmp_path):
    files, numeric = a018u.fixture(tmp_path, 10, 10, 'sorted')
    with patch.object(a018u, 'instrument', side_effect=AssertionError('opt-in only')):
        a018u.run(files, numeric)


@pytest.mark.parametrize('neurons,edges', [(20001, 0), (10, 1000001), (0, 0)])
def test_synthetic_bounds(tmp_path, neurons, edges):
    with pytest.raises(ValueError):
        a018u.fixture(tmp_path, neurons, edges, 'sorted')
