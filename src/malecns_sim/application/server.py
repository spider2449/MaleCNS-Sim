"""Loopback HTTP shell for one bounded A002 experiment at a time."""

from __future__ import annotations

import json
import logging
import secrets
import socket
import tempfile
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from .errors import ApplicationError, ErrorCode
from .comparisons import PairingError, build_comparison, build_comparison_playback, verify_pair
from .models import canonical_bytes
from .playback import build_playback
from .retention import ParentResultStore
from .robustness import RobustnessManager, decode_request
from .service import run_experiment
from .serialization import read_result, write_result
from .subgraph import MODES, NODE_CAPS, build_subgraph
from .workbench import DatasetCatalog

MAX_BODY = 2048
HISTORY_LIMIT = 8
STATIC = Path(__file__).parent / "static"


@dataclass(slots=True)
class RunRecord:
    job_id: str
    spec: object
    state: str = "CREATED"
    events: list[dict] = field(default_factory=list)
    result: object | None = None
    error: dict | None = None
    export_path: Path | None = None
    export_hash: str | None = None
    subgraphs: dict[tuple[str, int], dict] = field(default_factory=dict)


class RunManager:
    def __init__(self, catalog: DatasetCatalog, result_root: Path):
        self.catalog = catalog
        self.result_root = result_root
        self.records: OrderedDict[str, RunRecord] = OrderedDict()
        self.lock = threading.Lock()
        self.active = False

    def create(self, spec) -> RunRecord:
        with self.lock:
            if self.active:
                raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "one scientific run is already active")
            self.active = True
            record = RunRecord(uuid4().hex, spec)
            self.records[record.job_id] = record
            while len(self.records) > HISTORY_LIMIT:
                self.records.popitem(last=False)
        threading.Thread(target=self._execute, args=(record,), daemon=True).start()
        return record

    def _execute(self, record: RunRecord) -> None:
        def receive(event):
            with self.lock:
                record.events.append(event.to_dict())
                if event.phase not in ("COMPLETED", "FAILED", "CANCELLED"):
                    record.state = event.phase
        def prepared(prepared_graph):
            snapshots = {}
            run_id = record.events[0]["run_id"] if record.events else None
            for mode in MODES:
                for cap in NODE_CAPS:
                    snapshots[(mode, cap)] = build_subgraph(prepared_graph.projection, record.spec, mode, cap, run_id=run_id)
            with self.lock:
                record.subgraphs = snapshots
        try:
            result = run_experiment(record.spec, self.catalog.files, event_sink=receive, engine=self.catalog.engine, prepared_sink=prepared)
            destination = self.result_root / f"{record.job_id}.json"
            digest = write_result(result, destination)
            read_result(destination, expected_sha256=digest)
            with self.lock:
                record.result = result
                record.export_path = destination
                record.export_hash = digest
                record.state = result.status
                self.active = False
        except ApplicationError as exc:
            with self.lock:
                record.error = exc.to_dict()
                record.result = exc.partial_result
                record.state = exc.partial_result.status if exc.partial_result else "FAILED"
                self.active = False
        except Exception:
            logging.exception("Unhandled local run failure")
            with self.lock:
                record.error = {"code": "SIMULATION_FAILED", "message": "local run failed", "phase": record.state}
                record.state = "FAILED"
                self.active = False
        finally:
            with self.lock:
                self.active = False

    def get(self, job_id: str) -> RunRecord | None:
        with self.lock:
            return self.records.get(job_id)


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def server_close(self) -> None:
        if hasattr(self, "robustness"):
            self.robustness.close()
        if hasattr(self, "parent_results"):
            self.parent_results.close()
        super().server_close()

    def server_bind(self) -> None:
        # Windows SO_REUSEADDR can permit multiple listeners on one port.
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def __init__(self, port: int, catalog: DatasetCatalog | None = None, result_root: Path | None = None):
        self.server_instance_id = uuid4().hex[:12]
        self.token = secrets.token_urlsafe(32)
        self.catalog = catalog or DatasetCatalog.local()
        self.result_root = result_root or Path(tempfile.mkdtemp(prefix="malecns-workbench-"))
        self.manager = RunManager(self.catalog, self.result_root)
        self.parent_results = ParentResultStore(self.token)
        self.robustness = RobustnessManager(self.manager, self.parent_results, self.token)
        self.comparisons: dict[str, tuple[str, str, dict]] = {}
        super().__init__(("127.0.0.1", port), Handler)


class Handler(BaseHTTPRequestHandler):
    server: LocalServer

    def _headers(self, status: int, content_type: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()

    def _json(self, status: int, value: object) -> None:
        body = canonical_bytes(value)
        self._headers(status, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def _valid_request(self, protected: bool = False, mutating: bool = False) -> bool:
        host = self.headers.get("Host", "")
        allowed = f"127.0.0.1:{self.server.server_port}"
        if host != allowed:
            self._json(HTTPStatus.FORBIDDEN, {"error": {"code": "FORBIDDEN", "message": "invalid Host"}})
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin != f"http://{allowed}":
            self._json(HTTPStatus.FORBIDDEN, {"error": {"code": "FORBIDDEN", "message": "invalid Origin"}})
            return False
        if protected and (self.headers.get("X-Local-Session") != self.server.token or (mutating and origin != f"http://{allowed}")):
            self._json(HTTPStatus.FORBIDDEN, {"error": {"code": "FORBIDDEN", "message": "local session required", "session_reason": "missing" if not self.headers.get("X-Local-Session") else "rejected", "server_instance_id": self.server.server_instance_id}})
            return False
        return True

    def _body(self) -> dict | None:
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": {"code": "INVALID_SPEC", "message": "JSON required"}})
            return None
        try:
            size = int(self.headers.get("Content-Length", ""))
            if not 0 < size <= MAX_BODY:
                raise ValueError("invalid body length")
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError("object required")
            return body
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._json(HTTPStatus.BAD_REQUEST, {"error": {"code": "INVALID_SPEC", "message": "invalid bounded JSON body"}})
            return None

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path
        if not self._valid_request(protected=path == "/api/runs" or path.startswith("/api/runs/") or path.startswith("/api/comparisons") or path.startswith("/api/robustness")):
            return
        if path == "/":
            self._static("index.html", "text/html; charset=utf-8")
        elif path in ("/app.js", "/run-status.js", "/playback.js", "/compare.js", "/style.css"):
            self._static(path[1:], "text/javascript; charset=utf-8" if path.endswith(".js") else "text/css; charset=utf-8")
        elif path == "/api/status":
            self._json(200, {"service": "MaleCNS visual workbench", "status": "READY", "active": self.server.manager.active, "server_instance_id": self.server.server_instance_id})
        elif path == "/api/datasets":
            self._json(200, {"datasets": [self.server.catalog.metadata()]})
        elif path == "/api/experiment/options":
            try:
                self._json(200, self.server.catalog.options())
            except ApplicationError as exc:
                self._json(503, {"error": exc.to_dict()})
        elif path == "/api/robustness" or path.startswith("/api/robustness/"):
            parts = path.split("/")
            try:
                query = parse_qs(parsed.query, keep_blank_values=True)
                role = None
                if query:
                    if (len(parts) != 7 or parts[4] != "variants" or parts[6] not in ("playback", "subgraph")
                            or set(query) != {"role"} or query["role"] not in (["baseline"], ["intervention"])):
                        raise ValueError("only a bounded child role filter is supported")
                    role = query["role"][0]
                if path == "/api/robustness":
                    value = {"robustness": self.server.robustness.list()}
                elif len(parts) == 4:
                    value = self.server.robustness.get(parts[3])
                elif len(parts) == 5 and parts[4] in ("events", "export"):
                    value = self.server.robustness.export(parts[3]) if parts[4] == "export" else {"events": self.server.robustness.get(parts[3])["events"]}
                elif len(parts) in (6, 7) and parts[4] == "variants":
                    value = self.server.robustness.variant(parts[3], parts[5]) if len(parts) == 6 else self.server.robustness.evidence(parts[3], parts[5], parts[6], role)
                else:
                    raise ValueError("unknown robustness route")
                self._json(200, value)
            except (ApplicationError, ValueError, KeyError) as exc:
                self._json(409, {"error": {"code": "ROBUSTNESS_UNAVAILABLE", "message": str(exc)}})
        elif path == "/api/runs":
            self._json(200, {"runs": [{"job_id": r.job_id, "state": r.state, "run_id": r.result.identity.run_id if r.result else None,
                                        "mode": r.spec.intervention.kind, "side": r.spec.stimulus.side} for r in self.server.manager.records.values()]})
        elif path == "/api/comparisons/candidates":
            query = parse_qs(parsed.query)
            baseline = self.server.manager.get(query.get("baseline_job_id", [""])[0]) if set(query) == {"baseline_job_id"} and len(query["baseline_job_id"]) == 1 else None
            if baseline is None:
                self._json(404, {"error": {"code": "NOT_FOUND", "message": "baseline run not retained"}})
            else:
                candidates = []
                for record in self.server.manager.records.values():
                    if record.job_id == baseline.job_id:
                        continue
                    try:
                        verify_pair(baseline, record)
                        code = None
                    except PairingError as exc:
                        code = exc.code
                    candidates.append({"job_id": record.job_id, "run_id": record.result.identity.run_id if record.result else None,
                                       "eligible": code is None, "reason": code})
                self._json(200, {"baseline_job_id": baseline.job_id, "candidates": candidates})
        elif path.startswith("/api/comparisons/"):
            parts = path.split("/")
            stored = self.server.comparisons.get(parts[3]) if len(parts) in (4, 5) else None
            if stored is None:
                self._json(404, {"error": {"code": "NOT_FOUND", "message": "comparison not retained"}})
            else:
                baseline = self.server.manager.get(stored[0])
                intervention = self.server.manager.get(stored[1])
                try:
                    current = build_comparison(baseline, intervention)
                    if current != stored[2]:
                        raise PairingError("COMPARISON_IDENTITY_MISMATCH")
                    if len(parts) == 4:
                        self._json(200, current)
                    elif parts[4] == "export":
                        self._json(200, current)
                    elif parts[4] == "playback":
                        query = parse_qs(parsed.query)
                        if set(query) != {"mode", "cap"} or len(query["mode"]) != 1 or len(query["cap"]) != 1 or query["mode"][0] not in MODES or query["cap"][0] not in {str(c) for c in NODE_CAPS}:
                            raise PairingError("INVALID_FILTER")
                        key = (query["mode"][0], int(query["cap"][0]))
                        self._json(200, build_comparison_playback(baseline, intervention, current, baseline.subgraphs[key], intervention.subgraphs[key]))
                    else:
                        self._json(404, {"error": {"code": "NOT_FOUND", "message": "route not found"}})
                except (PairingError, ValueError, KeyError) as exc:
                    self._json(409, {"error": {"code": getattr(exc, "code", "COMPARISON_UNAVAILABLE"), "message": str(exc)}})
        elif path.startswith("/api/runs/"):
            parts = path.split("/")
            record = self.server.manager.get(parts[3]) if len(parts) in (4, 5) else None
            if record is None:
                self._json(404, {"error": {"code": "NOT_FOUND", "message": "run not found"}})
            elif len(parts) == 4:
                self._json(200, {"job_id": record.job_id, "state": record.state, "spec": record.spec.to_dict(), "spec_digest": record.spec.digest, "error": record.error,
                                 "run_id": record.result.identity.run_id if record.result else (record.events[0]["run_id"] if record.events else None)})
            elif parts[4] == "events":
                self._json(200, {"events": list(record.events)})
            elif parts[4] == "subgraph":
                query = parse_qs(parsed.query, keep_blank_values=True)
                if set(query) != {"mode", "cap"} or len(query["mode"]) != 1 or len(query["cap"]) != 1 or query["mode"][0] not in MODES or query["cap"][0] not in {str(c) for c in NODE_CAPS}:
                    self._json(400, {"error": {"code": "INVALID_FILTER", "message": "bounded mode and cap required"}})
                elif record.state == "FAILED":
                    self._json(409, {"error": {"code": "RUN_FAILED", "message": "run failed"}})
                else:
                    view = record.subgraphs.get((query["mode"][0], int(query["cap"][0])))
                    if view is None:
                        self._json(409, {"error": {"code": "GRAPH_PENDING", "message": "Preparing simulation graph"}})
                    else:
                        import copy
                        view = copy.deepcopy(view)
                        if record.result is not None and record.result.status == "COMPLETED" and record.result.trials:
                            if view["graph_fingerprint"] != record.result.provenance["graph_fingerprint"] or view["run_id"] != record.result.identity.run_id or view["spec_digest"] != record.spec.digest:
                                self._json(409, {"error": {"code": "IDENTITY_MISMATCH", "message": "graph and completed result differ"}})
                                return
                            trial = record.result.trials[0]
                            counts = {}
                            for spike in trial.spikes:
                                counts[spike.neuron_id] = counts.get(spike.neuron_id, 0) + 1
                            counts[record.spec.target.neuron_id] = trial.target_spikes
                            for node in view["nodes"]:
                                neuron = node["neuron_id"]
                                if neuron in counts:
                                    node["activity"] = {"available": True, "spike_count": counts[neuron], "firing_rate_hz": trial.target_rate_hz if neuron == record.spec.target.neuron_id else counts[neuron] * 1000.0 / record.spec.duration_ms}
                        self._json(200, view)
            elif parts[4] == "result" and record.result is not None:
                self._json(200, record.result.to_dict())
            elif parts[4] == "playback":
                if record.state != "COMPLETED" or record.result is None:
                    self._json(409, {"error": {"code": "PLAYBACK_UNAVAILABLE", "message": "Playback available after recorded result is finalized." if record.state not in ("FAILED", "CANCELLED") else "No completed playback result."}})
                else:
                    try:
                        payload, body = build_playback(record.result, record.job_id, graph_fingerprint=record.result.provenance["graph_fingerprint"])
                    except (ValueError, KeyError) as exc:
                        self._json(409, {"error": {"code": "PLAYBACK_UNAVAILABLE", "message": str(exc)}})
                    else:
                        self._headers(200, "application/json; charset=utf-8", len(body))
                        self.wfile.write(body)
            elif parts[4] == "export" and record.export_path is not None:
                body = record.export_path.read_bytes()
                self._headers(200, "application/json; charset=utf-8", len(body))
                self.wfile.write(body)
            else:
                self._json(404, {"error": {"code": "NOT_FOUND", "message": "result unavailable"}})
        else:
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "route not found"}})

    def _static(self, name: str, media: str) -> None:
        body = (STATIC / name).read_bytes()
        self._headers(200, media, len(body))
        self.wfile.write(body)

    def do_POST(self) -> None:
        if not self._valid_request(protected=True, mutating=True):
            return
        path = urlsplit(self.path).path
        robustness_action = path.startswith("/api/robustness/") and len(path.split("/")) == 5 and path.split("/")[4] in ("cancel", "release")
        if path not in ("/api/experiments/validate", "/api/runs", "/api/comparisons", "/api/runs/paired-intervention", "/api/robustness") and not robustness_action:
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "route not found"}})
            return
        selection = self._body()
        if selection is None:
            return
        if path == "/api/robustness" or robustness_action:
            try:
                if urlsplit(self.path).query:
                    raise ValueError("unexpected query")
                if robustness_action:
                    if selection:
                        raise ValueError("empty action body required")
                    parts = path.split("/")
                    getattr(self.server.robustness, parts[4])(parts[3])
                    self._json(200, {"robustness_id": parts[3], "action": parts[4]})
                else:
                    spec = decode_request(self.server.catalog, selection)
                    identity = self.server.robustness.create(spec)
                    self._json(202, {"robustness_id": identity, "spec_digest": spec.spec_digest})
            except (ApplicationError, ValueError, TypeError) as exc:
                self._json(400, {"error": {"code": "INVALID_ROBUSTNESS_SPEC", "message": str(exc)}})
            return
        if path == "/api/comparisons":
            if set(selection) != {"baseline_job_id", "intervention_job_id"} or not all(isinstance(v, str) and len(v) == 32 for v in selection.values()):
                self._json(400, {"error": {"code": "INVALID_COMPARISON_SPEC", "message": "registered job IDs required"}})
                return
            try:
                baseline = self.server.manager.get(selection["baseline_job_id"])
                intervention = self.server.manager.get(selection["intervention_job_id"])
                comparison = build_comparison(baseline, intervention)
                self.server.comparisons[comparison["comparison_id"]] = (baseline.job_id, intervention.job_id, comparison)
                self._json(201, comparison)
            except (PairingError, ValueError) as exc:
                self._json(409, {"error": {"code": getattr(exc, "code", "COMPARISON_UNAVAILABLE"), "message": str(exc)}})
            return
        if path == "/api/runs/paired-intervention":
            if set(selection) != {"baseline_job_id"} or not isinstance(selection["baseline_job_id"], str):
                self._json(400, {"error": {"code": "INVALID_SPEC", "message": "baseline job ID required"}})
                return
            baseline = self.server.manager.get(selection["baseline_job_id"])
            if baseline is None or baseline.state != "COMPLETED" or baseline.spec.intervention.kind != "none":
                self._json(409, {"error": {"code": "RESULT_NOT_COMPLETE", "message": "completed baseline required"}})
                return
            source = baseline.spec
            selection = {"dataset_key": "male-cns-v1", "side": source.stimulus.side,
                         "frequency_hz": source.stimulus.frequency_hz, "mode": "outgoing_silence",
                         "backend": source.backend, "seed": source.seed_policy.trial_seeds[0]}
            try:
                spec = self.server.catalog.spec(selection)
                record = self.server.manager.create(spec)
                self._json(202, {"job_id": record.job_id, "spec_digest": spec.digest, "paired_baseline_job_id": baseline.job_id})
            except ApplicationError as exc:
                self._json(409, {"error": exc.to_dict()})
            return
        try:
            spec = self.server.catalog.spec(selection)
            if spec.backend == "cuda" and not self.server.catalog.engine.cuda_available():
                raise ApplicationError(ErrorCode.GPU_UNAVAILABLE, "CUDA backend is unavailable")
            if path.endswith("validate"):
                self._json(200, {"valid": True, "spec": spec.to_dict(), "spec_digest": spec.digest})
            else:
                record = self.server.manager.create(spec)
                self._json(202, {"job_id": record.job_id, "spec_digest": spec.digest})
        except ApplicationError as exc:
            self._json(400 if exc.code != ErrorCode.DATASET_PROVENANCE else 503, {"error": exc.to_dict()})


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Local MaleCNS visual workbench")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--open", action="store_true", help="Open the session URL in the default browser")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0..65535")
    try:
        server = LocalServer(args.port)
    except OSError as exc:
        parser.exit(1, f"Cannot start loopback workbench on port {args.port}: {exc}. Use the default automatic port or choose an available port.\n")
    session_url = f"http://127.0.0.1:{server.server_port}/#token={server.token}"
    print("MaleCNS workbench", flush=True)
    print(f"Server instance: {server.server_instance_id}", flush=True)
    print(f"Open {session_url}", flush=True)
    if args.open:
        import webbrowser
        webbrowser.open(session_url, new=2)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMaleCNS workbench stopped.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
