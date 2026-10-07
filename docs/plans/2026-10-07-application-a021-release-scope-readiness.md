# A021 — Application/runtime release scope and readiness

Date: 2026-10-07. User authorized A021, static review, this report, commit and push. **A021-B — RELEASE DIRECTION VALID; PUBLIC API SCOPE REQUIRES ONE DESIGN PASS**. This is a roadmap, not release authorization or fresh runtime certification.

## Starting gates and method

Root derived with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`, repository spider2449/MaleCNS-Sim. Local HEAD = origin/master = live GitHub master = **39ca0fe3486871f80869e4b36095cf68ec8230d4**. Worktree clean, staging empty, stash empty, version **0.3.0**, tracked workflows **0**. All gates passed before writing.

Plan: read named repository source, metadata, tests and committed reports as text; inventory public surfaces and evidence boundaries; assess bundles, API/docs/tests/packaging; choose one next task; write only this file; diff-check, commit/push and verify custody. No imports, Python invocation, test discovery, catalog traversal or payload inspection. Memory guidance supplied navigation only; conclusions below were checked against repository text. No external literature lookup or data download was needed.

Preserve [A020](2026-10-07-application-a020-roadmap-decision.md): **A020-D**, **MILESTONE-B complete with explicit deferred items**, **REL-A**, scientific preregistration **NOT_READY**. [Task026](2026-10-01-task-026-v0.4-post-banc-research-roadmap-gate.md) remains controlling. Engineering release work cannot reopen or imply a scientific claim.

## Evidence and release-worthy change

The historical v0.3.0 source is distinct from current master. The meaningful new engineering capability is prepare-once/advance-many stateful execution with independent fresh states, delayed/pending and refractory continuity, and deterministic replay, accompanied by an engineered application workbench. Existing CLI names are `malecns-sim` (`cli:main`) and `malecns-workbench` (`application.server:main`); historical analysis/benchmark scripts are reproducibility tools, not supported general runtime APIs. Ordinary `ProductionEngine.simulate` still selects one-shot CPU/CUDA execution; no general resumable workbench scenario UI is claimed.

Authority: [A011](2026-10-02-application-a011-closed-loop-arena.md) for CPU exact regular/irregular continuity and synthetic engineered Arena; [A012](2026-10-05-application-a012-real-closed-loop-feasibility.md) and A020's A013–A018 review for the distinction between real-runtime feasibility and unimplemented real adapters; [A018UJ](2026-10-05-application-a018uj-identity-evidence-adjudication.md) for accepted bounded preparation and identity-layer adjudication; [A019D](2026-10-06-application-a019d-full-real-stateful-benchmark.md), [A019J](2026-10-06-application-a019j-membrane-o1-optimization.md), [A019L](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md) for optimization/replay/latency; [A019S](2026-10-06-application-a019s-resumable-gpu-implementation.md), [A019T](2026-10-06-application-a019t-cpu-gpu-resumable-equivalence.md), [A019V](2026-10-06-application-a019v-synthetic-cpu-gpu-performance.md), [A019Y](2026-10-07-application-a019y-trace-observer-disposition.md) for GPU certification, negative performance and pause. Intermediate preparation failures and feasibility decisions are not relabeled successes by later reports.

## Public surface inventory

Export means explicit re-export at package/dynamics level; direct module importability alone is not a support commitment. PUB-STABLE below preserves existing documented surfaces within their present semantics, not a retroactive promise covering every implementation detail.

| Module / surface | Export and documentation now | Tests / evidence | Proposed classification and compatibility implication |
| --- | --- | --- | --- |
| `dynamics.lif.EffectiveSignedProjection`, `LIFParameters`, `simulate_lif` | Root and dynamics exports; reference documentation | Task005 and later regression evidence | PUB-STABLE existing model-level CPU surface; preserve defaults, fingerprints and one-shot behavior |
| `analysis.task008.PreparedNetwork` | Direct module only; architecture/report descriptions | Task008/A018UJ/D/L | INTERNAL envelope: scientific curation, timings, cache identity and optional one-shot CUDA graph are bundled; do not promise immutable deep ownership or expose all fields as a new runtime contract |
| `analysis.task008.prepare_network` | Direct module only; architecture entry | Task008 and preparation evidence | INTERNAL for this release: dataset paths, publication selection, sign policy, cache writes and `use_cuda` are policy-coupled; not a backend-neutral factory |
| `dynamics.lif.PreparedRuntime` | Neither root nor dynamics re-export; docstring/A011 reports | A011/J/D/L | PUB-CANDIDATE, API-B today; intended CPU core after design decision |
| `dynamics.lif.SimulationState` | Direct module only; report/docstring | A011 state isolation/identity and full-real replay | PUB-CANDIDATE, API-B as runtime-created handle; direct construction and mutable array layout INTERNAL |
| CPU `initial_state()` / `advance()` | Methods with type annotations and docstrings; no complete consumer guide | A011 exact continuity; J scratch/output isolation; D/L replay | PUB-CANDIDATE, API-B: explicit in-place state mutation and fresh allocation; fingerprint identity rather than strict object owner |
| `dynamics.stimulus.ExplicitStimulus`, `SpikeSchedule`, `PoissonStimulus` | Root/dynamics exports; existing dynamics usage | Task005/A011/S/T | PUB-STABLE inputs; resumable use accepts explicit events only, not per-chunk RNG regeneration |
| `dynamics.stimulus.schedule_events`, `validate_refractory_ids`; GPU packing helpers | Direct implementation functions, no supported packing API | S/T admission and multiplicity coverage | INTERNAL: position mapping, duplicate packing and instrumentation must remain replaceable |
| `dynamics.lif.SimulationResult` | Root/dynamics export; existing output contract | Task005/A011/J/S/T | PUB-STABLE existing result; new chunk interpretation requires documentation, not a new checkpoint format |
| `dynamics.cuda.GPUPreparedRuntime`, `GPUSimulationState`, their initial/advance/close methods | Direct module only; R/S/T lifecycle evidence | S structural/failure tests and T device certification | EXPERIMENTAL, API-B; separate device concrete types, owner token, lock, close/failure rules; no transparent interchangeability |
| `application.arena.ArenaSession`, `ArenaState`, `encode`, `decode`, `environment_step` | Internal module; Arena UI/report descriptions | A011 Python/JS/manual acceptance | EXPERIMENTAL example-only behavior; direct Python functions/session internals API-C, not extensible biological adapter contracts |
| Application experiment/result/export schemas | Versioned documented workbench contracts; not root runtime exports | A002–A011 contracts, playback/comparison/export | PUB-STABLE only at existing documented application boundary; no arbitrary chunk sequence or durable state restore |
| Backend selection | Existing ExperimentSpec/UI CPU/CUDA and task008 `use_cuda`; distinct direct runtime classes | Existing dispatch plus S/T | Preserve existing bounded selection; new unified resumable selector DEFERRED, not implied by EQ-B |
| `AdvanceTiming`, profiler hooks, private loop/state/packing seams | Direct/internal instrumentation | F–J/X tests/evidence | INTERNAL; exclude from public support even where advance currently exposes optional timing |

CPU arrays are observable/mutable; projection arrays are read-only but the preparation envelope contains other objects. GPU state buffers are observable but explicitly not caller-mutable. No clone, serialized checkpoint, arbitrary state editing, thread safety or cross-backend state migration is included.

## Coherent bundles and stability gate

**R1 + R4** form the smallest core: a CPU Python runtime on an explicitly supplied prepared projection, plus reproducibility/performance documentation. R2 is an optional experimental companion; R3 is an engineered synthetic example demonstrating the seam. They do not require a new scenario runner, UI integration or simulator. Existing workbench capability may accompany the distribution without enlarging the new supported runtime contract.

For every CPU PUB-CANDIDATE:

| Gate | PreparedRuntime | SimulationState handle | initial_state / advance |
| --- | --- | --- | --- |
| Naming | Coherent with prepared graph; distinguish envelope/runtime | Coherent but generic backend name | Coherent lifecycle verbs |
| Lifecycle | Construction from projection explicit; no CPU close | Created fresh; retained across calls | Allocate independently, mutate supplied state |
| Ownership | Frozen runtime fields; identity is fingerprint tuple | Public constructor/buffers invite unsupported editing | Equal-identity runtimes may accept CPU state; GPU strict owner differs |
| Errors | Existing ValueError/TypeError/KeyError routes | No selected public malformed-state policy | Need supported exception categories; no promise of message strings or transactional recovery |
| Inputs/outputs | Annotated projection/parameters/dt | NumPy fields annotated, no opaque public policy | Explicit stimulus/result typed; timing leaks instrumentation |
| Backend alignment | Same semantic chunk seam, different concrete lifecycle | Device/close/failure only on GPU | CPU lacks GPU failure poisoning/lock contract |
| Compatibility debt | Import path/export and supported constructor fields undecided | Freezing buffer layout now creates avoidable debt | Timing, concurrency, error recovery and event/result time rules need support exclusions |
| Coverage | A011/J and bounded D/L protect numerical behavior | Isolation/pending/refractory protected | Strong continuity evidence; not comprehensive public misuse/compatibility coverage |

All are **API-B now**. The intended supported subset can become **API-A** after one design pass freezes its support contract; this report does not silently promote tested internals. PreparedNetwork/preparation, packing, timing and adapter internals are **API-C** for this release. No implementation defect or required rewrite is inferred merely from different backend ownership models.

## GPU and closed-loop disposition

**GREL-B — experimental alternate backend**, retained, not removed. EQ-B means bounded synthetic application equivalence: exact discrete structure/output requirements plus floating `rtol=atol=2e-13` under A019T fixtures, not universal byte equality or full-real certification. Current i9-7900X versus RTX 3060 S1–S4 evidence has CPU faster at all 80 paired measured positions. GPU performance/profiling is **PAUSED**, backend **RETAIN-CERTIFIED**, full-real GPU benchmark **NOT JUSTIFIED**. No full-real GPU speedup, realtime or default-backend recommendation. Legacy one-shot CUDA evidence must not be confused with resumable certification.

**CREL-B — experimental/example-only**. Publish the existing fixed synthetic example with explicit engineered sensory encoder and engineered motor decoder; do not support arbitrary adapter/session Python internals or claim a biological fly behavior simulator. Preserve:

`WORLD -> ENGINEERED SENSORY ENCODER -> MaleCNS-Sim -> ENGINEERED MOTOR DECODER -> BODY/WORLD`.

## Documentation readiness — DOC-B

Existing architecture/user/reproducibility guides cover installation and bounded workbench contracts, but README still says no sensory/body coupling and emphasizes historical v0.3 scientific scope; architecture contains historical feasibility text and reproducibility names A008's older baseline. These should be qualified without erasing historical certification. No complete supported resumable API guide exists.

Bounded required documentation after API selection: architecture distinguishing projection/envelope/runtime/state; prepare-once/advance-many and independent-state synthetic examples; lifecycle/ownership/error exclusions; absolute output spike steps versus chunk-relative input times; exact grid, endpoint exclusion and duplicate multiplicity; pending/refractory continuation and trace boundary columns; stochastic schedule generated once then sliced; CPU/GPU support matrix, optional dependency/device close/failure rules; EQ-B and performance disclosures; local-data/resource prerequisites; claim boundaries; reproducibility and migration from v0.3.0. No tutorial execution is authorized here. Existing imports/one-shot defaults and historical tags remain unchanged; new API is additive only if the next design pass can specify that honestly. A009 is not certified and no new-user acceptance is inferred.

## Static validation inventory — TEST-B

Coverage is substantial, but the future release gate must consolidate scope and guards rather than reuse a historical scientific checklist as current certification.

| Release-critical area | Static evidence / future gate |
| --- | --- |
| CPU continuity/isolation | `tests/test_application_a011.py`: regular/irregular chunk traces, pending/refractory state, identity and independent allocation |
| Optimized CPU replay | `tests/test_application_a019j.py`: frozen replay, scratch ownership and independent outputs |
| Full-real evidence | `tests/test_application_a019d_result.py`, `test_application_a019l_result.py`: offline custody/statistics/replay; historical D/L execution, no routine full-real rerun |
| GPU structure/lifecycle | `tests/test_application_a019s.py`: fake-device/admission/overflow/close/failure/isolation; not a substitute for device certification |
| Synthetic EQ-B | `tests/test_application_a019t.py` and committed T matrix; actual device numerical execution needs separate explicit authorization, not implicit release-prep permission |
| Source/read containment | A019C-R18 guard-first certification and manifest/firewall tests; install task-wide fail-closed guard before future discovery/import/tests; preserve all historical STOP outcomes |
| Packaging/application | A008/A011 installed-wheel evidence, test_application_a008, packaged static assets and CLI operation; fresh artifact required for future release |
| Integrity/existing checks | `scripts/check_tracked_integrity.py`, tracked-integrity tests; documented pytest, compileall, diff-check, uv build and isolated wheel smoke |

Future gate must list exact guarded checks, skip/optional GPU policy, source SHA/lock/wheel digest, Python versions, installed import location/assets/entry points, and offline evidence custody. It must not make benchmarks/profiling/real preparation part of routine release validation. Any actual synthetic simulation in tests requires later explicit task authorization; A021 authorizes none. No tests or build were run, and no new passing gate is claimed.

## Packaging — PKG-B

Static metadata: setuptools>=68/build_meta, src discovery, application HTML/CSS/JS package data; Python >=3.12; numpy>=1.26, pandas>=2.1, pyarrow>=15.0, scipy>=1.11. GPU remains optional: `gpu = [cupy-cuda12x[ctk]==14.2.0]`; uv.lock includes that extra conditionally. Lazy CuPy access and CPU-only installed-wheel evidence support optionality, not every declared platform/Python combination. No dependency change is justified now.

Bounded packaging work is public export selection after design plus updating the package description/support matrix to include current engineering scope. No upper-bound churn or new extra is required by this audit. Current wheel/version declarations do not certify a future artifact; verify installed artifacts under the later authorized gate. GPU optionality itself has no identified material packaging blocker.

## Version recommendation — VERSION-C

Defer an exact candidate version until the public API design pass closes the support decisions. **0.4.0 is the conditional intended minor**, appropriate if coherent additive R1 capability becomes supported; it is not an unconditional recommendation in A021. A 0.3.x patch is inappropriate for meaningful new public runtime capability, and 1.0 is unjustified. Any engineering 0.4.0 would be explicitly unrelated to historical scientific v0.4/BANC roadmap concepts; it cannot resurrect unresolved studies. Package stays 0.3.0.

## Future release-note facts and resource disclosure

- CPU resumable runtime preserves pending/delayed and refractory state across chunks; synthetic A011 proves exact whole/chunk continuity. Independent full-real D/L replay uses **two fresh 12-call/240-ms states**, 24 aggregate calls, not one 480-ms trajectory. Concurrent full-real multi-state capacity and full-real whole/chunk equivalence are not established.
- Bounded full-real preparation and execution are demonstrated, not guaranteed for every host. A019L: 166,700 neurons / 24,904,953 effective edges; preparation 98.5804007 s; sampled contained-tree private peak 5,441,220,608 B and working set 4,472,893,440 B under separate 8-GiB caps. These are observations, not minimum-RAM promises or instantaneous peaks; raw data remains external.
- A019L-L1 / P2 optimized membrane path: mean **1.094710500 s per 20-ms simulated call**, **54.735525x slower** than 20 ms, qualified descriptive mean reduction 33.5629% versus D. Context: Intel i9-7900X 10-core/20-logical, Windows 10 Pro 19045, Python 3.14.0, NumPy 2.5.3, OpenBLAS 0.3.34.106.0, high-performance power plan. Historical thread/BLAS/power metadata is incomplete; no universal or randomized causal speedup claim.
- Optional GPU resumable state has bounded synthetic EQ-B certification and negative S1–S4 performance on RTX 3060; preserve frozen artifacts/raw calls and paused performance line.
- Engineered fixed synthetic closed-loop example and integrity/installed-wheel infrastructure are engineering facts, not biological findings or fresh release-artifact certification.

## Frozen non-scope

No new scientific preregistration, BANC identity work, indexed-writeback optimization, further CPU O1, GPU performance optimization/profiling, full-real GPU benchmark, realtime claims, real Arena integration, biological interpretation, dataset acquisition, scenario-runner feature or new adapter API. Release scope does not depend on completing these. No reconstructed biological brain, digital twin, behavior predictor, proof of mechanism/direct inhibition/necessity, validated biological sensory transduction/motor decoding, cognition/agency or biological realtime. Product framing: connectome simulation workbench / virtual intervention screening / computational hypothesis prioritization.

## Necessary bounded preparation sequence

1. **P1 design gate first:** freeze import/export paths and supported CPU constructor/handle/method subset; state ownership/editing/concurrency/error/time/result rules; existing preparation policy boundary; GPU experimental and example-only exclusions. Reason: prevent avoidable compatibility debt. This is the only recommended next task.
2. After that decision and separate authorization, combine **P2/P3/P5**: add consumer examples/migration/support matrix, chosen exports/metadata and factual changelog. Reason: make the selected existing capability usable and accurately described; no new feature or optimization.
3. Then separately authorize combined **P4/P6** final guarded validation/artifact/evidence review against the exact resulting source. Reason: old wheels and tests do not certify a changed release artifact. No automatic execution/publication or mandatory scientific/benchmark rerun.

These are dependent bounded categories, not three concurrently authorized tasks. Version bump/tag/release/publication remain separate release authority after preparation gates.

## Readiness scorecard and terminal decision

| Dimension | Score | Basis |
| --- | --- | --- |
| Scope coherence | HIGH | CPU runtime plus factual evidence; optional companions isolated |
| Public API maturity | MEDIUM | Working seam, unselected support/ownership/error surface |
| Documentation readiness | MEDIUM | Existing guides; bounded runtime and stale-context updates |
| Test/reproducibility readiness | HIGH | Strong scoped evidence; consolidated current release gate still needed |
| Packaging readiness | MEDIUM | Optional GPU/build assets present; exports/metadata pending |
| Scientific-claim safety | HIGH | Explicit engineered/non-biological scope and Task026 firewall |
| Deferred-item isolation | HIGH | No deferred science/performance dependency |
| Release preparation complexity | MEDIUM | One design pass then limited docs/exports/validation |

**A021-B**. General release preparation may not begin as an A021-A outcome; one API-scope design pass may be proposed for separate authorization. Release execution authorized: **No**.

Exactly one next task: **Application Task A022 — Design-Only CPU Resumable Runtime Public API and Compatibility Contract**. Deliver one support-contract document choosing paths/exports and supported lifecycle/ownership/error/input-output rules, preserving existing one-shot semantics, leaving dataset preparation internal, and fixing GREL-B/CREL-B boundaries; resolve whether additive 0.4.0 is justified and define a bounded subsequent preparation gate. No code, version/dependency change, test/build/simulation/benchmark/profiler/payload access or publication. A022 is recommended, not started or authorized here.

## Accounting and custody

| A021 operation | Count |
| --- | ---: |
| Simulations | 0 |
| CPU timing / GPU timing / GPU runs / profiler runs | 0 / 0 / 0 / 0 |
| Full-real preparations / real advances | 0 / 0 |
| Registered payload reads / data downloads / archive writes | 0 / 0 / 0 |
| Interventions / Arena runs | 0 / 0 |
| Tests / builds | 0 / 0 |
| Version bumps / tags / releases / publications | 0 / 0 / 0 / 0 |

Counts describe the static command scope; no executable guard/bootstrap or native-read telemetry was run or certified. Only this report changes. `git diff --check` and staged diff-check must pass before commit. Final commit/push identity and worktree/staging/stash/version/workflow verification are reported outside this file to avoid self-reference.
