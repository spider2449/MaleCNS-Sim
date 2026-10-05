# Application A012 — Real closed-loop demonstrator feasibility

## Decision and scope

**A12-A — REAL ARENA DEMONSTRATOR DESIGN READY; BOUNDED RUNTIME BENCHMARK REQUIRED NEXT.** The narrow design is a contact-gated **ENGINEERED VIRTUAL-SUGAR ENCODER**, the frozen real sugar populations, the existing CPU PreparedRuntime, and an explicitly engineered scalar MN9 stop/advance actuator. No biological steering reconstruction is justified. Design readiness means the equations and boundaries can be preregistered; it does not establish readout activation, useful feedback, affordable execution, or real demonstrator end-to-end feasibility. That feasibility remains **NOT YET ESTABLISHED**.

Exactly one next task: **A013 — Real MaleCNS Stateful Advance Benchmark**, under the bounded envelope below and separate future authorization. Do not start it in A012. A12-B is excluded because full-real stateful advance cost and peak memory have not been measured. The benchmark can fail and invalidate this direction without tuning or substituting neurons.

A012 is research/documentation only. No product behavior, adapter, UI, CI, version, historical evidence, or archive changes. All execution counts in the firewall below are counts for this task, not a denial of historical authorized runs.

## Start gate and evidence sources

Repository root was derived with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`. Local HEAD, origin/master, and live GitHub master all matched `60fb1eeb876b23c53baf0fbacb1f375c7fdf478e`. Worktree clean; stash empty; pyproject version 0.3.0; zero tracked workflows. The A011 plan records **A11-CLOSED-LOOP-ARENA-CERTIFIED**, runtime feasibility C2, no duplicated simulator, SimulationState / PreparedRuntime, neural dt 0.1 ms, control interval 20 ms, and `application-closed-loop-v1`. These facts remain unchanged.

Primary audit anchors, all repository-local:

- `src/malecns_sim/homology.py`: derive_sugar_population and population_fingerprint.
- `src/malecns_sim/analysis/task008.py`: derive_task008_populations / load_task008_identities; `analysis/task008a.py`: source-field predicate and rootSide audit.
- `src/malecns_sim/application/workbench.py`, `models.py`, `service.py`: registered dataset, strict application contracts, source verification, production preparation and stimulus generation.
- `src/malecns_sim/dynamics/stimulus.py`, `lif.py`: explicit/Poisson schedules, amplitude, state, resume semantics, graph arrays and output allocation.
- `tests/test_application_a011.py`: exact regular/irregular synthetic continuity, including traces, refractory deadlines and pending arrays.
- `data/provenance/task008a-sugar-candidate-audit.json`, Task007/007b identity plans, Task010/011 plans, Task017 frozen closure and Task018 anatomical records.
- A003 plan's A003R record and A004 plan's preparation-only record; `tests/fixtures/application-a003r-reference-spec.json` for exact registered source and parameter identities.

No web search or new neuron discovery was used. Metadata-only local identity resolution was performed, without graph preparation or dynamics. Both resolved membership tuples exactly equal the frozen Task008a root-defined tuples. Local source SHA-256 checks match the registered values below. Future execution must repeat these checks; this audit does not guarantee future file or graph identity.

## Frozen scientific basis and input-path audit (R2)

**R2 — REAL_INPUT_PATH_READY_WITH_LIMITATION.** Frozen MN9_L=10331, MN9_R=16949. Sugar total 85; LEFT 42; RIGHT 43. The user-facing frozen predicate is LB3 / cb_sensory / gustatory / MxLbN. Exact raw source fields are `flywireType=LB3`, `superclass=cb_sensory`, `class=gustatory`, `entryNerve=MxLbN`; normalized homology fields are flywire_type, superclass, cell_class, entry_nerve. This source-field distinction prevents applying the wrong column predicate. Side selection uses rootSide, not missing somaSide, and numerically sorted body IDs. This is a metadata-defined population, not a new receptor-level claim. The two excluded LB3 rows remain excluded.

Population fingerprints verified locally:

- LEFT: `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7`.
- RIGHT: `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b`.

A002 LEFT sugar -> MN9_R/16949 and RIGHT sugar -> MN9_L/10331 remain certified experiment selection relations. They do not imply anatomical motor polarity, steering direction, or the direction of a neural response. Task017 remains NOT_ROBUST; Task018 is anatomical decomposition only, with no mechanism/causality conclusion.

The populations are independently addressable. PoissonStimulus supports disjoint neuron_ids and neuron_ids2 with separate rates. Current real experiments use a seeded per-neuron Bernoulli timestep realization with probability `frequency_hz * dt_ms / 1000`, one possible direct event per neuron per step. This is the project's reference Poisson approximation, not a reproduced Brian2 random stream. Events become grid-aligned SpikeSchedule entries; explicit duplicate events add impulses. Weight is anatomical synaptic weight 0.275 mV times factor 250 = **68.75 mV per direct input event**. This is a direct voltage coupling, not a derived biological current or transduction model. The stimulated populations are refractory-free under the existing input semantics; retain that rule.

Application StimulusSpec permits one side, fixed rates 10/25/50/100/150/200 Hz, one start/end window and weight factor 250. The service realizes and slices that window. It cannot directly represent arbitrary simultaneous continuous LEFT/RIGHT feedback rates. PreparedRuntime.advance already accepts arbitrary validated ExplicitStimulus schedules local to each chunk. Times must lie in [0,20) ms on the 0.1-ms grid; output spike timestamps are absolute, at step endpoints. Membrane, synaptic state, refractory deadlines and delay-ring phase persist. Schedules can change at every control boundary without rebuilding the graph. Runtime identity binds projection fingerprint, parameter fingerprint and dt; input schedules must additionally be bound by a future adapter record.

Limitations: current arena hardcodes synthetic identities and rejects real readouts; current production application service is a batch path, not a real arena adapter. Future wiring and an additive identity envelope are needed. No change to scientific input coupling or simulator equations is required. Never silently force this proposal into A002's single-side fixed-rate contract.

## Engineered sensory proposal and contact semantics (S1)

**S1 — technically expressible with current real input contracts**, specifically ExplicitStimulus / SpikeSchedule at the prepared-runtime boundary. At the application StimulusSpec boundary this would be S2, requiring a bounded additive adapter contract for bilateral time-varying rates and schedule identity. The classification here refers to the actual neural input seam, not a claim that the present UI/service already supports it. A future adapter must version its own envelope while preserving `application-closed-loop-v1` and historical A002 records.

Normalized arena coordinates use mathematical positive heading counterclockwise. Let agent position p, heading theta, source q, d=norm(q-p), and beta=wrap(atan2(q_y-p_y,q_x-p_x)-theta) in [-pi,pi). At d=0 define beta=0. Let clip(x)=min(1,max(0,x)). Side factors are `b_L=(1+sin(beta))/2`, `b_R=(1-sin(beta))/2`.

Two explicitly engineered alternatives:

- PROXIMITY FIELD: `I_P=clip(1-d/sqrt(2))`; `f_L=100 I_P b_L`, `f_R=100 I_P b_R` Hz. Technically valid, but it makes long-range geometry drive gustatory identities. It is acceptable only as a prominently non-biological field controller; it risks implying remote sugar sensing.
- CONTACT / NEAR-CONTACT, recommended: contact radius **r=0.05 arena units**, `I_C=clip(1-d/r)` if d<r, else 0; `f_L=100 I_C b_L`, `f_R=100 I_C b_R` Hz. Both channels are zero outside contact. The radius is an engineered arena parameter, not a physical labellar reach or measured transduction law. Bearing asymmetry is engineered, not calibrated receptor geometry.

Contact is more defensible because it avoids the extra implication of distant gustatory sensing. It still does not claim biological gustatory transduction. Use the visible label **ENGINEERED VIRTUAL-SUGAR ENCODER**, and show contact radius, geometry, requested rates and realized event counts separately.

Exact deterministic rate realization for a future maximum 200-ms session: sort all 85 body IDs, draw a NumPy default_rng(1555062870) uniform table in shape (2000,85), once at reset, with rows for absolute neural timesteps and columns for sorted IDs. Record NumPy version and the canonical table digest. At interval k and local step j=0..199, emit one event on neuron i at time `j*0.1` ms iff `U[200k+j,i] < f_side*0.1/1000`. Freeze geometry-derived rates throughout each interval. Precomputed variates, not predetermined events, allow deterministic state-dependent thresholds. No chunk reseeding; no adaptive weights. Explicit input weight 68.75 mV and refractory-free IDs are the entire frozen 85-member population, even when rates are zero. Reset restores arena, runtime state, variate table and interval index.

Initial arena: p=(0.5,0.5), theta=0, q=(0.53,0.51), r=0.05. Starting inside contact is deliberate: no innate searching mechanism is assumed. No manual source moves in the first fixed replay. Motion updates heading first and position by `v*0.02*(cos(theta),sin(theta))`, clamped to [0,1]. Contact intensity can change even if it remains nonzero during this very short horizon. No promise of crossing the contact boundary or finding sugar.

## Real readout audit and MN9 decision

All listed individual IDs are observable through output spike arrays/counts and selected v/g traces at the runtime level. Application TargetSpec is restricted to the frozen MN9 pair; other observations would need an explicit future observables envelope. Frozen candidate status means the historical selection is fixed, not that directional motor meaning is proven.

| Candidate IDs | Existing evidence / anatomy | Identity / engineering use | Unsupported implications |
| --- | --- | --- | --- |
| 10331 MN9_L, 16949 MN9_R | Task007/007b type and laterality resolution; cb_motor, subclass pm, PhN; ingestion-motor correspondence; sugar-to-MN9 graph paths, Task008–011 dynamics | Frozen; directly observable; pair sum can serve an engineered scalar activity actuator, contingent on activation | Locomotor reconstruction, MN9_L=left turn, MN9_R=right turn, response symmetry |
| 10313 DNge031_R | Task010 descending_neuron/GABA; direct signed connections to both MN9; Task011 network-redistribution-compatible effects | Frozen candidate; observable; no first decoder use | Direct inhibitory mechanism, right steering command |
| 10135 DNge031_L | Task010 descending_neuron/GABA; direct MN9_L relation; Task011 LEFT redistribution-compatible, RIGHT mixed | Frozen candidate; observable; no first decoder use | Left steering command, causal motor reconstruction |
| 12752 DNge080_L | Descending/acetylcholine; direct MN9 pair relations; Task011 mixed temporal evidence | Frozen candidate; observable; no first decoder use | Descending label proves locomotor command |
| 512730 GNG089_L | cb_intrinsic/acetylcholine; largest selected structural proxy to MN9_L, small/negligible Task010 effects | Frozen candidate; observable; no first decoder use | Structural rank predicts effective motor control |
| 43765 GNG095_R | cb_intrinsic/GABA; MN9 relations; historical zero baseline/outgoing activity and null perturbation | Frozen candidate; observable but poor activation evidence; not selected | Right actuator or reliable activity source |
| 514753, 517861 (other frozen Task010 rows) | GNG568_L and GNG041_R intrinsic candidates; Task010 null/small effects | Historical IDs only; not selected | New validated controller identities |
| Full prepared population | Entire curated model activity, sum of counts | Observable, membership must bind exact graph; not selected because input/recurrent global activity is less specific | Population total has a natural motor meaning |

No additional descending neuron was discovered or selected. Existing descending candidates do not have project-supported directional command semantics. Repository evidence for locomotor decoding is insufficient.

**MN9_L and MN9_R classification: M2 — technically usable but semantically misleading as movement steering.** Bilateral difference is not supported as biological steering. Task010's strong baseline MN9 asymmetry and Task017 NOT_ROBUST reinforce the danger of inventing balanced left/right commands. MN9 is not rejected as an explicitly engineered scalar readout: its ingestion-related identity is stated, and summing activity avoids assigning a direction to either body. This conditional engineering use does not upgrade M2 into a biological motor claim. A003R's zero MN9_R spikes at 100 ms also means short-horizon activation cannot be assumed from longer historical trials.

## Motor decoder options (at most three)

For all options, count `n_L` on 10331 and `n_R` on 16949 over the just-completed interval (absolute endpoints in (20k,20(k+1)] ms). Rates are 50*n Hz. Define `a_L=clip(n_L/4)`, `a_R=clip(n_R/4)`. No rolling history, fitted normalization, hidden ML, training, or adaptive weights. Masking zeros decoder counts only, preserving network firing. Reset clears counts/action; initial command is zero. All zero-count windows produce v=0, omega=0.

1. BILATERAL DIFFERENCE (not recommended): `z=a_R-a_L`; `D(z)=0` for abs(z)<=0.25, otherwise `sign(z)*(abs(z)-0.25)/0.75`; `omega=3 D(z)` rad/s; v=0. Turning is bounded to [-3,3]. Exact identities/window/normalization above. Even with an engineered label, the bilateral anatomical direction association is easy to misconstrue; no directional support.
2. COMMON MODE + DIFFERENCE (not recommended): same omega; `v=0.25*(a_L+a_R)/2` arena units/s when a_L+a_R>0, else 0. Same dead zone, normalization, clipping, reset and zero behavior as option 1. More visual motion does not repair unsupported steering semantics.
3. THRESHOLD ACTION (recommended): `a=clip((n_L+n_R)/4)`; dead zone `a<0.25`. If a>=0.25, **ADVANCE** with v=0.25 arena units/s; otherwise **STOP**, v=0. **omega=0 always**. One or more spikes in either readout exercise a fixed actuator. This deliberately coarse, memoryless decoder uses no bilateral polarity and no claim that ingestion neurons control translation. It is an activity-to-engineered-action demonstrator, not a locomotion model.

Recommendation is option 3 only. Failure to activate either readout means this decoder cannot be exercised; do not compensate by choosing candidates, increasing input, extending duration or inventing steering after seeing results. A benchmark need not pass this activation criterion because its objective is operational cost only.

## Control interval (C20)

**C20 — retain 20 ms**, with dt unchanged at 0.1 ms: 200 neural steps per interval. Chunk-relative input can be replaced at each boundary; 1.8-ms reference delays span 18 neural steps and use a 19-slot ring, retaining events across chunks. Refractory deadlines remain absolute. Output includes counts and absolute spike times; a 20-ms window is technically measurable but quantizes a single neuron rate to 50 Hz and may be entirely silent. Do not infer reaction-time equivalence. Preserving the certified interval avoids an unnecessary new clock and lets A013 measure its actual cost. A change in interval requires a new documented decision, not automatic batching when slow.

CPU-first, sequential, **closed-loop simulated-time execution**. Synthetic A011 throughput has no predictive role for this graph. No full-MaleCNS realtime or real-time claim is authorized.

## State, memory and retention

SimulationState owns identity tuple, absolute timestep, float64 v and g, int64 refractory_until, float64 pending weights and int32 pending_event_counts. PreparedRuntime retains the immutable EffectiveSignedProjection, parameters and dt. The reference delay ring has D=19 slots. Exact principal state-array payload is `N*(24+12D)` bytes; at historical N=166700, `166700*252 = 42,008,400 bytes`. This is not a process-memory estimate. The formula excludes Python objects, allocator overhead, temporary arrays and output. State retention is structurally feasible; operational memory sufficiency is unmeasured.

The effective graph stores int64 neuron IDs, source/target positions, float64 effective weights, int64 outgoing indptr/targets and float64 outgoing weights. Independent copied outgoing arrays mean five 8-byte edge arrays, plus neuron IDs and indptr: `40E+8N+8(N+1)` payload bytes. At historical E=24904953, N=166700 this is **998,865,328 bytes**. This reliably derived payload is not peak RSS/private bytes: raw tables, normalized anatomy, signed graph, sorting/copies, cache/preparation ownership and temporaries can coexist. Fingerprinting, result counts/rates and per-step masks also allocate. Do not infer an overall MB/GiB budget from these two payloads alone.

Pending storage shape is fixed; occupied slots and summed event counts may vary greatly. It is not an unbounded Python event queue, but int32 counts can overflow. Selected two-neuron v/g history for 200 steps costs `2*2*201*8=6432` bytes per interval; retain only if explicitly requested. Runtime still collects **all graph spikes per chunk**, temporary lists plus concatenated int64 IDs/timesteps (16 bytes per event, excluding temporary duplication), and full-population counts/rates. Selected readout logging alone does not prevent this allocation. Dispose each result after counts/digests, never retain all SimulationResult instances or full-graph traces.

Future arena log: maximum ten interval records plus one setup and one closure record; retain geometry, 85 encoded-event counts/schedule digests, two readout counts, action, identity and bounded state summaries. Full event lists may be at most 85*200=17000 encoded events per interval under the Bernoulli rule; no whole-network spike export. Rendering is optional and cannot alter retained authoritative values.

166700/24904953 and prepared fingerprint below are historical certified preparation evidence, not guaranteed sizes for arbitrary future datasets or preparation variants. A013 explicitly requires those dimensions/fingerprint and aborts on mismatch. No graph was prepared to verify them in A012.

## Historical real runtime evidence

A003R: CPU reference, LEFT 42-member sugar, 100 Hz, target MN9_R/16949, seed 1555062870, no intervention, 100 ms at dt 0.1 ms. Historical timings: load ~5.588 s, prepare ~284.976 s, simulate ~7.560 s, finalize ~0.118 s, total ~290.682 s. These event-derived certification measurements are non-benchmark measurements, with no measured peak process memory. Preparation dominates that initial startup. A004's preparation-only 286.373-s record corroborates expensive preparation of the same graph, not stateful execution cost.

Keeping one prepared projection and one state plausibly avoids repeating preparation per advance: this follows from PreparedRuntime ownership, not measured speed. Each advance still allocates outputs and performs graph/model fingerprint work. A003R used batch simulate_lif rather than the new full-real stateful seam; one 100-ms measurement cannot bound 20-ms p95/max cost, later high-activity states, memory, or interactive throughput. No linear FPS/ETA extrapolation is used. End-to-end timing, including encoding, readout and environment, must be measured separately from browser/HTTP work before any realtime terminology.

## A013 — exact future benchmark envelope (not executed)

Non-scientific, CPU-first, no UI, no arena behavior claim, no new biological interpretation. Separate authorization is required to execute. Use existing local MaleCNS-v1.0 files; no downloads, archive writes or scientific matrix units. Bind the fixture `tests/fixtures/application-a003r-reference-spec.json`, including all three file hashes:

- annotations `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`;
- neurotransmitters `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621`;
- weights `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`.

Manifest `e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631`; mapping `832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269`; unsigned projection `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4`. Shiu2024SignPolicy, MaleCNSV1ConsensusThenPredictedThenCelltype, reference LIF model fingerprint `037ed13cf919f0ef9ddfdb8f1876e7f1e4712a5c6deb1adbba0fc64e230b0d27`. Require **166700 neurons, 24904953 effective edges**, prepared fingerprint `ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`. One preparation only, then PreparedRuntime, dt 0.1 ms. Abort if identity differs; do not repair or substitute.

Fixed prerecorded workload: LEFT frozen population at 100 Hz for the entire 240-ms horizon, RIGHT zero; 68.75-mV impulses, existing LEFT refractory-free semantics, seed 1555062870. Generate this complete PoissonStimulus realization once and slice twelve 20-ms explicit chunks. This is an engineering load profile, not an arena response experiment. Read out 10331/16949 counts. Encoder timing measures slice construction/packing; readout timing measures selection and scalar decoding. Environment timing measures a deterministic dummy application of the selected stop/advance formula to p=(0.5,0.5), theta=0, without affecting prerecorded input. No scientific interpretation of movement or firing.

Exactly **two sequences**, fresh state each, sharing the same prepared graph and input. Per sequence: two stateful warmup advances (40 ms), then **ten measured advances** (200 ms); warmup state is retained into measurement. Maximum **24 full-real advances**, including four warmups; **20 measured advances total**, with per-sequence distributions and pooled distributions clearly labeled. Warmup is a policy, not proof of equilibrium or cache stabilization. No monolithic real comparison, extra run, adaptive workload or retry. Keep first-sequence hashes/summaries only, dispose state before second sequence.

Use monotonic perf_counter_ns. Collect encode, neural advance, readout/decoder, environment and total interval timings separately; preparation/load/warmup and instrumentation overhead separately. p50/p95 use NumPy percentile(method='linear') on each set; report max and raw twenty observations. This small sample describes this workload only, not a general latency guarantee. Measure working set, peak working set and private bytes at pre-load, post-load, post-prepare, post-state and every boundary; use a watchdog sampling every 100 ms during preparation/advance. Report array nbytes, whole-graph spike counts/output bytes, pending shape, nonzero count, pending-event sum/max, and retained log bytes at each boundary.

Determinism: require exact corresponding input digests, spike ID/timestep digests, readout counts, dummy environment values, timestep and byte-level digests of v/g/refractory/pending/count arrays for both sequences, including warmups. Wall timings are excluded. Floating state digests must not use the existing rounded fingerprint as a substitute for exact equality. This checks repeatability, not full-real chunk-vs-monolithic equivalence.

Proposed hard limits, engineering authorization bounds rather than predicted resource needs: preparation <=600 wall s; one advance <=30 wall s; whole benchmark <=1500 wall s including preparation and instrumentation; process private bytes and working set each <=8 GiB. Before starting, available physical memory >=12 GiB; otherwise stop without execution. External watchdog may terminate a worker when a call exceeds its deadline. No increased caps or continuation after failure.

Pending checks: shape must remain (19,166700), counts nonnegative and max <=1000000 per slot/neuron, sum <=100000000 pending deliveries at any boundary. Stop on three consecutive boundary-to-boundary pending-total doublings when the last total exceeds 1000000. These are conservative overflow/workload guards, not expectations of stationarity. Bound each interval's whole-network output to <=1000000 spikes and retained summaries to <=1 MiB; guard sampling cannot promise to intercept every transient allocation, so process-memory watchdog remains necessary. Stop for nonfinite state, identity mismatch, wrong timestep (+200 required per advance), or replay digest mismatch. Readout inactivity is reported operationally and does not invalidate a cost measurement; it blocks later demonstrator authorization. No automatic extra activity-seeking experiment.

Completion answers the cost of this exact already-prepared full graph and stateful workload. It does not bound every future bilateral/feedback workload. Future arena authorization must review these measurements, retain hard limits, and stop for activity-dependent overload.

## First demonstrator horizon and controls (future only)

| Horizon | 20-ms intervals | Scientific usefulness | Operational cost risk | Visual usefulness |
| --- | ---: | --- | --- | --- |
| 0.2 s | 10 | Minimum bounded multi-update integration/feedback check; sparse MN9 may fail | Smallest listed horizon; cost still unmeasured | Small displacement (<=0.05 units); step inspection/trail sufficient |
| 0.5 s | 25 | More activity opportunities, no stronger biological claim | 2.5 times as many intervals; no cost promise | More visible displacement |
| 1.0 s | 50 | Longer engineering observation, not justified initially | 5 times as many intervals; output/retention pressure | More motion, not scientific justification |
| 2.0 s | 100 | No necessary first-loop advantage | 10 times as many intervals; largest exposure | Best animation only |

Select **0.2 s maximum initial duration**, ten intervals, no automatic extension for inactivity. This is a proposed cap, not execution authorization or a claim that ten windows will activate MN9.

Minimum future control set, one deterministic 200-ms sequence each, same initial state and variate table, **five conditions plus one intact replay, at most six runs**, pending separate authorization:

1. Intact network, contact encoder, selected decoder.
2. Both MN9 decoder readouts masked to zero; neural dynamics unchanged.
3. LEFT encoded sensory events suppressed, RIGHT normal.
4. RIGHT encoded sensory events suppressed, LEFT normal.
5. Fixed motor command v=0.25, omega=0, independent of readout; real neural dynamics retained.

The mask condition supplies zero-output comparison; the fixed-output condition supplies nonresponsive movement comparison. Side suppressions interrogate input dependence without inventing motor polarity. The sixth run repeats intact input/geometry/state initialization and requires exact per-interval input, neural-state, readout, action and geometry digest equality; timing is excluded. Compare realized input, readout and actions, not just trajectories. These controls establish only computational dependence in this model/engineered loop; a null difference is a valid failure of the desired demonstration. Randomized/shuffled readout is unnecessary: it adds stochastic/temporal confounds and extra runs without a minimum-protocol need. No Task010/011 candidates are used as decoder neurons or perturbations.

## Exact causal boundary map

`arena geometry -> engineered virtual sugar encoder -> frozen sugar sensory populations -> real MaleCNS model dynamics -> MN9 activity -> engineered threshold decoder -> arena movement -> next arena geometry/input`.

| Arrow | Boundary |
| --- | --- |
| Geometry -> distance/bearing/rate and rate -> explicit sensory voltage events | ENGINEERED, including contact radius, side factors and seeded event realization |
| Frozen sensory IDs -> downstream graph relations -> MN9 relations | CONNECTOME-DERIVED topology; transmitter/sign resolution and signed weight conversion additionally MODEL-DERIVED; no direct sugar->MN9 edge implied |
| Events plus graph/state -> evolving v/g/refractory/delay/spikes -> readout counts | MODEL-DERIVED LIF dynamics and observation; no biological mechanism conclusion |
| MN9 counts -> threshold command; command -> arena kinematics; moved geometry -> next input | ENGINEERED, no natural motor reconstruction |
| Authoritative geometry/neural counts/action -> glyphs, plots, trail and playback pacing | VISUALIZATION-ONLY; rendering never feeds the neural state |

## Narrow success and stop rules

Future success requires all of: real graph advances resumably to ten intervals; registered virtual sensory differences change real MN9 activity under at least one sensory suppression control; intact readout activity exercises the selected decoder and its mask changes an action; movement changes a later encoder intensity/rate/event decision compared with the nonmoving masked condition; exact deterministic replay holds within the separately authorized envelope; identities and bounds remain valid. None is established in A012. Movement alone is insufficient. Finding sugar, fly behavior, cognition and locomotor reconstruction are not success criteria.

Future arena uses A013's resource/nonfinite/identity/pending/output guards, total preparation<=600 s and each advance<=30 s; total six-run session<=2400 wall s, <=8 GiB process private bytes/working set, >=12 GiB available memory before preparation. Keep at most twelve log records per run and <=1 MiB retained summaries per run. Reset state/table per run while sharing immutable preparation. Stop without decoder retuning when intact n_L+n_R remains zero throughout all ten windows (or zero activity in both readouts after the first 100 ms: terminate early and classify inactive-under-cap). Decoder-masked controls are intentionally exempt from decoded-activity requirements. Never infer neural inactivity from masked commands. Identity, timestep, nonfinite, or exact replay mismatch stops immediately; lack of causal differences is failure, not permission to increase duration. Any required unpreregistered biological reinterpretation stops the task.

## Arena versus game versus drone

| Target | Added adapters / control dimensions | Interpretation and dependencies | Appeal / decorative-reservoir risk |
| --- | --- | --- | --- |
| Arena | Existing deterministic geometry; contact encoder and one scalar actuator | Smallest engineered boundary, no external simulator dependency | Simple inspection; controls can expose actual dependence; motion alone still risks decorative use |
| Simple game | Game state-to-sugar conversion, discrete actions, collision/reward/reset rules | Game success has no repository-supported neuronal meaning; possibly extra engine dependency | More appealing but incentives to select/tune arbitrary neural signals; higher decorative risk |
| Drone simulator | Spatial/visual sensory conversion, multiple actuation axes, dynamics/safety/timing adapters | No justified sugar-to-flight control semantics; external simulator/physics burden | Rich visualization, much higher engineering and decorative-reservoir risk |

**Arena remains the preferred first target**, conditional on A013 and honest scalar feedback. Neither game nor drone solves missing biological semantics or runtime bounds. This proposal deliberately removes bilateral steering rather than recruiting new identities for visual convenience.

## Scientific firewall and closure

A012 real MaleCNS closed-loop runs **0**; real scientific simulations **0**; full-real stateful benchmark advances **0**; Task017 units **0**; Task017Q **0**; raw-data downloads **0**; archive writes **0**; BANC **0**. Historical Task016 unchanged; Task017 unchanged / **NOT_ROBUST**; `B:\MaleCNS-Archive` unchanged and not accessed. New biological identities **No**; new biological behavior/mechanism claim **No**; hidden ML/training **No**; dt change **No**. Package version **0.3.0**; active tracked workflows **0**. A013 is not started automatically.

Validation and publication results are appended after completion. Only this plan is authorized for the A012 commit `docs: assess real closed-loop demonstrator feasibility`, then push origin master; no tag, release or version bump.

### A012 validation closure (2026-10-05)

`uv run pytest`: **392 passed, 14 skipped in 56.60 s**, including all eight A011 contract tests. Skips: eleven CuPy/device-unavailable cases, one opt-in real full-graph gate, and two further unavailable-CUDA cases. The real gate was not enabled; no real simulation or stateful benchmark was executed. Local dataset tests resolve/validate metadata and mock execution; synthetic fixture dynamics do not constitute real MaleCNS execution.

`uv run python -m compileall src scripts tests`: PASS. `uv run python scripts/check_tracked_integrity.py`: PASS, nine tracked files and internal identities. `git diff --check` and staged diff check: PASS. `uv build`: PASS, 0.3.0 sdist and wheel; repeated after this final documentation edit for closure consistency. Reviewed staged scope: this single new research plan only. No historical evidence or implementation diff. All firewall counts remain zero. Commit/push and exact final local/origin/live identity are verified and reported in the task response, avoiding a self-referential commit SHA in this file.
