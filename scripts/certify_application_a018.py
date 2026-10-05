"""Fresh-process synthetic A017/A018 merge-only memory comparison."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import numpy as np

from investigate_application_a014 import WindowsMemory
from malecns_sim.data.integer_aggregation import group_integer_pairs, merge_integer_runs
from malecns_sim.data.staged_integer_merge import merge_staged_integer_runs


def measure(rows, pattern, route):
    size = 1024 if pattern == "many" else 250000 if pattern == "few" else 65536
    cardinality = 10 if pattern == "high" else 10000 if pattern == "moderate" else rows
    runs = []
    for start in range(0, rows, size):
        keys = np.arange(start, min(start+size, rows), dtype=np.int64) % cardinality
        runs.append(group_integer_pairs(keys // 2000, keys % 2000, np.ones(keys.size, dtype=np.int64)))
    del keys
    gc.collect()
    monitor = WindowsMemory(os.getpid())
    samples = [monitor.snapshot()]
    stop = threading.Event()
    def sample():
        while not stop.wait(0.001):
            samples.append(monitor.snapshot())
    thread = threading.Thread(target=sample)
    thread.start()
    metrics = {}
    initial_runs = len(runs)
    partial_bytes = sum(a.nbytes for run in runs for a in run)
    try:
        result = (merge_integer_runs if route == "reference" else merge_staged_integer_runs)(runs, metrics)
    finally:
        samples.append(monitor.snapshot())
        stop.set()
        thread.join()
        monitor.close()
    digest = hashlib.sha256()
    for column in result:
        digest.update(memoryview(column))
    return dict(rows=rows, pattern=pattern, route=route, initial_runs=initial_runs,
                partial_bytes=partial_bytes, baseline=samples[0],
                peak_private=max(s["private_bytes"] for s in samples),
                peak_working_set=max(s["working_set"] for s in samples),
                metrics=metrics, digest=digest.hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--rows", type=int)
    parser.add_argument("--pattern", choices=("high", "moderate", "unique", "many", "few"))
    parser.add_argument("--route", choices=("reference", "staged"))
    args = parser.parse_args()
    if args.matrix:
        observations = []
        for rows in (100000, 1000000, 3000000):
            for pattern in ("high", "moderate", "unique", "many", "few"):
                pair = []
                for route in ("reference", "staged"):
                    result = subprocess.run([sys.executable, __file__, "--rows", str(rows),
                        "--pattern", pattern, "--route", route], check=True, capture_output=True, text=True)
                    observation = json.loads(result.stdout)
                    pair.append(observation)
                    observations.append(observation)
                assert pair[0]["digest"] == pair[1]["digest"]
                print(rows, pattern, "exact", flush=True)
        with args.matrix.open("x", encoding="utf-8") as stream:
            json.dump(observations, stream, indent=2)
        sys.exit(0)
    if args.rows is None or args.pattern is None or args.route is None:
        parser.error("provide --matrix or --rows/--pattern/--route")
    if not 1 <= args.rows <= 3000000:
        parser.error("synthetic rows must be 1..3000000")
    print(json.dumps(measure(args.rows, args.pattern, args.route)))
