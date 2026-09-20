"""External-table adapters and normalized connectome data structures."""

from malecns_sim.data.io import load_connectome
from malecns_sim.data.model import EdgeRecord, NeuronRecord, NormalizedConnectome
from malecns_sim.data.normalize import (
    EdgeColumns,
    NeuronColumns,
    normalize_connectome,
    normalize_edges,
    normalize_neurons,
)

__all__ = [
    "EdgeColumns",
    "EdgeRecord",
    "NeuronColumns",
    "NeuronRecord",
    "NormalizedConnectome",
    "load_connectome",
    "normalize_connectome",
    "normalize_edges",
    "normalize_neurons",
]
from malecns_sim.data.male_cns_v1 import (
    ADAPTER_SCHEMA_VERSION,
    FeatherInspection,
    MaleCNSV1ColumnMapping,
    inspect_feather,
    load_male_cns_v1,
)
from malecns_sim.data.provenance import (
    DatasetProvenance,
    FileProvenance,
    file_provenance,
    read_manifest,
    sha256_file,
    verify_file,
    write_manifest,
)

__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "FeatherInspection",
    "MaleCNSV1ColumnMapping",
    "inspect_feather",
    "load_male_cns_v1",
    "DatasetProvenance",
    "FileProvenance",
    "file_provenance",
    "read_manifest",
    "sha256_file",
    "verify_file",
    "write_manifest",
]
