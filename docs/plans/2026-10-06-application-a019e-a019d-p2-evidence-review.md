# Application A019E - Evidence-only review of A019D P2

Authorization: user explicitly authorized `授權 A019E`; evidence-only review and completed documentation commit/push. No implementation change or new execution authorized.

Starting root dynamically verified with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`. Local HEAD = origin/master = live GitHub master = `659b7f970ffb8f8ad9cd8c35a2d05296a4f88097`. Worktree, staging and stash empty; package 0.3.0; active tracked workflows 0. All starting gates passed before mutation.

Plan: verify baseline; read committed evidence and certified source statically; recalculate recorded arithmetic using isolated standard-library Python; audit timing boundaries and GPU route; document one disposition; diff-check; commit/push and verify identities. No project imports, test discovery, simulation, payload access or evidence regeneration.

## Evidence custody and established result

Primary sources: [A019D report](2026-10-06-application-a019d-full-real-stateful-benchmark.md), [raw evidence](2026-10-06-application-a019d-evidence.json), [R18 certification](2026-10-06-application-a019c-r18-synthetic-validation-closure.md), [frozen contract](2026-10-05-application-a019a-benchmark-contract.json), and [harness schema](2026-10-05-application-a019c-harness-contract.json). These remain unchanged.

Raw evidence SHA256: `ffe43022024d92063de118572d4e26ab93c6c3ec19137bfa2d2dd2f59c593ea4`. Verified 24 ledger rows, exactly 20 non-warmup rows, twelve exact corresponding A/B replay records, and all measured component sums equal total within 1e-12 s. Recalculated summary agrees with committed summary. Raw classification `A19C-A`, P1/P2 null, remains untouched: the committed report adjudicates **A019D-P2 - FULL-REAL STATEFUL BENCHMARK COMPLETE**.

Historical attempt consumed Yes; preparations 1; preparation PASS 101.304875 s; sampled peak private 5,473,751,040 bytes and working set 4,468,166,656 bytes; G1-G6 PASS. PreparedNetwork / PreparedRuntime / SimulationStates = 1 / 1 / 2. Schedule generated once, 948 events, fingerprint `6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.

A and B each 2 warmup + 10 measured x 20 ms, 24 real advances historically, exact state/output and pending/delayed replay PASS, horizons 240/240 ms. Independent states; A released before B; no continuous 480-ms trajectory, runtime reset/recreation or retries. This configuration establishes bounded completion below 30 s for all calls; none of the twenty measured calls met 20 ms. It does not establish realtime capability elsewhere or biological realtime.

## Arithmetic from recorded calls

Seconds, warmups excluded. p95 uses linear interpolation at sorted zero-based index (20-1)*0.95 = 18.05, consistent with the harness's NumPy percentile convention. Population standard deviation describes these twenty observations; sample standard deviation is also shown to avoid denominator ambiguity.

| Statistic | Value |
|---|---:|
| min | 1.515181500 s |
| median | 1.642870550 s |
| mean | 1.647739485 s |
| max | 1.774488700 s |
| p95 | 1.741707810 s |
| population std (n) | 0.062658750 s |
| sample std (n-1) | 0.064286521 s |
| population CV | 3.802709769% |
| sample CV | 3.901497902% |
| A mean | 1.613853650 s |
| B mean | 1.681625320 s |
| B-A mean | 0.067771670 s (4.1993690% of A, rounded) |
| mean / 0.020 | 82.38697425x |
| best / 0.020 | 75.759075x |
| worst / 0.020 | 88.724435x |

Mean excess above threshold = 1.627739485 s. Meeting 20 ms would require about 98.7862% less mean wall time; that arithmetic is not a predicted achievable improvement. Counts: <=20 ms 0/20, >20 ms 20/20, >=30 s 0/20.

| Measured index | A seconds | B seconds | A slowdown | B slowdown |
|---|---:|---:|---:|---:|
| 1 | 1.6200414 | 1.6553535 | 81.002070 | 82.767675 |
| 2 | 1.6382754 | 1.6560338 | 81.913770 | 82.801690 |
| 3 | 1.5658390 | 1.6930420 | 78.291950 | 84.652100 |
| 4 | 1.5151815 | 1.6120948 | 75.759075 | 80.604740 |
| 5 | 1.5569737 | 1.6327310 | 77.848685 | 81.636550 |
| 6 | 1.6918164 | 1.7399825 | 84.590820 | 86.999125 |
| 7 | 1.6992220 | 1.7744887 | 84.961100 | 88.724435 |
| 8 | 1.6094614 | 1.6397771 | 80.473070 | 81.988855 |
| 9 | 1.6459640 | 1.7308286 | 82.298200 | 86.541430 |
| 10 | 1.5957617 | 1.6819212 | 79.788085 | 84.096060 |

## Timing character

**T1 - relatively stable systematic latency**, with modest sequence shift and nonmonotonic within-sequence variation. Population std A/B = 0.055367201/0.049902018 s. Linear descriptive slopes = +0.004487146/+0.006610798 s per measured index. First-five versus last-five means: A 1.5792622/1.6484451 s; B 1.64985102/1.71339962 s. Increases are about 4.38%/3.85%; neither sequence is monotonic. B exceeds its corresponding A in all ten pairs, by 0.06777167 s on average. The later B run is confounded with elapsed machine time; no thermal, scheduling or cache cause is measured.

Pooled Q1/Q3 = 1.61143645/1.69212280 s, IQR 0.08068635 s; Tukey fences 1.490406925/1.813152325 s contain every measured call. No sporadic-outlier dominance. Warmup 1 A/B = 1.3715530/1.3779638 s, warmup 2 = 1.6174649/1.6295631 s. Earlier windows have different activity and pending histories, so these do not isolate a cold-cache effect. Only n=20, one machine, one attempt: T1 describes observations, not stationary latency or a proven hardware/code bottleneck.

## Certified call path and evidence boundaries

Source map: `scripts/execute_application_a019d.py` invocation adapter - `scripts/benchmark_application_a019.py::supervise/run_forward` - `scripts/benchmark_application_a013.py::run_sequences/pack` - Recorder.advance - `src/malecns_sim/dynamics/lif.py::PreparedRuntime.advance/simulate_lif` - `src/malecns_sim/dynamics/stimulus.py::schedule_events` and `linear_state_update` - canonical output/counts/digests - two-count readout - decoder/dummy environment bookkeeping - timer stop - verification/evidence persistence. Windows Job supervision runs concurrently, not as per-call request/response IPC.

M = directly measured at the named boundary; B = indirectly bounded by an enclosing measured interval or recorded sizes/counts; I = static source inference only; U = attribution unknown. An enclosing timer does not directly measure its children.

| Component | Level | Boundary / finding |
|---|---|---|
| total benchmark call | M | t0-t5; mean 1.647739485 s |
| window repacking | M | encode t0-t1; mean 0.000279850 s |
| runtime.advance including output assembly | M | t1-t2; mean 1.647439540 s |
| readout | M | t2-t3; mean 0.000016345 s |
| decoder | M | t3-t4; mean 0.000002110 s |
| dummy environment bookkeeping | M | t4-t5; mean 0.000001640 s; no Arena |
| internal event packing, masks and validation | B/I | inside advance; individual duration unknown |
| 200 CPU timesteps, dynamics, propagation, pending ring | B/I | inside advance; individual durations unknown |
| output concatenation, canonicalization, counts, byte copies/hashes | B/I | inside advance; individual durations unknown |
| initial state allocation | I/U | outside total-call timing; no isolated allocation timer |
| schedule generation and window slicing | I/U | once before call loop, outside timer |
| verification, state-array digests, accounting | M aggregate | instrumentation_seconds measured after t5; measured-call mean 0.104472770 s; not benchmark total |
| evidence JSON retention/persistence | I/U | after timed call; instrumentation timer ends before retention JSON encoding |
| process launch, stdout IPC, supervisor polling | I/U | outside call timer structurally; concurrent contention effect unknown |
| memory/state/output sizes, event counts | M records / B | sizes/counts constrain work, not elapsed-time attribution; sampled peaks not exact instantaneous peaks |

The measured advance interval is 99.9818% of total mean; all other timed components together average 0.000299945 s. This percentage is calculated from existing timers, not invented internal attribution. **Direct coarse per-stage timing exists. No direct per-stage timing exists inside advance**, so this localizes a broad interval but not one dominant implementation bottleneck. Even eliminating all timed work outside advance leaves roughly 1.64744 s. Supervisor interference, memory bandwidth, Python versus NumPy time, and internal allocation time remain unknown.

## Preparation versus advance

Preparation 101.304875 s is one-time within this attempt, distinct from ~1.65 s per measured 20-ms advance. Existing evidence also directly records preparation-route timers: bounded_loader 52.310535 s (contains subordinate publication/source/membership/aggregation/merge/metadata timers), downstream_projection_csr 8.047373 s, sign_construction 14.9989776 s, effective_weights_outgoing_csr 16.9231595 s. Subordinate staged_merge 26.707584 s and metadata_normalization 8.3392876 s are not additive to bounded_loader. These are preparation measurements, not advance cost evidence; do not sum nested timers or use them to explain call latency.

For a fresh preparation followed by a few calls, preparation dominates first-use delay, before adding source identity checks, runtime/state setup and verification. The certified runtime persists across twelve calls per independent state and across A/B without recreation; reuse is supported for that bounded lifetime. For repeated calls while it remains available, preparation is not paid each call and advance governs responsiveness. About 61.48 calls at the observed mean would accumulate wall time equal to preparation, but this is arithmetic extrapolation beyond the certified twelve-call trajectory per state, not proof of indefinite reuse. An application that prepares anew each interaction would pay preparation repeatedly; A019D does not certify that product lifecycle. Improving preparation does not establish realtime advances, and improving advance does not remove fresh-start preparation latency.

## Credible internal candidates, without bottleneck claims

All candidates below are I for mechanism, B for inclusion in advance, U for isolated cost; none is directly timed by A019D.

| Source / candidate | Why plausibly costly | Exactness / validation burden |
|---|---|---|
| lif.py::simulate_lif / linear_state_update | 200 steps over 166,700 neurons; repeated boolean gathers/scatters, temporary arrays, exp/isclose coefficient work | buffer/coefficient reuse potentially O1 only with identical expression evaluation and bits; validate threshold-sensitive states, refractory cases and every call boundary |
| simulate_lif outgoing CSR loop | Python iteration over fired sources and two np.add.at calls per source; repeated indexing and duplicate-target accumulation | equivalent dispatch may be O1; regrouping changes floating accumulation order and replay unless exact equivalence proven; high burden for mixed signs/duplicate targets |
| simulate_lif pending handling | dense slot scans, int64 count reductions, allowed masks and clearing each due slot | equivalent bookkeeping potentially O1; sparse tracking must preserve cancelled-weight events, counts, delivery order and ring phase; high delayed/refractory burden |
| stimulus.py::schedule_events and per-call setup | Python schedule validation/packing plus masks and allocations | reuse of immutable validated work potentially O1; same errors/input identities and boundaries required; moderate burden; size alone does not prove importance |
| simulate_lif output assembly | concatenation, lexsort, bincount/searchsorted, tobytes and SHA256 materialization | removing redundant work potentially O1 only with identical immutable arrays, canonical ordering and all digests; moderate/high aliasing and replay burden |

State arrays are reused by reference inside simulate_lif, not wholly cloned each advance. Recorded pending arrays are 25,338,400 + 12,669,200 bytes; v/g/refractory each 1,333,600 bytes. Verification makes state digest byte copies outside total timing. Do not claim full-state copying inside each timed advance. NumPy/CuPy conversion is absent from this CPU path. Sparse trace branches are disabled for this benchmark. Host allocation and Python loop overhead are candidates, not measured dominant causes. Readout/packing are directly small; IPC/serialization is not a plausible direct explanation of the timed interval under this boundary, although concurrent interference is unmeasured.

## Optimization contract classes

| Class | Plausible work / limit |
|---|---|
| O1 contract-preserving implementation | remove demonstrated redundant temporaries, cache identical scalar coefficients or immutable validation work, equivalent CSR/pending bookkeeping. Conditional opportunities only: preserve parameters, dt=0.1 ms, schedule, all 20-ms boundaries, two warmups/ten measured calls, states, pending semantics, outputs, exact deterministic replay and CPU identity. No selected optimization is justified yet. |
| O2 backend change | CPU to GPU, compiled backend or changed numeric backend requires separate backend/equivalence certification; intended mathematical equivalence is insufficient. |
| O3 benchmark change | larger chunks, batching A/B or multiple 20-ms calls, different warmups, moving output construction/readout out of timing, caching repacked windows outside the timed entry, changed API amortization or thresholds require a new frozen benchmark. |
| O4 scientific/model change | dt, reduced graph, float approximation, weights, thresholds, delays, event-order/pending semantics, schedule or dynamics changes are outside A019D performance optimization authority. |

Any future O1 change needs independent exact old/new CPU state/output checks, pending/delayed and chunk-boundary tests and unchanged timer/default contract. Synthetic success would not prove full-real speedup; subsequent real comparison would require separate authorization. Changing floating reduction order cannot be quietly classified O1 on approximate agreement.

## Existing GPU route

Static source: `src/malecns_sim/dynamics/cuda.py::simulate_lif_cuda_batch`, graph upload and scheduling RawKernel. Device arrays accelerate dense state updates, refractory/threshold/reset work, delay-ring handling and outgoing CSR propagation; scheduling uses float64 atomicAdd. Host retains stimulus preparation, Python timestep/trial orchestration, direct event lists and host-to-device transfers, synchronization, device-to-host output extraction, canonicalization/counts/digests and result packaging. Preparation and benchmark readout/supervision are not accelerated by this path.

The CUDA batch routine allocates fresh v/g/refractory/pending arrays per invocation. It accepts no resumable SimulationState equivalent to PreparedRuntime.advance; uploaded graph reuse is not dynamic-state continuity. Repeatedly invoking it at 20 ms would reset state and violate A019D. Atomic accumulation order is an exactness risk requiring evidence, not proof of observed divergence.

Historical [Task 007c](2026-09-21-task-007c-gpu-acceleration-gate.md) records canonical spike/output agreement and tight float64 state tolerances on its older contract and 6,113,545-edge graph; A019D has 24,904,953 effective edges. Historical GPU readiness/speedups do not certify current exact state/pending replay, resumable chunks or performance. **Existing CPU/GPU equivalence is insufficient** for A019D comparison. No speedup is projected and no GPU availability is probed here.

A prerequisite for any later comparison is separately authorized stateful GPU backend certification: a persistent state API with absolute timestep/ring phase; exact CPU/GPU v/g/refractory/pending/count/output identities at every corresponding 20-ms boundary, including delayed cross-boundary events, negative/cancelled weights and threshold edges; independent A/B lifetimes and repeat determinism; frozen graph/model/schedule identities; synchronized total-call boundary including required transfers/output construction; memory/VRAM, timeout, cleanup and no-retry controls. Begin synthetic; any full-real equivalence or comparison needs separate authorization and preregistration with unchanged call structure and explicit backend identity. If only tolerances are achievable, exact A019D equivalence is not certified and a separately defined contract is necessary. This is a prerequisite description, not the recommended next task.

## Decision and exactly one recommended next task

**A019E-B - PROFILING / INSTRUMENTATION REQUIRED BEFORE OPTIMIZATION.** The advance interval dominates directly, but several untimed child regions could dominate it. No one proven dominant internal bottleneck or sufficiently specific direct optimization target exists. GPU resumable equivalence is also not mature enough to prefer A019E-C.

Exactly one recommended task: **Application Task A019F - Bounded Synthetic CPU Advance Cost Instrumentation**. Proposed only, not executed or automatically authorized. Establish a task-wide fail-closed registered-source firewall before imports/discovery; instrument a separate opt-in diagnostic path for event preparation, per-step direct/pending work, linear updates, CSR propagation and output assembly using synthetic inputs only. Bound cases across neuron/activity/pending densities, preserve 200 timesteps and twelve-call state sequences, and compare instrumented/uninstrumented exact state/output/pending identities. Record timer perturbation and allocation measurements with explicit nested boundaries; keep production defaults and frozen A019D timer unchanged. No full-real preparation/advance, benchmark rerun, GPU, tuning or optimization. Synthetic stage shares guide hypotheses; they cannot identify the full-real dominant cost without separately authorized bounded profiling evidence if uncertainty remains.

## Unknowns, nonclaims and execution accounting

Unknown: internal advance stage split; memory bandwidth/cache/allocator behavior; CPU scheduling/thermal causes of B shift; full-real scaling of synthetic stage costs; achievable exact-preserving speedup; current GPU stateful exact equivalence and performance. No proven biological realtime, behavioral prediction, mechanism, brain reconstruction or digital-twin claim. No measured GPU speedup for this workload. No benchmark/model/hardware changes inferred from arithmetic.

A019E counters: full-real preparations 0; real advances 0; A019D reruns 0; GPU/CUDA runs 0; Arena runs 0; scientific interventions 0; downloads 0; archive writes 0; registered scientific payload reads 0. These counters follow the performed static/document-only operations, not newly instrumented native telemetry. Historical A019D attempt consumption remains Yes and unchanged. No tests or project code imported; arithmetic uses `python -I -S` and standard library on the committed JSON only. No runtime/test code changed.

Validation: isolated ledger/replay/stage-sum and summary arithmetic checks PASS; working and staged `git diff --check` PASS before commit; only this report may change. Publication requires local/origin/live equality, clean worktree/staging/stash, version 0.3.0 and workflows 0 after push. The containing commit SHA and final remote verification are reported in the delivery response, since a document cannot embed its own commit SHA. No tag/release/version bump.
