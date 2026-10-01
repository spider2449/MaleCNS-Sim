"""Atomic, hash-checked JSON result interchange."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .errors import ApplicationError, ErrorCode
from .models import ExperimentResult, canonical_bytes


def write_result(result: ExperimentResult, path: Path) -> str:
    """Write a manifest under a caller-controlled result directory and return its file SHA-256."""
    result.verify_integrity()
    payload = canonical_bytes(result.to_dict()) + b"\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".result-", suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "result manifest write failed") from exc
    return hashlib.sha256(payload).hexdigest()


def read_result(path: Path, *, expected_sha256: str | None = None) -> ExperimentResult:
    try:
        payload = Path(path).read_bytes()
        if expected_sha256 is not None and hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "result file SHA-256 mismatch")
        return ExperimentResult.from_dict(json.loads(payload))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "result manifest read failed") from exc
