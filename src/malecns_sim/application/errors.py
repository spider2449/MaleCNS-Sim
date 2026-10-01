"""Stable application error categories."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_SPEC = "INVALID_SPEC"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    UNSUPPORTED_BACKEND = "UNSUPPORTED_BACKEND"
    GPU_UNAVAILABLE = "GPU_UNAVAILABLE"
    DATASET_PROVENANCE = "DATASET_PROVENANCE"
    PREPARATION_FAILED = "PREPARATION_FAILED"
    SIMULATION_FAILED = "SIMULATION_FAILED"
    CANCELLED = "CANCELLED"
    RESULT_SERIALIZATION = "RESULT_SERIALIZATION"


@dataclass
class ApplicationError(Exception):
    code: ErrorCode
    message: str
    phase: str | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, str | None]:
        return {"code": self.code.value, "message": self.message, "phase": self.phase}
