"""Serial, session-owned robustness orchestration over certified preparation variants."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import re
import threading
import time
from types import SimpleNamespace

from .comparisons import build_comparison, build_comparison_playback
from .errors import ApplicationError, ErrorCode
from .models import ExperimentSpec, InterventionSpec, RunIdentity, canonical_bytes
from .playback import build_playback
from .preparation import PRESET_ID, PRESET_DIGEST, OVERRIDES, VariantExperimentSpec, digest, resolve_variant
from .service import _schedule, _file_digest, run_experiment
from .subgraph import build_subgraph

SCHEMA = "application-robustness-v1"
DOMAIN = "malecns-application-robustness-v1"
VARIANTS = tuple(v for v, _ in OVERRIDES)
NO_AGGREGATE_RULE = "NO_AGGREGATE_RULE"
METADATA_BYTES = 512_000
MAX_EVENTS = 256
TERMINAL = {"COMPLETE", "PARTIAL", "FAILED", "CANCELLED"}


def invalid(message):
    return ApplicationError(ErrorCode.INVALID_SPEC, message)


@dataclass(frozen=True, slots=True)
class RobustnessSpec:
    base_spec: ExperimentSpec
    variant_ids: tuple[str, ...] = VARIANTS
    schema_version: str = SCHEMA
    preset_id: str = PRESET_ID
    preset_digest: str = PRESET_DIGEST
    pairing_policy: str = "A006_EXACT_SAME_VARIANT"
    reuse_policy: str = "EXACT_REUSE_OR_EXECUTE"
    schedule_policy: str = "SAME_REALIZED_EVENT_TIMES"
    failure_policy: str = "STOP_ON_VARIANT_FAILURE"
    aggregate_rule: str = NO_AGGREGATE_RULE

    def __post_init__(self):
        if (not isinstance(self.base_spec, ExperimentSpec) or self.base_spec.trial_count != 1
                or self.base_spec.intervention.kind != "none" or self.base_spec.robustness.kind != "none"
                or type(self.variant_ids) is not tuple or not self.variant_ids
                or any(type(v) is not str or v not in VARIANTS for v in self.variant_ids)
                or len(set(self.variant_ids)) != len(self.variant_ids)
                or self.schema_version != SCHEMA or self.preset_id != PRESET_ID
                or self.preset_digest != PRESET_DIGEST or self.pairing_policy != "A006_EXACT_SAME_VARIANT"
                or self.reuse_policy not in ("EXACT_REUSE_OR_EXECUTE", "EXECUTE_ONLY")
                or self.schedule_policy != "SAME_REALIZED_EVENT_TIMES"
                or self.failure_policy != "STOP_ON_VARIANT_FAILURE" or self.aggregate_rule != NO_AGGREGATE_RULE):
            raise invalid("unsupported bounded robustness contract")
        for variant in self.variant_ids:
            self.child_spec(variant, "baseline")

    def child_spec(self, variant, role):
        if variant not in self.variant_ids or role not in ("baseline", "intervention"):
            raise invalid("unknown variant or role")
        intervention = InterventionSpec("outgoing_silence", (self.base_spec.target.neuron_id,)) if role == "intervention" else self.base_spec.intervention
        return VariantExperimentSpec(replace(self.base_spec, intervention=intervention), resolve_variant(self.preset_id, variant))

    def to_dict(self):
        return {"schema_version": self.schema_version, "base_spec": self.base_spec.to_dict(),
                "target": self.base_spec.to_dict()["target"],
                "intervention": {"kind": "outgoing_silence", "target_ids": [self.base_spec.target.neuron_id]},
                "seed_policy": self.base_spec.to_dict()["seed_policy"],
                "preset_id": self.preset_id, "preset_digest": self.preset_digest,
                "variant_ids": list(self.variant_ids), "pairing_policy": self.pairing_policy,
                "reuse_policy": self.reuse_policy, "schedule_policy": self.schedule_policy,
                "failure_policy": self.failure_policy, "aggregate_rule": self.aggregate_rule}

    @property
    def canonical_bytes(self):
        return canonical_bytes(self.to_dict())

    @property
    def spec_digest(self):
        return digest(DOMAIN + "-spec", self.to_dict())

    @property
    def robustness_id(self):
        return digest(DOMAIN, self.to_dict())

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw, dict):
            raise invalid("robustness object required")
        try:
            value = cls(ExperimentSpec.from_dict(raw["base_spec"]), tuple(raw["variant_ids"]),
                        **{k: raw[k] for k in ("schema_version", "preset_id", "preset_digest", "pairing_policy", "reuse_policy", "schedule_policy", "failure_policy", "aggregate_rule")})
            if canonical_bytes(raw) != value.canonical_bytes:
                raise invalid("robustness spec fields differ")
            return value
        except (KeyError, TypeError, ValueError) as exc:
            raise invalid("invalid robustness spec") from exc


def event_schedule_evidence(spec):
    """Fingerprint actual event IDs/times, excluding the prescribed variant amplitude."""
    schedules = tuple(_schedule(spec, seed) for seed in spec.seed_policy.trial_seeds)
    payload = {"schema_version": "application-input-event-schedule-v1", "dt_ms": spec.dt_ms,
               "duration_ms": spec.duration_ms,
               "trials": [{"seed": seed, "refractory_free_neuron_ids": s.refractory_free_neuron_ids,
                           "schedules": [{"neuron_id": item.neuron_id, "times_ms": item.spike_times_ms} for item in s.schedules]}
                          for seed, s in zip(spec.seed_policy.trial_seeds, schedules)]}
    return {"schedule_fingerprint": digest("malecns-application-input-event-schedule-v1", payload),
            "stimulus_fingerprints": [s.fingerprint for s in schedules],
            "event_counts": [sum(len(item.spike_times_ms) for item in s.schedules) for s in schedules],
            "input_amplitudes_mv": [s.weight_mV for s in schedules],
            "rule": "Exact realized neuron IDs/event times and time grid; amplitude follows A007A variant."}


@dataclass(frozen=True, slots=True)
class RobustnessResult:
    payload_bytes: bytes
    authoritative_digest: str

    @classmethod
    def create(cls, payload):
        encoded = canonical_bytes(payload)
        return cls(encoded, digest(DOMAIN + "-result", payload))

    def to_dict(self):
        value = json.loads(self.payload_bytes)
        if digest(DOMAIN + "-result", value) != self.authoritative_digest:
            raise invalid("robustness result integrity mismatch")
        return {**value, "authoritative_digest": self.authoritative_digest}


class Sweep:
    def __init__(self, spec, parent):
        self.spec, self.parent = spec, parent
        self.cancel = threading.Event()
        self.state = "CREATED"
        self.started = time.perf_counter()
        self.events = []
        self.current_variant = self.current_role = self.current_phase = None
        self.schedule_fingerprint = None
        self.warnings = ["Simulation comparison; no biological causal verdict.", "No aggregate robustness verdict requested."]
        self.variants = [{"variant_id": v, "definition": resolve_variant(spec.preset_id, v).to_dict(),
                          "variant_digest": resolve_variant(spec.preset_id, v).digest,
                          "state": "PENDING", "baseline": None, "intervention": None,
                          "comparison": None, "schedule_evidence": None, "error": None} for v in spec.variant_ids]

    def result(self):
        return RobustnessResult.create({"schema_version": SCHEMA, "robustness_id": self.spec.robustness_id,
               "spec_digest": self.spec.spec_digest, "preset_id": self.spec.preset_id,
               "preset_digest": self.spec.preset_digest, "variants": self.variants,
               "overall_state": self.state, "warnings": self.warnings,
               "aggregate_rule": self.spec.aggregate_rule, "aggregate_result": None,
               "schedule_fingerprint": self.schedule_fingerprint})


class RobustnessManager:
    """Whole-parent ownership shares RunManager's one-scientific-run admission lock.

    Parent evidence lives for this server session. It is not a disk checkpoint.
    One immutable combined/160 graph per child is retained; playback/comparison
    are reconstructed only from integrity-checked parent result snapshots.
    """

    def __init__(self, run_manager, store, token):
        self.runs, self.store, self.token = run_manager, store, token
        self.sweeps = {}
        self.lock = threading.RLock()
        self.closed = False

    def create(self, spec, *, background=True):
        if not isinstance(spec, RobustnessSpec):
            raise invalid("RobustnessSpec required")
        with self.lock, self.runs.lock:
            if self.closed or self.runs.active:
                raise invalid("scientific execution ownership unavailable")
            if spec.robustness_id in self.sweeps:
                return spec.robustness_id
            parent = self.store.create(self.token)
            sweep = Sweep(spec, parent)
            try:
                self._publish(sweep)
            except Exception:
                self.store.release(self.token, parent)
                raise
            self.sweeps[spec.robustness_id] = sweep
            self.runs.active = True
        if background:
            threading.Thread(target=self._execute, args=(sweep,), daemon=True).start()
        else:
            self._execute(sweep)
        return spec.robustness_id

    def _publish(self, sweep):
        snapshot = {"spec": sweep.spec.to_dict(), "result": sweep.result().to_dict(),
                    "events": sweep.events,
                    "progress": {"completed_variants": sum(v["state"] in ("COMPLETE", "REUSED") for v in sweep.variants),
                                 "total_variants": len(sweep.variants), "current_variant": sweep.current_variant,
                                 "current_role": sweep.current_role, "current_phase": sweep.current_phase},
                    "elapsed_seconds": time.perf_counter() - sweep.started}
        size = len(canonical_bytes({"snapshot": snapshot, "padding": ""}))
        if size > METADATA_BYTES:
            raise invalid("bounded parent metadata capacity reached")
        self.store.retain_evidence(self.token, sweep.parent, "metadata", {"snapshot": snapshot, "padding": " " * (METADATA_BYTES - size)})

    def _event(self, sweep, phase, **payload):
        with self.lock:
            sweep.current_phase = phase
            if len(sweep.events) >= MAX_EVENTS:
                raise invalid("bounded sweep event capacity reached")
            sweep.events.append({"sequence": len(sweep.events), "phase": phase,
                                 "variant_id": sweep.current_variant, "role": sweep.current_role,
                                 "completed_variants": sum(v["state"] in ("COMPLETE", "REUSED") for v in sweep.variants),
                                 "total_variants": len(sweep.variants), **payload})
            self._publish(sweep)

    def _owned(self, robustness_id):
        if not isinstance(robustness_id, str) or not re.fullmatch(r"[0-9a-f]{64}", robustness_id) or robustness_id not in self.sweeps:
            raise invalid("unknown bounded robustness ID")
        return self.sweeps[robustness_id]

    def get(self, robustness_id):
        with self.lock:
            sweep = self._owned(robustness_id)
            return self.store.evidence(self.token, sweep.parent, "metadata")["snapshot"]

    def list(self):
        with self.lock:
            return [{"robustness_id": key, "overall_state": self.get(key)["result"]["overall_state"]} for key in self.sweeps]

    def cancel(self, robustness_id):
        with self.lock:
            sweep = self._owned(robustness_id)
            if sweep.state not in TERMINAL:
                sweep.cancel.set()

    def release(self, robustness_id):
        with self.lock:
            sweep = self._owned(robustness_id)
            if sweep.state not in TERMINAL:
                raise invalid("active sweep cannot be released")
            self.store.release(self.token, sweep.parent)
            del self.sweeps[robustness_id]

    def close(self):
        with self.lock:
            self.closed = True
            for sweep in self.sweeps.values():
                sweep.cancel.set()

    def _check_cancel(self, sweep):
        if sweep.cancel.is_set():
            raise ApplicationError(ErrorCode.CANCELLED, "parent cancelled at a cooperative boundary")

    def _graph(self, result, view):
        result.verify_integrity()
        if (view["run_id"] != result.identity.run_id or view["spec_digest"] != result.executed_spec.digest
                or view["graph_fingerprint"] != result.provenance.get("graph_fingerprint")
                or view["filter_definition"]["mode"] != "combined" or view["filter_definition"]["node_cap"] != 160):
            raise invalid("retained graph identity mismatch")
        return {"view": view, "digest": digest(DOMAIN + "-graph", view)}

    def _graph_get(self, parent, result):
        envelope = self.store.evidence(self.token, parent, "graph:" + result.identity.run_id)
        if digest(DOMAIN + "-graph", envelope["view"]) != envelope["digest"]:
            raise invalid("retained graph integrity mismatch")
        return self._graph(result, envelope["view"])["view"]

    def _reusable(self, sweep, spec, identity):
        rejected = []
        if sweep.spec.reuse_policy == "EXECUTE_ONLY":
            return None, None, {"policy": "EXECUTE_ONLY", "rejected": []}
        for source in list(self.sweeps.values()):
            for child in self.store.children(self.token, source.parent):
                try:
                    result = self.store.get(self.token, source.parent, child)
                    if result.executed_spec.digest != spec.digest:
                        rejected.append({"run_id": child, "reason": "EXACT_SPEC_MISMATCH"})
                        continue
                    if result.status != "COMPLETED" or result.identity != identity:
                        raise invalid("exact execution identity mismatch")
                    view = self._graph_get(source.parent, result)
                    return result, view, {"source_robustness_id": source.spec.robustness_id, "rejected": rejected}
                except (ApplicationError, KeyError) as exc:
                    rejected.append({"run_id": child, "reason": str(exc)})
        return None, None, {"policy": "EXACT_REUSE_OR_EXECUTE", "rejected": rejected, "reason": "NO_EXACT_REUSABLE_CHILD"}

    def _child(self, sweep, variant, role):
        self._check_cancel(sweep)
        spec = sweep.spec.child_spec(variant["variant_id"], role)
        evidence = event_schedule_evidence(spec)
        if evidence["schedule_fingerprint"] != sweep.schedule_fingerprint:
            raise invalid("A007B-SCHEDULE-CONTRACT-GAP: cross-variant realized events differ")
        identity = RunIdentity.create(spec, tuple(evidence["stimulus_fingerprints"]), spec.dataset.projection_fingerprint)
        with self.lock:
            result, view, lookup = self._reusable(sweep, spec, identity)
        provenance = "REUSED" if result else "EXECUTED"
        sweep.current_role = role
        variant["state"] = "BASELINE_RUNNING" if role == "baseline" else "INTERVENTION_RUNNING"
        self._event(sweep, "CHILD_REUSED" if result else "CHILD_STARTED", provenance=provenance)
        if result is None:
            graphs = []
            def prepared(value):
                graph = build_subgraph(value.projection, spec, "combined", 160, run_id=identity.run_id)
                graph.pop("extraction_seconds", None)
                graph.pop("serialized_bytes", None)
                graphs.append(graph)
            def receive(event):
                # Only actual phase transitions are forwarded; no fabricated simulation fraction.
                if event.event_type == "PhaseChanged":
                    self._event(sweep, event.phase)
            try:
                result = run_experiment(spec, self.runs.catalog.files, engine=self.runs.catalog.engine,
                                        prepared_sink=prepared, event_sink=receive)
            except ApplicationError as exc:
                partial = exc.partial_result
                if partial is not None:
                    with self.lock:
                        self.store.retain(self.token, sweep.parent, partial)
                        variant[role] = {"run_id": partial.identity.run_id, "job_id": partial.invocation_id,
                                         "spec_digest": spec.digest, "result_digest": partial.authoritative_digest,
                                         "variant_digest": spec.variant.digest, "graph_fingerprint": None,
                                         "schedule_fingerprint": identity.schedule_fingerprints[0],
                                         "provenance": "EXECUTED", "reuse_lookup": lookup,
                                         "status": partial.status, "error": exc.to_dict()}
                raise
            if result.identity != identity or result.identity.schedule_fingerprints != tuple(evidence["stimulus_fingerprints"]):
                raise invalid("executed child schedule/identity mismatch")
            view = graphs[0]
        with self.lock:
            self.store.retain_evidence(self.token, sweep.parent, "graph:" + result.identity.run_id, self._graph(result, view))
            self.store.retain(self.token, sweep.parent, result)
            variant[role] = {"run_id": result.identity.run_id, "job_id": result.invocation_id,
                             "spec_digest": spec.digest, "result_digest": result.authoritative_digest,
                             "variant_digest": spec.variant.digest, "graph_fingerprint": result.provenance["graph_fingerprint"],
                             "schedule_fingerprint": result.trials[0].schedule_fingerprint,
                             "provenance": provenance, "reuse_lookup": lookup}
            variant["schedule_evidence"] = evidence
            variant["state"] = "BASELINE_COMPLETE" if role == "baseline" else "COMPARING"
            self._event(sweep, "CHILD_RETAINED", provenance=provenance)
        return SimpleNamespace(spec=spec, state="COMPLETED", result=result, job_id=result.invocation_id)

    def _execute(self, sweep):
        current = None
        try:
            sweep.state = "VALIDATING"
            self._event(sweep, "VALIDATING")
            self._check_cancel(sweep)
            files, dataset = self.runs.catalog.files, sweep.spec.base_spec.dataset
            if files.manifest_digest != dataset.manifest_digest or files.mapping_fingerprint != dataset.mapping_fingerprint:
                raise invalid("registered dataset identity mismatch")
            for path, expected in ((files.annotation, dataset.annotation_sha256), (files.neurotransmitter, dataset.neurotransmitter_sha256), (files.weights, dataset.weights_sha256)):
                if _file_digest(path) != expected:
                    raise invalid("registered dataset source digest mismatch")
            fingerprints = {event_schedule_evidence(sweep.spec.child_spec(v, role))["schedule_fingerprint"] for v in sweep.spec.variant_ids for role in ("baseline", "intervention")}
            if len(fingerprints) != 1:
                raise invalid("A007B-SCHEDULE-CONTRACT-GAP: requested variant events differ")
            sweep.schedule_fingerprint = fingerprints.pop()
            sweep.state = "RUNNING"
            for current in sweep.variants:
                sweep.current_variant = current["variant_id"]
                self._check_cancel(sweep)
                baseline = self._child(sweep, current, "baseline")
                self._check_cancel(sweep)
                intervention = self._child(sweep, current, "intervention")
                self._check_cancel(sweep)
                self._event(sweep, "COMPARING")
                current["comparison"] = build_comparison(baseline, intervention)
                current["state"] = "REUSED" if all(current[r]["provenance"] == "REUSED" for r in ("baseline", "intervention")) else "COMPLETE"
                self._event(sweep, "VARIANT_COMPLETE")
            self._check_cancel(sweep)
            sweep.state = "FINALIZING"
            self._event(sweep, "FINALIZING")
            self._check_cancel(sweep)
            sweep.state = "COMPLETE"
        except Exception as exc:
            cancelled = isinstance(exc, ApplicationError) and exc.code == ErrorCode.CANCELLED
            if current is not None and current["state"] not in ("COMPLETE", "REUSED"):
                current["state"] = "CANCELLED" if cancelled else "FAILED"
                current["error"] = {"code": getattr(getattr(exc, "code", None), "value", "SWEEP_FAILED"), "message": str(exc)}
            sweep.state = "CANCELLED" if cancelled else "PARTIAL" if any(v["state"] in ("COMPLETE", "REUSED") for v in sweep.variants) else "FAILED"
            sweep.warnings.append(str(exc))
        finally:
            sweep.current_role = None
            try:
                self._event(sweep, sweep.state)
            finally:
                with self.runs.lock:
                    self.runs.active = False

    def variant(self, robustness_id, variant_id):
        if variant_id not in VARIANTS:
            raise invalid("invalid variant ID")
        snapshot = self.get(robustness_id)
        for variant in snapshot["result"]["variants"]:
            if variant["variant_id"] == variant_id:
                return variant
        raise invalid("variant not requested by parent")

    def _record(self, sweep, variant, role):
        child = variant[role]
        if child is None:
            raise invalid("child evidence pending")
        result = self.store.get(self.token, sweep.parent, child["run_id"])
        spec = sweep.spec.child_spec(variant["variant_id"], role)
        if (result.executed_spec.digest != spec.digest or result.authoritative_digest != child["result_digest"]
                or result.identity.run_id != child["run_id"] or result.invocation_id != child["job_id"]
                or spec.variant.digest != child["variant_digest"]
                or result.provenance["graph_fingerprint"] != child["graph_fingerprint"]):
            raise invalid("parent child identity mismatch")
        return SimpleNamespace(spec=spec, result=result, job_id=child["job_id"], state=result.status)

    def evidence(self, robustness_id, variant_id, kind, role=None):
        with self.lock:
            sweep = self._owned(robustness_id)
            variant = self.variant(robustness_id, variant_id)
            if role is not None:
                if role not in ("baseline", "intervention") or kind not in ("subgraph", "playback"):
                    raise invalid("unsupported child evidence selection")
                record = self._record(sweep, variant, role)
                view = self._graph_get(sweep.parent, record.result)
                if kind == "subgraph":
                    return {"variant_digest": variant["variant_digest"], "role": role, "view": view}
                payload, _ = build_playback(record.result, record.job_id, graph_fingerprint=view["graph_fingerprint"])
                return {"variant_digest": variant["variant_digest"], "role": role, "playback": payload}
            a, b = [self._record(sweep, variant, role) for role in ("baseline", "intervention")]
            comparison = build_comparison(a, b)
            if canonical_bytes(comparison) != canonical_bytes(variant["comparison"]):
                raise invalid("comparison identity mismatch")
            if kind == "comparison":
                return comparison
            views = [self._graph_get(sweep.parent, r.result) for r in (a, b)]
            if kind == "subgraph":
                ids = [set(n["neuron_id"] for n in view["nodes"]) for view in views]
                return {"baseline": views[0], "intervention": views[1],
                        "shared_node_ids": sorted(ids[0] & ids[1]), "union_node_ids": sorted(ids[0] | ids[1]),
                        "variant_digest": variant["variant_digest"]}
            if kind == "playback":
                return build_comparison_playback(a, b, comparison, *views)
            raise invalid("unknown evidence route")

    def export(self, robustness_id):
        snapshot = self.get(robustness_id)
        payload = {"schema_version": "application-robustness-export-v1", "robustness_id": robustness_id,
                   "spec": snapshot["spec"], "result": snapshot["result"]}
        return {**payload, "authoritative_digest": digest(DOMAIN + "-export", payload)}


def decode_request(catalog, raw):
    allowed = {"selection", "preset_id", "variant_ids", "reuse_policy", "aggregate_rule"}
    if not isinstance(raw, dict) or set(raw) != allowed or not isinstance(raw["variant_ids"], list):
        raise invalid("exact bounded robustness request fields required")
    return RobustnessSpec(catalog.spec(raw["selection"]), tuple(raw["variant_ids"]),
                          preset_id=raw["preset_id"], reuse_policy=raw["reuse_policy"], aggregate_rule=raw["aggregate_rule"])
