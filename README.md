# MaleCNS-Sim

MaleCNS-Sim is a research software foundation for turning the Drosophila
MaleCNS connectome into a deterministic executable graph for later
sensorimotor research.

It is not a complete brain simulation, a biological claim that a connectome is
an executable brain, or an embodied fly environment. It has a deterministic
CPU reference Leaky Integrate-and-Fire engine, but no sensory/body coupling,
FlyGym, NeuroMechFly, MuJoCo, GPU backend, or learning system.

## Current stage

Task 001 establishes data ingestion, normalization, sparse CSR graph
construction, deterministic scalar propagation, and small measurements. The
propagation operation is a graph test primitive, not a neural model.

The intended pipeline is:

```text
MaleCNS data
→ normalization
→ sparse directed graph
→ signed anatomical projection
→ reference LIF dynamics
→ future FlyGym integration
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

## Installation

Python 3.12 or newer is required.

```powershell
python -m pip install -e ".[test]"
```

## Tests

```powershell
python -m pytest
python -m compileall src
git diff --check
```

Tests use small in-memory fixtures and do not download or require real MaleCNS
data.

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
counts are not functional synaptic weights. The baseline has no membrane
state, delays, stochasticity, plasticity, receptor identity, gap-junction
representation, or biological validation.

Raw source data and normalized records are separate concepts. Raw or derived
connectome files should remain outside Git.

See [the Task 001 plan](docs/plans/task-001-malecns-data-ingestion-and-executable-graph.md)
and [the adapter boundary](docs/data-adapter.md) for assumptions and known
unknowns.
