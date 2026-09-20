# MaleCNS data adapter boundary

The repository does not currently contain a downloaded MaleCNS dataset, and
the exact public v1.0 file names and schema have not been verified here. Task
001 therefore does not guess a source-specific adapter or download data.

The supported local boundary is two CSV/TSV tables:

- a neuron table with an explicitly configured ID column and optional metadata
  columns;
- an edge table with explicitly configured source ID, target ID, and synapse
  count columns.

The default names (`neuron_id`, `source_id`, `target_id`, and
`synapse_count`) are canonical internal example names, not claims about the
MaleCNS publication or download. Use CLI column options or the
`NeuronColumns`/`EdgeColumns` Python objects for a verified external schema.
No raw data belongs in Git and unit tests never access the network.
