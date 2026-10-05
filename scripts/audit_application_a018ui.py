"""Audit-only identity decomposition; no dataset loading or execution entry point."""
import hashlib
import json

import numpy as np

from malecns_sim.graph.sparse import SparseDirectedGraph


def metadata_bytes(value):
    """Mirror the prepared-network JSON contract without replacing its digest."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def fingerprint(value):
    """Fingerprint exact audit bytes, recording array interpretation separately."""
    if isinstance(value, np.ndarray):
        raw = value.tobytes(order="C")
        return dict(sha256=hashlib.sha256(raw).hexdigest(), dtype=str(value.dtype),
                    shape=list(value.shape), bytes=len(raw))
    raw = value if isinstance(value, bytes) else metadata_bytes(value)
    return dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def components(prepared, *, threshold=0, parameters=None, dt_ms=0.1,
               preparation_parameters=None):
    """Inspect an existing small prepared object; never prepare or advance it."""
    signed = prepared.signed_connectome
    graph = signed.connectome
    projection = prepared.projection
    matrix = SparseDirectedGraph.from_numeric_connectome(graph).matrix
    incoming = matrix.T.tocsr()
    retained = signed.signed_edge_mask
    source = np.searchsorted(graph.neuron_ids, graph.source_ids[retained])
    target = np.searchsorted(graph.neuron_ids, graph.target_ids[retained])
    payload = dict(graph=prepared.graph_name, unsigned=projection.unsigned_graph_fingerprint,
                   signed=projection.signed_policy_fingerprint, effective=projection.fingerprint)
    if preparation_parameters is not None:
        payload["parameters"] = preparation_parameters.fingerprint
    values = dict(neuron_ids=graph.neuron_ids, edge_source_ids=graph.source_ids,
                  edge_destination_ids=graph.target_ids, anatomical_counts=graph.synapse_counts,
                  signs=signed.presynaptic_signs, signed_counts=signed.signed_counts,
                  effective_weights=projection.effective_weights_mV,
                  threshold_mask=graph.synapse_counts >= threshold, retained_mask=retained,
                  outgoing_permutation=np.lexsort((target, source)),
                  prepared_sources=projection.source_positions,
                  prepared_targets=projection.target_positions,
                  outgoing_indptr=projection.outgoing_indptr,
                  outgoing_indices=projection.outgoing_targets,
                  outgoing_data=projection.outgoing_weights_mV,
                  anatomical_csr_indptr=matrix.indptr, anatomical_csr_indices=matrix.indices,
                  anatomical_csr_data=matrix.data, incoming_indptr=incoming.indptr,
                  incoming_indices=incoming.indices, incoming_data=incoming.data,
                  policy_config=dict(sign=signed.sign_policy_id,
                                     resolution=signed.resolution_policy_id, threshold=threshold),
                  canonical_metadata=metadata_bytes(payload))
    if parameters is not None:
        values["delay_grid"] = dict(dt_ms=dt_ms, steps=parameters.grid_steps(dt_ms),
                                    parameters=parameters.fingerprint)
    return {name: fingerprint(value) for name, value in values.items()}
