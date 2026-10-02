"""Smoke an explicitly supplied local launcher without executing real simulations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import queue
import re
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-only", action="store_true")
    parser.add_argument("--launcher", nargs="+", required=True)
    args = parser.parse_args()
    if args.cpu_only and importlib.util.find_spec("cupy") is not None:
        raise RuntimeError("CPU-only smoke requires an environment without CuPy")
    import malecns_sim
    from malecns_sim.application.robustness import SCHEMA

    lines = queue.Queue()
    process = subprocess.Popen(args.launcher, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    def receive():
        for line in process.stdout:
            lines.put(line)
    reader = threading.Thread(target=receive, daemon=True)
    reader.start()
    try:
        deadline = time.monotonic() + 30
        url = None
        while time.monotonic() < deadline:
            try:
                line = lines.get(timeout=.25)
            except queue.Empty:
                if process.poll() is not None:
                    raise RuntimeError("launcher exited before startup")
                continue
            match = re.search(r"http://127\.0\.0\.1:\d+/#token=\S+", line)
            if match:
                url = match[0]
                break
        if url is None:
            raise RuntimeError("startup URL unavailable")
        base, token = url.split("/#token=")
        with urlopen(base + "/", timeout=5) as response:
            assert response.status == 200
        for route in ("/api/robustness", "/api/robustness/" + "0" * 64 + "/export"):
            try:
                urlopen(base + route, timeout=5)
            except HTTPError as exc:
                assert exc.code == 403
            else:
                raise AssertionError("robustness API did not require session protection")
        request = Request(base + "/api/robustness", headers={"X-Local-Session": token})
        with urlopen(request, timeout=5) as response:
            assert json.load(response) == {"robustness": []}
        print(json.dumps({"startup": "PASS", "session_protection": "PASS", "schema": SCHEMA,
                          "cpu_only": args.cpu_only, "package_source": malecns_sim.__file__,
                          "real_simulations": 0}, sort_keys=True))
    finally:
        # Stop only the helper process created by this smoke script.
        if sys.platform == "win32" and process.poll() is None:
            # uv and Windows entry-point shims can have descendants holding the pipe.
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           capture_output=True, check=True)
        elif process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        process.stdout.close()
        reader.join(timeout=2)


if __name__ == "__main__":
    main()
