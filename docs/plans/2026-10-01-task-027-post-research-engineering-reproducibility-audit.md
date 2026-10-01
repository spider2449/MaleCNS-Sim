# Task 027 — Post-research engineering and reproducibility audit

## Starting checkpoint and firewall

On 2026-10-01 local HEAD, `origin/master`, and live GitHub `master` were `90eaaa2339f60e5a1cb0466081d62a0a1bafc02c`; the worktree and stash were empty. Package version was `0.3.0`; annotated `v0.3.0` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. Task 026 decision C is `NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY`: no preregistration, bounded scientific design, hypothesis, or replacement dataset is authorized. Task 017 remains `NOT_ROBUST`, Task 017Q `KEEP_DEFERRED`, Task 018 unchanged, and the BANC confirmatory route closed.

This is an engineering roadmap only. No Task 017, 018, or 017Q execution; no scientific design, candidate identity, morphology, motif, connectivity, or endpoint work. Frozen scientific artifacts remain untouched.

## Engineering architecture inventory

| Surface | Current mechanism and boundary |
| --- | --- |
| Package and dependencies | `pyproject.toml` declares Python `>=3.12`, CPU NumPy/pandas/PyArrow/SciPy, pytest test/dev groups, and optional `cupy-cuda12x[ctk]==14.2.0`; `uv.lock` is tracked. No uv version is pinned. |
| CPU and GPU | `dynamics/lif.py` is the CPU correctness path; `dynamics/cuda.py` is optional CUDA float64, with device preflight in `scripts/check_gpu.py`. GPU reproducibility also depends on NVIDIA hardware/driver and compatible CUDA runtime. |
| Data and graph | `data/provenance` tracks MaleCNS and Shiu file names, sizes, URLs, and SHA-256. CLI `data verify` checks local files. Normalization, signed projection, sparse graphs, graph fingerprints, and prepared cache are in `src/malecns_sim`. |
| Execution and sealing | Task runners live in `scripts/`; Task 017 audits journal, sidecars, unit inventory, fingerprints and digests. Export/import use a hashed ZIP, recovery manifest, staging, and final journal commit marker. Scoring is read only over a complete matrix. Task 018 has a tracked compact execution artifact. |
| Determinism and results | Seeded schedules, CPU/CUDA equivalence gates, graph/result digests, and canonical serialization are covered by implementation and synthetic tests. Hardware parity remains environment dependent. |
| Tests and portability | Task numbered test files cover synthetic units, integration with opt-in raw data/GPU, and Task 017 corruption/restore failures. A prior disposable CPU clone and temporary-root checkpoint import were tested; independent cross-machine restore was not. |
| CLI, docs, release | README covers CPU/GPU setup, verify, tests, and older task runners; Task 017P covers recovery commands. Release verification is documented and manual. No `.github/workflows` configuration exists. No automated release pipeline or archival service is declared. |

## Documentation and code drift

| ID | Class | Observation |
| --- | --- | --- |
| D1 | E_DOC | README installation/test section presents the v0.3 release's `255 passed, 1 skipped` as a dated baseline, correctly qualified, but does not give the current Task 017 recovery route or Task 026 pause in the quick-start. |
| D2 | E_REPRO | Task 017P says to obtain the bundle named by the tracked manifest, but the bundle's durable custody/access path and independent cross-machine retrieval are not certified. A machine-local path in a historical record is not a fresh-clone recovery service. |
| D3 | E_DEPENDENCY | Python lower bound and CuPy wheel are declared; supported/tested uv version and full GPU host/driver compatibility matrix are not pinned. Locking Python packages does not lock the host driver. |
| D4 | E_PORTABILITY | README PowerShell examples and the validated RTX 3060 Windows environment do not constitute Linux/macOS or different-GPU certification. Task 017 path normalization has Windows handling; portability claims must remain bounded. |
| D5 | E_DOC | The opt-in `MALECNS_TASK007C_REAL=1` full-graph test is visible in test code but absent from README's test instructions. |
| D6 | E_DATA | `data/derived/task008-results.json` is tracked despite the general README description of ignored derived outputs; artifact ownership is therefore path specific. |

No evidence found of an obsolete primary install command, a mismatched CuPy pin, or release instructions claiming CI exists. Historical task records retain historical counts and paths; they are not current setup instructions. Task 017P describes the current checkpoint model, not an old unsealed assumption.

## Fresh-clone reproducibility matrix

| Component | Status | Requirement or limit |
| --- | --- | --- |
| CPU package, imports, synthetic tests | REPRODUCIBLE_FROM_REPO | Python `>=3.12`, uv and `uv.lock`; Task 019's disposable CPU clone passed 241 tests with 15 environment/data skips. |
| GPU package environment | REPRODUCIBLE_WITH_DOCUMENTED_EXTERNAL_DATA | Optional locked CuPy/CUDA Python dependencies plus compatible NVIDIA GPU/driver; a fresh GPU host is not certified by source alone. |
| MaleCNS raw files | REPRODUCIBLE_WITH_DOCUMENTED_EXTERNAL_DATA | Three official v1.0 URLs and SHA-256 in tracked manifest; download and `data verify` needed. Availability is external. |
| Shiu reference files | REPRODUCIBLE_WITH_DOCUMENTED_EXTERNAL_DATA | Commit-pinned source URLs and hashes in tracked manifest. |
| Task 008/010/011 full local derived outputs | REQUIRES_PRIVATE_OR_LOCAL_STATE | Some compact Task 008 output is tracked; full caches/results are ignored and require external data plus authorized scientific regeneration. No regeneration was attempted here. |
| Task 017 compact matrix/scoring and recovery metadata | REPRODUCIBLE_FROM_REPO | Tracked JSON; release clone verified their digests. |
| Task 017 journal, sidecars, ZIP bundle | REQUIRES_PRIVATE_OR_LOCAL_STATE | Tracked manifest pins exact bundle hash, but bytes reside outside Git; retrieval and independent cross-machine restore remain uncertified. |
| Task 018 completed artifact | REPRODUCIBLE_FROM_REPO | `artifacts/task018/execution-result.json` is tracked and LF pinned; original ignored output is not required to inspect it. |
| New scientific execution | DEFERRED_BY_DESIGN | Task 026 paused scientific design/execution. |
| Future external availability/other OS parity | UNKNOWN | No fresh cross-platform certification or guaranteed external mirror. |

## Task 017Q disposition

**Q1 — KEEP_DEFERRED.** Task 017P already demonstrated temporary-root import and synthetic corruption handling. Task 019's source-only clone verified compact evidence. Cross-machine full-checkpoint certification would add value, but requires the external large bundle and another machine; no current scientific resume or release claim depends on it. Its absence is recorded as a risk, not an authorization to run Task 017Q.

## CI and test-suite audit

No GitHub Actions workflow is configured: `TAG_CI_NOT_CONFIGURED` remains true. Generic CPU CI could run locked install/import, synthetic and data-free CPU tests, `compileall`, build, tracked JSON/schema/digest checks, and manifest fixture checks. It must not silently set `MALECNS_TASK007C_REAL=1`. Full MaleCNS graph tests need raw data; CUDA parity tests need GPU/driver/CuPy; checkpoint restore of the actual matrix needs the external bundle; external source availability or credentials must be separated.

The authoritative local target is 255 passes and one established opt-in skip. Categories include data parsing/manifest fixtures, graph/sign/dynamics, deterministic digests, Task 008–011 synthetic analysis, Task 017 unit/scoring/portability, and Task 018 canonical artifact logic. `tests/test_task017_portability.py` already covers corrupt journal/bundle/sidecars, orphan/missing sidecars, wrong specification, partial destinations, interrupted staging, exact idempotence, and tracked recovery-point mismatch. Gaps are an automated generic CI gate, routine clean-clone install/build checks, live cross-machine full-bundle restore, broad OS parity, and GPU environment failure diagnostics. Real-data and GPU gates are intentionally conditional; their absence in generic CI is not a unit-test failure.

## Data and artifact classification

| Class | Important artifacts and recovery path |
| --- | --- |
| TRACKED | `uv.lock`, manifests/provenance, `data/derived/task008-results.json`, Task 017 matrix/scoring/recovery manifest, Task 018 execution artifact, release/source records in docs and Git tag. Clone recovers bytes; hashes/identities are recorded. |
| IGNORED_REGENERABLE | Prepared caches and some Task 008–011 derived outputs under `data/derived/`, provided exact raw inputs, environment, code and separate scientific execution authorization. This is conditional regeneration, not current permission. |
| IGNORED_NONREGENERABLE | Task 017 completed journal/sidecars and formal ZIP are not in Git; exact historical execution state requires preserved bundle bytes. The ignored original Task 018 output is replaceable for inspection by the tracked copy. |
| EXTERNAL_PINNED | MaleCNS v1.0 raw Feather files and Shiu reference inputs have tracked names, source revisions/URLs, sizes and hashes. Availability is not guaranteed. |
| EXTERNAL_MUTABLE | Hosting endpoints, NVIDIA drivers/hardware, package index service and any unpinned external web resources may change. Exact pinned raw bytes must be verified before use. |
| ARCHIVED_EXPORT | Task 017P's formal ZIP is hash identified by `artifacts/task017/recovery-manifest.json`; historical local custody is recorded, but independent durable retrieval is unproven. |

Task 010/011 scientific results have historical record/digest evidence; full local outputs need the ignored cache/results or authorized regeneration. Task 017 scoring and Task 018 compact artifact are tracked. No result values were inspected for this audit.

## Risk register

| ID | Class | Impact | Likelihood | Scope | Evidence | Issue |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | E_CHECKPOINT | HIGH | MEDIUM | SCIENTIFIC_REPRODUCIBILITY | PROVEN | Exact Task 017 journal/sidecars depend on external bundle custody without independently certified cross-machine retrieval. |
| R2 | E_CI | HIGH | HIGH | RELEASE | PROVEN | No automated install/test/build/digest gate protects future commits. |
| R3 | E_REPRO | MEDIUM | MEDIUM | CROSS_MACHINE | PROVEN | CPU fresh clone was release-tested once, not continuously certified. |
| R4 | E_PORTABILITY | MEDIUM | MEDIUM | CROSS_MACHINE | PROVEN | Windows/NVIDIA evidence does not establish other OS/driver parity. |
| R5 | E_DEPENDENCY | MEDIUM | MEDIUM | DEVELOPER_EXPERIENCE | LIKELY | uv tool version and host driver are not pinned by `uv.lock`. |
| R6 | E_DATA | MEDIUM | LOW | SCIENTIFIC_REPRODUCIBILITY | POSSIBLE | External pinned raw file hosts may cease serving matching bytes. |
| R7 | E_TEST | MEDIUM | MEDIUM | RELEASE | PROVEN | Build and tracked artifact digest checks are manual release checks, absent from routine tests. |
| R8 | E_DOC | LOW | MEDIUM | DEVELOPER_EXPERIENCE | PROVEN | README omits opt-in environment variable and current recovery/pause quick links. |
| R9 | E_ARCHITECTURE | LOW | LOW | LOCAL | PROVEN | Tracked Task 008 derived JSON is an exception to the general ignored-derived description. |

## Bounded candidates and readiness

| Candidate | Problem, evidence, users and boundary | Requirements and completion criterion | Readiness |
| --- | --- | --- | --- |
| CPU CI baseline | R2/R3/R7; maintainers and releases. Add one GitHub Actions workflow for pinned/locked CPU install, import, pytest with known conditional skips, compileall, package build, and tracked artifact integrity checks. No source or science semantics. | No raw data/GPU/scientific execution. Need fixture-safe digest verifier or existing read-only check; pass on clean GitHub runner, fail on deliberate build/test/digest defect. | M1 — READY_FOR_IMPLEMENTATION |
| Task 017 bundle custody and restore certification | R1; future scientific custodian. Locate exact hash-matching ZIP, document durable access and independently restore/audit on another host. | External bundle and second environment required; no scientific execution. Certify exact recovery manifest and full inventory. | M3 — BLOCKED_BY_ENVIRONMENT |
| GPU host preflight matrix | R4/R5; GPU operators. Compare documented host requirements and diagnostics across supported hosts. | Additional GPU/OS hardware; preflight only, no science. Pass/fail matrix with driver/runtime/CuPy evidence. | M3 — BLOCKED_BY_ENVIRONMENT |
| Raw-data mirror/archival study | R6; future researchers. Determine durable legally appropriate mirror/custody for manifest-pinned files. | External storage/access research; no science. Written acquisition and hash verification route. | M2 — ONE_BOUNDED_RESEARCH_TASK_REQUIRED |
| README recovery/setup correction | R8/R9; new researchers. Clarify opt-in test, tracked derived exception, Task 026 pause, recovery links. | No hardware/data/science; commands and paths checked against code. | M1 — READY_FOR_IMPLEMENTATION |
| Release automation | R2/R7; maintainers. Automate source verification and artifact gates after a CPU CI baseline. | No science; exact tag/build checks and protected release procedure. | M4 — LOW_PRIORITY until CI baseline |

## Decision and next task

**A — IMPLEMENT_ONE_ENGINEERING_TASK:** add a generic CPU GitHub Actions reproducibility gate. It has the highest demonstrated ongoing value because every future source change currently bypasses automated fresh-runner install, tests, build and artifact-integrity checks. R1 has high scientific impact, but the exact bundle and cross-machine host are external prerequisites; Task 017Q stays deferred. CI has a bounded, outcome-independent implementation and can detect drift before future scientific work resumes.

Acceptance: one workflow on push/pull request installs declared Python and uv with `uv.lock` enforced, runs the data-free CPU suite with documented expected conditional skips, `compileall`, package build/import, and read-only tracked artifact schema/digest verification; a clean generic runner passes, and a controlled broken fixture fails. It must not download MaleCNS raw data, require GPU, run scientific scripts, modify artifacts, or alter scientific semantics. This record authorizes a roadmap selection only; implementation is a separate task.

## Nonclaims and execution accounting

This audit does not certify a new fresh clone, other operating systems, generic GPU parity, external raw-host permanence, or cross-machine Task 017 restore. It does not revise historical task findings or infer scientific results. Scientific simulations **0**; scientific endpoint calculations **0**; new hypothesis tests **0**; candidate morphology inspections **0**; candidate identity decisions **0**; motif calculations **0**; partner-edge analyses **0**; synapse-count analyses **0**. Task 017 reruns **0**; Task 018 reruns **0**; Task 017Q executions **0**.
