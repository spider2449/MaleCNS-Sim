"""Bounded session-owned parent evidence, independent of Recent Runs eviction."""

from __future__ import annotations

import secrets
import threading
from uuid import uuid4

from .errors import ApplicationError, ErrorCode
from .models import ExperimentResult, canonical_bytes
from .preparation import VariantExperimentSpec

MAX_PARENTS = 2
MAX_CHILDREN = 16
MAX_PARENT_BYTES = 64_000_000


class ParentResultStore:
    """Retain immutable encoded results until explicit release or session shutdown.

    A full store rejects admission; it never evicts a parent's children. IDs are
    server generated. No filesystem paths are accepted or resolved by this store.
    """

    def __init__(self, session_token: str):
        if not isinstance(session_token, str) or not session_token:
            raise ValueError("session token required")
        self._session_token = session_token
        self._parents: dict[str, dict[str, bytes]] = {}
        self._lock = threading.Lock()
        self._closed = False

    def _authorize(self, token):
        if not isinstance(token, str) or not secrets.compare_digest(token, self._session_token):
            raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "parent/session ownership mismatch")

    def create(self, token: str) -> str:
        self._authorize(token)
        with self._lock:
            if self._closed or len(self._parents) >= MAX_PARENTS:
                raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "parent retention capacity reached")
            parent = uuid4().hex
            self._parents[parent] = {}
            return parent

    def retain(self, token: str, parent: str, result: ExperimentResult) -> str:
        self._authorize(token)
        result.verify_integrity()
        if not isinstance(result.executed_spec, VariantExperimentSpec):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "parent children require variant execution identity")
        encoded = canonical_bytes(result.to_dict())
        child = result.identity.run_id
        with self._lock:
            children = self._owned(parent)
            if child in children:
                if children[child] != encoded:
                    raise ApplicationError(ErrorCode.INVALID_SPEC, "child identity already retained")
                return child
            if len(children) >= MAX_CHILDREN or sum(map(len, children.values())) + len(encoded) > MAX_PARENT_BYTES:
                raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "parent evidence capacity reached")
            children[child] = encoded
        return child

    def _owned(self, parent):
        if self._closed or not isinstance(parent, str) or parent not in self._parents:
            raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "unknown parent ownership")
        return self._parents[parent]

    def get(self, token: str, parent: str, child: str) -> ExperimentResult:
        import json

        self._authorize(token)
        with self._lock:
            encoded = self._owned(parent).get(child)
            if encoded is None:
                raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "unknown child ownership")
        return ExperimentResult.from_dict(json.loads(encoded))

    def children(self, token: str, parent: str) -> tuple[str, ...]:
        self._authorize(token)
        with self._lock:
            return tuple(self._owned(parent))

    def release(self, token: str, parent: str) -> None:
        self._authorize(token)
        with self._lock:
            self._owned(parent)
            del self._parents[parent]

    def close(self) -> None:
        with self._lock:
            self._parents.clear()
            self._closed = True
