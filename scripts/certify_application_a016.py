"""Fresh-process bounded synthetic memory and stage-time certification."""
import argparse
from functools import partial
import gc
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
from unittest.mock import patch

import certify_application_a015 as oracle
from malecns_sim.data.experimental_preparation import experimental_load_batched_publication_numeric


def measure(rows, route, size):
    with tempfile.TemporaryDirectory(prefix="malecns-a016-synthetic-") as directory:
        files = oracle.synthetic_files(Path(directory), rows)
        if size < 65536:
            import pyarrow.feather as feather
            table = feather.read_table(files[2])
            feather.write_feather(table, files[2], chunksize=size)
            del table
        gc.collect()
        monitor = oracle.a014.WindowsMemory(os.getpid())
        before = monitor.snapshot()
        samples = [before]
        stop = threading.Event()
        def sample():
            while not stop.wait(0.001):
                samples.append(monitor.snapshot())
        thread = threading.Thread(target=sample)
        thread.start()
        totals = {}
        batch_times = {}
        stage_memory = {}
        starts = {}
        names = {"get_batch": "source", "_integer_column": "validation",
                 "endpoint_membership": "membership", "concatenate": "concatenation",
                 "_aggregate_numeric_edges": "grouping", "read_table": "source",
                 "argsort": "sort_primitive", "unique": "unique_primitive"}
        def profile(frame, event, arg):
            name = frame.f_code.co_name if event in ("call", "return") else getattr(arg, "__name__", "")
            if name in names:
                key = (id(frame), name)
                if event in ("call", "c_call"):
                    starts[key] = time.perf_counter()
                elif event in ("return", "c_return") and key in starts:
                    stage = names[name]
                    totals[stage] = totals.get(stage, 0) + time.perf_counter() - starts.pop(key)
                    snapshot = monitor.snapshot()
                    previous = stage_memory.get(stage, {"private_bytes": 0, "working_set": 0})
                    stage_memory[stage] = {key: max(previous[key], snapshot[key]) for key in previous}
            return profile
        started = time.perf_counter()
        try:
            sys.setprofile(profile)
            if route == "reference":
                prepared = oracle.prepare_network(*files)
            else:
                with patch("malecns_sim.analysis.task008.load_male_cns_v1_numeric",
                           partial(experimental_load_batched_publication_numeric, max_rows_per_batch=size, metrics=batch_times)):
                    prepared = oracle.prepare_network(*files)
            seconds = time.perf_counter() - started
        finally:
            sys.setprofile(None)
            samples.append(monitor.snapshot())
            stop.set()
            thread.join()
            monitor.close()
        return {"rows": rows, "route": route, "batch_rows": size, "before": before,
                "private": max(x["private_bytes"] for x in samples + list(stage_memory.values())),
                "working_set": max(x["working_set"] for x in samples + list(stage_memory.values())), "seconds": seconds,
                "stage_seconds": totals, "fingerprint": prepared.fingerprint,
                "stage_memory": stage_memory,
                "batch_seconds": batch_times,
                "retained_rows": (rows + 9)//10, "retained_bytes": 24*((rows+9)//10)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--route", choices=("reference", "batched"), required=True)
    parser.add_argument("--batch-rows", type=int, default=65536)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.rows <= 2000000:
        parser.error("synthetic rows must be 1..2000000")
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(measure(args.rows, args.route, args.batch_rows), stream, indent=2)
