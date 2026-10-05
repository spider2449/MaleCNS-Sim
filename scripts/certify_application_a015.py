"""Synthetic-only A015 oracle comparison and isolated memory measurements."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

import numpy as np

from malecns_sim.analysis.task008 import prepare_network
from malecns_sim.data.experimental_preparation import experimental_load_publication_numeric

spec = importlib.util.spec_from_file_location("a014", Path(__file__).with_name("investigate_application_a014.py"))
a014 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a014)


def synthetic_files(directory, rows, seed=15):
    """Bounded high-exclusion files; unknown positive IDs remain valid rows."""
    import pyarrow as pa
    import pyarrow.feather as feather
    files = a014.synthetic_files(directory, 1, 100)
    rng = np.random.default_rng(seed)
    source = rng.integers(101, 10000000, rows, dtype=np.int64)
    target = rng.integers(101, 10000000, rows, dtype=np.int64)
    selected = np.arange(0, rows, 10)
    source[selected] = rng.integers(1, 101, selected.size)
    target[selected] = rng.integers(1, 101, selected.size)
    feather.write_feather(pa.table({"body_pre": source, "body_post": target,
                                    "weight": rng.integers(0, 10, rows)}), files[2])
    return files


def proposed(files, **kwargs):
    """Test-only scoped loader substitution; production dispatch stays intact."""
    with patch("malecns_sim.analysis.task008.load_male_cns_v1_numeric",
               experimental_load_publication_numeric):
        return prepare_network(*files, **kwargs)


def assert_exact(reference, candidate):
    """Compare existing canonical identities plus every scientific array."""
    assert reference.fingerprint == candidate.fingerprint
    assert reference.projection.fingerprint == candidate.projection.fingerprint
    for field in ("neuron_ids", "source_positions", "target_positions", "effective_weights_mV",
                  "outgoing_indptr", "outgoing_targets", "outgoing_weights_mV"):
        left, right = getattr(reference.projection, field), getattr(candidate.projection, field)
        assert left.dtype == right.dtype
        np.testing.assert_array_equal(left, right)
    for field in ("neuron_ids", "source_ids", "target_ids", "synapse_counts"):
        np.testing.assert_array_equal(getattr(reference.signed_connectome.connectome, field),
                                      getattr(candidate.signed_connectome.connectome, field))
    for field in ("presynaptic_signs", "signed_counts", "signed_edge_mask",
                  "resolved_neurotransmitters", "neuron_signs"):
        np.testing.assert_equal(getattr(reference.signed_connectome, field),
                                getattr(candidate.signed_connectome, field))
    assert reference.signed_connectome.connectome.annotated_neurons == candidate.signed_connectome.connectome.annotated_neurons
    assert reference.projection.synaptic_weight_mV == candidate.projection.synaptic_weight_mV
    from malecns_sim.graph.sparse import SparseDirectedGraph
    left = SparseDirectedGraph.from_numeric_connectome(reference.signed_connectome.connectome)
    right = SparseDirectedGraph.from_numeric_connectome(candidate.signed_connectome.connectome)
    for field in ("indptr", "indices", "data"):
        np.testing.assert_array_equal(getattr(left.matrix, field), getattr(right.matrix, field))
    assert left.node_index == right.node_index


def measure(rows, route):
    with tempfile.TemporaryDirectory(prefix="malecns-a015-synthetic-") as directory:
        files = synthetic_files(Path(directory), rows)
        monitor = a014.WindowsMemory(os.getpid())
        before = monitor.snapshot()
        started = time.perf_counter()
        probe = a014.PreparationProbe()
        probe.names = probe.names | {"experimental_load_publication_numeric", "endpoint_membership"}
        with probe:
            prepared = prepare_network(*files) if route == "reference" else proposed(files)
        seconds = time.perf_counter() - started
        monitor.close()
        highest = max(probe.rows, key=lambda row: row["private_bytes"])
        return {"rows": rows, "route": route, "before": before, "seconds": seconds,
                "sampled_peak_private": highest["private_bytes"],
                "sampled_peak_working_set": max(row["working_set"] for row in probe.rows),
                "highest_stage": highest["stage"], "effective_bytes": prepared.memory_bytes,
                "fingerprint": prepared.fingerprint, "trace": probe.rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-rows", type=int, required=True)
    parser.add_argument("--route", choices=("reference", "prototype"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.synthetic_rows <= 1000000:
        parser.error("synthetic rows must be 1..1000000")
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(measure(args.synthetic_rows, args.route), stream, indent=2)
