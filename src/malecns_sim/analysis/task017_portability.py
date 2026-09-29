"""Portable audit, export, and restoration for Task 017 checkpoints."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence

from malecns_sim.analysis import task017


PORTABILITY_SCHEMA = "malecns-sim-task017-recovery-v1"
PORTABILITY_TOOL_VERSION = "1.0.0"
DEFAULT_CHECKPOINT_RELATIVE = Path("data/derived/task017-checkpoint.jsonl")
DEFAULT_BUNDLE_NAME = "task017-recovery-bundle.zip"
DEFAULT_MANIFEST_NAME = "recovery-manifest.json"


class PortabilityError(RuntimeError):
    """Raised when a checkpoint bundle fails a recovery gate."""


@dataclass(frozen=True)
class CheckpointAudit:
    root: Path
    checkpoint_path: Path
    identity: dict[str, object]
    fingerprint: str
    task016_fingerprint: str
    journal_sha256: str
    records: tuple[dict[str, object], ...]
    sidecar_digests: dict[str, str]
    pending_keys: tuple[dict[str, object], ...]
    per_variant: dict[str, dict[str, int]]
    per_side: dict[str, dict[str, int]]
    per_analysis: dict[str, dict[str, int]]
    invalid_technical_count: int

    @property
    def completed_count(self) -> int:
        return len(self.records)

    @property
    def expected_count(self) -> int:
        return len(self.records) + len(self.pending_keys)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(("git", "-C", str(root), "rev-parse", "HEAD"), text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PortabilityError(f"cannot determine source Git HEAD: {exc}") from exc


def _expected_matrix(expected_keys: Sequence[task017.Task017UnitKey] | None) -> tuple[task017.Task017UnitKey, ...]:
    return tuple(expected_keys) if expected_keys is not None else task017.expected_task017_unit_keys()


def audit_checkpoint(
    checkpoint_path: str | Path,
    *,
    root: str | Path | None = None,
    expected_keys: Sequence[task017.Task017UnitKey] | None = None,
    expected_task016_fingerprint: str | None = None,
    expected_checkpoint_fingerprint: str | None = None,
) -> CheckpointAudit:
    """Audit a checkpoint without creating, truncating, or rewriting files."""

    checkpoint = Path(checkpoint_path)
    repo_root = Path(root).resolve() if root is not None else checkpoint.resolve().parent.parent.parent
    checkpoint = checkpoint.resolve()
    artifact_dir = checkpoint.with_name(checkpoint.name + ".units")
    if not checkpoint.is_file():
        raise PortabilityError(f"checkpoint journal is absent: {checkpoint}")
    raw = checkpoint.read_bytes()
    if not raw.endswith(b"\n"):
        raise PortabilityError("checkpoint journal has an incomplete tail")
    try:
        lines = raw.decode("utf-8").splitlines()
        header = json.loads(lines[0])
    except (UnicodeDecodeError, IndexError, json.JSONDecodeError) as exc:
        raise PortabilityError(f"checkpoint journal header is invalid: {exc}") from exc
    if header.get("kind") != task017.CHECKPOINT_HEADER_KIND or header.get("schema") != task017.CHECKPOINT_SCHEMA:
        raise PortabilityError("checkpoint journal schema/header mismatch")
    identity = header.get("identity")
    if not isinstance(identity, dict):
        raise PortabilityError("checkpoint identity is not an object")
    fingerprint = task017._digest("malecns-sim-task017-checkpoint-state-v1", identity)
    spec_fingerprint = task017.task016_specification_fingerprint()
    identity_spec = identity.get("task016_specification_fingerprint")
    if identity_spec != spec_fingerprint:
        raise PortabilityError("checkpoint Task 016 fingerprint does not match this repository")
    if expected_task016_fingerprint is not None and spec_fingerprint != expected_task016_fingerprint:
        raise PortabilityError("Task 016 fingerprint differs from the required recovery point")
    if expected_checkpoint_fingerprint is not None and fingerprint != expected_checkpoint_fingerprint:
        raise PortabilityError("checkpoint fingerprint differs from the required recovery point")
    matrix = _expected_matrix(expected_keys)
    expected_by_token = {item.token: item for item in matrix}
    if len(expected_by_token) != len(matrix):
        raise PortabilityError("expected Task 017 matrix contains duplicate unit identities")
    if identity.get("expected_unit_count") != len(matrix):
        raise PortabilityError("checkpoint expected-unit count does not match the Task 017 matrix")

    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines[1:], start=2):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PortabilityError(f"invalid journal JSON at line {line_number}: {exc}") from exc
        if record.get("kind") == task017.CHECKPOINT_DUPLICATE_KIND:
            raise PortabilityError(f"duplicate-unit journal marker at line {line_number}")
        if record.get("kind") != task017.CHECKPOINT_UNIT_KIND:
            raise PortabilityError(f"unknown journal record kind at line {line_number}")
        try:
            key = task017.Task017UnitKey(**record["key"])
        except (KeyError, TypeError) as exc:
            raise PortabilityError(f"invalid unit key at line {line_number}") from exc
        token = key.token
        if token not in expected_by_token:
            raise PortabilityError(f"unit key is outside the expected Task 017 matrix: {token}")
        if token in seen:
            raise PortabilityError(f"duplicate completed unit: {token}")
        seen.add(token)
        metadata = record.get("metadata")
        if not isinstance(metadata, dict) or task017._digest(task017.CHECKPOINT_UNIT_PREFIX, metadata) != record.get("unit_fingerprint"):
            raise PortabilityError(f"metadata fingerprint mismatch for {token}")
        if metadata.get("key") != key.as_record():
            raise PortabilityError(f"record/metadata unit identity mismatch for {token}")
        artifact_name = record.get("result_artifact")
        if artifact_name != f"{token}.npz" or Path(str(artifact_name)).name != artifact_name:
            raise PortabilityError(f"noncanonical result sidecar name for {token}")
        records.append(record)

    if not artifact_dir.is_dir():
        raise PortabilityError(f"checkpoint sidecar directory is absent: {artifact_dir}")
    sidecar_paths = sorted(artifact_dir.glob("*.npz"), key=lambda item: item.name)
    referenced = {str(record["result_artifact"]) for record in records}
    present = {path.name for path in sidecar_paths}
    if present - referenced:
        raise PortabilityError(f"orphan sidecar(s): {sorted(present - referenced)[:5]}")
    if referenced - present:
        raise PortabilityError(f"missing sidecar(s): {sorted(referenced - present)[:5]}")

    sidecar_digests: dict[str, str] = {}
    invalid_technical = 0
    for record in records:
        token = task017.Task017UnitKey(**record["key"]).token
        sidecar = artifact_dir / str(record["result_artifact"])
        try:
            result = task017._read_result_artifact(sidecar)
        except Exception as exc:
            raise PortabilityError(f"sidecar cannot be decoded for {token}: {exc}") from exc
        if result.spike_result_digest != record.get("result_digest"):
            raise PortabilityError(f"result digest mismatch for {token}")
        sidecar_digests[sidecar.name] = _sha256_file(sidecar)
        if record.get("technical_validity") != "PASS":
            invalid_technical += 1

    pending = tuple(item for item in matrix if item.token not in seen)
    by_variant: dict[str, dict[str, int]] = {}
    by_side: dict[str, dict[str, int]] = {}
    by_analysis: dict[str, dict[str, int]] = {}
    for key in matrix:
        completed = key.token in seen
        for summary, group_name in (
            (by_variant, key.variant_id),
            (by_side, key.stimulus_side),
            (by_analysis, key.analysis_kind),
        ):
            counts = summary.setdefault(group_name, {"completed": 0, "expected": 0, "pending": 0})
            counts["expected"] += 1
            counts["completed"] += int(completed)
            counts["pending"] += int(not completed)
    return CheckpointAudit(
        root=repo_root,
        checkpoint_path=checkpoint,
        identity=identity,
        fingerprint=fingerprint,
        task016_fingerprint=spec_fingerprint,
        journal_sha256=_sha256_bytes(raw),
        records=tuple(records),
        sidecar_digests=sidecar_digests,
        pending_keys=tuple(item.as_record() for item in pending),
        per_variant=by_variant,
        per_side=by_side,
        per_analysis=by_analysis,
        invalid_technical_count=invalid_technical,
    )


def audit_payload(audit: CheckpointAudit) -> dict[str, object]:
    return {
        "artifact_type": "task017_checkpoint",
        "task": "017",
        "task016_fingerprint": audit.task016_fingerprint,
        "checkpoint_fingerprint": audit.fingerprint,
        "completed_units": audit.completed_count,
        "expected_units": audit.expected_count,
        "variant_completion_counts": audit.per_variant,
        "side_completion_counts": audit.per_side,
        "analysis_completion_counts": audit.per_analysis,
        "pending_count": len(audit.pending_keys),
        "pending_unit_keys": list(audit.pending_keys),
        "journal_sha256": audit.journal_sha256,
        "sidecar_count": len(audit.sidecar_digests),
        "sidecar_digest_inventory": audit.sidecar_digests,
        "sidecar_inventory_sha256": _sha256_bytes(_canonical_json(audit.sidecar_digests)),
        "duplicate_count": 0,
        "missing_sidecar_count": 0,
        "orphan_sidecar_count": 0,
        "invalid_digest_count": 0,
        "technical_invalid_count": audit.invalid_technical_count,
        "scientific_status": "INDETERMINATE",
    }


def write_recovery_bundle(
    checkpoint_path: str | Path,
    destination: str | Path,
    *,
    root: str | Path | None = None,
    expected_keys: Sequence[task017.Task017UnitKey] | None = None,
    expected_task016_fingerprint: str | None = None,
    expected_checkpoint_fingerprint: str | None = None,
) -> tuple[Path, Path, dict[str, object]]:
    """Audit then create a deterministic zip plus its recovery manifest."""

    audit = audit_checkpoint(
        checkpoint_path,
        root=root,
        expected_keys=expected_keys,
        expected_task016_fingerprint=expected_task016_fingerprint,
        expected_checkpoint_fingerprint=expected_checkpoint_fingerprint,
    )
    if audit.invalid_technical_count:
        raise PortabilityError("checkpoint contains technical-invalid units and cannot be certified for recovery")
    target = Path(destination).resolve()
    target.mkdir(parents=True, exist_ok=True)
    bundle_path = target / DEFAULT_BUNDLE_NAME
    manifest_path = target / DEFAULT_MANIFEST_NAME
    if bundle_path.exists() or manifest_path.exists():
        raise PortabilityError(f"bundle destination already contains an export: {target}")
    staged_bundle = target / (DEFAULT_BUNDLE_NAME + ".tmp")
    manifest = audit_payload(audit)
    manifest.update(
        {
            "schema_version": PORTABILITY_SCHEMA,
            "source_git_head": _git_head(audit.root),
            "python_version": platform.python_version(),
            "cupy_version": None,
            "cuda_runtime_version": None,
            "cuda_driver_version": None,
            "export_tool_version": PORTABILITY_TOOL_VERSION,
            "bundle_filename": DEFAULT_BUNDLE_NAME,
        }
    )
    try:
        import cupy

        manifest["cupy_version"] = cupy.__version__
        try:
            manifest["cuda_runtime_version"] = int(cupy.cuda.runtime.runtimeGetVersion())
            manifest["cuda_driver_version"] = int(cupy.cuda.runtime.driverGetVersion())
        except Exception:
            pass
    except Exception:
        pass
    try:
        with zipfile.ZipFile(staged_bundle, "w", compression=zipfile.ZIP_STORED) as archive:
            entries = [("task017-checkpoint.jsonl", audit.checkpoint_path)]
            entries.extend(
                (f"task017-checkpoint.jsonl.units/{name}", audit.checkpoint_path.with_name(audit.checkpoint_path.name + ".units") / name)
                for name in sorted(audit.sidecar_digests)
            )
            for archive_name, source in entries:
                info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, source.read_bytes())
        manifest["bundle_sha256"] = _sha256_file(staged_bundle)
        manifest_path.write_bytes(_canonical_json(manifest) + b"\n")
        os.replace(staged_bundle, bundle_path)
    except Exception:
        staged_bundle.unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)
        raise
    return bundle_path, manifest_path, manifest


def _load_manifest(bundle_dir: Path) -> tuple[Path, Path, dict[str, object]]:
    manifest_path = bundle_dir / DEFAULT_MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortabilityError(f"recovery manifest is absent or invalid: {exc}") from exc
    if manifest.get("schema_version") != PORTABILITY_SCHEMA or manifest.get("artifact_type") != "task017_checkpoint":
        raise PortabilityError("unsupported Task 017 recovery manifest schema")
    filename = manifest.get("bundle_filename")
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise PortabilityError("unsafe bundle filename in recovery manifest")
    bundle_path = bundle_dir / filename
    if not bundle_path.is_file() or _sha256_file(bundle_path) != manifest.get("bundle_sha256"):
        raise PortabilityError("bundle checksum mismatch")
    return bundle_path, manifest_path, manifest


def _verify_tracked_recovery_point(
    root: Path,
    bundle_path: Path,
    manifest_path: Path,
    manifest: Mapping[str, object],
    *,
    required: bool,
) -> None:
    tracked_path = root / "artifacts" / "task017" / "recovery-manifest.json"
    if not tracked_path.exists():
        if required:
            raise PortabilityError("tracked Task 017 recovery manifest is absent")
        return
    try:
        tracked = json.loads(tracked_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortabilityError(f"tracked Task 017 recovery manifest is invalid: {exc}") from exc
    if tracked.get("schema_version") != "malecns-sim-task017-recovery-point-v1" or tracked.get("artifact_type") != "task017_checkpoint" or tracked.get("task") != "017":
        raise PortabilityError("tracked recovery manifest describes an unsupported artifact")
    if (
        tracked.get("bundle_filename") != bundle_path.name
        or tracked.get("bundle_sha256") != manifest.get("bundle_sha256")
        or tracked.get("recovery_manifest_sha256") != _sha256_file(manifest_path)
        or tracked.get("task016_fingerprint") != manifest.get("task016_fingerprint")
        or tracked.get("checkpoint_fingerprint") != manifest.get("checkpoint_fingerprint")
        or tracked.get("completed_units") != manifest.get("completed_units")
        or tracked.get("expected_units") != manifest.get("expected_units")
        or tracked.get("pending_unit_keys") != manifest.get("pending_unit_keys")
        or tracked.get("variant_completion_counts") != manifest.get("variant_completion_counts")
    ):
        raise PortabilityError("bundle does not match the tracked Task 017 recovery point")


def _verify_archive(bundle_path: Path, manifest: Mapping[str, object], staging: Path) -> None:
    try:
        inventory = manifest.get("sidecar_digest_inventory")
        if not isinstance(inventory, dict) or any(
            not isinstance(name, str) or Path(name).name != name or not name.endswith(".npz")
            for name in inventory
        ):
            raise PortabilityError("sidecar digest inventory contains an unsafe filename")
        with zipfile.ZipFile(bundle_path, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise PortabilityError("bundle contains duplicate archive members")
            expected_names = {"task017-checkpoint.jsonl"}
            expected_names.update(f"task017-checkpoint.jsonl.units/{name}" for name in inventory)
            if set(names) != expected_names:
                raise PortabilityError("bundle file inventory does not match the recovery manifest")
            for name in names:
                member = PurePosixPath(name)
                if member.is_absolute() or ".." in member.parts:
                    raise PortabilityError(f"unsafe bundle path: {name}")
                target = staging.joinpath(*member.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    except (OSError, zipfile.BadZipFile, KeyError) as exc:
        raise PortabilityError(f"cannot read recovery bundle: {exc}") from exc
    journal = staging / "task017-checkpoint.jsonl"
    if _sha256_file(journal) != manifest.get("journal_sha256"):
        raise PortabilityError("journal digest mismatch")
    sidecar_inventory = manifest.get("sidecar_digest_inventory")
    if not isinstance(sidecar_inventory, dict):
        raise PortabilityError("sidecar digest inventory is invalid")
    for name, digest in sidecar_inventory.items():
        if Path(name).name != name or not isinstance(digest, str):
            raise PortabilityError("invalid sidecar inventory entry")
        path = staging / "task017-checkpoint.jsonl.units" / name
        if not path.is_file() or _sha256_file(path) != digest:
            raise PortabilityError(f"sidecar digest mismatch: {name}")
    if _sha256_bytes(_canonical_json(sidecar_inventory)) != manifest.get("sidecar_inventory_sha256"):
        raise PortabilityError("sidecar aggregate digest mismatch")


def restore_recovery_bundle(
    bundle_dir: str | Path,
    repo_root: str | Path,
    *,
    expected_task016_fingerprint: str | None = None,
    expected_checkpoint_fingerprint: str | None = None,
    expected_keys: Sequence[task017.Task017UnitKey] | None = None,
    before_install: Callable[[], None] | None = None,
    require_tracked_recovery_point: bool = False,
) -> CheckpointAudit:
    """Verify and atomically install a checkpoint into repo-relative derived data."""

    source = Path(bundle_dir).resolve()
    root = Path(repo_root).resolve()
    bundle_path, _, manifest = _load_manifest(source)
    manifest_path = source / DEFAULT_MANIFEST_NAME
    _verify_tracked_recovery_point(
        root,
        bundle_path,
        manifest_path,
        manifest,
        required=require_tracked_recovery_point,
    )
    task016_fingerprint = task017.task016_specification_fingerprint()
    if manifest.get("task016_fingerprint") != task016_fingerprint:
        raise PortabilityError("recovery manifest Task 016 fingerprint mismatch")
    if expected_task016_fingerprint is not None and task016_fingerprint != expected_task016_fingerprint:
        raise PortabilityError("Task 016 fingerprint differs from the required recovery point")
    if expected_checkpoint_fingerprint is not None and manifest.get("checkpoint_fingerprint") != expected_checkpoint_fingerprint:
        raise PortabilityError("manifest checkpoint fingerprint differs from the required recovery point")
    destination = root / DEFAULT_CHECKPOINT_RELATIVE
    artifact_destination = destination.with_name(destination.name + ".units")
    if destination.exists() or artifact_destination.exists():
        if destination.is_file() and artifact_destination.is_dir():
            existing = audit_checkpoint(
                destination,
                root=root,
                expected_keys=expected_keys,
                expected_task016_fingerprint=task016_fingerprint,
                expected_checkpoint_fingerprint=str(manifest.get("checkpoint_fingerprint")),
            )
            if existing.journal_sha256 == manifest.get("journal_sha256") and existing.sidecar_digests == manifest.get("sidecar_digest_inventory"):
                return existing
        raise PortabilityError("destination contains incompatible or partial checkpoint state")

    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    stale_staging = sorted(path.name for path in parent.glob(".task017-import-*"))
    if stale_staging:
        raise PortabilityError(f"partial staged import directory exists: {stale_staging}")
    stage_parent = Path(tempfile.mkdtemp(prefix=".task017-import-", dir=parent))
    installed_artifacts = False
    installed_journal = False
    try:
        _verify_archive(bundle_path, manifest, stage_parent)
        staged_checkpoint = stage_parent / "task017-checkpoint.jsonl"
        staged_audit = audit_checkpoint(
            staged_checkpoint,
            root=root,
            expected_keys=expected_keys,
            expected_task016_fingerprint=task016_fingerprint,
            expected_checkpoint_fingerprint=str(manifest.get("checkpoint_fingerprint")),
        )
        expected_counts = (
            staged_audit.completed_count == manifest.get("completed_units")
            and staged_audit.expected_count == manifest.get("expected_units")
            and len(staged_audit.pending_keys) == manifest.get("pending_count")
            and list(staged_audit.pending_keys) == manifest.get("pending_unit_keys")
            and staged_audit.per_variant == manifest.get("variant_completion_counts")
            and staged_audit.per_side == manifest.get("side_completion_counts")
            and staged_audit.per_analysis == manifest.get("analysis_completion_counts")
            and len(staged_audit.sidecar_digests) == manifest.get("sidecar_count")
            and staged_audit.invalid_technical_count == manifest.get("technical_invalid_count") == 0
            and staged_audit.fingerprint == manifest.get("checkpoint_fingerprint")
        )
        if not expected_counts:
            raise PortabilityError("recovery manifest completion ledger does not match staged checkpoint")
        if before_install is not None:
            before_install()
        staged_artifacts = stage_parent / "task017-checkpoint.jsonl.units"
        os.replace(staged_artifacts, artifact_destination)
        installed_artifacts = True
        os.replace(staged_checkpoint, destination)
        installed_journal = True
        return audit_checkpoint(
            destination,
            root=root,
            expected_keys=expected_keys,
            expected_task016_fingerprint=task016_fingerprint,
            expected_checkpoint_fingerprint=staged_audit.fingerprint,
        )
    except Exception:
        if installed_journal:
            destination.unlink(missing_ok=True)
        if installed_artifacts:
            shutil.rmtree(artifact_destination, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)


def main_audit(root: Path, checkpoint: Path | None = None) -> dict[str, object]:
    path = checkpoint or root / DEFAULT_CHECKPOINT_RELATIVE
    audit = audit_checkpoint(path, root=root)
    payload = audit_payload(audit)
    report = {key: value for key, value in payload.items() if key not in {"pending_unit_keys", "sidecar_digest_inventory"}}
    report["pending_unit_keys_sha256"] = _sha256_bytes(_canonical_json(audit.pending_keys))
    report["audit_status"] = "PASS" if not audit.invalid_technical_count else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    if audit.invalid_technical_count:
        raise PortabilityError("checkpoint contains technically invalid records")
    return payload
