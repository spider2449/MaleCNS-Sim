# A024 — Application/runtime release preparation

Date: 2026-10-07. Authorization: continue A024. Starting local HEAD,
origin/master and live GitHub master all equal
`70d494b144162aff2e8918bf81e96508dea92a34`.

## Scope and plan

Complete A021 P2/P3/P5 after A022 and A023-A: author the consumer runtime guide,
synthetic examples, migration/support boundaries, candidate release notes,
packaging/export review and an explicit future artifact gate. Correct stale
current-scope prose while preserving historical records. Review named ordinary
source/docs as text; validate links, signatures, changed-file scope and diff.
No imports, collection, tests, simulations, builds, protected content reads,
GPU preflight, benchmark or profiler execution. Version stays 0.3.0; 0.4.0 is
the intended candidate only. No tag, publication or release artifact claim.

Incoming `docs/references/deep-research-report.md` is the sole untracked WIP;
A023 explicitly records it as unrelated. Preserve and exclude it. Staging and
stash are empty. Existing worktrees, including prunable entries, are preserved.
No reset, stash, discard or cleanup. No dependency/lock/runtime semantics changes.

Deliverables: `docs/runtime/USER_GUIDE.md`,
`docs/runtime/RELEASE_GATE.md`, `docs/releases/0.4.0-preparation.md`,
README/application/reproducibility navigation and qualified current-scope notes,
and the package description reflecting the implemented engineering scope.
Examples are inline Python, wholly English, statically reviewed in this task;
their execution belongs to separately authorized artifact validation.

## Entry authority

A023-A / G16 PASS is the committed release-safe H/I/N result: 1556 collected,
1544 passed, 12 NOT RUN. I0 unprotected content and bounded I2 passed; I1 remains
NOT RUN — REGISTERED-PAYLOAD-REQUIRED. This is historical implementation
evidence, not certification of the A024 candidate or a newly built wheel.
Task026 remains NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY. GPU GREL-B and
engineered synthetic Arena CREL-B remain experimental; performance is paused.

## Packaging/export review

Static review confirms `malecns_sim.runtime.__all__` contains only
prepare_runtime, PreparedRuntime, SimulationState and AdvanceResult. Root and
dynamics legacy exports remain intact; the new names require the runtime module.
The optional `experimental.gpu` module exports prepare_gpu_runtime,
GPUPreparedRuntime and GPUSimulationState, with lazy backend construction.
PreparedNetwork, dataset preparation, raw buffers, packing and timing stay
internal. No export modification is needed.

Setuptools src discovery includes runtime and experimental modules; application
HTML/CSS/JS are declared package data. Python >=3.12 and the existing four
runtime dependencies remain unchanged. GPU extra is
cupy-cuda12x[ctk]==14.2.0; both existing CLI entry points remain unchanged.
Only descriptive metadata changes. Repository Markdown guides are linked from
the package README, not promised as wheel package data. An installed wheel's
actual contents, entry points and dependency isolation remain unverified here.

## Completion disposition

**A024-A — BOUNDED RELEASE PREPARATION READY; ARTIFACT CERTIFICATION DEFERRED.**
Consumer documentation, two CPU examples and an experimental GPU lifecycle
example, migration/support matrix, candidate notes and artifact gate are written.
README and application/reproducibility entry points distinguish historical
release/certification from current preparation. Package description reflects
the implemented workbench/runtime; version/dependencies/lock/exports are unchanged.

Static review checked example constructors and factory/event/result signatures
against ordinary source and existing synthetic fixture construction; no executable
correctness claim is made. Relative links in the new runtime/release guides are
checked for target existence only, without opening protected targets.
`git diff --check` passes. Final allowed changes are this plan, the three new
runtime/release documents, README, pyproject.toml, docs/REPRODUCIBILITY.md and
the three application guides. Unrelated incoming research WIP remains untouched.
No tests/imports/collection/builds/simulations/GPU preflight/performance work or
registered content reads were performed. No commit/push, version bump, tag,
release or publication was performed in A024.

The next task is A025: separately authorized
guarded candidate/artifact validation against the final A024 bytes. No automatic
A025 start, version bump, publication or scientific execution.
