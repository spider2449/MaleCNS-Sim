"""Local live viewer for a running closed loop: circuit graph, spike raster, rates and game frame.

Read-only, loopback-only and token protected. The loop publishes one row per decision;
the page polls for rows newer than the last one it holds. Nothing here steers the loop.
"""

from collections import deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
import json
import secrets
import threading
from urllib.parse import parse_qs, urlsplit

_CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
        "img-src 'self'; connect-src 'self'")


class LiveView:
    def __init__(self, meta: dict, *, history: int = 600, port: int = 0):
        self.meta = json.loads(json.dumps(meta, allow_nan=False))
        self.token = secrets.token_urlsafe(24)
        self._lock = threading.Lock()
        self._rows: deque = deque(maxlen=history)
        self._seq, self._frame = 0, None
        self._page = resources.files("malecns_sim.application").joinpath("static/closed_loop.html").read_bytes()
        view = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status, body, content_type):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", _CSP)
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                parts = urlsplit(self.path)
                query = parse_qs(parts.query)
                port_text = str(view.server.server_port)
                if self.headers.get("Host") not in (f"127.0.0.1:{port_text}", f"localhost:{port_text}"):
                    return self._send(HTTPStatus.FORBIDDEN, b"bad host", "text/plain")
                if not secrets.compare_digest(query.get("token", [""])[0], view.token):
                    return self._send(HTTPStatus.FORBIDDEN, b"token required", "text/plain")
                if parts.path == "/":
                    return self._send(HTTPStatus.OK, view._page, "text/html; charset=utf-8")
                if parts.path == "/api/meta":
                    return self._send(HTTPStatus.OK, json.dumps(view.meta).encode(), "application/json")
                if parts.path == "/api/state":
                    try:
                        since = int(query.get("since", ["0"])[0])
                    except ValueError:
                        return self._send(HTTPStatus.BAD_REQUEST, b"bad since", "text/plain")
                    with view._lock:
                        rows = [row for row in view._rows if row["seq"] > since]
                    return self._send(HTTPStatus.OK, json.dumps({"rows": rows}).encode(), "application/json")
                if parts.path == "/frame.png":
                    with view._lock:
                        frame = view._frame
                    if frame is None:
                        return self._send(HTTPStatus.NOT_FOUND, b"no frame yet", "text/plain")
                    return self._send(HTTPStatus.OK, frame, "image/png")
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, name="closed-loop-view", daemon=True)
        self.thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}/?token={self.token}"

    def publish(self, row: dict, frame_png: bytes | None = None) -> None:
        with self._lock:
            self._seq += 1
            self._rows.append({**row, "seq": self._seq})
            if frame_png is not None:
                self._frame = frame_png

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
