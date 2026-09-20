"""Small immutable records used after external data normalization."""

from dataclasses import dataclass


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
