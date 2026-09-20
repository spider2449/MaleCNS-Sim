"""Derived signed anatomical connectivity; the unsigned graph remains intact."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence,
    NeurotransmitterResolutionPolicy,
    ResolvedNeurotransmitter,
)
from malecns_sim.graph.fingerprint import graph_fingerprint
from malecns_sim.graph.sparse import SparseDirectedGraph
from malecns_sim.sign import NeurotransmitterSignPolicy, SignResult

UNRESOLVED_SIGN = np.int8(2)


@dataclass(frozen=True, slots=True)
class SignedCoverage:
    neuron_count: int
    resolved_transmitter_neurons: int
    assigned_sign_neurons: int
    unresolved_neurons: int
    edge_count: int
    signed_outgoing_edges: int
    unresolved_outgoing_edges: int
    anatomical_weight: int
    signed_anatomical_weight: int
    unresolved_anatomical_weight: int
    signed_anatomical_weight_fraction: float
    excitatory_edge_count: int
    excitatory_weight: int
    inhibitory_edge_count: int
    inhibitory_weight: int
    neutral_edge_count: int
    neutral_weight: int


@dataclass(frozen=True, slots=True)
class SignedAnatomicalConnectome:
    """An unsigned projection plus policy-derived per-presynaptic sign arrays."""

    connectome: NumericNormalizedConnectome
    resolved_neurotransmitters: tuple[ResolvedNeurotransmitter, ...]
    neuron_signs: tuple[SignResult, ...]
    resolution_policy_id: str
    sign_policy_id: str
    unsigned_graph_fingerprint: str
    presynaptic_signs: np.ndarray
    signed_counts: np.ndarray
    signed_edge_mask: np.ndarray

    @classmethod
    def from_projection(
        cls,
        projection: CuratedNeuronProjection,
        evidence: tuple[NeurotransmitterEvidence, ...] | list[NeurotransmitterEvidence],
        resolution_policy: NeurotransmitterResolutionPolicy,
        sign_policy: NeurotransmitterSignPolicy,
    ) -> "SignedAnatomicalConnectome":
        connectome = projection.connectome
        by_id = {str(item.neuron_id): item for item in evidence}
        resolved: list[ResolvedNeurotransmitter] = []
        signs: list[SignResult] = []
        for neuron_id in connectome.neuron_ids:
            item = by_id.get(str(int(neuron_id)))
            if item is None:
                item = NeurotransmitterEvidence(neuron_id=int(neuron_id))
            selected = resolution_policy.resolve(item)
            resolved.append(selected)
            signs.append(sign_policy.sign_for(selected))

        sign_by_id = {
            str(int(neuron_id)): result.sign
            for neuron_id, result in zip(connectome.neuron_ids, signs)
        }
        edge_signs = np.asarray(
            [
                sign_by_id[str(int(source))]
                if sign_by_id[str(int(source))] is not None
                else UNRESOLVED_SIGN
                for source in connectome.source_ids
            ],
            dtype=np.int8,
        )
        assigned = edge_signs != UNRESOLVED_SIGN
        signed_counts = np.zeros(connectome.edge_count, dtype=np.int64)
        signed_counts[assigned] = (
            connectome.synapse_counts[assigned] * edge_signs[assigned].astype(np.int64)
        )
        for array in (edge_signs, signed_counts, assigned):
            array.flags.writeable = False
        return cls(
            connectome=connectome,
            resolved_neurotransmitters=tuple(resolved),
            neuron_signs=tuple(signs),
            resolution_policy_id=resolution_policy.policy_id,
            sign_policy_id=sign_policy.policy_id,
            unsigned_graph_fingerprint=graph_fingerprint(
                SparseDirectedGraph.from_curated_projection(projection)
            ),
            presynaptic_signs=edge_signs,
            signed_counts=signed_counts,
            signed_edge_mask=assigned,
        )

    @property
    def anatomical_weights(self) -> np.ndarray:
        return self.connectome.synapse_counts

    @property
    def edge_count(self) -> int:
        return self.connectome.edge_count

    @property
    def resolved_transmitter_neuron_count(self) -> int:
        return sum(item.resolved for item in self.resolved_neurotransmitters)

    @property
    def assigned_sign_neuron_count(self) -> int:
        return sum(item.assigned for item in self.neuron_signs)

    def coverage(self) -> SignedCoverage:
        weights = self.anatomical_weights
        assigned = self.signed_edge_mask
        signs = self.presynaptic_signs
        total = int(weights.sum(dtype=np.int64))
        signed_weight = int(weights[assigned].sum(dtype=np.int64))
        unresolved_weight = total - signed_weight
        neutral = signs == 0
        excitatory = signs == 1
        inhibitory = signs == -1
        return SignedCoverage(
            neuron_count=len(self.connectome.neuron_ids),
            resolved_transmitter_neurons=self.resolved_transmitter_neuron_count,
            assigned_sign_neurons=self.assigned_sign_neuron_count,
            unresolved_neurons=len(self.connectome.neuron_ids) - self.assigned_sign_neuron_count,
            edge_count=self.edge_count,
            signed_outgoing_edges=int(assigned.sum()),
            unresolved_outgoing_edges=int((~assigned).sum()),
            anatomical_weight=total,
            signed_anatomical_weight=signed_weight,
            unresolved_anatomical_weight=unresolved_weight,
            signed_anatomical_weight_fraction=(signed_weight / total if total else 0.0),
            excitatory_edge_count=int(excitatory.sum()),
            excitatory_weight=int(weights[excitatory].sum(dtype=np.int64)),
            inhibitory_edge_count=int(inhibitory.sum()),
            inhibitory_weight=int(weights[inhibitory].sum(dtype=np.int64)),
            neutral_edge_count=int(neutral.sum()),
            neutral_weight=int(weights[neutral].sum(dtype=np.int64)),
        )

    def signed_count(self, edge_index: int) -> int | None:
        """Return a derived count, or ``None`` when the presynaptic sign is unresolved."""

        if not self.signed_edge_mask[edge_index]:
            return None
        return int(self.signed_counts[edge_index])


def signed_graph_fingerprint(graph: SignedAnatomicalConnectome) -> str:
    """Hash unsigned graph identity, evidence resolution, policy, and signs."""

    digest = hashlib.sha256()

    def add(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "little"))
        digest.update(value)

    add(b"malecns-sim-signed-connectome-v1")
    add(graph.unsigned_graph_fingerprint.encode("ascii"))
    add(graph.resolution_policy_id.encode("utf-8"))
    add(graph.sign_policy_id.encode("utf-8"))
    for array in (
        graph.connectome.neuron_ids,
        graph.connectome.source_ids,
        graph.connectome.target_ids,
        graph.connectome.synapse_counts,
        graph.presynaptic_signs,
        graph.signed_edge_mask,
    ):
        add(str(array.dtype).encode("ascii"))
        add(array.tobytes(order="C"))
    records = []
    for item, result in zip(graph.resolved_neurotransmitters, graph.neuron_signs):
        evidence = item.evidence
        records.append(
            {
                "id": str(evidence.neuron_id),
                "consensus": evidence.consensus_nt,
                "predicted": evidence.predicted_nt,
                "celltype": evidence.celltype_predicted_nt,
                "predicted_confidence": evidence.predicted_nt_confidence,
                "celltype_confidence": evidence.celltype_predicted_nt_confidence,
                "ground_truth": evidence.ground_truth,
                "superclass": evidence.superclass,
                "source_field": item.source_field,
                "source_label": item.source_label,
                "identity": item.identity,
                "source_confidence": item.source_confidence,
                "sign": result.sign,
            }
        )
    add(json.dumps(records, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    return digest.hexdigest()
