# Task 032 — Reproducibility and recovery documentation reconciliation

## Start gate and scope

Starting local HEAD, `origin/master`, and live GitHub master: `c50cc6987d84570529b3bf2760ac98f3b2a0a868`. Worktree and stash: empty. Package: `0.3.0`. `v0.3.0` peeled target: `a1a6651163840a982799b1fa82c1904e67f84660`. Active tracked GitHub Actions workflows: zero. Task 026: `NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY`; Task 029: `P1 / NO_GITHUB_CI_LOCAL_REPRODUCIBILITY_PRESERVED`; Task 030: `A1 / ARCHIVAL_IMPLEMENTATION_READY`; Task 031: `CUSTODY1 / INDEPENDENT_ARCHIVE_VERIFIED`; Task 017Q: `Q1 / KEEP_DEFERRED`.

This task changed current documentation only. Historical task records, implementation, dependencies, tests, scientific artifacts, tag, and release were not changed.

## Inventory and drift

Audited current `README.md`, `docs/MALECNS_RESEARCH_CHECKPOINT.md`, `docs/MALECNS_RELEASE_GATE.md`, `docs/data-adapter.md`, `pyproject.toml`, `uv.lock`, `scripts/check_gpu.py`, `scripts/check_tracked_integrity.py`, `.gitignore`, provenance and Task 017 recovery manifests, and the relevant Task 017P and Task 026–031 records. The dated release gate and plans are historical evidence, not evergreen setup instructions.

| ID | Class | Finding and correction |
| --- | --- | --- |
| 1 | D2 stale command | README installed the older `test` extra and used a CuPy version probe instead of the current GPU preflight. Current CPU and optional GPU commands now follow tracked project configuration. |
| 2 | D4 ambiguous | README mixed setup, testing, build, and integrity checks. These now have distinct purposes in the canonical guide. |
| 3 | D3 stale state | Research checkpoint said all `data/derived/` scientific artifacts were ignored; compact Task 008 evidence is tracked. Corrected the path-specific statement. |
| 4 | D6 missing | Current guidance lacked the Task 031 independent custody state and a safe conceptual recovery sequence. Added them without machine-specific archive paths. |
| 5 | D6 missing | Current guidance did not clearly distinguish tracked integrity checks from external raw bytes and exact Task 017 checkpoint bytes. Added the boundary. |
| 6 | D5 duplicated inconsistently | README and dated release gate offered different setup routes without identifying the dated gate as historical. README now links to the current guide; the historical record remains intact. |

No permanent exact pytest count was found in the current README instructions. Exact counts in dated records were retained. No active GitHub CI claim was found in the current README. Task 028 remains historical CI evidence; Task 029 is the later no-GitHub-CI policy. No instruction to overwrite a checkpoint was found, but the prior recovery path did not present the full identify/verify/stage/authorized import/verify order in current guidance.

## Canonical local workflow and boundaries

| Purpose | Command |
| --- | --- |
| CPU setup | `uv sync --frozen --group dev` |
| Normal testing | `uv run pytest` |
| Compilation | `uv run python -m compileall src scripts tests` |
| Package build | `uv build` |
| Tracked integrity | `uv run python scripts/check_tracked_integrity.py` |
| Optional GPU setup | `uv sync --extra gpu --group dev` |
| GPU preflight | `uv run --extra gpu --group dev python scripts/check_gpu.py` |

The optional extra pins `cupy-cuda12x[ctk]==14.2.0`; CPU setup does not require it. `GPU_READY` checks host environment availability, not scientific correctness or another host. Hardware/driver compatibility is external to Git. Raw MaleCNS bytes are external; tracked provenance pins names, sizes, and hashes. Prepared caches and most derived state are ignored; selected compact evidence is tracked. The local integrity checker validates tracked evidence, not raw-data availability or the external Task 017 ZIP.

The exact Task 017 journal and sidecars are external to Git. Task 017P's formal recovery pair has pinned hashes; Task 031 verified a separately stored second copy. Custody readback is not import, restore, runnable-state proof, or Task 017Q. Recovery order: identify, verify exact identities, stage separately, import only with authorization into suitable empty state, verify again. Task 017 remains `NOT_ROBUST`; Task 018 remains unchanged; Task 026 has no ready v0.4 scientific question.

Local checks do not certify biological correctness, scientific generalization, GPU parity, cross-machine restore, raw-data availability, external validation, BANC replication, or GitHub CI.

## Validation and scientific firewall

Validation: `uv sync --frozen --group dev` PASS. CPU-only `uv run pytest`: **243 passed, 14 skipped** (CUDA unavailable and one established opt-in full-graph skip). Optional `uv sync --extra gpu --group dev` PASS; `scripts/check_gpu.py`: **GPU_READY** on the local RTX 3060. With the optional GPU environment, `uv run pytest`: **256 passed, 1 established opt-in skip**, one CuPy CUDA-path warning. `uv run python -m compileall src scripts tests`: PASS. `uv build`: PASS for `0.3.0` sdist and wheel. `uv run python scripts/check_tracked_integrity.py`: **Integrity PASS, 9 tracked files and internal identities**. `git diff --check`: PASS.

Scientific simulations **0**; scientific endpoint calculations **0**; checkpoint exports **0**; checkpoint imports **0**; checkpoint restores **0**; Task 017Q executions **0**; archive writes **0**; external uploads **0**; MaleCNS raw-data downloads **0**; BANC work **0**; motif calculations **0**. Task 031 archive was not modified.
