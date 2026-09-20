"""CSR graph specifically shaped for the Task 001 connectome baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from scipy.sparse import csr_matrix

from malecns_sim.data.model import (
    CuratedNeuronProjection,
    NormalizedConnectome,
    NumericNormalizedConnectome,
)


@dataclass(frozen=True, slots=True)
class GraphSummary:
    neuron_count: int
    edge_count: int
    total_synapses: int
    min_synapses: int | None
    max_synapses: int | None
    mean_out_degree: float


@dataclass(frozen=True, slots=True)
class SparseDirectedGraph:
    """Deterministic source-row/target-column CSR connectivity graph."""

    neuron_ids: tuple[str, ...] | np.ndarray
    matrix: csr_matrix
    min_synapses: int

    @classmethod
    def from_connectome(
        cls, connectome: NormalizedConnectome, *, min_synapses: int = 0
    ) -> "SparseDirectedGraph":
        if isinstance(min_synapses, bool) or not isinstance(min_synapses, int):
            raise TypeError("min_synapses must be an integer")
        if min_synapses < 0:
            raise ValueError("min_synapses must be a non-negative integer")
        neuron_ids = connectome.neuron_ids
        index = {neuron_id: position for position, neuron_id in enumerate(neuron_ids)}
        selected = [edge for edge in connectome.edges if edge.synapse_count >= min_synapses]
        rows = np.fromiter((index[edge.source_id] for edge in selected), dtype=np.int64)
        cols = np.fromiter((index[edge.target_id] for edge in selected), dtype=np.int64)
        values = np.fromiter((edge.synapse_count for edge in selected), dtype=np.float64)
        matrix = csr_matrix((values, (rows, cols)), shape=(len(neuron_ids), len(neuron_ids)))
        matrix.sort_indices()
        return cls(neuron_ids, matrix, min_synapses)

    @classmethod
    def from_numeric_connectome(
        cls, connectome: NumericNormalizedConnectome, *, min_synapses: int = 0
    ) -> "SparseDirectedGraph":
        if isinstance(min_synapses, bool) or not isinstance(min_synapses, int):
            raise TypeError("min_synapses must be an integer")
        if min_synapses < 0:
            raise ValueError("min_synapses must be a non-negative integer")
        selected = connectome.synapse_counts >= min_synapses
        rows = np.searchsorted(connectome.neuron_ids, connectome.source_ids[selected])
        cols = np.searchsorted(connectome.neuron_ids, connectome.target_ids[selected])
        values = connectome.synapse_counts[selected].astype(np.float64, copy=False)
        matrix = csr_matrix(
            (values, (rows, cols)),
            shape=(connectome.neuron_count, connectome.neuron_count),
        )
        matrix.sort_indices()
        return cls(connectome.neuron_ids, matrix, min_synapses)

    @classmethod
    def from_curated_projection(
        cls, projection: CuratedNeuronProjection
    ) -> "SparseDirectedGraph":
        """Build a CSR graph whose dimension is the curated neuron set."""

        return cls.from_numeric_connectome(
            projection.connectome, min_synapses=projection.threshold
        )

    @property
    def node_index(self) -> dict[str, int]:
        if isinstance(self.neuron_ids, np.ndarray):
            return {str(neuron_id): index for index, neuron_id in enumerate(self.neuron_ids)}
        return {neuron_id: index for index, neuron_id in enumerate(self.neuron_ids)}

    @property
    def summary(self) -> GraphSummary:
        values = self.matrix.data
        return GraphSummary(
            neuron_count=len(self.neuron_ids),
            edge_count=int(self.matrix.nnz),
            total_synapses=int(values.sum()) if values.size else 0,
            min_synapses=int(values.min()) if values.size else None,
            max_synapses=int(values.max()) if values.size else None,
            mean_out_degree=float(self.matrix.getnnz(axis=1).mean())
            if len(self.neuron_ids)
            else 0.0,
        )

    @property
    def sparse_storage_bytes(self) -> int:
        """Bytes in CSR arrays; excludes Python/allocator overhead."""

        return int(self.matrix.data.nbytes + self.matrix.indices.nbytes + self.matrix.indptr.nbytes)

    def propagate(self, activations: Mapping[str, float]) -> dict[str, float]:
        """Perform one scalar outgoing-edge propagation step.

        This is a graph propagation primitive, not a neural model. Every input
        ID must be known; output keys are returned in deterministic neuron order.
        """

        index = None if isinstance(self.neuron_ids, np.ndarray) else self.node_index
        source_values = np.zeros(len(self.neuron_ids), dtype=np.float64)
        if isinstance(self.neuron_ids, np.ndarray):
            numeric_ids = np.asarray([int(neuron_id) for neuron_id in activations], dtype=np.int64)
            positions = np.searchsorted(self.neuron_ids, numeric_ids)
            unknown = [
                int(neuron_id)
                for neuron_id, position in zip(numeric_ids, positions)
                if position >= len(self.neuron_ids) or self.neuron_ids[position] != neuron_id
            ]
            if unknown:
                raise KeyError(f"unknown neuron ID(s): {unknown!r}")
            for position, value in zip(positions, activations.values()):
                source_values[position] = float(value)
        else:
            unknown = sorted(set(activations) - set(index))
            if unknown:
                raise KeyError(f"unknown neuron ID(s): {unknown!r}")
            for neuron_id, value in activations.items():
                source_values[index[neuron_id]] = float(value)
        target_values = self.matrix.T.dot(source_values)
        return {
            (int(neuron_id) if isinstance(self.neuron_ids, np.ndarray) else neuron_id): float(target_values[position])
            for position, neuron_id in enumerate(self.neuron_ids)
            if target_values[position] != 0.0
        }
