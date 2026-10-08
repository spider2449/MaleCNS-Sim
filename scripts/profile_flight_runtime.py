"""Guarded synthetic profiling of 0.2-ms public runtime chunks at 166700 IDs."""
import validation_firewall
if not validation_firewall.ACTIVE:
    raise RuntimeError("source firewall required")

from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from malecns_sim.dynamics.lif import EffectiveSignedProjection
from malecns_sim.runtime import prepare_runtime, _preflight
from malecns_sim.dynamics.stimulus import ExplicitStimulus

n = 166700
projection = EffectiveSignedProjection(
    neuron_ids=np.arange(1, n+1, dtype=np.int64),
    source_positions=np.empty(0, dtype=np.int64), target_positions=np.empty(0, dtype=np.int64),
    effective_weights_mV=np.empty(0), outgoing_indptr=np.zeros(n+1, dtype=np.int64),
    outgoing_targets=np.empty(0, dtype=np.int64), outgoing_weights_mV=np.empty(0),
    synaptic_weight_mV=0.275, fingerprint="synthetic-profile", unsigned_graph_fingerprint="synthetic-profile",
    signed_policy_fingerprint="synthetic-profile", sign_policy_id="synthetic-profile", resolution_policy_id="synthetic-profile",
    excluded_unresolved_edge_count=0, excluded_anatomical_weight=0, included_anatomical_weight=0)
runtime = prepare_runtime(projection)
state = runtime.initial_state()
stimulus = ExplicitStimulus()

def median_ms(function):
    values = []
    for _ in range(30):
        start = time.perf_counter()
        function()
        values.append((time.perf_counter()-start)*1000)
    return statistics.median(values)

before = median_ms(lambda: set(runtime.neuron_ids))
cached = median_ms(lambda: _preflight(runtime, state, 0.2, stimulus))
advance = median_ms(lambda: runtime.advance(state, duration_ms=0.2, stimulus=stimulus))
print({"fixture": "synthetic-empty-graph-166700-ids", "old_membership_rebuild_ms": before,
       "cached_full_preflight_ms": cached, "full_advance_ms": advance,
       "real_source_access": False, "claim": "synthetic overhead measurement only"})
