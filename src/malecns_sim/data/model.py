"""Small immutable records used after external data normalization."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class NeuronRecord:
    """A normalized neuron and metadata preserved from the source when present."""

    neuron_id: str
    cell_type: str | None = None
    neurotransmitter: str | None = None
    ascending: bool | None = None
    descending: bool | None = None
    sensory: bool | None = None
    motor_related: bool | None = None
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class EdgeRecord:
    """A normalized directed connection with an aggregated synapse count."""

    source_id: str
    target_id: str
    synapse_count: int


@dataclass(frozen=True, slots=True)
class NormalizedConnectome:
    """Deterministically ordered normalized input plus adapter provenance."""

    neurons: tuple[NeuronRecord, ...]
    edges: tuple[EdgeRecord, ...]
    provenance: tuple[tuple[str, str], ...] = ()

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(neuron.neuron_id for neuron in self.neurons)


@dataclass(frozen=True, slots=True)
class NumericNormalizedConnectome:
    """Compact normalized representation for large integer-ID connectomes.

    The Feather release contains tens of millions of segment IDs. Keeping each
    ID and edge as a Python object would add substantial avoidable overhead, so
    this representation keeps exact source integers in NumPy arrays while
    retaining normalized annotation records separately.
    """

    neuron_ids: np.ndarray
    source_ids: np.ndarray
    target_ids: np.ndarray
    synapse_counts: np.ndarray
    annotated_neurons: tuple[NeuronRecord, ...] = ()
    provenance: tuple[tuple[str, str], ...] = ()

    @property
    def neuron_count(self) -> int:
        return int(self.neuron_ids.size)

    @property
    def edge_count(self) -> int:
        return int(self.source_ids.size)


@dataclass(frozen=True, slots=True)
class CuratedNeuronSelection:
    """Publication-defined neuron identity selection and audit counts."""

    neuron_ids: np.ndarray
    annotation_count: int
    excluded_ids: np.ndarray
    exclusion_counts: tuple[tuple[str, int], ...]
    missing_status_count: int = 0
    glia_status_count: int = 0
    glia_retained_count: int = 0

    @property
    def retained_count(self) -> int:
        return int(self.neuron_ids.size)


@dataclass(frozen=True, slots=True)
class CuratedNeuronProjection:
    """Neuron-level projection of the normalized segment-level edge arrays."""

    connectome: NumericNormalizedConnectome
    raw_edge_count: int
    endpoint_edge_count: int
    projected_edge_count: int
    duplicate_pair_count: int
    threshold: int = 0

    @property
    def edge_count(self) -> int:
        return self.connectome.edge_count

    @property
    def endpoint_excluded_edge_count(self) -> int:
        return self.raw_edge_count - self.endpoint_edge_count

    @property
    def threshold_excluded_edge_count(self) -> int:
        return self.projected_edge_count - self.connectome.edge_count

    @property
    def retained_source_count(self) -> int:
        return int(np.unique(self.connectome.source_ids).size)

    @property
    def retained_target_count(self) -> int:
        return int(np.unique(self.connectome.target_ids).size)

    @property
    def participating_count(self) -> int:
        if self.connectome.edge_count == 0:
            return 0
        return int(
            np.unique(
                np.concatenate((self.connectome.source_ids, self.connectome.target_ids))
            ).size
        )

    @property
    def isolated_count(self) -> int:
        return self.connectome.neuron_count - self.participating_count

    @property
    def self_edge_count(self) -> int:
        return int(
            np.count_nonzero(self.connectome.source_ids == self.connectome.target_ids)
        )

    @property
    def total_synaptic_weight(self) -> int:
        return int(self.connectome.synapse_counts.sum(dtype=np.int64))

    @property
    def min_synaptic_weight(self) -> int | None:
        return (
            int(self.connectome.synapse_counts.min())
            if self.connectome.edge_count
            else None
        )

    @property
    def max_synaptic_weight(self) -> int | None:
        return (
            int(self.connectome.synapse_counts.max())
            if self.connectome.edge_count
            else None
        )
