"""Narrow adapter for the original Shiu et al. FlyWire v630 inputs.

This module intentionally does not reuse the MaleCNS v1.0 curation or
neurotransmitter resolver.  The companion connectivity table already carries
the signed ``Excitatory x Connectivity`` value used by the published model.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from malecns_sim.dynamics.lif import EffectiveSignedProjection


SHIU_REPOSITORY_URL = "https://github.com/philshiu/Drosophila_brain_model"
SHIU_REFERENCE_COMMIT = "91bdd1e7dcf193f3e7ca5a8933497fcef63b7960"
SHIU_RAW_BASE_URL = (
    f"https://raw.githubusercontent.com/philshiu/Drosophila_brain_model/"
    f"{SHIU_REFERENCE_COMMIT}"
)
MN9_FLYWIRE_ID = 720575940660219265
SHIU_SYNAPTIC_WEIGHT_MV = 0.275

SHIU_SUGAR_NEURON_IDS = (
    720575940624963786,
    720575940630233916,
    720575940637568838,
    720575940638202345,
    720575940617000768,
    720575940630797113,
    720575940632889389,
    720575940621754367,
    720575940621502051,
    720575940640649691,
    720575940639332736,
    720575940616885538,
    720575940639198653,
    720575940620900446,
    720575940617937543,
    720575940632425919,
    720575940633143833,
    720575940612670570,
    720575940628853239,
    720575940629176663,
    720575940611875570,
)


class ShiuV630ReferenceError(ValueError):
    """Raised when the historical v630 reference cannot be admitted."""


@dataclass(frozen=True, slots=True)
class ShiuV630Schema:
    """Observed schema of the two original v630 model inputs."""

    completeness_id_column: str
    completeness_neuron_count: int
    connectivity_columns: tuple[str, ...]
    presynaptic_id_column: str = "Presynaptic_ID"
    postsynaptic_id_column: str = "Postsynaptic_ID"
    presynaptic_index_column: str = "Presynaptic_Index"
    postsynaptic_index_column: str = "Postsynaptic_Index"
    connectivity_count_column: str = "Connectivity"
    excitatory_column: str = "Excitatory"
    signed_connectivity_column: str = "Excitatory x Connectivity"


@dataclass(frozen=True, slots=True)
class ShiuV630Reference:
    """Compact, immutable v630 graph data in original neuron-index space."""

    neuron_ids: np.ndarray
    source_positions: np.ndarray
    target_positions: np.ndarray
    connectivity_counts: np.ndarray
    excitatory_signs: np.ndarray
    signed_connectivity_counts: np.ndarray
    schema: ShiuV630Schema

    def __post_init__(self) -> None:
        arrays = (
            self.neuron_ids,
            self.source_positions,
            self.target_positions,
            self.connectivity_counts,
            self.excitatory_signs,
            self.signed_connectivity_counts,
        )
        edge_arrays = arrays[1:]
        if any(array.ndim != 1 for array in arrays):
            raise ShiuV630ReferenceError("v630 arrays must be one-dimensional")
        if len({array.size for array in edge_arrays}) != 1:
            raise ShiuV630ReferenceError("v630 edge arrays have inconsistent lengths")
        if np.unique(self.neuron_ids).size != self.neuron_ids.size:
            raise ShiuV630ReferenceError("v630 completeness IDs must be unique")
        for array in arrays:
            array.flags.writeable = False

    @property
    def neuron_count(self) -> int:
        return int(self.neuron_ids.size)

    @property
    def edge_count(self) -> int:
        return int(self.source_positions.size)

    @property
    def graph_fingerprint(self) -> str:
        return _digest(
            b"malecns-sim-shiu-v630-unsigned-v1",
            self.neuron_ids,
            self.source_positions,
            self.target_positions,
            self.connectivity_counts,
        )

    @property
    def signed_graph_fingerprint(self) -> str:
        return _digest(
            b"malecns-sim-shiu-v630-signed-column-v1",
            self.graph_fingerprint.encode("ascii"),
            self.excitatory_signs,
            self.signed_connectivity_counts,
        )

    def positions_for_ids(self, neuron_ids: tuple[int, ...] | list[int]) -> np.ndarray:
        """Map FlyWire IDs through the exact completeness row ordering."""

        values = np.asarray(neuron_ids, dtype=np.int64)
        positions = np.searchsorted(self.neuron_ids, values)
        valid = positions < self.neuron_ids.size
        if np.any(~valid) or np.any(self.neuron_ids[positions[valid]] != values[valid]):
            missing = values[~valid].tolist()
            if np.any(valid):
                missing.extend(values[valid][self.neuron_ids[positions[valid]] != values[valid]].tolist())
            raise ShiuV630ReferenceError(f"reference neuron ID(s) missing from v630 completeness: {missing!r}")
        return positions.astype(np.int64, copy=False)


@dataclass(frozen=True, slots=True)
class ShiuV630NeuronSet:
    sugar_ids: tuple[int, ...]
    sugar_positions: np.ndarray
    mn9_id: int
    mn9_position: int

    def __post_init__(self) -> None:
        self.sugar_positions.flags.writeable = False


def _digest(prefix: bytes, *values: object) -> str:
    digest = hashlib.sha256()
    digest.update(prefix)
    for value in values:
        if isinstance(value, str):
            value = value.encode("utf-8")
        elif isinstance(value, (bytes, bytearray)):
            value = bytes(value)
        elif isinstance(value, np.ndarray):
            value = str(value.dtype).encode("ascii") + value.tobytes(order="C")
        else:
            value = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest.update(len(value).to_bytes(8, "little"))
        digest.update(value)
    return digest.hexdigest()


def _read_int_array(table: object, name: str) -> np.ndarray:
    column = table[name].combine_chunks().to_numpy(zero_copy_only=False)
    return np.asarray(column, dtype=np.int64)


def load_shiu_v630(
    completeness_path: str | Path,
    connectivity_path: str | Path,
) -> ShiuV630Reference:
    """Load and validate the original v630 index-based graph inputs."""

    completeness_path = Path(completeness_path)
    connectivity_path = Path(connectivity_path)
    completeness = pd.read_csv(completeness_path, index_col=0)
    try:
        neuron_ids = completeness.index.to_numpy(dtype=np.int64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ShiuV630ReferenceError("v630 completeness index is not integer FlyWire IDs") from exc
    if neuron_ids.size == 0 or np.any(neuron_ids < 0):
        raise ShiuV630ReferenceError("v630 completeness contains no valid neuron IDs")
    if np.any(neuron_ids[:-1] >= neuron_ids[1:]):
        raise ShiuV630ReferenceError("v630 completeness order must be unique and strictly ascending")

    schema = pq.read_schema(connectivity_path)
    columns = tuple(field.name for field in schema)
    required = (
        "Presynaptic_ID",
        "Postsynaptic_ID",
        "Presynaptic_Index",
        "Postsynaptic_Index",
        "Connectivity",
        "Excitatory",
        "Excitatory x Connectivity",
    )
    missing = [name for name in required if name not in columns]
    if missing:
        raise ShiuV630ReferenceError(f"v630 connectivity schema is missing columns: {missing!r}")
    table = pq.read_table(
        connectivity_path,
        columns=[
            "Presynaptic_Index",
            "Postsynaptic_Index",
            "Connectivity",
            "Excitatory",
            "Excitatory x Connectivity",
        ],
    )
    source_positions = _read_int_array(table, "Presynaptic_Index")
    target_positions = _read_int_array(table, "Postsynaptic_Index")
    connectivity_counts = _read_int_array(table, "Connectivity")
    excitatory_signs = _read_int_array(table, "Excitatory")
    signed_counts = _read_int_array(table, "Excitatory x Connectivity")
    if np.any((source_positions < 0) | (source_positions >= neuron_ids.size)):
        raise ShiuV630ReferenceError("v630 presynaptic indices exceed completeness ordering")
    if np.any((target_positions < 0) | (target_positions >= neuron_ids.size)):
        raise ShiuV630ReferenceError("v630 postsynaptic indices exceed completeness ordering")
    if np.any(connectivity_counts <= 0):
        raise ShiuV630ReferenceError("v630 connectivity counts must be positive")
    if not np.all(np.isin(excitatory_signs, (-1, 1))):
        raise ShiuV630ReferenceError("v630 Excitatory values must be -1 or +1")
    if not np.array_equal(signed_counts, excitatory_signs * connectivity_counts):
        raise ShiuV630ReferenceError(
            "v630 signed connectivity is not Excitatory x Connectivity"
        )
    return ShiuV630Reference(
        neuron_ids=neuron_ids,
        source_positions=source_positions,
        target_positions=target_positions,
        connectivity_counts=connectivity_counts,
        excitatory_signs=excitatory_signs,
        signed_connectivity_counts=signed_counts,
        schema=ShiuV630Schema(
            completeness_id_column="CSV index",
            completeness_neuron_count=int(neuron_ids.size),
            connectivity_columns=columns,
        ),
    )


def parse_sugar_ids_from_notebook(path: str | Path) -> tuple[int, ...]:
    """Extract the ordered ``neu_sugar`` literal from the official notebook."""

    notebook = json.loads(Path(path).read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    )
    match = re.search(r"\bneu_sugar\s*=\s*(\[[\s\S]*?\])", source)
    if match is None:
        raise ShiuV630ReferenceError("official notebook does not define neu_sugar")
    try:
        values = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError) as exc:
        raise ShiuV630ReferenceError("official neu_sugar value is not a literal list") from exc
    if not isinstance(values, list) or any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ShiuV630ReferenceError("official neu_sugar value is not an integer list")
    return tuple(values)


def verify_reference_neurons(
    reference: ShiuV630Reference,
    sugar_ids: tuple[int, ...] | list[int],
    *,
    mn9_id: int = MN9_FLYWIRE_ID,
) -> ShiuV630NeuronSet:
    """Fail closed unless the exact requested IDs exist in v630."""

    sugar_ids = tuple(int(value) for value in sugar_ids)
    if len(sugar_ids) != 21 or len(set(sugar_ids)) != 21:
        raise ShiuV630ReferenceError("the reference sugar set must contain 21 unique IDs")
    if sugar_ids != SHIU_SUGAR_NEURON_IDS:
        raise ShiuV630ReferenceError("sugar IDs differ from the official example order")
    sugar_positions = reference.positions_for_ids(sugar_ids)
    mn9_position = int(reference.positions_for_ids((int(mn9_id),))[0])
    return ShiuV630NeuronSet(sugar_ids, sugar_positions, int(mn9_id), mn9_position)


def prepare_shiu_v630_projection(
    reference: ShiuV630Reference,
    *,
    synaptic_weight_mV: float = SHIU_SYNAPTIC_WEIGHT_MV,
) -> EffectiveSignedProjection:
    """Prepare the original signed graph once for immutable trial reuse."""

    weight = float(synaptic_weight_mV)
    if not np.isfinite(weight) or weight < 0.0:
        raise ValueError("synaptic_weight_mV must be finite and non-negative")
    source = reference.source_positions.copy()
    target = reference.target_positions.copy()
    signed = reference.signed_connectivity_counts.astype(np.float64) * weight
    order = np.lexsort((target, source))
    source = source[order]
    target = target[order]
    signed = signed[order]
    indptr = np.zeros(reference.neuron_count + 1, dtype=np.int64)
    np.add.at(indptr, source + 1, 1)
    np.cumsum(indptr, out=indptr)
    outgoing_targets = target.copy()
    outgoing_weights = signed.copy()
    projection_digest = _digest(
        b"malecns-sim-shiu-v630-effective-projection-v1",
        reference.signed_graph_fingerprint.encode("ascii"),
        str(weight),
        reference.neuron_ids,
        source,
        target,
        signed,
        indptr,
    )
    arrays = (source, target, signed, indptr, outgoing_targets, outgoing_weights)
    for array in arrays:
        array.flags.writeable = False
    neuron_ids = reference.neuron_ids.copy()
    neuron_ids.flags.writeable = False
    return EffectiveSignedProjection(
        neuron_ids=neuron_ids,
        source_positions=source,
        target_positions=target,
        effective_weights_mV=signed,
        included_anatomical_weight=int(reference.connectivity_counts.sum(dtype=np.int64)),
        excluded_anatomical_weight=0,
        excluded_unresolved_edge_count=0,
        synaptic_weight_mV=weight,
        sign_policy_id="shiu-v630-original-signed-connectivity-v1",
        resolution_policy_id="shiu-v630-connectivity-column-v1",
        unsigned_graph_fingerprint=reference.graph_fingerprint,
        signed_policy_fingerprint=reference.signed_graph_fingerprint,
        fingerprint=projection_digest,
        outgoing_indptr=indptr,
        outgoing_targets=outgoing_targets,
        outgoing_weights_mV=outgoing_weights,
    )
