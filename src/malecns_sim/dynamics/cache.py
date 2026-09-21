"""Compact, fail-closed persistence for immutable prepared LIF graphs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from malecns_sim.dynamics.lif import EffectiveSignedProjection


PREPARED_CACHE_SCHEMA_VERSION = "malecns-sim-prepared-graph-cache-v1"


@dataclass(frozen=True, slots=True)
class PreparedCacheIdentity:
    """All external and simulation inputs that define a prepared graph cache."""

    male_cns_release_identity: str
    curated_graph_fingerprint: str
    sign_policy_fingerprint: str
    unresolved_edge_policy: str
    min_synapses: int
    synaptic_weight_mV: float
    lif_parameter_identity: str
    schema_version: str = PREPARED_CACHE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.male_cns_release_identity:
            raise ValueError("male_cns_release_identity must not be empty")
        if not self.curated_graph_fingerprint:
            raise ValueError("curated_graph_fingerprint must not be empty")
        if not self.sign_policy_fingerprint:
            raise ValueError("sign_policy_fingerprint must not be empty")
        if isinstance(self.min_synapses, bool) or self.min_synapses < 0:
            raise ValueError("min_synapses must be a non-negative integer")
        if not np.isfinite(self.synaptic_weight_mV) or self.synaptic_weight_mV < 0.0:
            raise ValueError("synaptic_weight_mV must be finite and non-negative")

    def as_dict(self) -> dict[str, object]:
        return {
            "male_cns_release_identity": self.male_cns_release_identity,
            "curated_graph_fingerprint": self.curated_graph_fingerprint,
            "sign_policy_fingerprint": self.sign_policy_fingerprint,
            "unresolved_edge_policy": self.unresolved_edge_policy,
            "min_synapses": self.min_synapses,
            "synaptic_weight_mV": self.synaptic_weight_mV,
            "lif_parameter_identity": self.lif_parameter_identity,
            "schema_version": self.schema_version,
        }

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(b"malecns-sim-prepared-cache-identity-v1\0" + payload).hexdigest()


@dataclass(frozen=True, slots=True)
class PreparedGraphCache:
    """Immutable CSR state that can be rehydrated into a Task 005 projection."""

    identity: PreparedCacheIdentity
    neuron_ids: np.ndarray
    indptr: np.ndarray
    indices: np.ndarray
    weights_mV: np.ndarray
    projection_fingerprint: str
    included_anatomical_weight: int
    excluded_anatomical_weight: int
    excluded_unresolved_edge_count: int

    def __post_init__(self) -> None:
        arrays = (self.neuron_ids, self.indptr, self.indices, self.weights_mV)
        if self.neuron_ids.ndim != 1 or self.indptr.ndim != 1 or self.indices.ndim != 1 or self.weights_mV.ndim != 1:
            raise ValueError("prepared cache arrays must be one-dimensional")
        if self.indptr.size != self.neuron_ids.size + 1:
            raise ValueError("prepared cache indptr has the wrong length")
        if self.indices.size != self.weights_mV.size or self.indptr[-1] != self.indices.size:
            raise ValueError("prepared cache CSR arrays are inconsistent")
        if self.indptr[0] != 0 or np.any(self.indptr[1:] < self.indptr[:-1]):
            raise ValueError("prepared cache indptr must be monotonic from zero")
        if self.indices.size and np.any((self.indices < 0) | (self.indices >= self.neuron_ids.size)):
            raise ValueError("prepared cache indices are out of range")
        if self.neuron_ids.size > 1 and np.any(self.neuron_ids[1:] <= self.neuron_ids[:-1]):
            raise ValueError("prepared cache neuron IDs must be strictly ascending")
        if not np.all(np.isfinite(self.weights_mV)):
            raise ValueError("prepared cache weights must be finite")
        for array in arrays:
            array.flags.writeable = False

    @classmethod
    def from_projection(
        cls,
        projection: EffectiveSignedProjection,
        *,
        male_cns_release_identity: str,
        min_synapses: int,
    ) -> "PreparedGraphCache":
        identity = PreparedCacheIdentity(
            male_cns_release_identity=male_cns_release_identity,
            curated_graph_fingerprint=projection.unsigned_graph_fingerprint,
            sign_policy_fingerprint=projection.signed_policy_fingerprint,
            unresolved_edge_policy=projection.resolution_policy_id,
            min_synapses=min_synapses,
            synaptic_weight_mV=projection.synaptic_weight_mV,
            lif_parameter_identity="shiu-reference-lif-parameters-v1",
        )
        return cls(
            identity=identity,
            neuron_ids=np.asarray(projection.neuron_ids, dtype=np.int64).copy(),
            indptr=np.asarray(projection.outgoing_indptr, dtype=np.int64).copy(),
            indices=np.asarray(projection.outgoing_targets, dtype=np.int64).copy(),
            weights_mV=np.asarray(projection.outgoing_weights_mV, dtype=np.float64).copy(),
            projection_fingerprint=projection.fingerprint,
            included_anatomical_weight=projection.included_anatomical_weight,
            excluded_anatomical_weight=projection.excluded_anatomical_weight,
            excluded_unresolved_edge_count=projection.excluded_unresolved_edge_count,
        )

    @property
    def cache_fingerprint(self) -> str:
        digest = hashlib.sha256()
        digest.update(self.identity.fingerprint.encode("ascii"))
        digest.update(self.projection_fingerprint.encode("ascii"))
        for array in (self.neuron_ids, self.indptr, self.indices, self.weights_mV):
            digest.update(str(array.dtype).encode("ascii"))
            digest.update(array.tobytes(order="C"))
        return digest.hexdigest()

    def to_projection(self) -> EffectiveSignedProjection:
        """Rehydrate only immutable graph state; all trial state remains fresh."""

        source_positions = np.repeat(
            np.arange(self.neuron_ids.size, dtype=np.int64),
            np.diff(self.indptr),
        )
        target_positions = self.indices.copy()
        effective_weights = self.weights_mV.copy()
        for array in (source_positions, target_positions, effective_weights):
            array.flags.writeable = False
        return EffectiveSignedProjection(
            neuron_ids=self.neuron_ids.copy(),
            source_positions=source_positions,
            target_positions=target_positions,
            effective_weights_mV=effective_weights,
            included_anatomical_weight=self.included_anatomical_weight,
            excluded_anatomical_weight=self.excluded_anatomical_weight,
            excluded_unresolved_edge_count=self.excluded_unresolved_edge_count,
            synaptic_weight_mV=self.identity.synaptic_weight_mV,
            sign_policy_id="cached",
            resolution_policy_id=self.identity.unresolved_edge_policy,
            unsigned_graph_fingerprint=self.identity.curated_graph_fingerprint,
            signed_policy_fingerprint=self.identity.sign_policy_fingerprint,
            fingerprint=self.projection_fingerprint,
            outgoing_indptr=self.indptr.copy(),
            outgoing_targets=self.indices.copy(),
            outgoing_weights_mV=self.weights_mV.copy(),
        )

    def save(self, path: str | Path) -> Path:
        """Write a compact binary NPZ without permitting implicit path changes."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "identity": self.identity.as_dict(),
            "projection_fingerprint": self.projection_fingerprint,
            "included_anatomical_weight": self.included_anatomical_weight,
            "excluded_anatomical_weight": self.excluded_anatomical_weight,
            "excluded_unresolved_edge_count": self.excluded_unresolved_edge_count,
            "cache_fingerprint": self.cache_fingerprint,
        }
        with target.open("wb") as handle:
            np.savez_compressed(
                handle,
                metadata=np.asarray(json.dumps(metadata, sort_keys=True, separators=(",", ":"))),
                neuron_ids=self.neuron_ids,
                indptr=self.indptr,
                indices=self.indices,
                weights_mV=self.weights_mV,
            )
        return target

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        expected_identity: PreparedCacheIdentity | None = None,
    ) -> "PreparedGraphCache":
        """Load and validate every identity field before exposing arrays."""

        with np.load(Path(path), allow_pickle=False) as archive:
            try:
                metadata = json.loads(str(archive["metadata"].item()))
                identity = PreparedCacheIdentity(**metadata["identity"])
                cache = cls(
                    identity=identity,
                    neuron_ids=np.asarray(archive["neuron_ids"], dtype=np.int64),
                    indptr=np.asarray(archive["indptr"], dtype=np.int64),
                    indices=np.asarray(archive["indices"], dtype=np.int64),
                    weights_mV=np.asarray(archive["weights_mV"], dtype=np.float64),
                    projection_fingerprint=str(metadata["projection_fingerprint"]),
                    included_anatomical_weight=int(metadata["included_anatomical_weight"]),
                    excluded_anatomical_weight=int(metadata["excluded_anatomical_weight"]),
                    excluded_unresolved_edge_count=int(metadata["excluded_unresolved_edge_count"]),
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError("invalid prepared graph cache") from exc
            if metadata.get("cache_fingerprint") != cache.cache_fingerprint:
                raise ValueError("prepared graph cache fingerprint mismatch")
        if expected_identity is not None and cache.identity != expected_identity:
            raise ValueError("prepared graph cache identity mismatch")
        return cache


def write_prepared_cache(
    path: str | Path,
    projection: EffectiveSignedProjection,
    *,
    male_cns_release_identity: str,
    min_synapses: int,
) -> PreparedGraphCache:
    """Build and persist a cache, returning the immutable in-memory form."""

    cache = PreparedGraphCache.from_projection(
        projection,
        male_cns_release_identity=male_cns_release_identity,
        min_synapses=min_synapses,
    )
    cache.save(path)
    return cache
