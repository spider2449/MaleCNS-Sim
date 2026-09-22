# MaleCNS-Sim

MaleCNS-Sim is a research software foundation for turning the Drosophila
MaleCNS connectome into a deterministic executable graph for later
sensorimotor research.

It is not a complete brain simulation, a biological claim that a connectome is
an executable brain, or an embodied fly environment. It has deterministic CPU
reference and optional CUDA float64 Leaky Integrate-and-Fire engines, but no
sensory/body coupling, FlyGym, NeuroMechFly, MuJoCo, or learning system.

## Current stage

Task 011 is the current scientific endpoint. Task 012 records the authoritative
research checkpoint, and Task 013 prepares that checkpoint for reproducible
release. The validated state covers the curated MaleCNS v1.0 graph, explicit
sign policies, reference LIF dynamics, the Shiu v630 reference reproduction,
Task 008 dynamics, Task 009 structural analysis, Task 010 frozen-candidate
perturbations, and the Task 011 temporal mechanism audit.

The intended pipeline is:

```text
MaleCNS data
→ normalization
→ sparse directed graph
→ signed anatomical projection
→ reference LIF dynamics
→ validated reference dynamics
```

Task 005 adds the CPU reference dynamics layer. It uses the published Shiu
equations with an exact linear state update, explicit `dt=0.1 ms`, integer
1.8 ms delayed sparse events, explicit refractory handling, deterministic
spike schedules, and seeded reference-style Poisson input. It consumes only
resolved Task 004 signed edges and reports excluded unresolved edge counts and
weights. This is a numerical reference and bounded engineering substrate, not
a reproduction of the Shiu FlyWire network or a biological validation.

Task 002 validated MaleCNS v1.0 locally from the three official Feather
files. The measured full segment graph contains 88,404,403 node IDs and
151,856,684 edges; the `min_synapses=5` graph contains 7,622,864 edges.
Both CSR builds are deterministic, and source neurotransmitter predictions
are preserved as metadata without assigning biological sign. See the
[Task 002 validation record](docs/plans/task-002-malecns-v1-real-data-validation-and-provenance.md)
and the local provenance manifest at `data/provenance/male-cns-v1.0.json`.

Task 003 projected the raw segment graph onto the publication-defined curated
neuron identity set: 166,700 curated IDs, 25,582,938 full neuron-level edges,
and 6,242,118 edges at `min_synapses=5`. The full graph has 217 isolated
curated IDs; the thresholded graph has 864. The curated graph, not the raw
88-million-segment graph, is the intended future simulation substrate. See the
[Task 003 validation record](docs/plans/2026-09-20-task-003-curated-neuron-level-connectome-projection.md).

Task 004 adds explicit MaleCNS neurotransmitter resolution and named sign
policies without changing the unsigned anatomical graph. The curated set has
163,523 resolved neurotransmitter identities and 3,177 unresolved identities
under the consensus-first policy. The Shiu-compatible policy signs 97.7988% of
full curated anatomical weight and 97.9549% of `min_synapses=5` weight; the
conservative policy signs 79.8927% and 81.2499%, respectively. Signed counts
are derived data, not functional synaptic weights. See the
[Task 004 validation record](docs/plans/2026-09-20-task-004-neurotransmitter-sign-policy-and-signed-connectome.md).

Task 006 reproduces the Shiu et al. FlyWire v630 sugar-to-MN9 experiment as a
separate reference-data validation. Against the official stored
`sugarR_100Hz.parquet`, the local 30-trial run measured MN9 mean firing rates
of 67.0667 Hz versus 67.0333 Hz, with all trials active; the original signed
`Excitatory x Connectivity` column times 0.275 mV was used directly. The
frequency curve was measured at 10, 25, 50, 100, 150, and 200 Hz, and rose
from 0 Hz at 10/25 Hz to 93.1333 Hz at 200 Hz. This validates engine behavior
on the historical v630 graph only; it does not map FlyWire IDs to MaleCNS v1.0
IDs. See the [Task 006 validation record](docs/plans/2026-09-20-task-006-shiu-v630-sugar-mn9-reproduction.md)
and [its provenance manifest](data/provenance/shiu-2024-v630.json).

Task 007 establishes a provenance-pinned homolog mapping boundary without
running a MaleCNS experiment. Twenty historical sugar roots have later
FlyWire `LB3`/`sugar/water` type evidence and one remains unresolved; their
MaleCNS `flywireType=LB3` mapping contains 87 type-level candidates. The
evidence-backed right-side MaleCNS input population contains 43 gustatory
`MxLbN` bodies, with 42 Task 004-resolved NT records and one unresolved NT
record. FlyWire MN9 type `CB0701` maps to MaleCNS `type=MN9` bodies `10331`
and `16949` at `TYPE_LEVEL`; neither is silently selected. Structural checks
found no direct sugar-to-MN9 edge and shortest curated paths of two hops to
both candidates. This is an identity result, not a firing or behavioral
claim. See the [Task 007 mapping record](docs/plans/2026-09-20-task-007-malecns-sugar-mn9-homolog-mapping.md)
and [its compact evidence summaries](data/provenance/task007-mapping-summary.json).

The complete release gate, including scientific nonclaims, fingerprints,
environment, and reproduction commands, is in the
[MaleCNS release gate](docs/MALECNS_RELEASE_GATE.md). The authoritative
scientific state is in the
[research checkpoint](docs/MALECNS_RESEARCH_CHECKPOINT.md).

## Installation

Python 3.12 or newer is required.

```powershell
uv sync --extra test
```

The optional CUDA environment used by the validated GPU analyses is:

```powershell
uv sync --extra test --extra gpu
uv run python -c "import cupy; print(cupy.__version__, cupy.cuda.runtime.runtimeGetVersion())"
```

The GPU extra is pinned to `cupy-cuda12x==14.2.0`. Python 3.12 or newer is
required. A pip-based CPU installation is also supported:

```powershell
python -m pip install -e ".[test]"
```

## Tests

```powershell
uv run pytest
uv run python -m compileall src scripts tests
git diff --check
```

The accepted checkpoint baseline is `183 passed, 1 skipped`. Unit tests use
small in-memory fixtures and do not download real MaleCNS data.

## Reproducing the validated analyses

Place the exact raw files named by
[`data/provenance/male-cns-v1.0.json`](data/provenance/male-cns-v1.0.json)
under `data/raw/male-cns/v1.0`, then verify them:

```powershell
uv run malecns-sim data verify `
  --manifest data/provenance/male-cns-v1.0.json `
  --root data/raw/male-cns/v1.0
```

The validated Task 008 run prepares and caches the full curated graph and the
separate `min_synapses=5` sensitivity graph:

```powershell
uv run python scripts/run_task008.py
```

This script requests CUDA and writes ignored cache/result files under
`data/derived/`. Task 009, 010, and 011 are then run in order:

```powershell
uv run python scripts/run_task009.py
uv run python scripts/run_task010.py
uv run python scripts/run_task011.py
```

Task 010 and Task 011 load and validate the full Task 008 cache. Task 006 has
no standalone runner in this repository; its pinned Shiu v630 inputs, API
entry points, and nonclaims are documented in the
[release gate](docs/MALECNS_RELEASE_GATE.md) and the
[Task 006 plan](docs/plans/2026-09-20-task-006-shiu-v630-sugar-mn9-reproduction.md).
The repository does not claim a one-command reproduction for Task 006.

## Local data inspection and benchmarking

Task 001 uses an explicit CSV/TSV adapter boundary because the exact public
MaleCNS v1.0 schema has not been verified in this repository. The default
column names are canonical internal names, not invented claims about the
external dataset. Map a verified source schema with CLI options such as
`--neuron-id-column` and `--synapse-column`.

```powershell
malecns-sim inspect --neurons neurons.csv --edges edges.csv --min-synapses 5
malecns-sim benchmark --neurons neurons.csv --edges edges.csv --min-synapses 5
```

The benchmark reports measured graph construction and propagation times.
Sparse storage values are measured sizes of CSR arrays and are estimates of
the complete in-memory object because Python and allocator overhead are not
included. No real-data benchmark is claimed until a documented MaleCNS data
release is successfully loaded and inspected.

## Scientific limitations

Neuron and edge metadata are preserved where supplied, including
neurotransmitter predictions and classifications. Model signs are explicit
policy assumptions and edge weights remain anatomical synapse counts; signed
counts are not functional synaptic weights. The LIF model is a deterministic
reference model, not a complete biological neuron model, and the simulation
does not provide biological causality, behavioral validation, receptor-level
physiology, or an embodied fly environment.

Raw source data and normalized records are separate concepts. Raw or derived
connectome files should remain outside Git.

See [the Task 001 plan](docs/plans/task-001-malecns-data-ingestion-and-executable-graph.md)
and [the adapter boundary](docs/data-adapter.md) for assumptions and known
unknowns.
