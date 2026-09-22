# MaleCNS-Sim Research Release Gate

Status: Task 013 release preparation

This gate records the reproducibility and claim boundaries for the validated
MaleCNS-Sim research checkpoint. It is a release-preparation record, not a new
scientific result.

## 1. Release purpose

Prepare a reproducible software and documentation checkpoint for the validated
research state through Task 011. The release preserves the existing model,
candidate definitions, data interpretation, scientific results, and accepted
nonclaims.

## 2. Exact source checkpoint

- Task 013 starting HEAD: `4fa0d2d9f977ca0f307b0490345b466b8c9fee91`
- Branch: `master`, tracking `origin/master`
- Task 011 scientific endpoint commit: `ae589a9b9726fa2510fff8f32658bc02176f66a3`
- Task 012 checkpoint-synthesis commit: `4fa0d2d9f977ca0f307b0490345b466b8c9fee91`
- Accepted Task 011 result digest:
  `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`
- No Git tag or published release is created by Task 013.

## 3. Scientific scope

The checkpoint covers the curated MaleCNS v1.0 neuron-level graph, explicit
neurotransmitter sign policies, the deterministic reference LIF model, the
Shiu v630 reference reproduction, side-resolved sugar/MN9 correspondence,
Task 008 dynamics, Task 009 structural analysis, Task 010 frozen-candidate
perturbations, and the Task 011 temporal mechanism audit.

Task 011 is the current scientific endpoint. Task 012 and Task 013 are
documentation, reproducibility, and release-preparation work only.

## 4. Scientific nonclaims

- A connectome is not an executable biological brain.
- Simulation causality is not biological causality.
- MaleCNS MN9 correspondence is homolog/side-resolved correspondence, not
  segmentation identity, lineage identity, or identical bilateral physiology.
- The full curated graph is primary.
- The `>=5` graph is sensitivity analysis only.
- Structural prominence does not imply causal influence.
- `NETWORK_REDISTRIBUTION_COMPATIBLE` is a model-level compatibility
  classification.
- Task 011 does not establish direct biological inhibition or disinhibition.
- The checkpoint does not establish biological necessity, behavioral
  necessity, receptor-specific physiology, exact Brian2 scheduling/RNG
  equivalence, or an actual-fly mechanism.

## 5. Dataset / graph state

- Dataset: MaleCNS v1.0, using the committed provenance manifest and the three
  official Feather files kept outside Git.
- Curated identity dimension: 166,700 neurons.
- Full curated anatomical graph: 25,582,938 directed edges and total
  anatomical weight 124,177,617 synapses.
- Full graph: primary scientific substrate.
- `min_synapses=5`: 6,242,118 anatomical edges and weight 89,860,280;
  sensitivity analysis only.
- Full Task 004 Shiu projection: 24,904,953 resolved effective edges,
  121,444,188 signed anatomical weight, and 677,985 unresolved edges.

The Shiu v630 reference inputs and `sugarR_100Hz.parquet` are separately
provenanced and are not MaleCNS v1.0 data.

## 6. LIF model baseline

The validated reference parameters are fixed at:

| Parameter | Value |
| --- | ---: |
| `v_rest` / `v_reset` | -52.0 mV |
| `v_threshold` | -45.0 mV, strict `v > threshold` |
| `tau_membrane` | 20.0 ms |
| `tau_synapse` | 5.0 ms |
| refractory period | 2.2 ms |
| synaptic delay | 1.8 ms |
| synaptic weight | 0.275 mV per anatomical synapse |
| timestep | 0.1 ms |

The engine uses the analytical linear update and delayed sparse events. CPU
NumPy is the correctness oracle. Silencing suppresses outgoing event
scheduling only; it does not remove incoming edges or prevent internal state
updates and spikes.

## 7. Sign policy

The exact Task 004 `Shiu2024SignPolicy` remains in force:

| Resolved identity | Effective sign |
| --- | ---: |
| acetylcholine | +1 |
| GABA | -1 |
| glutamate | -1 |
| dopamine, octopamine, serotonin | +1 |
| histamine | unresolved |
| unclear, missing, unsupported | unresolved |

Resolution precedence is `consensus_nt -> predicted_nt ->
celltype_predicted_nt -> unresolved`. Unresolved signs remain excluded from
the resolved signed projection and are not silently assigned a sign.

## 8. MN9 identity state

- `MN9_L` is MaleCNS body `10331`.
- `MN9_R` is MaleCNS body `16949`.
- `16949` is the Shiu-aligned cross-brain homolog/readout selected by the
  side-resolved evidence.
- `SIDE_RESOLVED` means annotation-supported anatomical side/type
  correspondence. It is not segmentation identity.
- Sugar populations were frozen before connectivity or firing interpretation:
  42 left bodies and 43 right bodies, selected by `rootSide` because
  `somaSide` is missing for these candidates.

## 9. GPU validation status

Status: validated as an optional implementation path.

The CUDA backend uses float64 for scientific mode. CPU/CUDA synthetic and
bounded real-graph checks passed exact canonical spike-event equality. The
representative Task 011 trace also matched, with digest
`f4bfec70b46d63e5933099b3b8b81cf67d00166f7edba6d80e18c361c94dd5ff`.
GPU equivalence is implementation validation, not an independent scientific
model. Float32 is not the scientific mode.

## 10. Task 006 reproduction status

Status: reproduced and validated as a separate Shiu v630 reference-data
check, not as a MaleCNS identity or biological validation.

The read-only oracle is `results/example/sugarR_100Hz.parquet`. Across 30
one-second trials, the official MN9 mean was 67.0333 Hz and the
MaleCNS-Sim reference reproduction was 67.0667 Hz. The exact Shiu inputs and
file digests are in `data/provenance/shiu-2024-v630.json`.

There is no standalone `run_task006.py` script in this repository. A fresh
reproduction must load the pinned v630 inputs with
`prepare_shiu_v630_projection`, run the declared seeded schedules through the
reference LIF engine, and compare with
`summarize_reference_parquet`, `summarize_simulation_results`, and
`compare_summaries`, following the Task 006 plan. The release makes no
one-command Task 006 claim.

## 11. Task 008 dynamics status

Status: simulated and validated on the full curated graph with CUDA float64.

The primary condition used 42 left sugar bodies, 30 one-second trials at each
of 10, 25, 50, 100, 150, and 200 Hz, with the mirror, normalized-input, and
`>=5` sensitivity conditions recorded separately. The 100 Hz full-graph
readouts were 5.9 Hz contralateral `MN9_R` and 66.5333 Hz ipsilateral `MN9_L`.
The right-sugar mirror condition was 95.1 Hz in `MN9_L` and 2.4333 Hz in
`MN9_R`. These are model results, not a male/female comparison.

## 12. Task 009 structural status

Status: analyzed and validated as structural-only.

All four direct sugar-to-MN9 routes were empty. The full graph remains primary;
the `>=5` graph is sensitivity-only. The frozen candidates, in order, are
`10135, 10313, 12752, 43765, 512730, 514753, 517861`. The strongest signed
structural proxy was body `512730` at 1,904. This is a structural diagnostic,
not current activity, a firing predictor, or causal influence.

## 13. Task 010 perturbation status

Status: simulated and validated under the frozen Task 009 candidate set.

The 30-trial baseline replay matched the preserved Task 008 trials, seeds,
spike counts, and canonical digests. Task 010 is a model-sensitivity
perturbation analysis. Its result digest is
`20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45`.
The effects do not establish biological necessity or a biological causal
mechanism.

## 14. Task 011 mechanism-audit status

Status: simulated, audited, and accepted as the current scientific endpoint.

Only frozen cases `10313`, `10135`, `12752`, `512730`, and `43765` were used,
with trial indices 0, 10, and 20 on both 100 Hz stimulus sides. The accepted
labels are model-level compatibility classifications. The accepted result
digest is:

`fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`

Task 011 does not establish direct biological inhibition or disinhibition.

## 15. Task 012 checkpoint-document status

Status: documented and accepted.

`docs/MALECNS_RESEARCH_CHECKPOINT.md` is the authoritative scientific
checkpoint through Task 011. Task 012 did not regenerate, normalize, or
rewrite scientific-result artifacts. Task 013 adds this release gate and
reproducibility-facing instructions only.

## 16. Deterministic fingerprints / digests

| Artifact or identity | Fingerprint / digest |
| --- | --- |
| Task 008-011 full cache | `8064dbec4ecf5ac72a4ab23835e4fcbdc6cdcc5315a1b71f71c135de9eb8cf4d` |
| Task 008 prepared graph | `d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495` |
| Task 009 candidate list | `113b9a767eeb61a56419e7b76e57b785fe26d9bb77e4ad6c9f6e2020be2f6ea9` |
| Task 010 result | `20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45` |
| Task 011 representative CPU/CUDA trace | `f4bfec70b46d63e5933099b3b8b81cf67d00166f7edba6d80e18c361c94dd5ff` |
| Task 011 accepted result | `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4` |

The committed provenance manifests provide source-file SHA-256 values for the
MaleCNS v1.0 and Shiu v630 inputs.

## 17. Environment

The Task 013 host record is:

| Component | Recorded value |
| --- | --- |
| system Python | 3.11.15; below the project requirement and not used for project validation |
| `uv run` Python | 3.14.0 |
| uv | 0.11.8 |
| Windows | Windows 10 Pro, version 10.0.19045, build 19045 |
| NVIDIA driver | 581.15 |
| GPU | NVIDIA GeForce RTX 3060, 12,288 MiB VRAM |
| `nvidia-smi` CUDA compatibility | 13.0 |
| CUDA Toolkit / nvcc | 12.4.99 |
| CuPy in `uv run` environment | 14.2.0 |
| CuPy CUDA runtime | 12.9 (`12090`) |

The plain system Python environment has no CuPy installation; this does not
alter the declared optional GPU dependency or the validated `uv` environment.

## 18. Reproducibility commands

All commands below are run from the repository root in PowerShell.

### Installation

CPU-only test environment:

```powershell
uv sync --extra test
```

Optional CUDA/CuPy environment used by the validated GPU runs:

```powershell
uv sync --extra test --extra gpu
uv run python -c "import cupy; print(cupy.__version__, cupy.cuda.runtime.runtimeGetVersion())"
```

The GPU extra is pinned to `cupy-cuda12x==14.2.0`. Python `>=3.12` is required.
The CPU installation and unit tests do not require CuPy or an NVIDIA device.

### Source-data verification

Place the exact raw files named by the committed manifest under
`data/raw/male-cns/v1.0`, then verify their recorded sizes and SHA-256 values:

```powershell
uv run malecns-sim data verify `
  --manifest data/provenance/male-cns-v1.0.json `
  --root data/raw/male-cns/v1.0
```

The Shiu v630 files belong under the ignored reference-data path described by
`data/provenance/shiu-2024-v630.json`.

### Tests and syntax validation

```powershell
uv run pytest
uv run python -m compileall src scripts tests
git diff --check
```

The accepted baseline is `183 passed, 1 skipped`.

### Graph cache preparation and loading

The validated Task 008 script loads the three raw MaleCNS Feather files,
builds the full curated graph and the separate `>=5` sensitivity graph, and
writes the ignored caches and Task 008 result artifact:

```powershell
uv run python scripts/run_task008.py
```

This script intentionally requests CUDA and therefore requires the optional GPU
environment and an available CUDA device. It writes:

- `data/derived/task008/full-prepared-graph.npz`
- `data/derived/task008/min-synapses-5-prepared-graph.npz`
- `data/derived/task008-results.json`

Task 010 and Task 011 load and identity-check the full cache through
`PreparedGraphCache.load` before running. A cache is valid only when its
embedded identity and fingerprint match the declared Task 008-011 fingerprint;
do not substitute a threshold cache for the full cache.

### Validated reference and analysis runs

Task 006 has no standalone script; use the APIs and limitations recorded in
Section 10 and the Task 006 plan.

After the verified raw data and Task 008 caches are available, run the
validated analysis sequence:

```powershell
uv run python scripts/run_task009.py
uv run python scripts/run_task010.py
uv run python scripts/run_task011.py
```

The scripts write ignored artifacts `data/derived/task009-results.json`,
`task010-results.json`, and `task011-results.json`. Each later task validates
the preceding artifact, frozen identities, fingerprints, and result digests;
an unexpected mismatch is a stop condition, not a reason to regenerate or
reinterpret results.

## 19. Validation matrix

| Check | Status / evidence |
| --- | --- |
| exact starting HEAD | validated: `4fa0d2d9f977ca0f307b0490345b466b8c9fee91` |
| local branch / upstream | validated: `master` / `origin/master` |
| live remote HEAD | validated equal to starting HEAD before Task 013 |
| clean worktree before changes | validated |
| empty stash before changes | validated |
| CPU-only install path | documented and declared |
| optional GPU dependency | declared and checkpoint-validated |
| `uv run pytest` | PASS: `183 passed, 1 skipped` in 6.13 s |
| `compileall src scripts tests` | PASS |
| `git diff --check` | PASS |
| Task 011 digest | validated against accepted digest above |
| scientific source/result state | unchanged by Task 013 scope |
| tag / release publication | intentionally not performed |

## 20. Known limitations

- Raw MaleCNS and Shiu reference files are large and intentionally not
  committed.
- Derived caches and result JSON files are intentionally not committed and
  must be regenerated or obtained from a separately preserved artifact store.
- Task 008-011 full-graph runs are expensive and the validated scripts require
  CUDA float64.
- CPU/CUDA equivalence is an implementation check; CPU remains the correctness
  oracle.
- The reference LIF model is not a complete biological neuron model and has no
  body, sensory, behavioral, receptor-specific, or learning system.
- The finite deterministic trials, annotation uncertainty, unresolved signs,
  and model-policy assumptions limit interpretation.
- No live Brian2 trace-equivalence or Brian2 RNG-stream reproduction is claimed.

## 21. Release checklist

- [x] Scientific endpoint remains Task 011.
- [x] Full curated graph remains primary; `>=5` remains sensitivity-only.
- [x] Candidate set, MN9 correspondence, LIF parameters, and sign policy are
  unchanged.
- [x] Task 011 digest is recorded and verified.
- [x] CPU-only and optional GPU installation paths are documented.
- [x] Validated scripts and ignored derived-artifact policy are documented.
- [x] Task 013 final pytest, compileall, and diff-check results recorded.
- [x] Complete Task 013 diff reviewed and limited to release-preparation files.
- [ ] Task 013 commit pushed and local/remote HEAD equality reverified.
- [x] No tag created.
- [x] No release published.
- [x] Task 014 not started automatically.
