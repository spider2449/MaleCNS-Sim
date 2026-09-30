# Task 018A — MN9 Anatomical-Asymmetry Preregistered Execution

Date: 2026-09-30. Verdict: completed locally, subject to the commit and remote verification recorded in the final closeout.

## Starting checkpoint and frozen design

- Starting HEAD, `origin/master`, and live GitHub master: `abb7cc8d385c6a1daa9e9bb87f7488ab5685783b`.
- Starting worktree clean; stash empty. No pull, reset, or stash was used.
- Exact committed Task 018 preregistration SHA-256 before and after: `4f767ab2bfcbf5e5773a803ee6fdb601e39d5521d7f30a12d35a3a5506de5bb4`. HEAD, index, and worktree Git blobs agreed before implementation. The document was not edited.
- MaleCNS v1.0 tracked manifest: `data/provenance/male-cns-v1.0.json`; SHA-256 `e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631`. All three raw Feather files matched its sizes and SHA-256 values before loading.
- Adapter: `malecns-v1-feather-explicit-mapping-v2`. The graph is the full publication-superclass curated directed neuron projection. Primary graph: 166,700 nodes, 25,582,938 edges, 124,177,617 synapses, unsigned fingerprint `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4`. Threshold-5 graph: 166,700 nodes, 6,242,118 edges, 89,860,280 synapses, unsigned fingerprint `661a07e346541da75e81fa0eac487102af496fcfc9f6bdc743c9ca957b4f4a74`.
- MN9 identities: `10331 = MN9_L`, `16949 = MN9_R`, `SIDE_RESOLVED`. Both were in the curated node set and had matching `type`, `instance`, and `somaSide` annotations.

## Implementation and pre-execution gate

- `src/malecns_sim/analysis/task018.py` contains integer partner aggregation, exact partition, decision order, fixed sensitivity, and canonical result digest. Pre-execution SHA-256: `e51c75e0cd6dd9458713a89cc4e9a405368d6ee97e10c2a5356dc399475a4767`.
- `scripts/run_task018.py` verifies raw and design identity, uses the existing graph adapter and projection, checks graph and MN9 identities, repeats deterministic partner calculations, and publishes the ignored JSON and local report after validation. Pre-execution SHA-256: `733db6cad7fadc4127b33f9b01c908a33cdc01dbf34ad290984e0aa0f9ee466b`.
- Synthetic `tests/test_task018.py` pre-execution SHA-256: `ff3b3dc7f6e1d870c3af58688161b7613a5ec639116d50f860756d1e106ea679`.
- Pre-execution command: `uv run pytest tests/test_task018.py -q`; result: **5 passed**. The pre-execution worktree contained only these three untracked implementation and test files. No real MN9 values were used to tune the tests.
- Exact scientific execution command: `uv run python scripts/run_task018.py`. **One** intentional real Task 018 scientific execution completed. No extra real-data execution or unregistered exploratory analysis was performed.

## Confirmed preregistered result

| Frozen measure | Value |
| --- | ---: |
| `W_L` | 6,012 |
| `W_R` | 556 |
| `D = W_L - W_R` | 5,456 |
| `D_shared` | 4,281 |
| `D_left_only` | 1,315 |
| `D_right_only` | -140 |
| `|P_L|`, `|P_R|` | 278, 137 |
| `|C|`, `|U_L|`, `|U_R|` | 65, 213, 72 |

The exact identity holds: `4,281 + 1,315 - 140 = 5,456`. The signed fractions are approximately 0.7846407625, 0.2410190616, and -0.0256598240, respectively. Primary classification: **`SHARED_PARTNER_DIFFERENCE_LARGEST`**. Input hashes, MN9 identity, graph counts, set partition, arithmetic identity, and repeated deterministic partition checks passed.

## Frozen sensitivity

Only `min_synapses=5` was run. The threshold was applied after duplicate-pair aggregation. `SENSITIVITY_MIN_SYNAPSES_5`: `W_L=5,699`, `W_R=386`, `D=5,313`; signed components `D_shared=2,032`, `D_left_only=3,322`, `D_right_only=-41`. Partner counts are `|P_L|=93`, `|P_R|=27`, `|C|=22`, `|U_L|=71`, `|U_R|=5`. Its descriptive largest-component label is `LEFT_ONLY_INPUT_LARGEST`; this **does not change** the primary classification. The sensitivity identity holds: `2,032 + 3,322 - 41 = 5,313`.

## Artifact and reproducibility

- Canonical ignored result path: `data/derived/task018-results.json`; local report path: `data/derived/task018-report.md`. These are the proposed paths in the preregistration, adopted before execution. The JSON SHA-256 is `b112712fc747c41332ebd5772c4ba24839f1c2f771e04533e34fdc24ca490e89`; its canonical scientific-content digest is `270c931a2420df475ff54ea185e7e7d03da1a868af8a35f7f68e38ebbf98f9f4`.
- The JSON uses schema `malecns-sim-task018-anatomical-asymmetry-v1` and records the source commit, exact data fingerprints, graph fingerprints, checked MN9 annotations, primary and sensitivity calculations, integrity status, UTC execution timestamp, and Python/NumPy/PyArrow versions. An independent read-only JSON check verified schema, provenance, both arithmetic identities, and recomputed the canonical digest. Classification was also checked against the frozen rule.
- To reproduce from the pinned checkout and manifest-matching raw files: `uv run pytest tests/test_task018.py -q`, then `uv run python scripts/run_task018.py` in a checkout where the two final ignored Task 018 output paths do not already exist. The runner refuses to overwrite existing final outputs. Compare the scientific fields and graph fingerprints; the whole-payload digest includes the execution timestamp and will differ on a later run.
- Full validation after execution: `uv run pytest` yielded **255 passed, 1 established opt-in skip**; `uv run python -m compileall src scripts tests` passed; `git diff --check` passed. The one warning from CuPy was about an unavailable CUDA path; Task 018 uses CPU integer operations.

## Sealed Task 017 and nonclaims

The read-only `uv run python scripts/audit_task017_checkpoint.py` audit passed before and after Task 018A. Both audits found 3,168 completed, zero pending, each of R0 and V1–V7 at 396/396, checkpoint fingerprint `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`, journal SHA-256 `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e`, and sidecar inventory SHA-256 `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553`. The sealed complete-matrix digest remained `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028`. Tracked `artifacts/task017/robustness-scoring.json` remained byte-identical at SHA-256 `06aa2febc33ae294bbd8ef3d302f5caea52ab3a8d96945944b5abfb175240142`; Task 016 fingerprint remained `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`. Task 017 status remains `NOT_ROBUST`; Task 017Q remains `DEFERRED`.

This is an anatomical synapse-count decomposition for one frozen connectome representation. It does not establish a biological causal mechanism, functional, behavioral, or physiological asymmetry, a developmental mechanism, direct inhibition, network redistribution, or generality beyond this representation. No model dynamics, Task 017 execution, Task 017Q, null population, significance test, or exploratory follow-up was run. The local outputs are ignored by Git as specified by the preregistration; a separate checkout requires the manifest-pinned raw data and a reproduction run to create them.
