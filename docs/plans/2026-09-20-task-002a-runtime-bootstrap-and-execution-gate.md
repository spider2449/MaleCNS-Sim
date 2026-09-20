# Task 002A - Runtime Bootstrap and Execution Gate

## Status

TASK 002A - COMPLETE

Formal execution date: 2026-09-20. All required offline execution gates
passed during this execution. No MaleCNS real data was downloaded, Task 002
was not resumed, and no Task 003 work, commit, push, or tag was performed.

## Repository state at inspection

- `git status --short` and `git status` showed no commits and all project files
  untracked: `.gitignore`, `LICENSE`, `README.md`, `docs/`, `pyproject.toml`,
  `src/`, `tests/`, and `uv.lock`.
- `git log` confirmed that branch `master` has no commits.
- The package structure, tests, Task 001 documentation, Task 002 documentation,
  and the existing Task 002A plan were inspected before execution.
- Production graph logic was not changed.

## Runtime and dependency gate

- `uv --version`: `uv 0.12.17 (635500036 2026-09-18 x86_64-pc-windows-msvc)`.
- `uv python list` showed the installed project runtime
  `cpython-3.12.13-windows-x86_64-none`.
- `uv run python --version`: `Python 3.12.13`.
- Exact interpreter: `F:\coding\otherPrj\MaleCNS-Sim\.venv\Scripts\python.exe`.
- `pyproject.toml` declares Python `>=3.12`, runtime dependencies numpy,
  pandas, pyarrow, and scipy, and the pytest test extra.
- Observed dependency versions:
  - numpy `2.5.3`
  - pandas `3.0.6`
  - scipy `1.18.1`
  - pyarrow `25.0.1`
  - pytest `9.1.1`
- The first `uv sync --check` correctly detected that the test extra was not
  selected and reported an outdated environment. The existing uv workflow was
  used with `uv sync --extra test`; no dependency versions or project files
  were changed. Final `uv sync --extra test --check` passed and reported that
  no changes were needed.
- Direct package imports passed for `malecns_sim`, its CLI, Feather adapter,
  and sparse graph module.

## Execution gate results

- `uv run python -m compileall src`: PASS.
- `uv run python -m pytest -v`: PASS; 14 collected, 14 passed, 0 failed.
- The complete suite included the corrected self-edge expectation. No test or
  production source fix was needed during this formal execution.

## CLI smoke tests

The actual entry point is `malecns-sim = malecns_sim.cli:main` in
`pyproject.toml`.

- `uv run malecns-sim --help`: PASS.
- `uv run malecns-sim inspect --help`: PASS.
- `uv run malecns-sim benchmark --help`: PASS.
- `uv run malecns-sim data --help`: PASS.
- A temporary CSV fixture was run through the actual `inspect` and `benchmark`
  commands. Both exited successfully. Inspect reported 4 neurons, 4 full
  edges, 3 filtered edges, 17 filtered synapses, and filtered mean out-degree
  `0.75`. The temporary fixture was removed.
- `data inspect-feather` was run against a temporary Feather fixture and
  exited successfully, reporting the expected `uint64` body column and sample.
  The temporary file was removed.

## PyArrow and integer-ID gate

- PyArrow imported successfully.
- A temporary Feather file was written and read successfully.
- A `uint64` body ID of `9007199254740993` round-tripped exactly as a Python
  `int`; its Arrow type remained `uint64`.
- The `uint64` synapse count also round-tripped as an integer with no float
  conversion. Temporary files were cleaned up.

## Graph determinism sanity check

The existing deterministic synthetic graph was executed directly and through
the full test suite:

- Duplicate `1 -> 2` edges aggregated from `2 + 3` to `5`.
- Self-edge `2 -> 2` was retained and counted.
- Filtered graph neuron ordering was `("1", "2", "3", "10")`.
- Filtered graph summary was `neuron_count=4`, `edge_count=3`,
  `total_synapses=17`, and `mean_out_degree=0.75`.
- The retained self-edge appeared in the CSR matrix at `2 -> 2` with weight
  `7`.
- Repeated graph construction produced the same fingerprint:
  `81c293571e3f9bcc95ffe87a084c67d7b279c7975df4580ce7291eb0e2b93483`.

## Repository hygiene

- Repository-wide trailing-whitespace scan: PASS; no matches.
- `git diff --check`: PASS, with the explicit limitation that it does not
  validate the currently untracked project files.
- `git check-ignore` confirmed ignore rules for `.venv/`, `.pytest_cache/`,
  `__pycache__/`, `data/raw/`, `data/derived/`, Feather, Parquet, `build/`,
  `dist/`, `.pyc`, and `.egg-info` generated paths.
- No raw MaleCNS data directory exists in the worktree. Representative raw,
  derived, and generated paths were checked against the ignore rules.

## Defects and fixes

The only issue found was environment synchronization state: the initial check
omitted the declared test extra. It was corrected with `uv sync --extra test`
and verified with `uv sync --extra test --check`. No source, test, dependency
version, or production graph logic change was required.

## Gate decision

All required Task 002A gates passed during this formal execution:

- usable Python runtime;
- uv-managed project environment;
- package imports;
- compileall;
- complete pytest suite;
- CLI smoke tests;
- PyArrow Feather round-trip;
- large integer-ID preservation; and
- repository hygiene checks.

Task 002 may now resume under its separate real-data authorization. This
document does not authorize or perform that work.
