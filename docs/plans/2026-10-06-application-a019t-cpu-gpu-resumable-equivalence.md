# A019T CPU/GPU resumable equivalence

Authorization: 授權 A019T. Starting local/origin/live master:
`99357ac3af23c3ebf2b44fb48d3902dfe81d010e`. Initial worktree, staging and stash
empty; version 0.3.0; tracked workflows zero.

Plan: freeze the existing CPU reference and A019S GPU subject, use common
small synthetic fixtures, compare every chunk boundary and canonical result,
certify C1-C10, admission, ring edges and fresh-state GPU repeatability with
rtol=atol=2e-13. Run scoped regressions, compileall and diff check under the
existing fail-closed Python/Arrow source guard. Commit and push the coherent
terminal evidence. No performance execution, real data, scientific changes,
downloads, archives, Arena, version change, tag or release.

CPU reference: dynamics/lif.py PreparedRuntime.initial_state/advance,
SimulationState and simulate_lif; shared stimulus.py schedule_events packs
ordered chunk-relative events and preserves multiplicity. Float64 v/g and
pending [delay+1,N], int32 pending counts, int64 inclusive absolute refractory
deadlines; integer timestep controls physical ring cursor. Direct input,
pending delivery, linear integration, strict threshold/reset, ordered enqueue,
then immutable SimulationResult materialization. No CPU edits authorized.

GPU subject: dynamics/cuda.py GPUPreparedRuntime and GPUSimulationState,
initial_state/advance/_advance_device. Same retained array shapes/dtypes,
absolute clock and inclusive deadlines, shared event admission, ordered
incoming scheduler, state-private buffers and explicit close. Shared static
CSR/runtime survives state-A close. Test snapshots read device arrays only.

CPU has no close API: C10 drops its A reference; GPU explicitly closes A.
Released-GPU-state rejection is an additional device lifecycle guarantee,
not a CPU API requirement. Special floats use the frozen finite-only policy;
signed zero is numerically admitted but byte equality is reported separately.

## Terminal certification

**A019T-A — CPU/GPU RESUMABLE-STATE EQ-B CERTIFIED.** Application equivalence
is now **EQ-B CERTIFIED** for the bounded synthetic application contract.
A019S-A remains preserved. Selected byte-exact results do not promote policy
to EQ-A or establish universal correctness or performance readiness.

Preflight PASS: NVIDIA GeForce RTX 3060, one device, CuPy 14.2.0, driver API
13000, runtime API 12090; float64 allocation/arithmetic and NVRTC compilation
pass. Existing nonfatal CUDA-path discovery warning did not prevent execution.
Frozen/offline GPU extra used without dependency or environment changes.

CPU blob `25de1770f4736df94bf5899ba7aa5ce57d77fca6`; GPU blob
`b8b0577ef663eca4d107cd69e1c805c59ee0bc78`; shared stimulus blob
`e2a6c96ba736b17240ca90421f8076548b84e372`. No production source changed.
No GPU correction, CPU correction, model change or tolerance adjustment.

| Certification | Result and evidence |
|---|---|
| C1 | PASS: empty events, two boundaries |
| C2 | PASS: direct input admission and continuation |
| C3 | PASS: pending bin 0/count 1/weight 0.275 retained; no early delivery; chunk-2 delivery |
| C4 | PASS: explicitly nonempty pending ring after chunk 1; quiet continuation |
| C5 | PASS: absolute deadline 23; suppression through step 23; spikes at 1 and 25 |
| C6 | PASS: CPU arrays disjoint, GPU pointers disjoint, untouched B byte-unchanged |
| C7 | PASS: five boundaries at steps 7,20,24,50,100, including ring wraps |
| C8 | PASS: two differing trajectories with independent same-runtime repetitions |
| C9 | PASS: every SimulationResult field, canonical spikes/counters/identities/traces; readback byte-unchanged |
| C10 | PASS: drop CPU A/close GPU A twice; B continues at every subsequent boundary |
| Admission | PASS: 19 cases, identical acceptance or exception category; rejected input leaves both states byte-unchanged |
| Delay/ring | PASS: zero/default/3-step delay, maximum physical slot, wrap, count-3 collisions with canceled weights, zero-new-event continuation |
| GPU repeats | PASS: C3/C5/C7 twice with fresh states; every state and output array byte-exact |

Common fixture definitions freeze graph, ordered duplicate edges, parameters,
dt, rest/zero/-1 initial arrays, absolute input events, weights, refractory-free
IDs and chunk lengths. Trajectory fixture digests and per-chunk stimulus
digests are recorded in the JSON. Additional fixtures exercise equal/near-equal
time constants, near-threshold input and retained conductance. No sparse output
is offered by the resumable APIs; sparse_trace is None on both.

Admission includes zero/one event, duplicate times/IDs within and across
schedules, last grid point, endpoint, nextafter-before-endpoint, negative,
out-of-window, unknown ID, off-grid, NaN/inf input, malformed schedule/time
shape, boolean ID, wrong public stimulus type, zero/off-grid duration.
The just-before-endpoint value rounds to the excluded endpoint under the
existing grid contract: both reject. Constructor errors use the shared public
payload types. This does not add public error guarantees for arbitrary mutated
internal arrays or unsupported raw event buffers.

Exact discrete mismatches **0**. Max absolute/relative errors: voltage **0/0**,
conductance **0/0**, pending weights **0/0**, voltage/conductance traces **0/0**.
All compared floats are finite and byte-exact. Frozen rtol=atol=**2e-13**;
floating failures **0**. Relative error is evaluated only for nonzero reference
elements; absolute policy still covers zero. C7 voltage/conductance/pending
errors remain zero at every boundary; no observed accumulating drift.

## Validation and execution accounting

Existing source guard installed before preflight, discovery and imports;
source/read controls **11 PASS** before workload. Commands use
`MALECNS_A019C_R2_FIREWALL=1`, `PYTHONPATH=scripts/a019c_firewall` and
`uv run --offline --frozen --extra gpu --group dev python scripts/a019c_firewall/guarded_child.py`.

Final A019T suite **33 PASS**, after the final harness edit. Scoped regressions
**76 PASS**, one real-data node explicitly deselected: A019S **33**, Task007c
**14** (11 GPU correctness and 3 cache/import controls), Task010 **1**, Task017
**1**, Task005 CPU **24**, A011 CPU runtime **3**. No Arena node selected.
Guarded `python -m compileall -q src scripts tests` and `git diff --check` PASS.
The final harness edit adds report fields and two admission cases; no production
correction occurred and no production matrix invalidation was necessary.

GPU performance benchmarks **0**; no speedup, throughput, CPU/GPU timing or
tuning evidence. Full-real preparations **0**, real advances **0**, A019D/A019L
reruns **0**, registered payload reads across all seven categories **0**,
Arena/intervention application runs **0**, downloads **0**, archive writes **0**.
Zero reads describe explicit synthetic command scope plus the existing
fail-closed Python/Arrow guard, not independent native-byte telemetry.
Historical synthetic mask regression tests do not run application interventions.

Exact next task: **A019U — evidence-only gate for GPU performance benchmark
authorization under the now-certified resumable application contract**.
Not started; no benchmark authorization is inferred from this certification.

Commit/push and final local/origin/live identity are reported externally to
avoid self-referential evidence. No tag/release/version bump.
