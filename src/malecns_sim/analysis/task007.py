"""Deterministic Task 007 identity mapping over validated local artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather

from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence,
    NeurotransmitterResolutionPolicy,
)
from malecns_sim.data.shiu_v630 import MN9_FLYWIRE_ID, SHIU_SUGAR_NEURON_IDS
from malecns_sim.homology import (
    MaleCNSCandidate,
    MappingRecord,
    MappingStatus,
    MN9Readout,
    StructuralPathSummary,
    SugarPopulation,
    define_mn9_readout,
    derive_sugar_population,
    mapping_fingerprint,
    population_fingerprint,
)
from malecns_sim.sign import Shiu2024SignPolicy


TASK007_REFERENCE_PATH = Path("data/provenance/task007-flywire-evidence.json")
MALE_CNS_ANNOTATION_COLUMNS = (
    "bodyId",
    "flywireType",
    "type",
    "supertype",
    "mancType",
    "mancBodyid",
    "receptorType",
    "entryNerve",
    "somaSide",
    "somaNeuromere",
    "dimorphism",
    "matchingNotes",
    "superclass",
    "subclass",
    "class",
    "exitNerve",
    "status",
    "rootSide",
)
NT_COLUMNS = (
    "body",
    "consensus_nt",
    "predicted_nt",
    "celltype_predicted_nt",
    "predicted_nt_confidence",
    "celltype_predicted_nt_confidence",
)


def _clean(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    text = str(value).strip()
    return text or None


def _clean_float(value: object) -> float | None:
    if value is None:
        return None
    result = float(value)
    return result if np.isfinite(result) else None


def reference_ids() -> tuple[str, ...]:
    return tuple(str(value) for value in SHIU_SUGAR_NEURON_IDS) + (str(MN9_FLYWIRE_ID),)


def reference_population_fingerprint(evidence: dict[str, Any]) -> str:
    source = evidence["reference_source"]
    payload = {
        "repository": source["repository"],
        "commit": source["commit"],
        "notebook": source["notebook"],
        "materialization": source["materialization"],
        "sugar_ids": list(reference_ids()[:-1]),
        "mn9_id": reference_ids()[-1],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007-reference-v1\0" + encoded).hexdigest()


def load_task007_evidence(path: str | Path = TASK007_REFERENCE_PATH) -> dict[str, Any]:
    evidence = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = evidence.get("version_matched_annotations", [])
    row_ids = tuple(str(row["root_id"]) for row in rows)
    if row_ids != reference_ids():
        raise ValueError("Task 007 evidence does not preserve the ordered 22-ID reference set")
    typed = evidence["later_type_evidence"]["typed_root_ids"]
    if set(typed) - set(reference_ids()):
        raise ValueError("later typed evidence contains an out-of-scope root ID")
    expected = reference_population_fingerprint(evidence)
    stored = evidence.get("reference_population_fingerprint")
    if stored is not None and stored != expected:
        raise ValueError("Task 007 reference fingerprint does not match its pinned IDs")
    evidence["reference_population_fingerprint"] = expected
    return evidence


def _candidate_from_rows(row: dict[str, Any], nt_row: dict[str, Any]) -> MaleCNSCandidate:
    evidence = NeurotransmitterEvidence(
        neuron_id=int(row["bodyId"]),
        consensus_nt=_clean(nt_row.get("consensus_nt")),
        predicted_nt=_clean(nt_row.get("predicted_nt")),
        celltype_predicted_nt=_clean(nt_row.get("celltype_predicted_nt")),
        predicted_nt_confidence=_clean_float(nt_row.get("predicted_nt_confidence")),
        celltype_predicted_nt_confidence=_clean_float(nt_row.get("celltype_predicted_nt_confidence")),
        superclass=_clean(row.get("superclass")),
    )
    resolved = NeurotransmitterResolutionPolicy().resolve(evidence)
    sign = Shiu2024SignPolicy().sign_for(resolved)
    return MaleCNSCandidate(
        body_id=str(int(row["bodyId"])),
        type=_clean(row.get("type")),
        instance=_clean(row.get("instance")),
        flywire_type=_clean(row.get("flywireType")),
        side=_clean(row.get("rootSide")) or _clean(row.get("somaSide")),
        soma_side=_clean(row.get("somaSide")),
        root_side=_clean(row.get("rootSide")),
        superclass=_clean(row.get("superclass")),
        subclass=_clean(row.get("subclass")),
        cell_class=_clean(row.get("class")),
        supertype=_clean(row.get("supertype")),
        receptor_type=_clean(row.get("receptorType")),
        entry_nerve=_clean(row.get("entryNerve")),
        soma_neuromere=_clean(row.get("somaNeuromere")),
        dimorphism=_clean(row.get("dimorphism")),
        matching_notes=_clean(row.get("matchingNotes")),
        manc_type=_clean(row.get("mancType")),
        manc_body_id=(str(int(row["mancBodyid"])) if _clean(row.get("mancBodyid")) else None),
        exit_nerve=_clean(row.get("exitNerve")),
        consensus_nt=_clean(nt_row.get("consensus_nt")),
        resolved_nt=resolved.identity,
        nt_source_field=resolved.source_field,
        nt_source_confidence=resolved.source_confidence,
        task004_sign=sign.sign,
    )


def load_male_cns_candidates(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
) -> tuple[MaleCNSCandidate, ...]:
    """Load only the annotation and NT rows needed by Task 007."""

    annotations = feather.read_table(annotation_path, columns=list(MALE_CNS_ANNOTATION_COLUMNS)).to_pylist()
    nt_rows = feather.read_table(neurotransmitter_path, columns=list(NT_COLUMNS)).to_pylist()
    nt_by_body = {int(row["body"]): row for row in nt_rows}
    result = tuple(
        _candidate_from_rows(row, nt_by_body.get(int(row["bodyId"]), {}))
        for row in annotations
        if _clean(row.get("flywireType")) in {"LB3", "CB0701"}
    )
    if len({item.body_id for item in result}) != len(result):
        raise ValueError("MaleCNS annotation file contains duplicate candidate body IDs")
    return tuple(sorted(result, key=lambda item: int(item.body_id)))


def build_mapping_records(
    evidence: dict[str, Any],
    candidates: Iterable[MaleCNSCandidate],
    *,
    male_cns_release: str = "v1.0",
) -> tuple[MappingRecord, ...]:
    candidate_rows = tuple(candidates)
    by_type: dict[str, tuple[MaleCNSCandidate, ...]] = {}
    for flywire_type in {item.flywire_type for item in candidate_rows if item.flywire_type}:
        by_type[flywire_type] = tuple(
            item for item in candidate_rows if item.flywire_type == flywire_type
        )
    later = evidence["later_type_evidence"]["typed_root_ids"]
    records = []
    for order, row in enumerate(evidence["version_matched_annotations"]):
        root_id = str(row["root_id"])
        flywire_type = later.get(root_id)
        selected = by_type.get(flywire_type, ()) if flywire_type else ()
        status = MappingStatus.TYPE_LEVEL if selected else MappingStatus.UNRESOLVED
        notes = [
            "Version-matched v1.0.0 annotation row is retained independently of later typing.",
            "No updated root was substituted because public lineage was not queried.",
        ]
        if root_id in evidence["later_type_evidence"]["absent_v3_root_ids"]:
            notes.append("Historical root is absent from the later v3.0.0 table; no updated root is claimed.")
        if flywire_type:
            notes.append(f"Later v3.0.0 overlap reports FlyWire type {flywire_type}.")
        if root_id in SHIU_SUGAR_NEURON_IDS and row.get("side") == "left":
            notes.append("Versioned annotation side is left although the Shiu experiment labels this input set right-side; side conventions are not normalized here.")
        sources = (
            "philshiu/Drosophila_brain_model@91bdd1e7dcf193f3e7ca5a8933497fcef63b7960",
            "flyconnectome/flywire_annotations@v1.0.0",
            "flyconnectome/flywire_annotations@v3.0.0" if flywire_type else "flyconnectome/flywire_annotations@v3.0.0 absence check",
            "MaleCNS v1.0 body annotations and neurotransmitter evidence",
        )
        records.append(
            MappingRecord(
                reference_order=order,
                reference_role=row["role"],
                shiu_v630_root_id=root_id,
                flywire_materialization="630",
                flywire_annotation_release="v1.0.0; later overlap v3.0.0" if flywire_type else "v1.0.0; later absence v3.0.0",
                flywire_type=flywire_type,
                updated_root_ids=(),
                lineage_method=evidence["lineage_method"]["status"],
                male_cns_release=male_cns_release,
                candidates=selected,
                status=status,
                evidence_sources=sources,
                evidence_notes=tuple(notes),
            )
        )
    return tuple(records)


@dataclass(frozen=True, slots=True)
class Task007Result:
    reference_fingerprint: str
    records: tuple[MappingRecord, ...]
    mapping_fingerprint: str
    sugar_population: SugarPopulation
    sugar_population_fingerprint: str
    mn9_readout: MN9Readout
    structural_summary: StructuralPathSummary | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_fingerprint": self.reference_fingerprint,
            "records": [
                {
                    **{key: value for key, value in asdict(record).items() if key != "status"},
                    "status": record.status.value,
                }
                for record in self.records
            ],
            "mapping_fingerprint": self.mapping_fingerprint,
            "sugar_population": asdict(self.sugar_population),
            "sugar_population_fingerprint": self.sugar_population_fingerprint,
            "mn9_readout": asdict(self.mn9_readout),
            "structural_summary": asdict(self.structural_summary) if self.structural_summary else None,
        }


def build_task007_result(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    *,
    weights_path: str | Path | None = None,
    evidence_path: str | Path = TASK007_REFERENCE_PATH,
    task007b_path: str | Path | None = "data/provenance/task007b-mn9-laterality-evidence.json",
) -> Task007Result:
    evidence = load_task007_evidence(evidence_path)
    candidates = load_male_cns_candidates(annotation_path, neurotransmitter_path)
    records = build_mapping_records(evidence, candidates)
    sugar_candidates = tuple(item for item in candidates if item.flywire_type == "LB3")
    population = derive_sugar_population(sugar_candidates, side="R")
    mn9_record = next(record for record in records if record.reference_role == "mn9")
    if task007b_path is not None:
        from malecns_sim.analysis.task007b import (
            apply_mn9_laterality,
            load_task007b_provenance,
            resolve_task007b_provenance,
        )

        task007b_evidence = load_task007b_provenance(task007b_path)
        task007b_resolution = resolve_task007b_provenance(task007b_evidence, mn9_record.candidates)
        if task007b_resolution.status is MappingStatus.SIDE_RESOLVED:
            mn9_record = apply_mn9_laterality(mn9_record, task007b_resolution)
    readout = define_mn9_readout(mn9_record)
    result = Task007Result(
        reference_fingerprint=reference_population_fingerprint(evidence),
        records=records,
        mapping_fingerprint=mapping_fingerprint(records),
        sugar_population=population,
        sugar_population_fingerprint=population_fingerprint(population),
        mn9_readout=readout,
    )
    if weights_path is not None:
        result = Task007Result(
            reference_fingerprint=result.reference_fingerprint,
            records=result.records,
            mapping_fingerprint=result.mapping_fingerprint,
            sugar_population=result.sugar_population,
            sugar_population_fingerprint=result.sugar_population_fingerprint,
            mn9_readout=result.mn9_readout,
            structural_summary=structural_sanity_from_feather(
                annotation_path,
                weights_path,
                result.sugar_population.candidate_body_ids,
                result.mn9_readout.candidate_body_ids,
            ),
        )
    return result


def _stream_edges_for_sources(
    weights_path: str | Path,
    source_ids: Iterable[str],
    *,
    curated_ids: np.ndarray,
    mn9_ids: np.ndarray,
) -> tuple[np.ndarray, int]:
    reader = pa.ipc.open_file(weights_path)
    sources = np.asarray(sorted({int(value) for value in source_ids}), dtype=np.int64)
    selected_targets: list[np.ndarray] = []
    mn9_edge_count = 0
    for index in range(reader.num_record_batches):
        batch = reader.get_batch(index)
        presynaptic = np.asarray(batch.column(0))
        postsynaptic = np.asarray(batch.column(1))
        mask = np.isin(presynaptic, sources)
        if not mask.any():
            continue
        targets = postsynaptic[mask]
        targets = targets[np.isin(targets, curated_ids)]
        if targets.size:
            selected_targets.append(targets.astype(np.int64, copy=False))
            mn9_edge_count += int(np.isin(targets, mn9_ids).sum())
    if not selected_targets:
        return np.asarray([], dtype=np.int64), 0
    return np.unique(np.concatenate(selected_targets)), mn9_edge_count


def structural_sanity_from_feather(
    annotation_path: str | Path,
    weights_path: str | Path,
    sugar_ids: Iterable[str],
    mn9_ids: Iterable[str],
) -> StructuralPathSummary:
    """Run the non-dynamic two-hop curated-graph sanity check."""

    annotation = feather.read_table(annotation_path, columns=["bodyId", "superclass"]).to_pylist()
    curated = np.asarray(
        sorted(int(row["bodyId"]) for row in annotation if _clean(row.get("superclass"))),
        dtype=np.int64,
    )
    sugar = tuple(str(value) for value in sugar_ids)
    mn9 = tuple(str(value) for value in mn9_ids)
    mn9_array = np.asarray(sorted({int(value) for value in mn9}), dtype=np.int64)
    first_hop, direct = _stream_edges_for_sources(
        weights_path, sugar, curated_ids=curated, mn9_ids=mn9_array
    )
    second_hop, second_edges = _stream_edges_for_sources(
        weights_path, (str(value) for value in first_hop), curated_ids=curated, mn9_ids=mn9_array
    )
    hits = sorted(set(map(int, second_hop)).intersection(map(int, mn9_array)))
    distances = tuple((str(value), 2) for value in hits)
    first_payload = "\n".join(str(value) for value in first_hop).encode("ascii")
    first_fingerprint = hashlib.sha256(
        b"malecns-sim-task007-id-set-v1\0" + first_payload
    ).hexdigest()
    return StructuralPathSummary(
        direct_sugar_to_mn9_edges=direct,
        first_hop_target_count=int(first_hop.size),
        shortest_path_lengths=distances,
        reachable_mn9_candidate_ids=tuple(str(value) for value in hits),
        total_structural_path_availability=len(hits),
        first_hop_target_fingerprint=first_fingerprint,
    )
