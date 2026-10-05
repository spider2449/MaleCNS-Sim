"""Explicit one-shot CPU preparation; no simulation or download entry point."""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
import gc
import json
from pathlib import Path
import queue
import sys
import threading
import time
from unittest.mock import patch

import numpy as np

from preparation_identity_contract import expected_identity, observe_identity, compare_identity

from investigate_application_a014 import ProcessJob

MEMORY_CAP = 8589934592
PREPARATION_CAP = 600.0
BATCH_ROWS = 65536
EXPECTED_EFFECTIVE_PROJECTION_FINGERPRINT = expected_identity()["effective_projection_fingerprint"]
EXPECTED_PREPARED_NETWORK_DIGEST = expected_identity()["prepared_network_digest"]
CONFIG_ID = "a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9"
EXPECTED_NEURONS = 166700
EXPECTED_EDGES = 24904953


class BoundedFallback(RuntimeError):
    """Stop before invoking any reference/full-materialization fallback."""


def emit(kind, **fields):
    print(json.dumps(dict(kind=kind, clock_ns=time.perf_counter_ns(), **fields),
                     allow_nan=False), flush=True)


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def verify_sources(root):
    from malecns_sim.application.workbench import DatasetCatalog, SOURCE_FILES
    from malecns_sim.application.service import _file_digest
    catalog = DatasetCatalog(root / "data", None)
    paths = (catalog.files.annotation, catalog.files.neurotransmitter, catalog.files.weights)
    rows = [dict(path=str(path.resolve()), bytes=path.stat().st_size,
                 sha256=_file_digest(path)) for path in paths]
    if any(row["sha256"] != expected for row, (_, expected) in zip(rows, SOURCE_FILES)):
        raise ValueError("A018R-DATASET-PROVENANCE-MISMATCH")
    return catalog.files, rows


@contextmanager
def bounded_route(metrics, notify):
    """Harness-only wiring; all production and certified algorithms are restored."""
    from malecns_sim.analysis import task008
    from malecns_sim.data import integer_aggregation as aggregation
    from malecns_sim.data import experimental_preparation as early
    from malecns_sim.data import feather_batches as batches
    from malecns_sim.data import staged_integer_merge as staged
    times = metrics.setdefault("timings", {})

    def timed(name, function, boundary=False):
        def call(*args, **kwargs):
            if boundary:
                notify("stage", stage=name)
            started = time.perf_counter_ns()
            try:
                return function(*args, **kwargs)
            finally:
                times[name] = times.get(name, 0.0) + (time.perf_counter_ns() - started) / 1e9
                if boundary:
                    notify("boundary", stage=name, timings=dict(times))
        return call

    def reject(trigger):
        def call(*args, **kwargs):
            metrics["fallback"] = trigger
            notify("fallback", trigger=trigger)
            raise BoundedFallback(trigger)
        return call

    original_batches = batches.edge_batches
    @contextmanager
    def observed_batches(*args, **kwargs):
        notify("source_access", stage="source_batches")
        with original_batches(*args, **kwargs) as iterator:
            def iterate():
                while True:
                    started = time.perf_counter_ns()
                    try:
                        table = next(iterator)
                    except StopIteration:
                        times["source_iteration"] = times.get("source_iteration", 0.0) + (time.perf_counter_ns()-started)/1e9
                        return
                    times["source_iteration"] = times.get("source_iteration", 0.0) + (time.perf_counter_ns()-started)/1e9
                    yield table
                    del table
            observed = iterate()
            try:
                yield observed
            finally:
                observed.close()
                notify("boundary", stage="source_processing", timings=dict(times))

    def merger(runs, inner_metrics):
        notify("stage", stage="staged_merge", metrics=inner_metrics)
        last = time.perf_counter()
        def observe(current, following):
            nonlocal last
            if time.perf_counter() - last >= 5:
                notify("progress", stage="staged_merge", metrics=inner_metrics)
                last = time.perf_counter()
        started = time.perf_counter_ns()
        try:
            return staged.merge_staged_integer_runs(runs, inner_metrics, observe)
        finally:
            times["staged_merge"] = (time.perf_counter_ns()-started)/1e9
            notify("boundary", stage="staged_merge", metrics=inner_metrics, timings=dict(times))

    def loader(*args, **kwargs):
        return staged.experimental_load_staged_publication_numeric(*args, **kwargs,
            max_rows_per_batch=BATCH_ROWS, metrics=metrics, merger=merger)

    with ExitStack() as stack:
        stack.enter_context(patch.object(task008, "load_male_cns_v1_numeric", timed("bounded_loader", loader, True)))
        # The loader imports this name inside its function; patch the source too.
        from malecns_sim.data import male_cns_v1
        original_reference = male_cns_v1.load_male_cns_v1_numeric
        def guarded_reference(annotation, nt, weights, mapping):
            if Path(weights).name != "empty.feather":
                return reject("negative_endpoint_reference")(annotation, nt, weights, mapping)
            return original_reference(annotation, nt, weights, mapping)
        stack.enter_context(patch.object(male_cns_v1, "load_male_cns_v1_numeric", guarded_reference))
        stack.enter_context(patch.object(early, "experimental_load_batched_publication_numeric", reject("int64_overflow_reference")))
        stack.enter_context(patch.object(batches, "edge_batches", observed_batches))
        stack.enter_context(patch.object(aggregation, "endpoint_membership", timed("endpoint_membership", aggregation.endpoint_membership)))
        stack.enter_context(patch.object(aggregation, "group_integer_pairs", timed("local_aggregation", aggregation.group_integer_pairs)))
        stack.enter_context(patch.object(male_cns_v1, "select_publication_neuron_ids", timed("publication_universe", male_cns_v1.select_publication_neuron_ids, True)))
        stack.enter_context(patch.object(aggregation, "_publication_from_retained", timed("metadata_normalization", aggregation._publication_from_retained, True)))
        stack.enter_context(patch.object(task008, "project_numeric_connectome", timed("downstream_projection_csr", task008.project_numeric_connectome, True)))
        stack.enter_context(patch.object(task008.SignedAnatomicalConnectome, "from_projection", timed("sign_construction", task008.SignedAnatomicalConnectome.from_projection, True)))
        stack.enter_context(patch.object(task008.EffectiveSignedProjection, "from_signed_connectome", timed("effective_weights_outgoing_csr", task008.EffectiveSignedProjection.from_signed_connectome, True)))
        yield


def prepare_only(files, notify=emit, expected=None):
    from malecns_sim.application.service import ProductionEngine
    from malecns_sim.application.preparation import REFERENCE_CONFIG
    from malecns_sim.application.workbench import PROJECTION_FINGERPRINT
    from malecns_sim.dynamics.lif import PreparedRuntime
    metrics = {}
    prepared = runtime = None
    started = time.perf_counter_ns()
    notify("prepare_start", stage="before_dataset_load", started_ns=started)
    result = dict(completed=False, fallback=None, config=REFERENCE_CONFIG.to_dict(),
                  config_digest=REFERENCE_CONFIG.digest)
    try:
        if REFERENCE_CONFIG.digest != CONFIG_ID:
            raise RuntimeError("reference configuration identity differs")
        with bounded_route(metrics, notify):
            prepared = ProductionEngine().prepare(files, "cpu_reference")
            runtime = PreparedRuntime(prepared.projection, REFERENCE_CONFIG.parameters, 0.1)
        elapsed = (time.perf_counter_ns()-started)/1e9
        result.update(completed=True, preparation_seconds=elapsed)
        notify("prepare_done", stage="prepared_resident", preparation_seconds=elapsed)
        projection = prepared.projection
        observed = observe_identity(prepared, files, REFERENCE_CONFIG.digest)
        expected = expected if expected is not None else expected_identity()
        gates = compare_identity(observed, expected)
        identity_match = all(gates.values())
        finite = all(np.isfinite(getattr(projection, name)).all()
            for name in ("effective_weights_mV", "outgoing_weights_mV"))
        result.update(observed=observed, expected=expected, finite=bool(finite),
                      gates=gates, exact_identity_match=identity_match)
        result["classification"] = ("A018R-TIME-LIMIT" if elapsed > PREPARATION_CAP else
            "A018R-PREPARATION-CERTIFIED" if identity_match and finite else
            "A018R-GRAPH-IDENTITY-MISMATCH")
        del projection
    except BoundedFallback as exc:
        result.update(classification="A018R-BOUNDED-PATH-FALLBACK", fallback=str(exc))
    except Exception as exc:
        result.update(classification="A018R-PREPARATION-ERROR", error=repr(exc))
    finally:
        result["metrics"] = metrics
        prepared = runtime = None
        gc.collect()
        notify("cleanup", stage="released")
    return result


def supervise(command, path):
    """Reuse certified contained-tree accounting and termination, without retry."""
    job = ProcessJob(command)
    messages = queue.Queue()
    def reader():
        for line in job.process.stdout:
            try:
                messages.put(json.loads(line))
            except Exception:
                messages.put(dict(kind="invalid_output", line=line))
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    result = dict(classification="A018R-PREPARATION-ERROR", attempts=0,
                  samples=[], events=[], launcher_pid=job.process.pid)
    phase = "startup"
    phase_start = time.perf_counter_ns()
    preparation_start = None
    result_received = False
    try:
        while job.pids():
            while not messages.empty():
                event = messages.get_nowait()
                if event.get("pid") not in job.pids():
                    raise RuntimeError("worker boundary PID outside contained job")
                result["events"].append(event)
                if event["kind"] == "source_access":
                    result["attempts"] = 1
                if event["kind"] in ("prepare_start", "stage", "boundary", "source_access", "cleanup", "progress"):
                    boundary_memory = job.snapshot()
                    result["samples"].append(dict(clock_ns=time.perf_counter_ns(), stage=event.get("stage", phase), **boundary_memory))
                    if max(boundary_memory["private_bytes"], boundary_memory["working_set"]) > MEMORY_CAP:
                        result["classification"] = "A018R-MEMORY-LIMIT"
                        raise BoundedFallback("memory cap at stage boundary")
                if event["kind"] == "prepare_done":
                    boundary_memory = job.snapshot()
                    result["samples"].append(dict(clock_ns=time.perf_counter_ns(), stage="prepared_resident", **boundary_memory))
                    if max(boundary_memory["private_bytes"], boundary_memory["working_set"]) > MEMORY_CAP:
                        result["classification"] = "A018R-MEMORY-LIMIT"
                        raise BoundedFallback("memory cap at prepared boundary")
                    path.with_suffix(".prepared-captured").write_text("captured\n", encoding="utf-8")
                if event["kind"] == "prepare_start":
                    phase_start = preparation_start = event["started_ns"]
                if event["kind"] == "prepare_done":
                    result["preparation_seconds"] = event["preparation_seconds"]
                    result["completed"] = True
                    preparation_start = None
                    phase_start = event["clock_ns"]
                phase = event.get("stage", phase)
                if event["kind"] == "result":
                    result.update(event["result"])
                    result_received = True
                if event["kind"] in ("fallback", "invalid_output"):
                    result["classification"] = ("A018R-BOUNDED-PATH-FALLBACK" if event["kind"] == "fallback" else "A018R-PREPARATION-ERROR")
                    result["fallback"] = event.get("trigger")
                    raise BoundedFallback(event.get("trigger", "invalid worker output"))
            snapshot = job.snapshot()
            now = time.perf_counter_ns()
            result["samples"].append(dict(clock_ns=now, stage=phase, **snapshot))
            if max(snapshot["private_bytes"], snapshot["working_set"]) > MEMORY_CAP:
                result["classification"] = "A018R-MEMORY-LIMIT"
                break
            if result_received:
                break
            if (now-phase_start)/1e9 > PREPARATION_CAP:
                result["classification"] = "A018R-TIME-LIMIT" if preparation_start else "A018R-PREPARATION-ERROR"
                break
            time.sleep(0.02)
    except BoundedFallback:
        pass
    except Exception as exc:
        result.update(classification="A018R-PREPARATION-ERROR", instrumentation_error=repr(exc))
    finally:
        stopped_ns = time.perf_counter_ns()
        if preparation_start:
            result["interrupted_preparation_seconds"] = (stopped_ns-preparation_start)/1e9
        job.close()
        thread.join(timeout=5)
        # Exiting messages may arrive after the final inventory becomes empty.
        while not messages.empty():
            event = messages.get_nowait()
            result["events"].append(event)
            if event["kind"] == "result" and result["classification"] == "A018R-PREPARATION-ERROR" and "instrumentation_error" not in result:
                result.update(event["result"])
        result.update(orphans=[], exit_code=job.process.returncode)
        result["peak_private_bytes"] = max((s["private_bytes"] for s in result["samples"]), default=0)
        result["peak_working_set"] = max((s["working_set"] for s in result["samples"]), default=0)
        save(path, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorized-real", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.authorized_real:
        parser.error("explicit --authorized-real required")
    if args.worker:
        import os
        def notify(kind, **fields):
            emit(kind, pid=os.getpid(), **fields)
            if kind == "prepare_done":
                while not args.output.with_suffix(".prepared-captured").exists():
                    time.sleep(0.01)
        # Supervisor has already hash-verified these exact paths, without loading edges.
        from malecns_sim.application.workbench import DatasetCatalog
        files = DatasetCatalog(args.root / "data", None).files
        notify("result", result=prepare_only(files, notify))
        while True:
            time.sleep(1)
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    marker = args.output.with_suffix(".attempt-reserved")
    if args.output.exists() or marker.exists() or args.output.with_suffix(".prepared-captured").exists():
        parser.error("one-shot evidence/reservation already exists; no retry")
    files, sources = verify_sources(args.root)
    with marker.open("x", encoding="utf-8") as stream:
        stream.write("A018R one-shot reservation; never remove to retry\n")
    command = [sys.executable, __file__, "--authorized-real", "--worker", "--root",
               str(args.root.resolve()), "--output", str(args.output.resolve())]
    result = supervise(command, args.output)
    result["sources"] = sources
    save(args.output, result)
    print(json.dumps({key: value for key, value in result.items() if key not in ("samples", "events", "metrics")}, indent=2))


if __name__ == "__main__":
    main()
