"""Measure the serial CPU reference for the representative Task 007c workload."""

from __future__ import annotations

import json
import time
from pathlib import Path

from malecns_sim.analysis.task007 import build_task007_result
from malecns_sim.data.male_cns_v1 import official_v1_mapping
from malecns_sim.data.neurotransmitter import load_male_cns_v1_neurotransmitter_evidence
from malecns_sim.dynamics import PoissonStimulus
from malecns_sim.dynamics.cache import PreparedGraphCache
from malecns_sim.dynamics.lif import simulate_lif


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "male-cns" / "v1.0"
CACHE = ROOT / "data" / "derived" / "task007c" / "prepared-graph.npz"


def main() -> None:
    projection = PreparedGraphCache.load(CACHE).to_projection()
    task007 = build_task007_result(
        DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather",
        DATA / "body-neurotransmitters-male-cns-v1.0.feather",
    )
    available = set(projection.neuron_ids.tolist())
    sugar_ids = tuple(int(value) for value in task007.sugar_population.candidate_body_ids if int(value) in available)
    stimulus = PoissonStimulus(sugar_ids, rate_hz=100.0, weight_factor=250.0, seed=600100).generate(100.0, 0.1, 0.275)
    started = time.perf_counter()
    results = tuple(simulate_lif(projection, duration_ms=100.0, stimulus=stimulus) for _ in range(30))
    seconds = time.perf_counter() - started
    print(json.dumps({
        "trial_count": len(results),
        "duration_ms": 100.0,
        "seconds": seconds,
        "trials_per_second": len(results) / seconds,
        "first_digest": results[0].spike_result_digest,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
