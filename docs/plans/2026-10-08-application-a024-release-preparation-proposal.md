# A024 bounded application/runtime release-preparation proposal

Date: 2026-10-08. Status: bounded static documentation reconciliation completed
following the user's instruction to continue. Artifact execution remains outside scope.

## Repository inspection

The supplied A023 authority is `70d494b144162aff2e8918bf81e96508dea92a34`.
Current local master, local origin/master, and live origin master agree at
`c32919d4f0228310401abce17d09d3d68cb76deb`, whose direct parent is that A023
commit. The intervening commit is `docs: prepare A024 application runtime release`.
It already contains the runtime consumer guide, release gate, candidate notes,
navigation updates, and descriptive package metadata. Version is still 0.3.0.
There are no tracked modifications or staged changes and no stashes.
The existing detached execution worktree is preserved.

Incoming untracked files are preserved and excluded from this proposal:

- `docs/manifests/a025-development-stopped-evidence.json`
- `docs/plans/2026-10-07-application-a025-candidate-artifact-validation.md`
- `docs/references/deep-research-report.md`
- `scripts/a025_artifact_validation.py`

Their contents were not inspected in this task. No A025 continuation, cleanup,
reset, stash, rollback, or incorporation is proposed. The supplied baseline and
current checkout differ; do not silently relabel current master as A023-only.

## Product outcome

Make the reusable runtime understandable to an application author: prepare one
resolved projection once, create independent states, advance incrementally,
inject explicit stimuli, consume detached results, and embed the runtime in
engineered systems. Validation and recovery remain supporting evidence.

## Bounded work sequence

1. Reconcile the requested baseline with the already committed A024 preparation.
   Review the existing deliverables instead of duplicating them or reverting the
   checkout. Preserve historical evidence and unrelated WIP.
2. Review `docs/runtime/USER_GUIDE.md` against the existing public CPU contract.
   Cover preparation prerequisites, state ownership, canonical time, chunk-local
   event endpoints, independent trajectories, detached outputs, preflight errors,
   state poisoning, and sequential process-local use. Keep a complete synthetic
   quick start and incremental application example. State that examples are
   statically reviewed until separately executed from an installed artifact.
3. Review migration and support boundaries: legacy APIs remain available; CPU
   runtime is stable; GPU is optional and experimental; closed-loop adapters are
   engineered/application-only. No new persistence, concurrency, backend migration,
   data-loader API, tracing, performance promise, or biological claim.
4. Review package/export configuration as ordinary text: runtime exports,
   optional GPU imports, declared CPU dependencies, CLI entry points, and workbench
   static assets. Record repository-only guides versus promised artifact contents.
   Any executable or dependency change found necessary becomes a separate proposal.
5. Reconcile README/application/reproducibility navigation and
   `docs/releases/0.4.0-preparation.md` with the North Star and current evidence.
   Describe 0.4.0 as intended and unreleased; retain version 0.3.0.
6. Review `docs/runtime/RELEASE_GATE.md` as a finite future artifact checklist:
   exact candidate identity, approved ordinary-input build custody, isolated CPU
   installation, installed examples and continuity oracle, CLI/assets, exclusions,
   optional GPU metadata, and explicit integrity dispositions. Keep execution,
   version transition, and publication outside A024.

## Scope and validation

For this proposal, the only new file is this plan. A later authorized A024
reconciliation is bounded to the existing A024 documentation paths and, only
if needed, package description text. No runtime, tests, scripts, dependency,
lockfile, export, scientific fixture, or historical manifest changes.

Use exact-path static reads, link-target existence checks, changed-file review,
and `git diff --check`. No imports, test discovery, tests, builds, installs,
downloads, simulation, GPU preflight, benchmark, profiler, protected-payload
inspection, or archive work. Do not run validation/recovery infrastructure just
to prepare documentation. All code examples and descriptions remain in English.

## Acceptance and handoff

- Application authors have a coherent prepare/advance/stimulus/result lifecycle
  guide with explicit compatibility and support boundaries.
- Candidate notes and navigation describe the same bounded engineering scope.
- Packaging review distinguishes configuration from observed artifact behavior.
- A023 G1-G16 PASS remains historical implementation evidence: 1544 passed,
  12 NOT RUN; I0/I2 PASS and I1 NOT RUN. It is not new artifact certification.
- Scientific-v0.4 remains paused; GPU remains experimental; closed-loop remains
  engineered/application-only; package version remains 0.3.0.
- Final inventory contains only authorized documentation changes and preserves
  every incoming WIP path. No version bump, tag, release, or publication.

Given the current checkout, the immediate recommendation is static reconciliation
of the existing A024 preparation, not another implementation milestone. Any future
A025 artifact validation requires separately authorized candidate-specific route
certification before execution. Do not start it automatically. Commit/push and
publication are not part of this proposal.

## Reconciliation result

Reviewed the existing README, runtime guide, runtime release gate, candidate notes,
application guide/architecture/reproducibility entry points, general reproducibility
guide, package configuration, and CPU/GPU facade source as ordinary text.
The CPU lifecycle, owner checks, time/event/output semantics, and experimental GPU
boundary agree with the documented facade; no executable change was needed.

Updated README's opening to the reusable stateful runtime North Star. Added an
application-loop explanation to the runtime guide, including retained state,
explicit stimulus/result flow, application-owned adapters/environment, clock
separation, reset, and failure reconciliation. Updated the candidate gate with
the existing A024 commit and the separate status of this documentation overlay.
Existing candidate notes, migration policy, packaging configuration, and historical
records needed no changes. Synthetic examples remain statically reviewed only.

Final scope: this plan, README.md, docs/runtime/USER_GUIDE.md, and
docs/runtime/RELEASE_GATE.md. Incoming four WIP files remain excluded. All 65
relative-link targets in the reviewed documentation exist; target contents and
heading anchors were not validated. `git diff --check` passed, and the new plan
passed its separate trailing-whitespace check. Final HEAD remains c32919d4;
pyproject.toml and uv.lock have no diff.
No imports, discovery, tests, builds, installs, simulations, or protected content
reads were performed. No artifact, full-integrity, device, or scientific claim
is added. Version stays 0.3.0; no commit/push, tag, release, or publication.
