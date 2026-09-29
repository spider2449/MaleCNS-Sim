from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from malecns_sim.analysis import task017_portability as portability
from malecns_sim.analysis.task017 import (
    CHECKPOINT_SCHEMA,
    CHECKPOINT_UNIT_PREFIX,
    TASK010_BASELINE,
    Task017Checkpoint,
    Task017UnitKey,
    _digest,
    _synthetic_fixtures,
    _synthetic_projection,
    expected_task017_unit_keys,
    require_recovery_for_missing_checkpoint,
    task016_specification_fingerprint,
)
from malecns_sim.dynamics import simulate_lif


def _repo(root: Path) -> tuple[Path, Path]:
    checkpoint = root / "data" / "derived" / "task017-checkpoint.jsonl"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    return root, checkpoint


def _create_synthetic_checkpoint(root: Path, keys: tuple[Task017UnitKey, ...]) -> Path:
    _, checkpoint_path = _repo(root)
    identity = {
        "schema": CHECKPOINT_SCHEMA,
        "expected_unit_count": len(keys),
        "task016_specification_fingerprint": task016_specification_fingerprint(),
        "source_fingerprint": "synthetic-portability-fixture",
    }
    checkpoint = Task017Checkpoint(checkpoint_path, identity)
    result = simulate_lif(_synthetic_projection(0.275), duration_ms=1.0, stimulus=_synthetic_fixtures(0.275)[0])
    for key in keys:
        metadata = {
            "key": key.as_record(),
            "effective_model_parameters": {"variant_id": key.variant_id},
            "schedule_fingerprint": "synthetic-schedule",
            "candidate_identity": key.candidate_id,
            "stimulus_identity": key.stimulus_side,
        }
        checkpoint.put(key, unit_fingerprint=_digest(CHECKPOINT_UNIT_PREFIX, metadata), metadata=metadata, result=result)
    return checkpoint_path


def _fixture_keys() -> tuple[Task017UnitKey, ...]:
    expected = expected_task017_unit_keys()
    return (expected[0], expected[1])


def _make_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path, dict[str, object]]:
    root_a = tmp_path / "root-a"
    checkpoint = _create_synthetic_checkpoint(root_a, _fixture_keys())
    monkeypatch.setattr(portability, "_git_head", lambda root: "synthetic-source-head")
    bundle_dir = tmp_path / "outside-checkout" / "bundle"
    bundle, manifest_path, manifest = portability.write_recovery_bundle(
        checkpoint,
        bundle_dir,
        root=root_a,
        expected_keys=_fixture_keys(),
        expected_task016_fingerprint=task016_specification_fingerprint(),
    )
    assert bundle.exists() and manifest_path.exists()
    return root_a, bundle, manifest_path, manifest


def _rewrite_bundle(bundle_dir: Path, manifest: dict[str, object], mutate) -> dict[str, object]:
    bundle_path = bundle_dir / str(manifest["bundle_filename"])
    original = {}
    with zipfile.ZipFile(bundle_path) as archive:
        for name in archive.namelist():
            original[name] = archive.read(name)
    mutate(original, manifest)
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in original.items():
            archive.writestr(name, payload)
    manifest["bundle_sha256"] = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    (bundle_dir / portability.DEFAULT_MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def test_task017_synthetic_checkpoint_roundtrips_across_roots(tmp_path, monkeypatch):
    root_a, bundle, manifest_path, manifest = _make_bundle(tmp_path, monkeypatch)
    second_bundle, second_manifest_path, second_manifest = portability.write_recovery_bundle(
        root_a / portability.DEFAULT_CHECKPOINT_RELATIVE,
        tmp_path / "another-export-location",
        root=root_a,
        expected_keys=_fixture_keys(),
        expected_task016_fingerprint=task016_specification_fingerprint(),
    )
    assert second_manifest == manifest
    assert second_bundle.read_bytes() == bundle.read_bytes()
    assert hashlib.sha256(second_manifest_path.read_bytes()).hexdigest() == hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    root_b = tmp_path / "different" / "checkout-b"
    restored = portability.restore_recovery_bundle(
        bundle.parent,
        root_b,
        expected_task016_fingerprint=task016_specification_fingerprint(),
        expected_keys=_fixture_keys(),
    )
    source = portability.audit_checkpoint(
        root_a / portability.DEFAULT_CHECKPOINT_RELATIVE,
        root=root_a,
        expected_keys=_fixture_keys(),
    )
    assert restored.fingerprint == source.fingerprint == manifest["checkpoint_fingerprint"]
    assert restored.task016_fingerprint == source.task016_fingerprint
    assert [item["key"] for item in restored.records] == [item["key"] for item in source.records]
    assert restored.sidecar_digests == source.sidecar_digests
    assert restored.pending_keys == source.pending_keys
    assert restored.pending_keys == tuple(manifest["pending_unit_keys"])
    assert _digest("malecns-sim-task017-checkpoint-state-v1", source.identity) == _digest(
        "malecns-sim-task017-checkpoint-state-v1", restored.identity
    )
    assert not any(str(root_a).encode() in (root_b / portability.DEFAULT_CHECKPOINT_RELATIVE).read_bytes() for _ in (0,))
    second_root = tmp_path / "root-c"
    second_checkpoint = _create_synthetic_checkpoint(second_root, _fixture_keys())
    second = portability.audit_checkpoint(second_checkpoint, root=second_root, expected_keys=_fixture_keys())
    assert second.fingerprint == source.fingerprint
    assert second.task016_fingerprint == source.task016_fingerprint
    assert second.journal_sha256 == source.journal_sha256
    assert second.sidecar_digests == source.sidecar_digests
    assert manifest_path.exists()


def test_task017_audit_rejects_corrupted_journal_and_duplicate_unit(tmp_path):
    root, checkpoint = _repo(tmp_path / "corrupt")
    checkpoint = _create_synthetic_checkpoint(root, _fixture_keys())
    original = checkpoint.read_bytes()
    checkpoint.write_bytes(original + b"{bad json}\n")
    with pytest.raises(portability.PortabilityError, match="invalid journal JSON"):
        portability.audit_checkpoint(checkpoint, root=root, expected_keys=_fixture_keys())
    checkpoint.write_bytes(original + original.splitlines(keepends=True)[1])
    with pytest.raises(portability.PortabilityError, match="duplicate completed unit"):
        portability.audit_checkpoint(checkpoint, root=root, expected_keys=_fixture_keys())


def test_task017_import_rejects_bundle_checksum_and_wrong_specification(tmp_path, monkeypatch):
    _, bundle, _, manifest = _make_bundle(tmp_path, monkeypatch)
    bundle_dir = bundle.parent
    bundle.write_bytes(bundle.read_bytes() + b"corruption")
    with pytest.raises(portability.PortabilityError, match="bundle checksum mismatch"):
        portability.restore_recovery_bundle(bundle_dir, tmp_path / "dest-a", expected_keys=_fixture_keys())

    _, bundle2, _, manifest2 = _make_bundle(tmp_path / "second", monkeypatch)
    manifest2["task016_fingerprint"] = "wrong-specification"
    (bundle2.parent / portability.DEFAULT_MANIFEST_NAME).write_text(json.dumps(manifest2), encoding="utf-8")
    with pytest.raises(portability.PortabilityError, match="Task 016 fingerprint mismatch"):
        portability.restore_recovery_bundle(bundle2.parent, tmp_path / "dest-b", expected_keys=_fixture_keys())

    _, bundle3, _, manifest3 = _make_bundle(tmp_path / "third", monkeypatch)
    manifest3["checkpoint_fingerprint"] = "wrong-checkpoint"
    (bundle3.parent / portability.DEFAULT_MANIFEST_NAME).write_text(json.dumps(manifest3), encoding="utf-8")
    with pytest.raises(portability.PortabilityError, match="checkpoint fingerprint differs"):
        portability.restore_recovery_bundle(bundle3.parent, tmp_path / "dest-c", expected_keys=_fixture_keys())


@pytest.mark.parametrize("sidecar_mode", ("corrupt", "missing", "orphan"))
def test_task017_import_rejects_sidecar_corruption_missing_and_orphan(tmp_path, monkeypatch, sidecar_mode):
    _, bundle, _, manifest = _make_bundle(tmp_path, monkeypatch)

    def mutate(entries, current):
        sidecar_names = [name for name in entries if name.endswith(".npz")]
        if sidecar_mode == "corrupt":
            entries[sidecar_names[0]] += b"bad"
        elif sidecar_mode == "missing":
            del entries[sidecar_names[0]]
        else:
            entries["task017-checkpoint.jsonl.units/orphan.npz"] = b"orphan"

    _rewrite_bundle(bundle.parent, manifest, mutate)
    with pytest.raises(portability.PortabilityError):
        portability.restore_recovery_bundle(bundle.parent, tmp_path / "dest", expected_keys=_fixture_keys())
    assert not (tmp_path / "dest" / portability.DEFAULT_CHECKPOINT_RELATIVE).exists()


def test_task017_import_rejects_corrupt_journal_after_bundle_checksum_passes(tmp_path, monkeypatch):
    _, bundle, _, manifest = _make_bundle(tmp_path, monkeypatch)

    def mutate(entries, current):
        entries["task017-checkpoint.jsonl"] += b"{bad}\n"
        current["journal_sha256"] = hashlib.sha256(entries["task017-checkpoint.jsonl"]).hexdigest()

    _rewrite_bundle(bundle.parent, manifest, mutate)
    with pytest.raises(portability.PortabilityError, match="invalid journal JSON"):
        portability.restore_recovery_bundle(bundle.parent, tmp_path / "dest", expected_keys=_fixture_keys())


def test_task017_import_rejects_incompatible_or_partial_destination(tmp_path, monkeypatch):
    _, bundle, _, _ = _make_bundle(tmp_path, monkeypatch)
    with pytest.raises(portability.PortabilityError, match="tracked Task 017 recovery manifest is absent"):
        portability.restore_recovery_bundle(
            bundle.parent,
            tmp_path / "without-tracked-point",
            expected_keys=_fixture_keys(),
            require_tracked_recovery_point=True,
        )
    destination = tmp_path / "destination"
    units = destination / portability.DEFAULT_CHECKPOINT_RELATIVE.with_name("task017-checkpoint.jsonl.units")
    units.mkdir(parents=True)
    (units / "partial.npz").write_bytes(b"partial")
    with pytest.raises(portability.PortabilityError, match="incompatible or partial"):
        portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())
    assert (units / "partial.npz").read_bytes() == b"partial"


def test_task017_failed_import_cleans_staging_and_installs_nothing(tmp_path, monkeypatch):
    _, bundle, _, _ = _make_bundle(tmp_path, monkeypatch)
    destination = tmp_path / "interrupted"

    def fail_before_install():
        raise OSError("synthetic interruption")

    with pytest.raises(OSError, match="synthetic interruption"):
        portability.restore_recovery_bundle(
            bundle.parent,
            destination,
            expected_keys=_fixture_keys(),
            before_install=fail_before_install,
        )
    derived = destination / "data" / "derived"
    assert not (derived / "task017-checkpoint.jsonl").exists()
    assert not (derived / "task017-checkpoint.jsonl.units").exists()
    assert not list(derived.glob(".task017-import-*"))


def test_task017_import_rejects_partial_staging_directory(tmp_path, monkeypatch):
    _, bundle, _, _ = _make_bundle(tmp_path, monkeypatch)
    destination = tmp_path / "partial-stage"
    stage = destination / "data" / "derived" / ".task017-import-interrupted"
    stage.mkdir(parents=True)
    (stage / "task017-checkpoint.jsonl").write_text("partial", encoding="utf-8")
    with pytest.raises(portability.PortabilityError, match="partial staged import directory"):
        portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())
    assert (stage / "task017-checkpoint.jsonl").read_text(encoding="utf-8") == "partial"
    assert not (destination / portability.DEFAULT_CHECKPOINT_RELATIVE).exists()


def test_task017_import_is_idempotent_only_for_exact_destination(tmp_path, monkeypatch):
    _, bundle, _, _ = _make_bundle(tmp_path, monkeypatch)
    destination = tmp_path / "alternate"
    first = portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())
    second = portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())
    assert second.fingerprint == first.fingerprint
    checkpoint = destination / portability.DEFAULT_CHECKPOINT_RELATIVE
    checkpoint.write_bytes(checkpoint.read_bytes() + b"\n")
    with pytest.raises(portability.PortabilityError):
        portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())


def test_task017_missing_incomplete_recovery_point_cannot_initialize_silently(tmp_path):
    manifest = tmp_path / "recovery-manifest.json"
    checkpoint = tmp_path / "data" / "derived" / "task017-checkpoint.jsonl"
    manifest.write_text(json.dumps({
        "artifact_type": "task017_checkpoint",
        "task": "017",
        "completed_units": 3032,
        "expected_units": 3168,
    }), encoding="utf-8")
    with pytest.raises(RuntimeError, match="restore and audit"):
        require_recovery_for_missing_checkpoint(checkpoint, manifest)
    assert not checkpoint.exists()

    manifest.write_text(json.dumps({
        "artifact_type": "task017_checkpoint",
        "task": "017",
        "completed_units": 3168,
        "expected_units": 3168,
    }), encoding="utf-8")
    require_recovery_for_missing_checkpoint(checkpoint, manifest)


def test_task017_import_requires_exact_tracked_recovery_point_when_present(tmp_path, monkeypatch):
    _, bundle, manifest_path, manifest = _make_bundle(tmp_path, monkeypatch)
    destination = tmp_path / "tracked-destination"
    tracked_path = destination / "artifacts" / "task017" / "recovery-manifest.json"
    tracked_path.parent.mkdir(parents=True)
    tracked_path.write_text(json.dumps({
        "schema_version": "malecns-sim-task017-recovery-point-v1",
        "artifact_type": "task017_checkpoint",
        "task": "017",
        "bundle_filename": bundle.name,
        "bundle_sha256": manifest["bundle_sha256"],
        "recovery_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "task016_fingerprint": manifest["task016_fingerprint"],
        "checkpoint_fingerprint": manifest["checkpoint_fingerprint"],
        "completed_units": manifest["completed_units"],
        "expected_units": manifest["expected_units"],
        "pending_unit_keys": manifest["pending_unit_keys"],
        "variant_completion_counts": manifest["variant_completion_counts"],
    }), encoding="utf-8")
    result = portability.restore_recovery_bundle(bundle.parent, destination, expected_keys=_fixture_keys())
    assert result.fingerprint == manifest["checkpoint_fingerprint"]

    destination2 = tmp_path / "tracked-destination-mismatch"
    tracked_copy = destination2 / "artifacts" / "task017" / "recovery-manifest.json"
    tracked_copy.parent.mkdir(parents=True)
    point = json.loads(tracked_path.read_text(encoding="utf-8"))
    point["pending_unit_keys"] = [{"variant_id": "wrong-unit"}]
    tracked_copy.write_text(json.dumps(point), encoding="utf-8")
    with pytest.raises(portability.PortabilityError, match="tracked Task 017 recovery point"):
        portability.restore_recovery_bundle(bundle.parent, destination2, expected_keys=_fixture_keys())
