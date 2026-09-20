"""Measured baseline graph construction and propagation timings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter

from malecns_sim.data.model import NormalizedConnectome
from malecns_sim.graph.sparse import SparseDirectedGraph


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    neuron_count: int
    edge_count: int
    filtered_edge_count: int
    min_synapses: int
    graph_construction_seconds_measured: float
    full_sparse_storage_bytes_measured: int
    filtered_sparse_storage_bytes_measured: int
    propagation_seconds_measured: float
    propagation_output_count: int

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


def benchmark_connectome(
    connectome: NormalizedConnectome, *, min_synapses: int = 5
) -> BenchmarkResult:
    start = perf_counter()
    full_graph = SparseDirectedGraph.from_connectome(connectome)
    filtered_graph = SparseDirectedGraph.from_connectome(
        connectome, min_synapses=min_synapses
    )
    construction_seconds = perf_counter() - start
    if connectome.neuron_ids:
        workload = {connectome.neuron_ids[0]: 1.0}
    else:
        workload = {}
    start = perf_counter()
    output = filtered_graph.propagate(workload)
    propagation_seconds = perf_counter() - start
    return BenchmarkResult(
        neuron_count=len(connectome.neurons),
        edge_count=full_graph.summary.edge_count,
        filtered_edge_count=filtered_graph.summary.edge_count,
        min_synapses=min_synapses,
        graph_construction_seconds_measured=construction_seconds,
        full_sparse_storage_bytes_measured=full_graph.sparse_storage_bytes,
        filtered_sparse_storage_bytes_measured=filtered_graph.sparse_storage_bytes,
        propagation_seconds_measured=propagation_seconds,
        propagation_output_count=len(output),
    )
