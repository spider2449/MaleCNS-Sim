"""Small JSON provenance manifest and local SHA-256 verification boundary."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_METADATA_KIND = (
    "file size, timestamp, and SHA-256 are measured locally; no official "
    "checksum is implied"
)


@dataclass(frozen=True, slots=True)
class FileProvenance:
    """Published source identity plus locally measured file metadata."""

    source_url: str
    local_filename: str
    byte_size: int
    sha256: str
    validated_at_utc: str
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True, slots=True)
class DatasetProvenance:
    dataset_name: str
    release: str
    source_organization: str
    official_dataset_page: str
    adapter_schema_version: str
    files: tuple[FileProvenance, ...]
    metadata_kind: str = DEFAULT_METADATA_KIND


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_provenance(
    path: str | Path,
    *,
    source_url: str,
    validated_at_utc: str | None = None,
    etag: str | None = None,
    last_modified: str | None = None,
) -> FileProvenance:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    return FileProvenance(
        source_url=source_url,
        local_filename=path.name,
        byte_size=path.stat().st_size,
        sha256=sha256_file(path),
        validated_at_utc=validated_at_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        etag=etag,
        last_modified=last_modified,
    )


def write_manifest(path: str | Path, provenance: DatasetProvenance) -> None:
    payload: dict[str, Any] = asdict(provenance)
    payload["files"] = [asdict(file) for file in provenance.files]
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_manifest(path: str | Path) -> DatasetProvenance:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "dataset_name",
        "release",
        "source_organization",
        "official_dataset_page",
        "adapter_schema_version",
        "files",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"provenance manifest is missing required fields: {missing!r}")
    files = tuple(FileProvenance(**item) for item in payload["files"])
    return DatasetProvenance(
        dataset_name=payload["dataset_name"],
        release=payload["release"],
        source_organization=payload["source_organization"],
        official_dataset_page=payload["official_dataset_page"],
        adapter_schema_version=payload["adapter_schema_version"],
        files=files,
        metadata_kind=payload.get("metadata_kind", DEFAULT_METADATA_KIND),
    )


def verify_file(path: str | Path, expected: FileProvenance) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_size = path.stat().st_size
    actual_sha256 = sha256_file(path)
    return {
        "path": str(path),
        "expected_byte_size": expected.byte_size,
        "actual_byte_size": actual_size,
        "expected_sha256": expected.sha256,
        "actual_sha256": actual_sha256,
        "valid": actual_size == expected.byte_size and actual_sha256 == expected.sha256,
    }
