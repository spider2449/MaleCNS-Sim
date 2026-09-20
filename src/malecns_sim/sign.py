"""Explicit neurotransmitter-to-model-sign policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from malecns_sim.data.neurotransmitter import ResolvedNeurotransmitter


@dataclass(frozen=True, slots=True)
class SignResult:
    """A model sign, where ``None`` is a deliberate unresolved result."""

    policy_id: str
    transmitter: str | None
    sign: int | None
    rationale: str

    @property
    def assigned(self) -> bool:
        return self.sign is not None


class NeurotransmitterSignPolicy:
    """Small policy interface; source adapters never assign signs."""

    policy_id = "abstract"

    def sign_for(self, resolved: ResolvedNeurotransmitter) -> SignResult:
        raise NotImplementedError


class _MappingSignPolicy(NeurotransmitterSignPolicy):
    mapping: Mapping[str, int] = {}
    rationale: Mapping[str, str] = {}

    def sign_for(self, resolved: ResolvedNeurotransmitter) -> SignResult:
        transmitter = resolved.identity
        sign = self.mapping.get(transmitter) if transmitter is not None else None
        if sign is None:
            reason = "unresolved transmitter or policy deliberately declines assignment"
        else:
            reason = self.rationale.get(transmitter, "explicit model-policy assignment")
        return SignResult(self.policy_id, transmitter, sign, reason)


class Shiu2024SignPolicy(_MappingSignPolicy):
    """Aggregate-label equivalent of the sign assumptions stated by Shiu et al."""

    policy_id = "Shiu2024SignPolicy"
    mapping = {
        "acetylcholine": 1,
        "gaba": -1,
        "glutamate": -1,
        "dopamine": 1,
        "octopamine": 1,
        "serotonin": 1,
    }
    rationale = {
        "acetylcholine": "non-GABA/glutamate neurons are excitatory under Shiu's exclusive-category assumption",
        "gaba": "Shiu explicitly treats GABAergic neurons as inhibitory",
        "glutamate": "Shiu explicitly treats glutamatergic neurons as inhibitory",
        "dopamine": "Shiu explicitly assigns dopaminergic neurons to excitatory",
        "octopamine": "Shiu explicitly assigns octopaminergic neurons to excitatory",
        "serotonin": "Shiu explicitly assigns serotonergic neurons to excitatory",
    }


class ConservativeSignPolicy(_MappingSignPolicy):
    """Assign only the least ambiguous fast-transmitter cases."""

    policy_id = "ConservativeSignPolicy"
    mapping = {"acetylcholine": 1, "gaba": -1}
    rationale = {
        "acetylcholine": "conservative fast-excitatory assignment",
        "gaba": "conservative fast-inhibitory assignment",
    }
