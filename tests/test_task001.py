from __future__ import annotations

import pytest

from malecns_sim.data.io import load_connectome
from malecns_sim.data.model import NormalizedConnectome
from malecns_sim.data.normalize import (
    EdgeColumns,
    NeuronColumns,
    normalize_connectome,
    normalize_edges,
    normalize_neurons,
)
from malecns_sim.graph.sparse import SparseDirectedGraph


def fixture_connectome() -> NormalizedConnectome:
    neurons = [
        {"neuron_id": "10", "cell_type": "motor", "neurotransmitter": "GABA", "motor_related": True},
        {"neuron_id": "2", "cell_type": "sensory", "ascending": True},
        {"neuron_id": "1", "cell_type": "interneuron"},
        {"neuron_id": "3", "descending": True},
    ]
    edges = [
        {"source_id": "1", "target_id": "2", "synapse_count": 2},
        {"source_id": "1", "target_id": "2", "synapse_count": 3},
        {"source_id": "1", "target_id": "3", "synapse_count": 5},
        {"source_id": "2", "target_id": "2", "synapse_count": 7},
        {"source_id": "3", "target_id": "10", "synapse_count": 1},
    ]
    return normalize_connectome(neurons, edges)


def test_neuron_normalization_preserves_metadata_and_orders_ids():
    result = normalize_neurons(
        [
            {"neuron_id": 10, "cell_type": "motor", "neurotransmitter": "GABA", "motor": True},
            {"neuron_id": 2, "cell_type": "sensory", "ascending": "yes"},
            {"neuron_id": 1, "cell_type": "interneuron"},
        ],
        columns=None,
    )
    assert tuple(neuron.neuron_id for neuron in result) == ("1", "2", "10")
    assert result[1].ascending is True
    assert result[2].neurotransmitter == "GABA"


def test_neuron_metadata_mapping_and_duplicate_merge():
    from malecns_sim.data.normalize import NeuronColumns

    result = normalize_neurons(
        [
            {"body": "n1", "type": "sensory", "asc": True},
            {"body": "n1", "type": "sensory", "asc": None},
        ],
        NeuronColumns(neuron_id="body", cell_type="type", ascending="asc"),
    )
    assert len(result) == 1
    assert result[0].ascending is True
    with pytest.raises(ValueError, match="conflicting cell_type"):
        normalize_neurons(
            [{"neuron_id": "n1", "cell_type": "a"}, {"neuron_id": "n1", "cell_type": "b"}]
        )


def test_edge_normalization_aggregates_duplicates_and_keeps_self_edges():
    result = normalize_edges(
        [
            {"source_id": "b", "target_id": "a", "synapse_count": 2},
            {"source_id": "b", "target_id": "a", "synapse_count": 4},
            {"source_id": "a", "target_id": "a", "synapse_count": 1},
        ],
        ["a", "b"],
    )
    assert [(edge.source_id, edge.target_id, edge.synapse_count) for edge in result] == [
        ("a", "a", 1),
        ("b", "a", 6),
    ]


def test_unknown_edge_endpoint_is_rejected():
    with pytest.raises(ValueError, match="unknown neuron"):
        normalize_edges(
            [{"source_id": "a", "target_id": "missing", "synapse_count": 1}], ["a"]
        )


def test_threshold_and_csr_construction_are_deterministic():
    connectome = fixture_connectome()
    graph = SparseDirectedGraph.from_connectome(connectome, min_synapses=5)
    assert graph.neuron_ids == ("1", "2", "3", "10")
    assert graph.matrix.shape == (4, 4)
    assert graph.matrix.toarray().tolist() == [
        [0.0, 5.0, 5.0, 0.0],
        [0.0, 7.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]
    assert graph.matrix[graph.node_index["2"], graph.node_index["2"]] == 7.0
    assert graph.matrix.nnz == 3
    assert graph.summary.neuron_count == 4
    assert graph.summary.edge_count == 3
    assert graph.summary.total_synapses == 17
    assert graph.summary.min_synapses == 5
    assert graph.summary.max_synapses == 7
    assert graph.summary.mean_out_degree == 0.75


def test_propagation_from_one_and_multiple_neurons():
    graph = SparseDirectedGraph.from_connectome(fixture_connectome())
    assert graph.propagate({"1": 2.0}) == {"2": 10.0, "3": 10.0}
    assert graph.propagate({"1": 1.0, "2": 2.0}) == {"2": 19.0, "3": 5.0}


def test_propagation_unknown_neuron_is_rejected():
    graph = SparseDirectedGraph.from_connectome(fixture_connectome())
    with pytest.raises(KeyError, match="unknown neuron"):
        graph.propagate({"missing": 1.0})


def test_summary_for_empty_graph_is_deterministic():
    connectome = normalize_connectome([{"neuron_id": "n1"}], [])
    graph = SparseDirectedGraph.from_connectome(connectome, min_synapses=5)
    assert graph.summary.neuron_count == 1
    assert graph.summary.edge_count == 0
    assert graph.summary.total_synapses == 0
    assert graph.summary.min_synapses is None
    assert graph.summary.mean_out_degree == 0.0


def test_csv_adapter_loads_local_tables_without_network(tmp_path):
    neuron_path = tmp_path / "neurons.csv"
    edge_path = tmp_path / "edges.csv"
    neuron_path.write_text(
        "body,type,nt\n1,sensory,glutamate\n2,motor,GABA\n", encoding="utf-8"
    )
    edge_path.write_text("src,dst,count\n1,2,6\n", encoding="utf-8")
    connectome = load_connectome(
        neuron_path,
        edge_path,
        neuron_columns=NeuronColumns(
            neuron_id="body", cell_type="type", neurotransmitter="nt"
        ),
        edge_columns=EdgeColumns(source_id="src", target_id="dst", synapse_count="count"),
    )
    assert connectome.neuron_ids == ("1", "2")
    assert connectome.edges[0].synapse_count == 6
    assert ("adapter", "explicit-csv-tsv-columns") in connectome.provenance
