"""Fresh-process synthetic A016/A017 comparison; never opens real inputs."""
import argparse
import gc
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from unittest.mock import patch

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather

import certify_application_a015 as oracle
from malecns_sim.data.experimental_preparation import experimental_load_batched_publication_numeric
from malecns_sim.data.integer_aggregation import experimental_load_aggregated_publication_numeric


def measure(rows, pattern, route):
    with tempfile.TemporaryDirectory(prefix="malecns-a017-synthetic-") as directory:
        files = oracle.a014.synthetic_files(Path(directory), 1, 2000)
        sequence = np.arange(rows, dtype=np.int64)
        excluded = sequence % (2 if pattern == "cardinality" else 10) != 0
        retained_index = sequence // (2 if pattern == "cardinality" else 10)
        cardinality = {"high": 10, "moderate": 1000, "unique": rows, "cardinality": rows}[pattern]
        pair = retained_index % cardinality
        source, target = pair // 2000 + 1, pair % 2000 + 1
        source[excluded] = 9999999
        feather.write_feather(pa.table({"body_pre": source, "body_post": target,
                                       "weight": np.ones(rows, dtype=np.int64)}), files[2], chunksize=65536)
        del sequence, excluded, retained_index, pair, source, target
        gc.collect()
        monitor = oracle.a014.WindowsMemory(os.getpid())
        samples = [monitor.snapshot()]
        stop = threading.Event()
        def sample():
            while not stop.wait(0.001):
                samples.append(monitor.snapshot())
        thread = threading.Thread(target=sample)
        thread.start()
        metrics = {}
        loader = experimental_load_batched_publication_numeric if route == "reference" else experimental_load_aggregated_publication_numeric
        loader_seconds = 0.0
        def timed_loader(*args, **kwargs):
            nonlocal loader_seconds
            start = time.perf_counter()
            result = loader(*args, metrics=metrics, **kwargs)
            loader_seconds += time.perf_counter() - start
            return result
        started = time.perf_counter()
        try:
            with patch("malecns_sim.analysis.task008.load_male_cns_v1_numeric", timed_loader):
                prepared = oracle.prepare_network(*files)
            seconds = time.perf_counter() - started
        finally:
            samples.append(monitor.snapshot())
            stop.set()
            thread.join()
            monitor.close()
        retained = (rows + (1 if pattern == "cardinality" else 9)) // (2 if pattern == "cardinality" else 10)
        return {"rows": rows, "pattern": pattern, "route": route, "baseline": samples[0],
                "peak_private": max(s["private_bytes"] for s in samples),
                "peak_working_set": max(s["working_set"] for s in samples),
                "seconds": seconds, "loader_seconds": loader_seconds,
                "downstream_seconds": seconds - loader_seconds,
                "metrics": metrics, "fingerprint": prepared.fingerprint,
                "retained_rows": retained, "raw_retained_bytes": 24 * retained,
                "prepared_memory_bytes": prepared.memory_bytes,
                "final_pairs": prepared.signed_connectome.connectome.synapse_counts.size}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--pattern", choices=("high", "moderate", "unique", "cardinality"), required=True)
    parser.add_argument("--route", choices=("reference", "aggregated"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.rows <= 3000000:
        parser.error("synthetic rows must be 1..3000000")
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(measure(args.rows, args.pattern, args.route), stream, indent=2)
