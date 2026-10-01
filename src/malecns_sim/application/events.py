"""Controlled lifecycle and serializable execution events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable

from .errors import ApplicationError, ErrorCode
from .models import EVENT_SCHEMA, canonical_bytes


class State(StrEnum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    LOADING_DATA = "LOADING_DATA"
    PREPARING_NETWORK = "PREPARING_NETWORK"
    RUNNING = "RUNNING"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


_NEXT = {
    State.CREATED: State.VALIDATING,
    State.VALIDATING: State.LOADING_DATA,
    State.LOADING_DATA: State.PREPARING_NETWORK,
    State.PREPARING_NETWORK: State.RUNNING,
    State.RUNNING: State.FINALIZING,
    State.FINALIZING: State.COMPLETED,
}


class EventType(StrEnum):
    RUN_STARTED = "RunStarted"
    PHASE_CHANGED = "PhaseChanged"
    TRIAL_STARTED = "TrialStarted"
    TRIAL_COMPLETED = "TrialCompleted"
    RUN_COMPLETED = "RunCompleted"
    RUN_FAILED = "RunFailed"
    RUN_CANCELLED = "RunCancelled"
    WARNING = "Warning"
    SPIKE_BATCH = "SpikeBatch"
    POPULATION_ACTIVITY_SAMPLE = "PopulationActivitySample"
    TRACE_SAMPLE = "TraceSample"
    SIMULATION_TIME_ADVANCED = "SimulationTimeAdvanced"


_VISUAL = {EventType.SPIKE_BATCH, EventType.POPULATION_ACTIVITY_SAMPLE, EventType.TRACE_SAMPLE, EventType.SIMULATION_TIME_ADVANCED}


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    event_schema_version: str
    run_id: str
    invocation_id: str
    sequence: int
    timestamp: str
    phase: str
    event_type: str
    visualization_only: bool
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = {name: getattr(self, name) for name in self.__dataclass_fields__}
        canonical_bytes(data)
        return data


class Lifecycle:
    def __init__(self, run_id: str, invocation_id: str, sink: Callable[[ExecutionEvent], None] | None = None):
        self.run_id = run_id
        self.invocation_id = invocation_id
        self.state = State.CREATED
        self.sequence = 0
        self.sink = sink
        self.events: list[ExecutionEvent] = []

    def emit(self, kind: EventType, payload: dict[str, Any] | None = None) -> ExecutionEvent:
        self.sequence += 1
        event = ExecutionEvent(EVENT_SCHEMA, self.run_id, self.invocation_id, self.sequence, datetime.now(timezone.utc).isoformat(), self.state.value, kind.value, kind in _VISUAL, payload or {})
        event.to_dict()
        self.events.append(event)
        if self.sink is not None:
            self.sink(event)
        return event

    def transition(self, state: State, *, payload: dict[str, Any] | None = None) -> None:
        if self.state not in _NEXT or (state != _NEXT[self.state] and state not in (State.FAILED, State.CANCELLED)):
            raise ApplicationError(ErrorCode.INVALID_SPEC, f"invalid state transition {self.state} -> {state}")
        self.state = state
        self.emit(EventType.PHASE_CHANGED, payload)
