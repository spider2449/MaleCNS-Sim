# A023 — Public runtime implementation

Authorization: **授權 A023**. Starting root derived with git rev-parse:
`D:/spider/working/MaleCNS-Sim`. Local HEAD, origin/master and live GitHub master
all equaled `c5ad89377575592665344f6420126b16c29b4339`. Worktree/staging/stash
empty, version 0.3.0, tracked workflows zero. A022 is authoritative.

Plan: audit A022/source/export/test boundaries; wrap retained CPU/GPU engines;
add bounded synthetic contract tests; validate with source guard before imports
and discovery; run increasing checks; record gates; commit/push only on full pass.
No scientific equations, legacy signatures, kernels or production defaults change.

## Architecture and scope

Stable module exports: runtime.prepare_runtime, PreparedRuntime, SimulationState,
AdvanceResult. Experimental module exports: experimental.gpu.prepare_gpu_runtime,
GPUPreparedRuntime, GPUSimulationState. Root/dynamics legacy exports unchanged.
PreparedNetwork, packing, instrumentation, raw arrays and Arena adapters stay
outside these exports. Closed-loop remains engineered synthetic example-only.

Factory validates and copies execution projection arrays, checks edge/CSR
consistency and parameters/grid, and retains existing identities. CPU uses the
unchanged dense lif PreparedRuntime. GPU construction lazily wraps the retained
cuda engine/current device. No backend selection, tuning or timing options.
Opaque slotted handles reject direct construction, copying and serialization;
only private storage holds the engine and state. Each state strongly retains
its exact facade owner. Identity equality, rather than matching fingerprints,
controls admission. Fresh initial_state calls allocate independent buffers.

ADV-A preflight checks state/owner/health, numeric types, positive grid duration,
int64 bounds and normalized explicit events; packs events before engine entry.
The unchanged engine also performs its existing packing. This deliberately
avoids adding a new packed-input execution seam or changing the numerical loop.
Ordinary exceptional exits from engine entry through result conversion poison
only that state and propagate unchanged; preflight failures do not poison.
Tests monkeypatch existing private engine/result seams; no production failure
control is introduced. Time is derived from integer timestep times dt_ms.
AdvanceResult contains only immutable detached Python scalar tuples and A022
fields/properties. Existing duplicate, endpoint, weight and refractory semantics
remain in the legacy explicit-event inputs and integrator.

A023 explicitly directs not catching KeyboardInterrupt/SystemExit; this takes
precedence over A022's broader interruption wording. Only Exception is caught;
process-level exceptions are neither caught nor relabeled. No other deviation
is intended. CPU close/context manager remains absent; experimental GPU close
delegates to the existing idempotent resource lifecycle.

## Validation and terminal decision

Guard-first bootstrap: existing R2/R3/R4/R5 controls, **39 passed**. Mandatory
activation and absolute firewall PYTHONPATH apply before Python imports/test
discovery. Audit log is outside the repository in the system temporary directory.
No guard implementation change. No benchmark, profiler, full-real preparation,
registered payload experiment or release execution is authorized here.

Remaining documentation belongs to one bounded release-preparation task:
synthetic quick-start/lifecycle/migration, endpoint/error/poisoning guidance,
CPU resource/evidence disclosures, optional GPU close/EQ-B disclosure, and
packaging/release gates. Candidate 0.4.0; package remains **0.3.0**.

**A023-B — IMPLEMENTATION PARTIALLY COMPLETE; ONE CONTRACT BLOCKER REMAINS.**
The sole blocker is completion of G16 under the mandatory zero-registered-payload
validation boundary: the current ordinary suite and child-process tests are not
compatible with that guarded execution route. This is not an A022 API redesign
finding. No release readiness or full-validation pass is claimed.

| Check | Actual result |
| --- | --- |
| Guard bootstrap R2/R3/R4/R5 | 39 passed, 5.56 s |
| A023 first targeted attempt | 1 passed, 1 failed: new test incorrectly assumed three fixture neurons; corrected to existing four-neuron fixture |
| A023 corrected targeted suite | 27 passed, 2.47 s; bounded functional GPU smoke passed |
| Affected initial CPU/application run | 58 passed, 1 failed: existing A011 HTTP/UI test's Node child rejected by unchanged firewall |
| Final isolated runtime regressions | 124 passed, 12.14 s |
| Full pytest discovery/run (`uv run pytest -x`) | 1503 collected; 22 passed, 1 failed; remaining not run after fail-fast |
| compileall src scripts tests | PASS, exit 0 (quiet mode) |
| uv build | NOT RUN after full-validation blocker; no build success claimed |
| tracked integrity checker | NOT RUN after blocker; its static source shows reads under data/ prohibited by current guard, no exception/bypass introduced |
| git diff --check | PASS; final untracked files also checked using no-index diff checks |

The full-suite failure is
`tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields`.
`DatasetCatalog.local().spec()` attempted
`data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather`;
the Arrow wrapper raised SourceAccessDenied **before content read**. It did not
execute a registered payload experiment. Neither the guard nor the existing test
was weakened or repaired. The A011 Node launch was also rejected before launch.
No rerun of the full suite with the guard removed, relocated inputs or altered
catalog availability was attempted.

Final isolated set: test_application_a023.py, test_task005.py,
test_application_a011.py::test_exact_continuity,
test_application_a011.py::test_initial_state_and_identity,
test_application_a019j.py, test_application_a019s.py, test_application_a019t.py.
It protects analytical update, refractory/delay, exact chunk continuity, retained
pending storage, independent replay and bounded GPU correctness. Existing
numerical expected outputs and tests remain unchanged. One environment warning
reports undetected CUDA_PATH; GPU correctness execution nevertheless passed.

## API acceptance

| Gate | Disposition |
| --- | --- |
| G1 stable import | PASS |
| G2 PreparedNetwork internal | PASS |
| G3 opaque facades | PASS |
| G4 independent exact-owner initial states | PASS |
| G5 ADV-A | PASS |
| G6 pre-mutation validation | PASS |
| G7 ordinary execution/result failure poisoning | PASS under explicit A023 process-exception boundary |
| G8 canonical duration/time | PASS |
| G9 existing explicit event semantics | PASS |
| G10 internal packing | PASS |
| G11 immutable detached result | PASS |
| G12 error categories without string lock-in | PASS |
| G13 experimental GPU boundary | PASS |
| G14 additive v0.3 imports/behavior | PASS; legacy export/source surfaces untouched |
| G15 underlying runtime regression | PASS, isolated 124-test set |
| G16 full validation | NOT PASS; full suite blocked and build/integrity unrun |

## Exact changed-file inventory and custody

Only new files:

- src/malecns_sim/runtime.py
- src/malecns_sim/experimental/__init__.py
- src/malecns_sim/experimental/gpu.py
- tests/test_application_a023.py
- docs/plans/2026-10-07-application-a023-public-runtime-implementation.md

No existing source/test/doc file was edited. No metadata/dependency/version edit.
No performance benchmark or profiler runs, A019 full-real reruns, registered
payload reads accepted, downloads, archive changes or scientific interventions.
Only bounded synthetic tests ran; existing A011 regression tests exercised the
engineered synthetic Arena fixture, with no separate Arena experiment or
implementation expansion. No new scientific claim or GPU certification scope.
Task guard audit logs remain outside tracked files in C:/TEMP/a023-*.jsonl.

Commit/push **NOT PERFORMED**, because G16 is not satisfied. No tag, release,
publication or version bump. Local/origin/live remain the starting SHA, staging
and stash empty, worktree contains exactly these five untracked A023 files;
tracked workflows zero, version 0.3.0. No reset/stash/discard used.

Exact next task: **A023-R — establish a separately authorized zero-payload
validation route for the ordinary suite, required child controls, build and
tracked metadata integrity; then complete A023 G16 and commit/push this retained
implementation.** Do not start release preparation until that closure passes.

## A023-R recovery (2026-10-07)

Authorized recovery stopped as **A023-R-B**; overall **A023-B** and the original G16 blocker remain. See [the recovery report](2026-10-07-application-a023r-zero-payload-validation-recovery.md) for frozen five-file fingerprints, guarded 1503-node collection, static payload dependency evidence, and the unresolved all-Z0 execution route. No runtime or test changes, commit, push, build, or integrity execution occurred in recovery.

## A023-R2 stop (2026-10-07)

**A023-R2-CONTRACT-VIOLATION**: an unexpectedly broad native source search ran
outside the Python guard; task-wide zero registered-content reads cannot be
certified. See the appended R2 incident record in the recovery report. Overall
**A023-B**, prior G1-G15 history and G16 NOT PASS remain. Original runtime/test
bytes are preserved. No final validation, build, integrity, commit or push ran.

## A023-R4 stop (2026-10-07)

**A023-R4-B — ONE RELEASE-SAFE VALIDATION BLOCKER REMAINS.** Incoming guarded
ordinary collection yielded 1515 distinct nodes, not the required 1503; exactly
12 nodes belong to the existing R3 inspector self-tests. The explicit collection
mismatch STOP gate was honored without subtracting or hiding those tests.
See the recovery report's R4 section for incoming fingerprints and guard logs.
Overall A023-B and G16 NOT PASS remain. No runtime/test/guard edits, test
execution, build, integrity, commit or push followed. R1/R2/R3 history preserved.

## A023-R6 stop (2026-10-07)

**A023-R6-CONTRACT-VIOLATION**: the agent ran the guarded 27-node A023 targeted
suite before certifying A011's terminal disposition and the R6 taxonomy gate.
The tests passed with no denied reads, but premature execution violates the
required ordering and does not satisfy G16. See the appended R6 incident record
in the recovery report. Overall **A023-B**, historical G1-G15 dispositions and
**G16 NOT PASS** remain. All source/test/guard/manifest bytes are preserved;
only the two reports receive incident records. No final release-safe suite,
compile/build/integrity, commit or push followed recognition of the violation.
R1-R5 history remains intact. A024 is not started.
