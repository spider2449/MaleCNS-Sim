# Resumable runtime guide

The stable CPU API is `malecns_sim.runtime`. It snapshots an already resolved
`EffectiveSignedProjection` once, creates independent trajectory handles and
advances each handle in place. The implementation is accepted under
[A023-A](../plans/2026-10-07-application-a023-r11-closeout-result.md).
Package metadata is still 0.3.0; the intended application/runtime release is
0.4.0 and has not been published. See the [candidate notes](../releases/0.4.0-preparation.md).

## Synthetic quick start

Use Python >=3.12 and the locked CPU environment (`uv sync --frozen --group dev`
from the checkout). This complete example constructs four synthetic neurons
without datasets or test helpers. It is statically reviewed in A024; fresh
installed-artifact execution is still required by the [release gate](RELEASE_GATE.md).
Its construction objects are existing model/preparation surfaces, not new
supported dataset-loader APIs.

```python
import numpy as np
from collections import Counter
from malecns_sim import EffectiveSignedProjection, ExplicitStimulus, SpikeSchedule
from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence, NeurotransmitterResolutionPolicy,
)
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import Shiu2024SignPolicy
from malecns_sim.runtime import prepare_runtime

graph = NumericNormalizedConnectome(
    np.array([1, 2, 3, 4], dtype=np.int64),
    np.array([1, 1, 2], dtype=np.int64),
    np.array([2, 3, 3], dtype=np.int64),
    np.array([1, 1, 1], dtype=np.int64),
)
curated = CuratedNeuronProjection(graph, 3, 3, 3, 0)
evidence = [
    NeurotransmitterEvidence(neuron_id=i, consensus_nt=label)
    for i, label in ((1, "acetylcholine"), (2, "gaba"),
                     (3, "acetylcholine"), (4, "gaba"))
]
signed = SignedAnatomicalConnectome.from_projection(
    curated, evidence, NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy(),
)
projection = EffectiveSignedProjection.from_signed_connectome(signed)
runtime = prepare_runtime(projection, dt_ms=0.1)
a = runtime.initial_state()
b = runtime.initial_state()

first = runtime.advance(
    a, duration_ms=2.0,
    stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0, 0.1)),), weight_mV=20.0),
)
independent = runtime.advance(b, duration_ms=1.0)
second = runtime.advance(a, duration_ms=2.0)
assert (a.timestep, b.timestep) == (40, 10)
assert (first.start_timestep, first.end_timestep) == (0, 20)
assert (second.start_timestep, second.end_timestep) == (20, 40)
counts = Counter(first.spike_neuron_ids + second.spike_neuron_ids)
print(a.time_ms, b.time_ms, dict(counts))
```

Both states start at rest with fresh pending/refractory storage. Advancing `b`
does not advance `a`; calls above are sequential interleaving. Keeping `a`
across chunks preserves delayed events and refractory deadlines. Creating a new
state resets the trajectory. No particular spike count is asserted by this guide.

## Supported interface and lifecycle

```python
prepare_runtime(projection, *, parameters=REFERENCE_LIF_PARAMETERS, dt_ms=0.1)
runtime.initial_state()
runtime.advance(state, *, duration_ms, stimulus=ExplicitStimulus())
```

Import the reference parameters and existing event/model types from
`malecns_sim` or `malecns_sim.dynamics`. Import PreparedRuntime,
SimulationState and AdvanceResult from `malecns_sim.runtime` for type references;
construct them only through the factory/methods. Runtime properties are backend
(`"cpu"`), dt_ms, neuron_ids (tuple), projection_fingerprint and
parameter_fingerprint. State exposes read-only timestep and time_ms.

The factory copies execution arrays and validates their topology and parameter
agreement. Each state retains its exact runtime owner. Another runtime rejects
it even with the same fingerprints. CPU handles use reference/GC lifetime with
no close/context manager. Copying, serialization, checkpoint restoration,
private-array editing, concurrency, process transfer and CPU/GPU state migration
are outside the supported API. Use sequential process-local calls.

`advance` follows ADV-A: admission errors occur before state mutation. Once
execution/result conversion begins, an ordinary exception poisons only that
state and propagates; no rollback is promised. Further inspection or use of the
failed state raises RuntimeError. Obtain a fresh state; sibling trajectories
remain independent. Process-level interruption is outside this guarantee.

| Error category | Supported meaning |
| --- | --- |
| TypeError | Wrong public object/type; direct handle construction/copy/serialization |
| ValueError | Invalid value/grid/topology/range, weight disagreement or foreign owner |
| KeyError | Unknown stimulus or refractory-free neuron ID |
| RuntimeError | Failed state; experimental GPU closed/busy/device lifecycle conditions |

Messages and validation order are not compatibility promises. Unexpected
execution exceptions keep their original category.

## Time, events and output

Durations are positive grid-aligned milliseconds. The default dt is 0.1 ms;
model delay and refractory intervals must also fit it. Grid acceptance uses
absolute tolerance 1e-10 ms, zero relative tolerance, then canonical integer
steps. Factory/advance numeric arguments accept finite Python int/float values,
excluding bool. Very large timestep/counter/end-time values are rejected.

Input event times are relative to the current chunk: `0 <= t < duration_ms`.
An event at the chunk endpoint belongs at time zero of the next chunk. Only
ExplicitStimulus is accepted by advance. Duplicate event occurrences are
preserved and add direct voltage impulses; schedules refer to neuron IDs, not
array positions. `weight_mV=None` uses the existing model default input weight;
an explicit finite weight overrides it. `refractory_free_neuron_ids` selects
the existing input-neuron refractory exemption, not a new biological mechanism.

AdvanceResult has immutable fields start_timestep, end_timestep, dt_ms,
duration_ms, spike_neuron_ids and spike_timesteps. Paired spike tuples are ordered
by timestep then neuron ID. Output uses absolute post-update steps:
`start_timestep < step <= end_timestep`. Properties start_time_ms, end_time_ms,
spike_times_ms and emitted_spike_count derive from those records. Results are
detached and survive later advances; use Counter as above for sparse counts,
and explicitly add zeros for `runtime.neuron_ids` when dense counts are needed.

This facade provides no voltage/conductance traces, raw buffers, timing hooks,
silencing option or serialized fingerprint/checkpoint envelope. Legacy dense
SimulationResult remains a separate one-shot/internal-runtime result. In the
legacy trace API, each chunk includes its initial boundary column; concatenating
chunks requires retaining that column once and dropping subsequent initial
columns. This does not add trace support to AdvanceResult.

### Generate stochastic input once, then slice

Regenerating a seeded Poisson schedule per chunk changes the trajectory. Generate
one explicit schedule for the full horizon and slice on integer steps, preserving
duplicates, weight and refractory policy. With `runtime` above:

```python
from malecns_sim import PoissonStimulus, REFERENCE_LIF_PARAMETERS

full = PoissonStimulus(neuron_ids=(1,), rate_hz=100.0, seed=7).generate(
    duration_ms=4.0, dt_ms=runtime.dt_ms,
    synaptic_weight_mV=REFERENCE_LIF_PARAMETERS.synaptic_weight_per_anatomical_synapse_mV,
)
state = runtime.initial_state()
for start, stop in ((0, 20), (20, 40)):
    local = ExplicitStimulus(
        schedules=tuple(
            SpikeSchedule(schedule.neuron_id, tuple(
                (step - start) * runtime.dt_ms
                for time in schedule.spike_times_ms
                for step in (int(round(time / runtime.dt_ms)),)
                if start <= step < stop
            ))
            for schedule in full.schedules
        ),
        weight_mV=full.weight_mV,
        refractory_free_neuron_ids=full.refractory_free_neuron_ids,
    )
    result = runtime.advance(
        state, duration_ms=(stop - start) * runtime.dt_ms, stimulus=local,
    )
```

## Support and migration

| Surface | Support |
| --- | --- |
| CPU runtime factory, opaque handles, advance/result contract | Stable public CPU contract selected in A022, implemented in A023 |
| Existing root/dynamics one-shot exports and CLI commands | Retained; no mandatory migration or default change |
| malecns_sim.experimental.gpu | Experimental optional concrete backend |
| Fixed synthetic Arena | Experimental engineered example behavior |
| PreparedNetwork/prepare_network, packing, profiler, Arena adapter internals | Internal; no new dataset/adapter API commitment |

The intended 0.4.x policy preserves supported import names, signatures/defaults,
event/result meaning, ownership and lifecycle. Bug fixes may enforce the
contract; additive optional features require documentation. Deprecations require
notice and a working migration path throughout 0.4.x. Experimental APIs may
change with release-note notice. Cross-platform/dependency byte identity and an
indefinite compatibility promise are not established.

Existing v0.3.0 users may keep simulate_lif, SimulationResult and CLI workflows.
New resumable consumers opt into this module and stop relying on state arrays
or dense legacy results. The legacy `analysis.task008.prepare_network` envelope
can supply `.projection` when already prepared under its own data/policy/cache
requirements; the runtime factory itself loads no files. Dataset preparation
remains internal and separate from this guide's stable factory.

## Experimental GPU and engineered Arena

GPU requires the existing optional extra `cupy-cuda12x[ctk]==14.2.0`, compatible
NVIDIA device/driver/runtime and separately authorized host preflight. It is never
selected implicitly. CPU installation/import does not require CuPy construction.
After preparing a projection and admitting GPU execution on your host:

```python
from malecns_sim.experimental.gpu import prepare_gpu_runtime

gpu = prepare_gpu_runtime(projection)
state = None
try:
    state = gpu.initial_state()
    result = gpu.advance(state, duration_ms=1.0)
finally:
    if state is not None:
        state.close()
    gpu.close()
```

GPU uses exact owner/current-device/busy/closed/failure rules; close is idempotent
and explicit, with no context manager. Runtime close prevents further runtime
operations; retained states keep backing storage until closed/released. No
cross-backend handle interchange is supported. Historical EQ-B is bounded
synthetic equivalence, not universal byte equality or new-wheel device evidence.
[A019V](../plans/2026-10-06-application-a019v-synthetic-cpu-gpu-performance.md)
found CPU faster at all 80 paired positions on its host; GPU performance is paused
and a full-real GPU benchmark is not justified.

The workbench's fixed synthetic Arena demonstrates
`WORLD -> ENGINEERED SENSORY ENCODER -> MaleCNS-Sim -> ENGINEERED MOTOR DECODER -> BODY/WORLD`.
It is not a supported arbitrary adapter framework or a validated biological fly
behavior model. See the [application guide](../application/USER_GUIDE.md).

## Resources and reproducibility

The synthetic examples need no raw data. Full-real preparation requires locally
registered provenance-matching inputs, which are not bundled. Costs depend on
host, graph, output and simultaneous state count; fresh states allocate separate
trajectory storage. No multi-state full-real capacity promise is established.

[A019L](../plans/2026-10-06-application-a019l-full-real-cpu-rebenchmark.md)
observed 166,700 neurons / 24,904,953 effective edges, 98.5804007 s preparation,
sampled contained-tree private peak 5,441,220,608 B under an 8-GiB cap, and mean
1.094710500 s per 20-ms call (54.735525x slower than realtime) on its Windows
i9-7900X host. These are historical observations, not minimum RAM, instantaneous
peak or universal speed guarantees. Replay used two fresh 12-call/240-ms states:
24 aggregate calls, not one 480-ms trajectory. No benchmark rerun is needed for
ordinary API use or release preparation.

Use the [release gate](RELEASE_GATE.md) for exact source/lock/wheel custody and
fresh artifact requirements. Preserve A023's bounded zero-payload/I0/I2 claims;
I1 protected integrity is NOT RUN. Earlier invalidated validation and
PE3-UNRESOLVED remain historical. No new scientific question, biological
mechanism, brain reconstruction, digital twin or realtime claim follows from
this engineering API.
