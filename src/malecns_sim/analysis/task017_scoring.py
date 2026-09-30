"""Read-only Task 017 robustness scoring from a sealed checkpoint matrix."""

from __future__ import annotations

import gc
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace

from malecns_sim.analysis import task017
from malecns_sim.analysis.task008 import PreparedNetwork, load_task008_identities
from malecns_sim.analysis.task010 import (
    TASK008_FULL_CACHE_FINGERPRINT,
    TASK008_PREPARED_FINGERPRINT,
    load_frozen_candidate_manifest,
    summarize_condition,
)
from malecns_sim.analysis.task017_portability import CheckpointAudit, audit_checkpoint
from malecns_sim.dynamics import EffectiveSignedProjection
from malecns_sim.dynamics.cache import PreparedGraphCache


TASK016_FINGERPRINT = "2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6"
CHECKPOINT_FINGERPRINT = "8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63"
COMPLETE_MATRIX_DIGEST = "19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028"
COMPLETE_MATRIX_MANIFEST_SHA256 = "73c9e51ae06e7d924f80c75578536c6d1ce2b0cf5e2657041ddcfdf5a2262cd8"
RECOVERY_MANIFEST_SHA256 = "f65261013717d7cc7739cdfbdd4c6e4c002f0b22bc4edbba50ac1952d0810208"
SCORING_SCHEMA = "malecns-sim-task017-preregistered-robustness-scoring-v1"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(prefix: str, value: object) -> str:
    return hashlib.sha256(prefix.encode("utf-8") + b"\0" + _canonical_json(value)).hexdigest()


class _ReadOnlyCheckpoint:
    """Expose validated sidecars while rejecting every missing-unit request."""

    def __init__(self, root: Path, audit: CheckpointAudit):
        self._records = {}
        self._root = root
        for record in audit.records:
            key = task017.Task017UnitKey(**record["key"])
            self._records[key.token] = record
        self.read_count = 0

    def get(self, key: task017.Task017UnitKey, unit_fingerprint: str):
        self.read_count += 1
        if key.token not in self._records:
            raise RuntimeError(f"read-only scoring refused missing checkpoint unit: {key.token}")
        record = self._records[key.token]
        if record["unit_fingerprint"] != unit_fingerprint:
            raise RuntimeError(f"read-only scoring detected unit metadata drift: {key.token}")
        sidecar = self._root / "data/derived/task017-checkpoint.jsonl.units" / str(record["result_artifact"])
        return task017._read_result_artifact(sidecar)


def _task010_trials_read_only(
    checkpoint: _ReadOnlyCheckpoint,
    variant_id: str,
    candidate_id: str,
    side: str,
    analysis_kind: str,
    condition,
    schedules,
    projection,
):
    trials = []
    for schedule in schedules:
        key = task017.Task017UnitKey(variant_id, candidate_id, side, schedule.trial_index, analysis_kind)
        record = checkpoint._records.get(key.token)
        if record is None:
            raise RuntimeError(f"read-only scoring refused missing checkpoint unit: {key.token}")
        result = checkpoint.get(key, str(record["unit_fingerprint"]))
        trials.extend(
            task017._trials_from_results(
                candidate_id,
                condition,
                side[0],
                ((schedule.trial_index, schedule.seed, schedule.stimulus),),
                (result,),
                projection,
            )
        )
        del result
    return tuple(trials)


def verify_sealed_matrix(root: Path) -> tuple[CheckpointAudit, dict[str, object]]:
    manifest_path = root / "artifacts/task017/complete-matrix-manifest.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    manifest_sha256 = hashlib.sha256(manifest_raw).hexdigest()
    if manifest_sha256 != COMPLETE_MATRIX_MANIFEST_SHA256:
        raise RuntimeError("complete-matrix manifest SHA-256 differs from the sealed Task 017K-R5 artifact")
    if manifest.get("complete_matrix_digest") != COMPLETE_MATRIX_DIGEST:
        raise RuntimeError("complete-matrix digest differs from the sealed Task 017K-R5 artifact")
    if manifest.get("complete_matrix_digest") != manifest.get("canonical_record_set_digest"):
        raise RuntimeError("complete-matrix and canonical record-set digests disagree")
    for field in (
        "duplicate_count",
        "duplicate_sidecar_ref_count",
        "missing_sidecar_count",
        "orphan_sidecar_count",
        "metadata_failure_count",
        "result_digest_failure_count",
        "technical_invalid_count",
    ):
        if manifest.get(field) != 0:
            raise RuntimeError(f"complete-matrix manifest reports {field}={manifest.get(field)}")

    audit = audit_checkpoint(
        root / "data/derived/task017-checkpoint.jsonl",
        root=root,
        expected_task016_fingerprint=TASK016_FINGERPRINT,
        expected_checkpoint_fingerprint=CHECKPOINT_FINGERPRINT,
    )
    if audit.completed_count != 3168 or audit.expected_count != 3168 or audit.pending_keys:
        raise RuntimeError("Task 017 checkpoint is not exactly complete")
    if audit.invalid_technical_count:
        raise RuntimeError("Task 017 checkpoint contains technical-invalid units")
    if len(audit.sidecar_digests) != 3168:
        raise RuntimeError("Task 017 sidecar count differs from the complete matrix")

    recovery_path = root / "artifacts/task017/recovery-manifest.json"
    recovery_raw = recovery_path.read_bytes()
    if hashlib.sha256(recovery_raw).hexdigest() != RECOVERY_MANIFEST_SHA256:
        raise RuntimeError("tracked recovery-manifest SHA-256 differs from the Task 017K-R5 report")
    recovery = json.loads(recovery_raw)
    for name, expected in (
        ("completed_units", 3168),
        ("expected_units", 3168),
        ("remaining_units", 0),
        ("task016_fingerprint", TASK016_FINGERPRINT),
        ("checkpoint_fingerprint", CHECKPOINT_FINGERPRINT),
        ("journal_sha256", audit.journal_sha256),
    ):
        if recovery.get(name) != expected:
            raise RuntimeError(f"tracked recovery manifest mismatch for {name}")
    if recovery.get("pending_unit_keys") != []:
        raise RuntimeError("tracked recovery manifest lists pending units")
    sidecar_inventory = hashlib.sha256(_canonical_json(audit.sidecar_digests)).hexdigest()
    if sidecar_inventory != manifest.get("sidecar_inventory_sha256"):
        raise RuntimeError("live sidecar inventory differs from the complete-matrix manifest")
    if recovery.get("sidecar_inventory_sha256") != sidecar_inventory:
        raise RuntimeError("complete-matrix and recovery sidecar inventories disagree")
    if manifest.get("journal_sha256") != audit.journal_sha256:
        raise RuntimeError("checkpoint journal SHA-256 differs from the complete-matrix manifest")
    return audit, {
        "complete_matrix_digest": COMPLETE_MATRIX_DIGEST,
        "complete_matrix_manifest_sha256": manifest_sha256,
        "journal_sha256": audit.journal_sha256,
        "sidecar_inventory_sha256": manifest["sidecar_inventory_sha256"],
    }


def _variant_network(variant: task017.VariantConfiguration, reference: PreparedNetwork, sign_source):
    projection = EffectiveSignedProjection.from_signed_connectome(
        sign_source, synaptic_weight_mV=variant.synaptic_weight_mV
    )
    return replace(
        reference,
        projection=projection,
        signed_connectome=sign_source,
        graph_name=f"task017-read-only-{variant.variant_id}",
        cuda_graph=None,
    )


def score_task017(root: str | Path) -> dict[str, object]:
    repo_root = Path(root).resolve()
    audit, matrix_identity = verify_sealed_matrix(repo_root)
    if task017.task016_specification_fingerprint() != TASK016_FINGERPRINT:
        raise RuntimeError("Task 016 source fingerprint differs from the preregistered fingerprint")

    raw_root = repo_root / "data/raw/male-cns/v1.0"
    annotation = raw_root / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    neurotransmitter = raw_root / "body-neurotransmitters-male-cns-v1.0.feather"
    weights = raw_root / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    cache_path = repo_root / "data/derived/task008/full-prepared-graph.npz"
    task009_path = repo_root / "data/derived/task009-results.json"

    identities = load_task008_identities(annotation, neurotransmitter)
    cache = PreparedGraphCache.load(cache_path)
    cached_projection = cache.to_projection()
    if cache.cache_fingerprint != TASK008_FULL_CACHE_FINGERPRINT:
        raise RuntimeError("Task 008 cache fingerprint differs from the frozen source")
    if cached_projection.fingerprint != cache.projection_fingerprint:
        raise RuntimeError("Task 008 cached projection does not match its recorded fingerprint")
    reference_identity = SimpleNamespace(
        sign_policy_id="Shiu2024SignPolicy",
        unsigned_graph_fingerprint=cached_projection.unsigned_graph_fingerprint,
        signed_policy_fingerprint=cached_projection.signed_policy_fingerprint,
    )
    reference = PreparedNetwork(
        projection=cached_projection,
        signed_connectome=reference_identity,
        graph_name="task017-read-only-reference",
        preparation_seconds=0.0,
        graph_loading_seconds=0.0,
        setup_seconds=0.0,
        memory_bytes=0,
        fingerprint=TASK008_PREPARED_FINGERPRINT,
        cache_path=None,
        cache_fingerprint=cache.cache_fingerprint,
        cuda_graph=None,
    )
    manifest = load_frozen_candidate_manifest(task009_path)
    checkpoint = _ReadOnlyCheckpoint(repo_root, audit)
    reference_schedules = {
        "LEFT": task017._make_frozen_schedules(
            reference, identities, identities.sugar_left, side="L", trial_indices=range(task017.TASK010_TRIAL_COUNT), synaptic_weight_mV=0.275
        ),
        "RIGHT": task017._make_frozen_schedules(
            reference, identities, identities.sugar_right, side="R", trial_indices=range(task017.TASK010_TRIAL_COUNT), synaptic_weight_mV=0.275
        ),
    }

    annotation_path = raw_root / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    neurotransmitter_path = raw_root / "body-neurotransmitters-male-cns-v1.0.feather"
    weights_path = raw_root / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    shiu_source = None
    conservative_source = None
    variant_results: dict[str, object] = {}
    for variant in task017.VARIANT_CONFIGURATIONS:
        if variant is task017.REFERENCE_VARIANT:
            prepared = reference
        elif variant.sign_policy_id == "ConservativeSignPolicy":
            del prepared
            del shiu_source
            gc.collect()
            conservative_source = task017._load_signed_connectome(
                annotation_path, neurotransmitter_path, weights_path, task017.ConservativeSignPolicy()
            )
            prepared = _variant_network(variant, reference, conservative_source)
        else:
            if shiu_source is None:
                shiu_source = task017._load_signed_connectome(
                    annotation_path, neurotransmitter_path, weights_path, task017.Shiu2024SignPolicy()
                )
            prepared = _variant_network(variant, reference, shiu_source)
        schedules = reference_schedules if variant is task017.REFERENCE_VARIANT else task017._reweight_frozen_schedules(reference_schedules, variant.synaptic_weight_mV)
        baseline_trials = {}
        outcomes = {}
        for condition, side in ((task017.PRIMARY_CONDITION, "LEFT"), (task017.MIRROR_CONDITION, "RIGHT")):
            side_schedules = schedules[side]
            baseline_trials[side] = _task010_trials_read_only(
                checkpoint,
                variant.variant_id,
                task017.BASELINE_CANDIDATE_ID,
                side,
                task017.TASK010_BASELINE,
                condition,
                side_schedules,
                prepared.projection,
            )

        for candidate_id in task017.FROZEN_TASK011_CANDIDATES:
            for condition, side in ((task017.PRIMARY_CONDITION, "LEFT"), (task017.MIRROR_CONDITION, "RIGHT")):
                side_schedules = schedules[side]
                trials = _task010_trials_read_only(
                    checkpoint,
                    variant.variant_id,
                    candidate_id,
                    side,
                    task017.TASK010_INTERVENTION,
                    condition,
                    side_schedules,
                    prepared.projection,
                )
                key = f"{candidate_id}:{condition.name}"
                outcomes[key] = {
                    "candidate_id": candidate_id,
                    "condition": condition.name,
                    "stimulus_side": side[0],
                    "technical_validity": "PASS",
                    "trials": [asdict(item) for item in trials],
                    "summary": summarize_condition(baseline_trials[side], trials),
                }
        task010 = {"variant_id": variant.variant_id, "outcomes": outcomes, "baseline_trials": {}}
        temporal = task017._task011_variant(variant, prepared, schedules, manifest, annotation, checkpoint)
        variant_results[variant.variant_id] = {
            "variant": variant.as_record(),
            "validity": {"status": "VALID", "exclusion_reason": None},
            "task010": task010,
            "temporal": temporal,
        }
        if variant.sign_policy_id == "ConservativeSignPolicy":
            del prepared
            del conservative_source
            gc.collect()

    if checkpoint.read_count != 3168:
        raise RuntimeError(f"expected exactly 3,168 read-only sidecar lookups, got {checkpoint.read_count}")
    cells = task017._robustness_cells(variant_results)
    global_support = task017._global_support(variant_results)
    classification, classification_details = task017._classify_global(variant_results, cells, global_support)
    nonreference = [item.variant_id for item in task017.VARIANT_CONFIGURATIONS if item is not task017.REFERENCE_VARIANT]

    cell_rows = []
    for candidate in task017.FROZEN_TASK011_CANDIDATES:
        for side in ("LEFT", "RIGHT"):
            key = f"{candidate}:{side}"
            cell = cells[key]
            cell_rows.append({
                "candidate": candidate,
                "stimulus_side": side,
                "reference": cell["reference"],
                "direction": cell["effect_direction"],
                "category": cell["effect_category"],
                "mechanism": cell["mechanism"],
            })

    support_rows = [
        {"variant_id": variant_id, **global_support[variant_id]}
        for variant_id in nonreference
    ]
    content: dict[str, object] = {
        "schema": SCORING_SCHEMA,
        "task016_fingerprint": TASK016_FINGERPRINT,
        "checkpoint_fingerprint": CHECKPOINT_FINGERPRINT,
        "complete_matrix_digest": COMPLETE_MATRIX_DIGEST,
        "cells": cell_rows,
        "global_support": support_rows,
        "global_supporting_variant_count": sum(bool(row["supports_global_conclusion"]) for row in support_rows),
        "global_support_variant_count": len(support_rows),
        "stable_cell_totals": {
            "direction": classification_details["effect_direction_stable_cells"],
            "category": classification_details["effect_category_stable_cells"],
            "mechanism_compatible": classification_details["mechanism_compatible_stable_cells"],
        },
        "global_classification": classification,
        "global_classification_details": classification_details,
        "coverage": {"cells_scored": len(cell_rows), "cells_expected": 10, "nonreference_variants_evaluated": len(nonreference), "nonreference_variants_expected": 7},
        "execution_claims": {"simulation_count": 0, "task018_started": False, "task017q_status": "DEFERRED"},
    }
    content["deterministic_scoring_digest"] = _digest(SCORING_SCHEMA, content)
    return {"scientific_content": content, "provenance": matrix_identity}


def write_scoring_artifact(root: str | Path, destination: str | Path) -> dict[str, object]:
    payload = score_task017(root)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    return payload
