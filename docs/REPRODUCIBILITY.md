# Local reproducibility and Task 017 recovery

This is the current engineering entry point. The [research checkpoint](MALECNS_RESEARCH_CHECKPOINT.md) records scientific state; dated [task records](plans/) preserve the evidence at the time of each task. Validation is local under the current no-GitHub-CI policy. Task 028's successful generic CPU CI run is historical evidence; Task 029 removed that workflow.

## Local CPU setup and verification

The [resumable runtime guide](runtime/USER_GUIDE.md) documents current consumer
usage. Its intended application/runtime release has a separate
[artifact gate](runtime/RELEASE_GATE.md). Generic commands below are ordinary
development checks and may read tracked scientific evidence; they do not certify
zero protected-payload access or satisfy protected I1 through split I0/I2 checks.
No real-source benchmark is part of routine runtime release validation.

Use Python 3.12 or newer and `uv` from the repository root. The tracked `pyproject.toml` and `uv.lock` define the environment. CPU development does not require GPU dependencies.

| Purpose | Command |
| --- | --- |
| Setup | `uv sync --frozen --group dev` |
| Normal testing | `uv run pytest` |
| Compile Python sources | `uv run python -m compileall src scripts tests` |
| Package build | `uv build` |
| Tracked integrity | `uv run python scripts/check_tracked_integrity.py` |

The test suite uses environment checks for raw-data and CUDA cases; the full-graph test is opt-in with `MALECNS_TASK007C_REAL=1`. The integrity script checks pinned tracked files and internal identities offline. It does not retrieve or validate external raw bytes or the external Task 017 ZIP. A build verifies packaging, not scientific results. Exact test counts belong in dated validation records.

## Optional GPU environment

The tracked GPU extra declares `cupy-cuda12x[ctk]==14.2.0`. On a host with compatible NVIDIA hardware, driver, and toolkit/runtime support:

```powershell
uv sync --extra gpu --group dev
uv run --extra gpu --group dev python scripts/check_gpu.py
```

Require `GPU_READY` before GPU work. This preflight checks device access, float64 arithmetic, NVRTC compilation, and backend availability. It certifies environment availability on that host, not scientific correctness, CPU/GPU parity, another machine, or Task 017Q. Host compatibility and raw data remain external to Git.

## Data and tracked evidence

| Class | Location and treatment |
| --- | --- |
| Tracked provenance | `data/provenance/` records pinned source names, locations, sizes, and SHA-256; compact evidence under `artifacts/` and selected tracked `data/derived/` files has separate integrity checks. |
| External raw bytes | MaleCNS v1.0 Feather inputs and Shiu reference inputs are not bundled with Git. Obtain them separately and verify exact pinned identities before any data-dependent work. |
| Ignored prepared and derived state | `data/raw/` and most `data/derived/` outputs, including prepared graph caches, are ignored. They are not silently recreated by local verification. |

For MaleCNS inputs, consult `data/provenance/male-cns-v1.0.json`, place the exact files at `data/raw/male-cns/v1.0`, then use `uv run malecns-sim data verify --manifest data/provenance/male-cns-v1.0.json --root data/raw/male-cns/v1.0`. The manifest and local check do not guarantee external availability. Do not treat the compact tracked Task 008 result as the full prepared cache.

## Task 017 checkpoint custody and recovery

The exact journal and 3,168 result sidecars are ignored execution state, not ordinary Git contents. Task 017P established audited export/import machinery; `artifacts/task017/recovery-manifest.json` pins the sealed recovery pair's identities. The current completed recovery point has a ZIP SHA-256 of `3bea57aec891c8ca90b89229d786e0260d9fcfb0f92d8de8b2b5239f6f1d5170` and external manifest SHA-256 of `a09661ac697614c05c6bafed88f590a5d00375f2eeeda0a84749ce73eb78edf8`. The [Task 031 custody receipt](plans/2026-10-01-task-031-task017-independent-archive-custody-receipt.md) records a separately stored, fully read-back-verified second copy on distinct physical storage. Custody is logically immutable by policy; neither copy should be overwritten in place.

Recovery has an explicit sequence:

1. **Identify** the intended recovery point against the tracked manifest and the custody receipt. Determine whether the destination already has any journal, sidecars, or partial state.
2. **Verify** the retrieved pair by exact SHA-256 and manifest/inventory checks. Do not infer identity from names or timestamps.
3. **Stage** the verified pair separately from the destination. Keep existing state intact; a partial or unknown destination requires investigation before any import.
4. **Import or restore only when authorized** into a suitable empty destination using `scripts/import_task017_checkpoint.py` and its documented safety checks. Do not merge or overwrite an existing checkpoint. Never casually regenerate the historical Task 017 state.
5. **Verify again** with `scripts/audit_task017_checkpoint.py` and compare the expected identities, completed units, and pending set before any separately authorized execution.

See the [Task 017P record](plans/2026-09-29-task-017p-portable-scientific-execution-state.md) for the formal tools and historical import tests. Custody readback did not import or restore a checkpoint, establish runnable state on another machine, or execute Task 017Q. Task 017Q remains **Q1 / KEEP_DEFERRED**. Task 017 remains **NOT_ROBUST**; Task 018 is unchanged; Task 026 found **NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY**.

Local verification does not certify biological correctness, scientific generalization, GPU parity, raw-data availability, external validation, BANC replication, or cross-machine restore.
