# A020 — Evidence-only application roadmap decision

Date: 2026-10-07. Authorization: **授權 A020**, including this report's commit and push. Terminal decision: **A020-D — CURRENT APPLICATION/RUNTIME MILESTONE COMPLETE; RELEASE ROADMAP SHOULD BE NEXT**. Milestone: **MILESTONE-B — COMPLETE WITH EXPLICIT DEFERRED ITEMS**. Release assessment: **REL-A — RELEASE ROADMAP JUSTIFIED**. Scientific preregistration: **NOT_READY**.

## Starting gates and review plan

Root derived with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`, repository `spider2449/MaleCNS-Sim`, branch master. Local HEAD = origin/master = live GitHub master = **8628088e4994fd40e6c45e87843cbe8d94c39635**. Worktree clean, staging empty, stash empty, package version **0.3.0**, tracked workflows **0**. All required gates passed before mutation.

Plan: review committed closure reports, application guides, package metadata and named source as text; inventory certified scopes; assess milestone, scientific readiness, bounded engineering alternatives and release value; select one direction; write only this report; run `git diff --check`; commit/push and verify final identities and clean state. No Python invocation, application import, catalog discovery, tests, preflight, profiler, payload traversal or execution. Shell reads were restricted to repository documentation/code/metadata and memory guidance; no registered payload or archive was opened. Prior execution results below are historical evidence, not A020 runs.

## Evidence index and precedence

- [A011](2026-10-02-application-a011-closed-loop-arena.md): exact regular/irregular CPU continuity, independent states, synthetic adapters/arena, manual UI and installed-wheel certification.
- [A012](2026-10-05-application-a012-real-closed-loop-feasibility.md), [A013](2026-10-05-application-a013-real-stateful-advance-benchmark.md): bounded real-runtime protocol and historical preparation memory stop. A013 is not retrospectively relabeled successful.
- [A018UJ](2026-10-05-application-a018uj-identity-evidence-adjudication.md): accepts A018UR completed preparation under the corrected prepared-envelope identity contract; preserves the effective-projection/envelope distinction.
- [A019D](2026-10-06-application-a019d-full-real-stateful-benchmark.md), [A019L](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md), [A019Q](2026-10-06-application-a019q-cpu-vs-gpu-direction-decision.md): full-real replay, optimized latency, qualified comparison and final CPU O1 dispositions.
- [A019S](2026-10-06-application-a019s-resumable-gpu-implementation.md), [A019T](2026-10-06-application-a019t-cpu-gpu-resumable-equivalence.md), [A019V](2026-10-06-application-a019v-synthetic-cpu-gpu-performance.md), [A019X](2026-10-07-application-a019x-synthetic-gpu-profiling-result.md), [A019Y](2026-10-07-application-a019y-trace-observer-disposition.md): implemented GPU seam, bounded EQ-B/self-continuity, negative synthetic performance and terminal profiling pause.
- [A010](2026-10-02-application-a010-workflow-checkpoint.md), [application architecture](../application/ARCHITECTURE.md), [reproducibility](../application/REPRODUCIBILITY.md), [user guide](../application/USER_GUIDE.md): existing workflows and their limitations. A009 remains uncertified; no new-user certification is inferred.
- [Task026](2026-10-01-task-026-v0.4-post-banc-research-roadmap-gate.md), [Task025G](2026-10-01-task-025g-banc-external-validation-route-closure.md): scientific readiness and closed identity route.
- Static source: `src/malecns_sim/dynamics/lif.py` (read-only projection arrays, PreparedRuntime, SimulationState), `dynamics/cuda.py` (GPU ownership/advance/close), `application/models.py` (bounded ExperimentSpec), `application/service.py` (one-shot production dispatch), `application/arena.py` (fixed synthetic session), and `pyproject.toml` (public entry points/GPU extra).

Later certification resolves only its named scope. The older architecture's statement that real runtime feasibility was unestablished is superseded by A018UJ/A019D/L for bounded CPU preparation/advance, **not** for real closed-loop adapters or browser integration. Older one-shot CUDA dispatch does not automatically inherit the resumable GPU certification.

## Phase 1 — Capability inventory

These labels describe engineering evidence scope, not biological validation or a universal production stability guarantee.

| Capability | Classification | Demonstrated scope and limit |
| --- | --- | --- |
| Immutable/prepared graph architecture | PRODUCTION-CERTIFIED | Prepared envelope/projection identities and read-only projection arrays; separate mutable state. A018UJ adjudicates identity layers. |
| Resumable CPU SimulationState | FULL-REAL-CERTIFIED | A011 synthetic continuity plus D/L bounded full-real stateful execution; v/g, absolute refractory deadlines, pending rings and timestep persist. |
| Independent CPU states from one runtime | FULL-REAL-CERTIFIED | D/L one prepared runtime, A then B; independent exact replay. Simultaneous full-real multi-state resource feasibility is not established. |
| Exact CPU chunk continuation | SYNTHETICALLY-CERTIFIED | A011 whole vs regular/irregular chunks with full traces/state exactness. Full-real evidence separately establishes repeated same-schedule replay, not full-real monolithic-vs-chunk equivalence. |
| Full-real CPU repeated replay | FULL-REAL-CERTIFIED | D/L exact state/output/pending comparisons at every boundary; two fresh 12-call/240-ms states, 24 aggregate calls, not one 480-ms trajectory. |
| Resumable GPU SimulationState | SYNTHETICALLY-CERTIFIED | S-A device-resident state, retained graph, isolation, ownership, failure/close rules. No full-real stateful GPU certification. |
| GPU self-continuity/repeatability | SYNTHETICALLY-CERTIFIED | T C3/C5/C7 fresh repetitions byte-exact, irregular boundaries/ring wrap and sibling continuation after close. |
| CPU/GPU EQ-B | SYNTHETICALLY-CERTIFIED | T-A, discrete exactness and float rtol=atol=2e-13 on bounded fixtures; observed byte equality does not promote policy to universal EQ-A. |
| Engineered sensory encoder | SYNTHETICALLY-CERTIFIED | A011 bearing/distance to synthetic impulses; no validated biological sensory transduction or real adapter. |
| Engineered motor decoder | SYNTHETICALLY-CERTIFIED | A011 synthetic spike counts to bounded action/readout masks; no validated biological motor interpretation. |
| Closed-loop application seam | SYNTHETICALLY-CERTIFIED | Manually accepted A011 four-neuron arena, deterministic event log/replay and independent render pacing; no real Arena certification. |
| Full-real CPU preparation | FULL-REAL-CERTIFIED | A018UR accepted by UJ: 166,700 neurons/24,904,953 effective edges, 101.3569613 s; L independently completed preparation in 98.5804007 s. |
| CPU latency / membrane optimization | FULL-REAL-CERTIFIED | L-L1/P2: 1.094710500 s per 20-ms call, -33.5629% mean versus D; exact replay PASS, non-realtime. |
| Current GPU performance disposition | CLOSED | V-C/G4: CPU wins all 80 paired positions in S1–S4. Y pauses performance/profiling; backend RETAIN-CERTIFIED. No full-real extrapolation. |
| Bounded resource feasibility | FULL-REAL-CERTIFIED | L sampled contained-tree private peak 5,441,220,608 B, working set 4,472,893,440 B under separate 8-GiB caps; 600/30/1500-s preparation/call/worker limits. Host/workload-specific, sampled, not instantaneous guarantees. |
| Workbench comparison/playback/export | PRODUCTION-CERTIFIED | Existing bounded MN9/sugar workflow, controlled model-output deltas, schematic/sparse views and integrity-checked export; no arbitrary scenario authoring. |
| Reproducibility/integrity infrastructure | PRODUCTION-CERTIFIED | Canonical identities, pinned provenance, lockfile/local validation, tracked-integrity tool, A008/A011 installed-wheel evidence and contained-worker guards; no fresh A020 validation of these executables. |
| Public resumable API stability envelope | EXPERIMENTAL | Implemented/certified seams exist; long-term compatibility/support commitments and release-surface selection are not established by those tests. |
| Realtime / real closed-loop application | DEFERRED | CPU misses threshold; approved real sensory/readout mapping and end-to-end workflow remain absent. Neither is silently required for this milestone. |

## Phase 2 — Milestone completeness

**MILESTONE-B**. All eight requested conditions are met: incremental state advance (A011/S/T); bounded full-real CPU preparation/execution (UJ/D/L); exact CPU replay/continuity within the scopes above; truthful measured latency (L/V); one implemented, full-real validated membrane optimization (J/L); alternate-backend synthetic semantics (T); enough GPU performance evidence for disposition (V/Y); and explicit residual debt (Q/Y).

The profiler does not explain a dominant GPU cause: X remains INDETERMINATE. Complete causal attribution is unnecessary to retain a correct optional backend and decline another performance attempt. No missing frozen user-facing requirement forces MILESTONE-C. Realtime was a measured threshold, not an established prerequisite for every workbench operation. Real Arena integration remains a distinct unimplemented capability, not a retroactive milestone requirement. Preserve A012-A's engineered virtual-sugar/scalar MN9 actuator design readiness: that proposal exists, but has no certified end-to-end real Arena implementation or useful-feedback result.

## Phase 3 — User/research value

A researcher/developer can now prepare the certified full graph once, create independent states, advance deterministic 20-ms chunks with explicit engineered inputs, preserve delayed/refractory activity across boundaries, reproduce the bounded CPU trajectory, inspect existing exported model-output evidence, and compare alternate-backend correctness on certified synthetic fixtures. Synthetic closed-loop adapter experiments can be replayed without confusing browser speed with neural time. These are virtual-intervention screening/computational hypothesis-prioritization infrastructure capabilities; they do not validate a biological intervention.

Practical limits are concrete: `ProductionEngine.simulate` still dispatches one-shot CPU/CUDA functions; the bounded ExperimentSpec has no general sequence of chunk events/state initialization; ArenaSession accepts its fixed synthetic projection/readouts. Thus a general resumable scenario workflow is not exposed through the ordinary workbench. Existing comparison, visualization and result exports already exist; claiming their wholesale absence would be wrong. Production setup does not request arbitrary voltage traces; A010 records bounded authoring, session-only recent results and no result-reopen route. No new demand study was performed.

Externally meaningful biological application still lacks biologically validated sensory/motor mappings, a new prospective question/control design and an eligible resolved external identity route. A012's engineered mapping proposal is not biological validation. A runtime API cannot supply those. Slow bounded CPU execution permits offline use but does not establish interactive full-real world/body control.

## Phase 4 — Scientific readiness gate

| Required item | Current evidence | Gate |
| --- | --- | --- |
| Concrete new scientific question | No new endpoint/question selected since Task026 | ABSENT |
| Prospectively frozen biological identities | Existing identities support historical tasks; no new-study population frozen; BANC route closed | ABSENT for a new study |
| Explicit intervention/control design | Historical comparison contracts exist; no new scientific design | ABSENT |
| Result-blind hypothesis formulation | Task026 quarantines result-derived leads; engineering certificates are not hypotheses | ABSENT |
| Required available data | Existing MaleCNS resources documented; required data for an undefined new study cannot be established | NOT_ESTABLISHED |
| No unresolved identity/evidence blocker | External-validation identity blocker unresolved | FAIL for that route |
| Compatible claim boundary | Model/connectome limits can be specified, but do not rescue the other missing requirements | CONSTRAINT_AVAILABLE |

**NOT_READY; Task026 remains controlling.** Exact new evidence since Task026 is A011 continuity/engineered integration, UJ accepted preparation, D/L full-real replay/latency and T/V/Y GPU correctness/performance disposition. This changes engineering/release readiness, not biological hypothesis readiness. Preserve Task017 NOT_ROBUST, Task017Q Q1 KEEP_DEFERRED, Task018 anatomy-only/noncausal, BANC_CONFIRMATORY_ROUTE_CLOSED / IDENTITY_NOT_PROSPECTIVELY_RESOLVABLE and Task026 C. No current external literature/data search was performed; no claim is made about all possible new external publications.

## Phase 5 — Bounded engineering candidates

| Candidate | Repository basis / possible payoff | Disposition |
| --- | --- | --- |
| E1 experiment specification / scenario runner | ExperimentSpec identities, PreparedRuntime explicit chunks and Arena event scripts could support bounded initial-state/input/chunk/output/replay definitions | Highest-value engineering candidate: design-only, CPU-first resumable scenario contract. Avoid a new simulator, arbitrary intervention editor or UI project; workflow demand and minimal scope still need justification. |
| E2 intervention comparison | A006 already supports controlled pairs; resumable extension would need new pairing/event semantics | Lower priority; no new contrast currently requires expansion. |
| E3 visualization/analysis | Playback, comparisons and Arena already display bounded evidence; trace authoring is a known narrow gap | Lower priority without a specified observation workflow; do not manufacture a missing entire reporting layer. |
| E4 packaging / CLI UX | Existing public entry points, installed-wheel evidence and later runtime additions | Strong practical value through release scope/docs/support consolidation; implementation changes are not selected here. |
| E5 engineered environment integration | A011 seam already exists; real mappings/budget unapproved and natural behavior unvalidated | Defer; no evidenced payoff beyond the synthetic Arena. |
| E6 backend/resource policy | Existing backend choice and GPU ownership contracts | Retain CPU preference for measured workload and optional GPU scope; no automatic performance-driven selector or GPU-first product. |

A010's A10-E was appropriate for its supported session workflow. Later runtime evidence supplies new potential for E1, but not a demanded general authoring product. It is insufficient to overturn that caution with immediate implementation. The release-roadmap option captures demonstrated value with fewer invented requirements.

## Phase 6 — Release readiness

**REL-A — RELEASE ROADMAP JUSTIFIED**, not release execution approved. The historical v0.3.0 commit is `a1a6651163840a982799b1fa82c1904e67f84660`; a static path diff confirms subsequent application modules/assets, runtime changes and package metadata. README advertises the workbench and pyproject exposes `malecns-workbench`: public consumption is evidenced, not assumed. New application/runtime capabilities materially exceed the original release while version remains 0.3.0.

Versioned experiment/result identities, accepted UI, installed-wheel records, local regression/integrity infrastructure and bounded full-real CPU evidence justify planning a new series. They do not certify current release artifacts or every runtime signature as permanently stable. The application reproducibility guide explicitly identifies A008's older baseline; architecture contains historical real-feasibility statements. A release roadmap should distinguish preserved historical evidence from a current consumer-facing support matrix.

GPU can belong as an optional, bounded-correctness backend with current performance limitations disclosed, if its support surface/lifecycle and dependency requirements are selected explicitly. It should not be the performance-preferred backend. Whether the resumable APIs are supported public API or marked experimental must be decided before publishing. Fresh release validation, artifact certification and compatibility decisions remain future gated work; A008/A011 wheels do not certify a new release automatically. No particular version number is chosen here, and a new engineering release does not declare a new scientific v0.4 question.

## Phase 7 — Deferred ledger

| Item | Preserved status | Reopening requirement; no automatic task |
| --- | --- | --- |
| CPU membrane O1 | CLOSED-SUCCESS | Preserve J/L; no reopening |
| CPU grid validation | CLOSED-NOT-WORTHWHILE | New material evidence, not old parent timing shares |
| CPU input gathers | CLOSED-NO-SAFE-TRANSFORMATION | Concrete safe/useful transformation with separate authority |
| CPU indexed writeback | DEFERRED-HIGH-RISK | Exact replacement/ownership/error semantics and independently justified validation |
| OPEN-HIGH-VALUE CPU O1 | NONE | No optimization continuation selected |
| GPU optimization | PAUSED (Y-A) | New evidence and separately justified scope |
| Profiler attribution | INDETERMINATE / PAUSED (X-C/Y-A) | No recapture justified by current record |
| Full-real GPU benchmark | NOT JUSTIFIED | Current V-C/G4 is negative readiness evidence |
| CPU realtime | NOT ACHIEVED | L mean slowdown 54.735525x; no realtime promise |
| Real closed-loop adapters | DEFERRED | Exact engineered mappings/readouts, budget and separate execution authorization |
| BANC identity | CLOSED under current evidence | New independent identity evidence/prospective route under Task025G |
| New scientific question | NOT_READY | Task026 prerequisites, not engineering progress |
| Task017Q | Q1 KEEP_DEFERRED | Selected study requiring portability, separately authorized |
| General resumable scenario/public API | EXPERIMENTAL / unselected extension | Consumer support scope first; no implied implementation |

## Phase 8 — Direction scorecard

Qualitative judgments are A020 roadmap inferences, not measured demand or numerical weighted scores. Complexity concerns the bounded next task, not all eventual execution.

| Direction | Evidence readiness | User/research value | Scientific risk | Engineering complexity | Unavailable-data dependency | Expected information/product value | Near-term feasibility |
| --- | --- | --- | --- | --- | --- | --- | --- |
| New engineering capability: E1 design | MEDIUM | MEDIUM | LOW | MEDIUM | LOW | MEDIUM | HIGH |
| New scientific preregistration | LOW | HIGH if eligible | HIGH | MEDIUM | HIGH for external validation | LOW now | LOW |
| Scientific-question research/design | LOW | MEDIUM | MEDIUM | LOW | MEDIUM | LOW now | LOW |
| Release/roadmap preparation | HIGH | HIGH | LOW | LOW | LOW | HIGH | HIGH |
| Pause pending biological/data evidence | HIGH | MEDIUM | LOW | LOW | HIGH for resumption | LOW | HIGH |

The highest-value retained scientific/research category is independent external-validation question/identity feasibility **if new independent evidence arrives**. Its concrete blocker is prospective identity/data eligibility. Task026's motif idea still requires coupled ontology/population/null/endpoint decisions; the record does not identify one bounded design step likely to resolve it. Neither category warrants a new research task now. Scientific development should pause pending an eligible question/evidence; a project-wide development pause is not warranted while release scope has demonstrated value.

## Phase 9 — Decision and exactly one next task

**A020-D** selects **release-roadmap preparation** as the sole primary direction. A coherent MILESTONE-B closes A011–A019. This outranks E1 because it consolidates capabilities already publicly exposed and certified, rather than selecting a new workflow without user evidence. It outranks preregistration/research because no scientific gate has changed; it outranks a global pause because distributing understandable existing capability has practical value without biological data acquisition. It avoids every closed CPU/GPU optimization line.

Exactly one next task: **Application Task A021 — Evidence-Only Application/Runtime Release Scope and Readiness Roadmap**.

Bound A021 to a documentation-only consumer capability/support matrix; explicit public-versus-experimental CPU/GPU API scope; historical-v0.3.0-to-current change inventory; documentation/compatibility/packaging gaps; and a proposed minimal future validation/publication gate. Preserve CPU P2, synthetic EQ-B and GPU performance pause; separate engineering release scope from scientific questions. Produce one release-readiness decision with explicit blockers. Do not execute tests/simulations/benchmarks, inspect registered payloads, implement fixes, bump a version, tag or release in that roadmap task. This is a recommendation only: **A021 is not started or automatically authorized by A020**. E1 and scientific feasibility are alternatives, not additional next tasks.

## Nonclaims, accounting and custody

MaleCNS-Sim is a connectome simulation workbench and virtual intervention screening/computational hypothesis prioritization infrastructure. Preserve **WORLD -> ENGINEERED SENSORY ENCODER -> MaleCNS-Sim dynamics -> ENGINEERED MOTOR DECODER -> BODY / WORLD**. No reconstructed biological brain, digital twin, behavior prediction, mechanism, direct inhibition, necessity, cognition/agency, validated sensory transduction/motor interpretation or biological realtime is inferred. CPU P2 is non-realtime; GPU is not performance-preferred. No historical scientific result or terminal performance outcome is revised.

| A020 operation | Count |
| --- | ---: |
| Simulations (including synthetic) | 0 |
| CPU timing runs | 0 |
| GPU timing runs | 0 |
| Profiler runs | 0 |
| Full-real preparations | 0 |
| Real advances | 0 |
| Registered payload reads | 0 |
| Data downloads | 0 |
| Archive writes | 0 |
| Interventions | 0 |
| Arena runs | 0 |

Counters describe A020's static command scope; no executable firewall bootstrap/native read telemetry is claimed. No tests are run because executable code is unchanged. Documentation review confirmed all linked evidence paths exist and exactly this report is staged. `git diff --check` and `git diff --cached --check`: **PASS**. Final commit/push identity and repository-state verification are reported externally to avoid self-reference. No tag/release/version bump.
