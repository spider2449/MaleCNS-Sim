# MaleCNS-Sim

MaleCNS-Sim is a research software foundation for turning the Drosophila
MaleCNS connectome into a deterministic executable graph for later
sensorimotor research.

It is not a complete brain simulation, a biological claim that a connectome is
an executable brain, or an embodied fly environment. It currently has no
Leaky Integrate-and-Fire model, sensory/body coupling, FlyGym, NeuroMechFly,
MuJoCo, GPU backend, or learning system.

## Current stage

Task 001 establishes data ingestion, normalization, sparse CSR graph
construction, deterministic scalar propagation, and small measurements. The
propagation operation is a graph test primitive, not a neural model.

The intended pipeline is:

```text
MaleCNS data
→ normalization
→ sparse directed graph
→ deterministic propagation
→ future neural dynamics
→ future FlyGym integration
```

Task 002 validated MaleCNS v1.0 locally from the three official Feather
files. The measured full segment graph contains 88,404,403 node IDs and
151,856,684 edges; the `min_synapses=5` graph contains 7,622,864 edges.
Both CSR builds are deterministic, and source neurotransmitter predictions
are preserved as metadata without assigning biological sign. See the
[Task 002 validation record](docs/plans/task-002-malecns-v1-real-data-validation-and-provenance.md)
and the local provenance manifest at `data/provenance/male-cns-v1.0.json`.

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
neurotransmitter predictions and classifications. Neurotransmitters do not
receive invented excitatory/inhibitory signs. Edge weights are synapse counts;
the baseline has no membrane state, delays, stochasticity, plasticity,
neuromodulation, or biological validation.

Raw source data and normalized records are separate concepts. Raw or derived
connectome files should remain outside Git.

See [the Task 001 plan](docs/plans/task-001-malecns-data-ingestion-and-executable-graph.md)
and [the adapter boundary](docs/data-adapter.md) for assumptions and known
unknowns.
