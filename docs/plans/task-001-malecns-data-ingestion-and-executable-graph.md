# Task 001 — MaleCNS Data Ingestion and Executable Graph Baseline

## Goal

Create the smallest testable foundation that turns externally supplied MaleCNS
neuron and connectivity tables into a deterministic normalized representation,
then into a sparse directed graph that supports a deliberately simple graph
propagation operation. This task establishes data and graph boundaries only;
it does not implement a biological neural simulator.

## Scope

- Initialize a Python 3.12+ package named `malecns_sim`.
- Represent neuron metadata and directed synapse-count edges explicitly.
- Normalize user-supplied tabular rows without hard-coding an unverified public
  MaleCNS filename or schema.
- Aggregate duplicate neuron and edge records deterministically, rejecting
  conflicting neuron identity metadata rather than silently choosing a value.
- Build both full and minimum-synapse-filtered CSR connectivity matrices.
- Provide deterministic graph summary statistics and scalar propagation.
- Add a narrow inspection/benchmark CLI and synthetic unit tests.
- Document measured benchmark values separately from estimates.

Out of scope are neural dynamics, biological sign inference, embodied agents,
GPU/distributed execution, network downloads, and committing raw connectome
data.

## Assumptions

- A normalized neuron identifier is represented as a non-empty string. This
  preserves identifiers from integer or string source files without guessing
  their external type.
- Synapse counts are non-negative integers. Duplicate source-target rows are
  summed before graph construction.
- Optional metadata is represented as immutable tuples of normalized strings;
  absent values remain absent.
- External schemas are not assumed. CSV/TSV loading requires an explicit
  column mapping, and callers may provide rows or DataFrames directly.
- The default experimental threshold is `min_synapses=5`, but all filtering is
  configurable.

## Internal data model

`NeuronRecord` contains `neuron_id`, optional `cell_type`, optional
`neurotransmitter`, and four optional classification flags:
ascending, descending, sensory, and motor-related.

`EdgeRecord` contains `source_id`, `target_id`, and a non-negative integer
`synapse_count`. `NormalizedConnectome` contains deterministic tuples of
neurons and aggregated edges plus provenance describing the adapter/source
configuration.

The data layer exposes generic row normalization and explicit `NeuronColumns`
and `EdgeColumns` mappings. It does not claim that any particular MaleCNS
download uses those columns. A future verified MaleCNS adapter can map its
documented schema into this boundary.

## Graph representation

`SparseDirectedGraph` stores deterministic neuron IDs, a CSR matrix whose
rows are sources and columns are targets, and the applied threshold. Matrix
values are synapse counts. The full graph uses threshold zero; a filtered graph
keeps edges with `synapse_count >= min_synapses`. Unknown edge endpoints are
rejected during normalization, while unknown propagation inputs are reported
as errors.

## Deterministic guarantees

- Neurons are sorted by normalized identifier using an explicit stable key.
- Edges are aggregated by `(source_id, target_id)` and sorted by source then
  target before CSR construction.
- CSR row/column mappings, summary statistics, and propagation output use the
  deterministic neuron ordering.
- Propagation computes `activation[target] += activation[source] *
  synapse_count` for selected outgoing edges. It is a graph operation and not
  a neural model; no neurotransmitter sign is inferred.

## Validation plan

- Use in-memory synthetic rows only for unit tests.
- Test normalization, duplicate aggregation, self-edges, thresholding,
  ordering, CSR values, single- and multi-source propagation, unknown IDs, and
  summary statistics.
- Run `python -m pytest`, `python -m compileall src`, and `git diff --check`.
- Run the CLI against a small temporary CSV fixture to verify the real loading
  path without downloading external data.

## Known unknowns

- The exact public MaleCNS v1.0 download location, file names, release
  packaging, and column names have not been verified in this repository.
- The source's precise annotation vocabularies and neurotransmitter prediction
  confidence/label semantics remain unknown.
- No real-data memory, timing, edge-count, or biological coverage result can
  be reported until a documented dataset is supplied and inspected.

## Scientific nonclaims

This graph is an executable connectivity baseline, not an executable
biological brain. Synapse counts are used as non-negative propagation weights
only. Neurotransmitter labels are preserved as metadata and do not imply
excitatory or inhibitory behavior. The propagation primitive has no membrane
state, delays, stochasticity, plasticity, neuromodulation, or body/sensory
coupling.

## Follow-up roadmap

The following sequence is provisional and is not implemented by Task 001:

1. Task 002 — MaleCNS real-data validation and dataset provenance
2. Task 003 — Neurotransmitter-aware signed connectivity model
3. Task 004 — Reference Leaky Integrate-and-Fire neural engine
4. Task 005 — Reproduce a known sensorimotor circuit experiment
5. Task 006 — Descending-neuron output interface
6. Task 007 — FlyGym motor adapter
7. Task 008 — Closed-loop sensory-motor experiment
