import numpy as np

from malecns_sim.data.male_cns_v1 import (
    project_numeric_connectome,
    select_publication_neuron_ids,
    threshold_curated_projection,
)
from malecns_sim.data.model import NumericNormalizedConnectome
from malecns_sim.graph.fingerprint import graph_fingerprint
from malecns_sim.graph.sparse import SparseDirectedGraph


LARGE_ID = 9_007_199_254_740_993


def test_publication_selection_is_explicit_and_reports_missing_status_and_glia():
    selection = select_publication_neuron_ids(
        [
            {"bodyId": LARGE_ID, "superclass": "cb_intrinsic", "status": "Glia"},
            {"bodyId": 2, "superclass": None, "status": None},
            {"bodyId": 3, "superclass": "", "status": "Traced"},
            {"bodyId": 4, "superclass": "vnc_tbc", "status": "Glia"},
        ]
    )

    assert selection.neuron_ids.tolist() == [4, LARGE_ID]
    assert selection.excluded_ids.tolist() == [2, 3]
    assert selection.exclusion_counts == (("missing_superclass", 2),)
    assert selection.missing_status_count == 1
    assert selection.glia_status_count == 2
    assert selection.glia_retained_count == 2


def test_publication_selection_rejects_float_ids_and_duplicates():
    try:
        select_publication_neuron_ids([{"bodyId": 1.5, "superclass": "cb_intrinsic"}])
    except ValueError as error:
        assert "integer" in str(error)
    else:
        raise AssertionError("floating-point IDs must be rejected")

    try:
        select_publication_neuron_ids(
            [
                {"bodyId": 1, "superclass": "cb_intrinsic"},
                {"bodyId": 1, "superclass": "cb_intrinsic"},
            ]
        )
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate annotation IDs must be rejected")


def test_projection_filters_both_endpoints_preserves_self_edges_and_isolates():
    connectome = NumericNormalizedConnectome(
        neuron_ids=np.asarray([2, 4, LARGE_ID, 99], dtype=np.int64),
        source_ids=np.asarray([4, LARGE_ID, 2, 99], dtype=np.int64),
        target_ids=np.asarray([4, LARGE_ID, 4, 4], dtype=np.int64),
        synapse_counts=np.asarray([7, 3, 5, 100], dtype=np.int64),
    )
    projection = project_numeric_connectome(
        connectome, np.asarray([4, LARGE_ID], dtype=np.int64)
    )

    assert projection.connectome.neuron_ids.tolist() == [4, LARGE_ID]
    assert projection.connectome.source_ids.tolist() == [4, LARGE_ID]
    assert projection.connectome.target_ids.tolist() == [4, LARGE_ID]
    assert projection.connectome.synapse_counts.tolist() == [7, 3]
    assert projection.raw_edge_count == 4
    assert projection.endpoint_edge_count == 2
    assert projection.endpoint_excluded_edge_count == 2
    assert projection.duplicate_pair_count == 0
    assert projection.self_edge_count == 2
    assert projection.isolated_count == 0


def test_projection_aggregates_duplicate_pairs_after_endpoint_filtering():
    connectome = NumericNormalizedConnectome(
        neuron_ids=np.asarray([4, LARGE_ID], dtype=np.int64),
        source_ids=np.asarray([LARGE_ID, LARGE_ID], dtype=np.int64),
        target_ids=np.asarray([4, 4], dtype=np.int64),
        synapse_counts=np.asarray([2, 3], dtype=np.int64),
    )
    projection = project_numeric_connectome(
        connectome, np.asarray([4, LARGE_ID], dtype=np.int64)
    )

    assert projection.edge_count == 1
    assert projection.connectome.synapse_counts.tolist() == [5]
    assert projection.duplicate_pair_count == 1


def test_threshold_is_applied_after_projection_and_preserves_isolated_neurons():
    connectome = NumericNormalizedConnectome(
        neuron_ids=np.asarray([1, 2, 3], dtype=np.int64),
        source_ids=np.asarray([1, 1, 2], dtype=np.int64),
        target_ids=np.asarray([2, 3, 2], dtype=np.int64),
        synapse_counts=np.asarray([4, 99, 5], dtype=np.int64),
    )
    projection = project_numeric_connectome(
        connectome, np.asarray([1, 2], dtype=np.int64)
    )
    thresholded = threshold_curated_projection(projection, min_synapses=5)

    assert projection.edge_count == 2
    assert thresholded.edge_count == 1
    assert thresholded.connectome.source_ids.tolist() == [2]
    assert thresholded.connectome.target_ids.tolist() == [2]
    assert thresholded.connectome.neuron_ids.tolist() == [1, 2]
    assert thresholded.isolated_count == 1
    assert thresholded.self_edge_count == 1


def test_curated_graph_shape_and_fingerprint_are_deterministic():
    connectome = NumericNormalizedConnectome(
        neuron_ids=np.asarray([1, 2, LARGE_ID], dtype=np.int64),
        source_ids=np.asarray([1, 2], dtype=np.int64),
        target_ids=np.asarray([2, LARGE_ID], dtype=np.int64),
        synapse_counts=np.asarray([5, 7], dtype=np.int64),
    )
    projection = project_numeric_connectome(
        connectome, np.asarray([1, 2, LARGE_ID], dtype=np.int64)
    )
    first = SparseDirectedGraph.from_curated_projection(projection)
    second = SparseDirectedGraph.from_curated_projection(projection)

    assert first.matrix.shape == (3, 3)
    assert first.matrix.nnz == 2
    assert first.matrix.data.dtype == np.float64
    assert graph_fingerprint(first) == graph_fingerprint(second)
    assert first.propagate({1: 1.0}) == {2: 5.0}
