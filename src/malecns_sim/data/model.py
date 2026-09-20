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
