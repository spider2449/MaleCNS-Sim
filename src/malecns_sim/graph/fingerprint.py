"""Stable, explicit fingerprints for normalized CSR graph state."""

from __future__ import annotations

import hashlib
import struct

from malecns_sim.graph.sparse import SparseDirectedGraph


def graph_fingerprint(graph: SparseDirectedGraph) -> str:
    """Hash IDs and CSR arrays without relying on object serialization."""

    digest = hashlib.sha256()

    def add_bytes(value: bytes) -> None:
        digest.update(struct.pack("<Q", len(value)))
        digest.update(value)

    if hasattr(graph.neuron_ids, "dtype"):
        add_bytes(graph.neuron_ids.tobytes(order="C"))
    else:
        for neuron_id in graph.neuron_ids:
            add_bytes(neuron_id.encode("utf-8"))
    for array in (graph.matrix.indptr, graph.matrix.indices, graph.matrix.data):
        add_bytes(str(array.dtype).encode("ascii"))
        add_bytes(array.tobytes(order="C"))
    return digest.hexdigest()
