"""Loopback HTTP shell for one bounded A002 experiment at a time."""

from __future__ import annotations

import json
import logging
import secrets
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
from .models import canonical_bytes
from .playback import build_playback
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
        except ApplicationError as exc:
            with self.lock:
                record.error = exc.to_dict()
                record.result = exc.partial_result
                record.state = exc.partial_result.status if exc.partial_result else "FAILED"
        except Exception:
            logging.exception("Unhandled local run failure")
            with self.lock:
                record.error = {"code": "SIMULATION_FAILED", "message": "local run failed", "phase": record.state}
                record.state = "FAILED"
        finally:
            with self.lock:
                self.active = False

    def get(self, job_id: str) -> RunRecord | None:
        with self.lock:
            return self.records.get(job_id)


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int, catalog: DatasetCatalog | None = None, result_root: Path | None = None):
        self.token = secrets.token_urlsafe(32)
        self.catalog = catalog or DatasetCatalog.local()
        self.result_root = result_root or Path(tempfile.mkdtemp(prefix="malecns-workbench-"))
        self.manager = RunManager(self.catalog, self.result_root)
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
            self._json(HTTPStatus.FORBIDDEN, {"error": {"code": "FORBIDDEN", "message": "local session required"}})
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
        if not self._valid_request(protected=path == "/api/runs" or path.startswith("/api/runs/")):
            return
        if path == "/":
            self._static("index.html", "text/html; charset=utf-8")
        elif path in ("/app.js", "/playback.js", "/style.css"):
            self._static(path[1:], "text/javascript; charset=utf-8" if path.endswith(".js") else "text/css; charset=utf-8")
        elif path == "/api/status":
            self._json(200, {"service": "MaleCNS visual workbench", "status": "READY", "active": self.server.manager.active})
        elif path == "/api/datasets":
            self._json(200, {"datasets": [self.server.catalog.metadata()]})
        elif path == "/api/experiment/options":
            try:
                self._json(200, self.server.catalog.options())
            except ApplicationError as exc:
                self._json(503, {"error": exc.to_dict()})
        elif path == "/api/runs":
            self._json(200, {"runs": [{"job_id": r.job_id, "state": r.state} for r in self.server.manager.records.values()]})
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
        if path not in ("/api/experiments/validate", "/api/runs"):
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "route not found"}})
            return
        selection = self._body()
        if selection is None:
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
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0..65535")
    server = LocalServer(args.port)
    print(f"Open http://127.0.0.1:{server.server_port}/#token={server.token}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
