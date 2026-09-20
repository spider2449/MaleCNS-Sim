# Task 002 — MaleCNS v1.0 Real-Data Validation and Provenance

## Status

PARTIAL/BLOCKED at the 2026-09-20 inspection. The repository environment has
no `python`, `py`, `uv`, or other installed Python runtime, so Feather schema
inspection, dependency installation, tests, graph construction, and real-data
benchmarks could not be executed. No official raw files were downloaded.

Task 001 is also an uncommitted worktree baseline: `git log` reports no commits
and the existing project files are untracked. No unrelated files were changed
and no commit or push was performed.

## Goal and scope

This task adds the narrow machinery needed to validate the official MaleCNS
v1.0 files through the existing normalized records and CSR graph boundary. It
does not implement neural dynamics, signed synapses, learning, embodiment, or
visualization.

## Official source identity

The authoritative source is HHMI Janelia / FlyEM:

- Dataset page: <https://male-cns.janelia.org/download/>
- Bulk-data base: `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`
- HTTPS base: <https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/>

The three in-scope object URLs are:

1. <https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather>
2. <https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather>
3. <https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather>

The large synapse-point, synapse-partner, t-bar-neurotransmitter, volume, and
skeleton artifacts remain outside scope.

## Implemented local boundary

- `pyarrow` is the only new runtime dependency and is loaded by the specific
  Feather adapter when used.
- `malecns_sim.data.male_cns_v1.inspect_feather` reports actual Feather row
  count, column names, Arrow types, and a small sample.
- `MaleCNSV1ColumnMapping` requires the inspected annotation ID, edge source,
  edge target, and edge weight columns. Optional annotation and prediction
  columns are explicit; raw names do not leak into the generic normalizer.
- Annotation IDs and IDs appearing only in connectivity are combined into the
  normalized neuron set, allowing isolated annotated neurons to remain visible.
- Prediction labels remain metadata. No neurotransmitter is converted to an
  excitatory or inhibitory sign.
- Floating-point body IDs are rejected instead of being converted to integers.
  Integer values are converted directly to their decimal string representation,
  preserving values beyond the IEEE-754 exact-integer range.
- `malecns_sim.data.provenance` writes and reads JSON manifests and computes
  local SHA-256 values. The manifest distinguishes locally measured values
  from any published metadata and does not invent official checksums.
- `malecns_sim.graph.fingerprint.graph_fingerprint` hashes ordered neuron IDs,
  CSR array dtypes, and CSR bytes with explicit length framing.
- `malecns-sim data fetch` supports the three explicit HTTPS URLs and resumes a
  partial `.part` file when the server returns HTTP 206. `data verify` checks a
  manifest; `data inspect-feather` performs schema discovery.

## Actual schemas discovered

None. This is intentionally left blank rather than filled with guessed column
names. The adapter mapping must be created only after running
`malecns-sim data inspect-feather` on each downloaded Feather file.

Required future record for each file:

| File | Row count | Columns | Arrow dtypes | Sample/null behavior |
| --- | ---: | --- | --- | --- |
| annotations | not measured | not inspected | not inspected | not inspected |
| neurotransmitters | not measured | not inspected | not inspected | not inspected |
| connectome weights | not measured | not inspected | not inspected | not inspected |

## Provenance and downloaded files

No official files were downloaded in this blocked run. Consequently there are
no local filenames, byte sizes, timestamps, or SHA-256 values to report yet.
The intended raw-file layout is `data/raw/male-cns/v1.0/`, which is ignored by
Git along with Feather files and derived data. The reproducible manifest is
intended for the tracked `data/provenance/male-cns-v1.0.json` path after real
validation.

## Measured statistics and graph results

No real-data statistics were measured. The following required fields remain
pending runtime and data access: annotation row/ID/null/duplicate counts;
neurotransmitter prediction columns, probabilities, missingness, and
duplicates; raw connectivity rows and unique source/target/participating IDs;
self edges; duplicate pairs; weight min/max/total; filtered edge and neuron
counts; isolated annotation neurons; full and `min_synapses=5` graph shapes,
nnz, index/data dtypes, CSR memory, construction time, intermediate peak
memory, graph fingerprints, and propagation summaries.

## Validation commands and results

Inspection commands run:

```text
git status --short                         PASS (untracked baseline reported)
python --version                           BLOCKED (command unavailable)
py --version                               BLOCKED (command unavailable)
py -0p                                     BLOCKED (command unavailable)
where.exe python                           PASS (no match)
where.exe py                               PASS (no match)
uv --version                               BLOCKED (command unavailable)
where.exe uv                               PASS (no match)
curl.exe -L -I https://male-cns.janelia.org/download/  PASS (HTTP 200)
```

Not run because no Python runtime exists:

```text
python -m compileall src
python -m pytest
malecns-sim --help
malecns-sim data inspect-feather ...
malecns-sim data verify ...
real annotation/neurotransmitter/connectivity inspection
real CSR and min_synapses=5 CSR builds
real propagation smoke test
real benchmark
```

`git diff --check` was not reported as failing during preparation; it must be
rerun after the final working-tree inspection. No formatter or linter is
configured in `pyproject.toml`.

## Unresolved scientific and data issues

- The actual v1.0 Arrow schema and nullability were not inspected.
- The adapter does not infer sensory, motor, ascending, or descending classes
  from free text. Those fields remain absent unless a documented source field
  is explicitly mapped in a later evidence-backed update.
- Aggregated connection weights are graph values, not validated functional
  synaptic efficacies.
- A connectome is not an executable biological brain.

## Explicit nonclaims

Task 002 does not validate biological neuron dynamics, functional synaptic
weights, neural firing, behavior, learning, motor control, or any biological
interpretation of deterministic propagation. Until a Python runtime and the
three official files are available, it also does not claim real-data identity,
schema, normalization, graph, propagation, or benchmark validation.

## Next execution steps

Install or expose a project-local Python 3.12+ runtime without changing
production dependencies beyond `pyarrow`; create `.venv`; install
`.[test]`; fetch the three listed files; inspect all schemas; record the
explicit mapping and local manifest; run the offline tests and all required
real-data commands; then append measured results to this plan. Do not commit
raw or generated large graph artifacts.
