# Application A019S: bounded resumable GPU implementation

Authorization: **授權 A019S**. Starting local HEAD = origin/master = live GitHub master = **2f20b4da8a6a90fe77e18d00d429beb9248d5934**. Root derived by git rev-parse. Worktree/staging/stash empty; version 0.3.0; tracked workflows 0.

## Pre-edit source map (frozen before production edits)

Inspected tracked source as text only. This agrees with A019R F1; no material contradiction. Current application status is **EQ-D**, proposed future policy EQ-B remains uncertified.

Exact pre-edit Git blobs at the starting SHA: cuda.py `42c5e77d956b7de918d815806dc11209ef544fc0`; lif.py `25de1770f4736df94bf5899ba7aa5ce57d77fca6`; stimulus.py `e2a6c96ba736b17240ca90421f8076548b84e372`. These identify the mapped surfaces independently of later edits.

| Existing surface in dynamics/cuda.py | Classification | Current ownership |
|---|---|---|
| CudaGraph / upload_graph, CSR pointers/targets/weights | R1 runtime-static | caller or one-shot call; upload synchronizes null stream |
| simulate_cuda -> simulate_cuda_batch | R5 resumable entry missing | creates dynamic state and starts at zero on every call |
| v/g float64[B,N], refractory_until int64[B,N] | R2 state mutable | invocation-local, replaced by cp.where; inclusive local deadlines |
| pending float64[B,R,N], pending_counts int32[B,R,N] | R2 state mutable | invocation-local rings; local step modulo R; future slots lost on return |
| _stimulus_inputs / schedule_events; direct cp.add.at | R3 call inputs / R4 host packing | endpoint rejected; duplicate floating scatter |
| _schedule_kernel / schedule_active_edges | R3 propagation | floating atomic additions; CSR graph is read-only |
| masks, scratch, queued/delivered counters, trace/sparse/spike arrays | R3 temporaries | recreated per invocation |
| target_positions | R1 static candidate | recreated per invocation |
| IDs, fingerprints, inputs, asnumpy results | R4 host mirrors | no retained dynamic mirror |
| absolute time, owner/device/lifecycle identity | R5 missing | no continuing state owner |
| final null-stream synchronization / asnumpy | R3 output boundary | outputs materialized then local allocations dereferenced |
| measure_memory | outside A019S | global pool reclamation must never be used for state release |

Plan: add GPUPreparedRuntime/GPUSimulationState in cuda.py with CPU-isomorphic initial_state/advance, ordered incoming scheduler, private retained device arrays, absolute time and scoped release/failure. Preserve legacy batch behavior, CPU equations and dependency pins. Run bounded synthetic structural/self-continuity and existing GPU regressions under the existing fail-closed source guard; compileall and diff check. No benchmark, real data, Arena, intervention, archive, tag, release or version change.

The default environment lacked CuPy. The documented optional GPU extra was activated using frozen/offline uv and cached packages only (no download or pin change). CuPy 14.2.0 device allocation/arithmetic succeeded under the guard. This is environment evidence only.

## Terminal result

**A019S-A — RESUMABLE GPU IMPLEMENTATION COMPLETE; STRUCTURAL SELF-CONTINUITY CERTIFIED.** All sixteen structural acceptance gates pass on the bounded synthetic matrix. This certifies backend self-continuity/lifecycle on these fixtures, not complete CPU/GPU numerical equivalence, universal correctness, full-real readiness, speedup or realtime capability. A019R-A/F1 is preserved. Application equivalence remains **EQ-D**; **EQ-B is not certified**.

Production changes are confined to `src/malecns_sim/dynamics/cuda.py`. Added tests: `tests/test_application_a019s.py`. This report and `a019s-resumable-gpu-evidence.json` complete the four-file scope. No CPU source, application service dispatch, preparation schema, legacy one-shot body, A019L contract, dependency pin or model changes.

## Final object and allocation ownership

`GPUPreparedRuntime` is a frozen backend-specific descriptor with CPU-isomorphic `initial_state()` / `advance(state, duration_ms=..., stimulus=ExplicitStimulus(...), trace_neuron_ids=..., silenced_neuron_ids=...)`. Separate concrete GPU types are necessary because CPU concrete buffers assume NumPy and lack device lifecycle; no competing packed-event public API is introduced. No service integration or Arena route is added.

Runtime owns one uploaded CSR graph, incoming offsets/source positions/outgoing ordinals grouped stably by target, model/grid/delay/refractory metadata, host-generated coefficients including equal/near-equal tau semantics, graph/model/dt identity, CuPy/device identity, a compiled ordered kernel, explicit nonblocking stream and serialization lock. No global mutable GPU state is added. Graph/static arrays are read-only by contract and byte-unchanged by advance tests; CuPy array contents themselves are not mechanically immutable. No static graph copy is made per state. Runtime construction uses direct untimed upload, not the legacy timed upload helper.

Every `initial_state()` allocates disjoint float64 voltage/conductance `[N]`, int64 inclusive refractory deadlines `[N]`, float64 pending weights `[R,N]`, int32 pending counts `[R,N]`, plus host integer timestep zero. Initial values are rest/zero/-1/zero/zero. Device initialization synchronizes before publication. States retain strong backing references. A/B device pointers differ for all mutable buffers and A activity leaves B byte-unchanged. No extra mutable continuity value is necessary.

Call-owned storage comprises validated compact event positions/multiplicities, masks, integration scratch, queued/delivered counters, spike arrays and requested traces. Only canonical chunk outputs are read back in production: spikes, full required spike counts, counters and requested traces. No complete voltage/conductance/deadline/ring host mirror or round trip occurs during production advance. Explicit full snapshots are test-only. GPU advance matches CPU advance's existing result boundary; optional sparse diagnostics remain on the existing one-shot APIs.

## Continuity, ordering and output

State integer timestep is the only canonical clock. For local step l, absolute k=offset+l controls refractory comparison, ring cursor k%R, spike step k+1 and deadline k+1+refractory_steps. Timestep publication occurs only after successful execution, result materialization and stream synchronization. Persistent array pointers remain stable across calls; tests trap hidden runtime/graph/state construction. No re-upload/reprepare/reset occurs per chunk.

Both pending rings remain device-resident. At k, direct input precedes due delivery; due counts include refractory-rejected delivery, slot contents are cleared, equations integrate, strict threshold/reset occur, then outgoing events queue at k+1+D. No endpoint flush occurs. R=D+1 means enqueue reuses the just-consumed physical slot, so each slot holds at most one step's incoming edges; E<=int32_max bounds pending counts without changing count dtype. CSR/index/grid/timestep/deadline/counter bounds are validated before unsafe execution.

One scheduler writer per target traverses incoming entries in ascending source and stored outgoing CSR ordinal, starting with the existing slot value. Floating atomic reductions are absent from the resumable path. Canceled-weight collisions retain their event counts. Explicit input uses shared schedule validation, deterministic step/target packing and integer multiplicity times one float64 weight, then one voltage addition per admitted target. Payload fingerprint/order remains authoritative. Zero events and zero-delay transitions work. Event zero belongs to this chunk; the last grid point before endpoint is accepted; endpoint itself is rejected before execution; off-grid/unknown/negative/nonfinite values follow existing validation.

Returned `SimulationResult` uses canonical absolute spike order, existing digest/fingerprint schema, per-call counters and immutable detached host arrays. Trace column zero is retained boundary state; subsequent columns follow the chunk. Output materialization and later output inspection do not destroy continuation or alias state.

## Lifecycle and failure

Strict owner token, semantic identity, backing and device checks reject mismatches. Runtime lock serializes GPU work and rejects busy use. Invalid input/identity/time is rejected before mutable execution and leaves state usable. Exceptions after device execution may begin mark that state failed; no rollback or retry is claimed and timestep is not published. Synthetic partial execution and synchronization failures verify non-resumability. Observable context-fatal CUDA statuses 700/710/719 poison the runtime and prevent sibling work/new state creation. The tests inject these failures; no actual fatal GPU fault was induced.

State close synchronizes and drops only its private arrays/backing reference, is idempotent, and never invokes global pool reclamation. Releasing A leaves the runtime and B usable; B continues successfully. Runtime close rejects new states/advances and drops its backing reference while live states retain the shared graph until state closure. CuPy allocator caching is outside this logical lifetime guarantee. Allocation failure during fresh-state construction leaves the runtime and an existing sibling valid.

## Synthetic validation evidence

Device: NVIDIA GeForce RTX 3060; CuPy 14.2.0; CUDA runtime API 12090; driver API 13000. Ordered RawKernel uses NVRTC with `--fmad=false`; membrane operations are separate CuPy ufunc stages and host NumPy-generated scalar coefficients. No block/stream/layout tuning or performance observation was performed.

| Validation | Result |
|---|---|
| New A019S tests | **33 PASS**, covering S1-S12, every-boundary snapshots, zero delay, equal/near-equal tau, threshold boundary, validation, bounds, failure and lifecycle |
| Existing Task007c subset | **14 PASS**: 11 synthetic GPU correctness cases, 2 cache controls, 1 lazy-import surface control; real node explicitly deselected |
| Existing Task010 synthetic GPU mask regression | **1 PASS** |
| Existing Task017 synthetic GPU per-trial mask/isolation regression | **1 PASS**; no historical matrix execution |
| Existing Task005 CPU equation/payload tests | **24 PASS** |
| Existing A011 CPU-only runtime continuity/initial-state nodes | **3 PASS**; no Arena nodes executed |
| Existing R2 source firewall controls | **11 PASS** before workload validation |
| `uv run python -m compileall src scripts tests` (guarded GPU environment) | **PASS** |
| `git diff --check` | **PASS** |

Validation commands used `uv run --offline --frozen --extra gpu --group dev python scripts/a019c_firewall/guarded_child.py`, `MALECNS_A019C_R2_FIREWALL=1`, and `PYTHONPATH=scripts/a019c_firewall`. No default uv invocation subsequently removed the GPU extra. The CuPy CUDA-path warning was nonfatal; device work and kernel compilation succeeded. Incidental pytest duration is not performance evidence.

Whole GPU trajectories versus equivalent chunks and independent whole-prefix states agree **byte-exactly** for all five persistent arrays, shapes/dtypes, physical pending bins/counts, refractory deadlines and canonical concatenated spikes/traces; timesteps and summed counters agree exactly. Floating self-continuity is **exact**, not tolerance-bounded. Explicit expected-state fixtures independently establish pending/refractory/conductance/voltage preconditions. The three small suitable legacy one-shot GPU references agree on discrete output/counters and meet rtol=atol=2e-13 for traces. The old one-shot path cannot expose final rings/deadlines and its atomic/duplicate/coefficient semantics are unsuitable as a complete retained-state oracle; it is not forced into that role.

## Numerical policy, counters and next task

Future EQ-B exact fields remain discrete output/event identity/order, refractory deadlines, pending counts/bins, timestep, shapes/dtypes and isolation/lifecycle. Future float fields remain voltage, conductance, pending weights and floating summaries with candidate rtol=atol=2e-13. No policy redefinition or CPU/GPU application promotion occurred. Existing scoped legacy GPU/CPU tests are regression evidence only.

GPU performance benchmarks=0; full-real preparations=0; real MaleCNS advances=0; A019D/A019L reruns=0; accepted registered payload reads in all seven categories=0; Arena/intervention application runs=0; downloads=0; archive operations/writes=0; tags/releases/version bumps=0. Synthetic per-trial mask correctness tests are existing regressions, not application intervention runs. Thirty-three new test nodes and thirteen existing actual-GPU correctness nodes passed (cache/import controls separately above); earlier development validation repeated bounded synthetic cases only. No GPU wall-time distribution, speedup or realtime claim exists.

Zero reads describe explicit command scope and fail-closed Python/Arrow guarded accounting, **not independent native byte telemetry**. Source inspection was limited to named tracked code/tests/reports and memory guidance; no registered directory traversal or payload inspection was performed. Firewall controls deliberately reject probes before content reads.

Exact next task: **A019T — bounded synthetic CPU/GPU resumable-state equivalence certification under the frozen EQ-B policy**. Not automatically started.

Commit/push authorized by this task; final commit SHA and local/origin/live equality are reported externally to avoid self-reference. Require final worktree/staging/stash empty, version 0.3.0, tracked workflows zero; no tag/release.
