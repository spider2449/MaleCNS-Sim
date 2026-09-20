from __future__ import annotations

import json

import pytest

from malecns_sim.data.male_cns_v1 import (
    MaleCNSV1ColumnMapping,
    inspect_feather,
    load_male_cns_v1,
)
from malecns_sim.data.model import NormalizedConnectome
from malecns_sim.data.normalize import normalize_edges, normalize_neurons
from malecns_sim.data.provenance import (
    DatasetProvenance,
    FileProvenance,
    file_provenance,
    read_manifest,
    sha256_file,
    verify_file,
    write_manifest,
)
from malecns_sim.graph.fingerprint import graph_fingerprint
from malecns_sim.graph.sparse import SparseDirectedGraph


def test_body_ids_reject_float_conversion_and_preserve_large_integer():
    large_id = 9_007_199_254_740_993
    result = normalize_neurons([{"neuron_id": large_id}])
    assert result[0].neuron_id == str(large_id)
    with pytest.raises(ValueError, match="floating-point"):
        normalize_neurons([{"neuron_id": float(large_id)}])


def test_required_columns_fail_closed_and_optional_annotation_fields_are_absent():
    with pytest.raises(ValueError, match="required configured column"):
        normalize_neurons([{"body": 1}])
    with pytest.raises(ValueError, match="required configured column"):
        normalize_edges([{"source_id": "1", "target_id": "1"}], ["1"])
    result = normalize_neurons([{"neuron_id": 1}])
    assert result[0].cell_type is None
    assert result[0].neurotransmitter is None


def test_provenance_round_trip_and_sha256(tmp_path):
    data_path = tmp_path / "sample.bin"
    data_path.write_bytes(b"MaleCNS-Sim")
    measured = file_provenance(data_path, source_url="https://example.invalid/sample")
    manifest_path = tmp_path / "manifest.json"
    provenance = DatasetProvenance(
        dataset_name="MaleCNS",
        release="v1.0",
        source_organization="HHMI Janelia / FlyEM",
        official_dataset_page="https://male-cns.janelia.org/download/",
        adapter_schema_version="test",
        files=(measured,),
    )
    write_manifest(manifest_path, provenance)
    assert read_manifest(manifest_path) == provenance
    assert sha256_file(data_path) == measured.sha256
    assert verify_file(data_path, measured)["valid"] is True
    assert json.loads(manifest_path.read_text())["files"][0]["source_url"] == measured.source_url


def test_graph_fingerprint_is_repeatable():
    connectome = NormalizedConnectome(
        neurons=normalize_neurons([{"neuron_id": 1}, {"neuron_id": 2}]),
        edges=(),
    )
    first = SparseDirectedGraph.from_connectome(connectome)
    second = SparseDirectedGraph.from_connectome(connectome)
    assert graph_fingerprint(first) == graph_fingerprint(second)


def test_male_cns_feather_mapping_and_schema_inspection(tmp_path):
    pa = pytest.importorskip("pyarrow")
    import pyarrow.feather as feather

    annotation = tmp_path / "annotations.feather"
    neurotransmitter = tmp_path / "neurotransmitters.feather"
    weights = tmp_path / "weights.feather"
    feather.write_feather(
        pa.table(
            {
                "body": pa.array([9_007_199_254_740_993, 2], type=pa.uint64()),
                "type": ["alpha", None],
                "side": ["L", "R"],
            }
        ),
        annotation,
    )
    feather.write_feather(
        pa.table(
            {
                "body": pa.array([9_007_199_254_740_993, 2], type=pa.uint64()),
                "prediction": ["GABA", "glutamate"],
                "probability": [0.9, 0.8],
            }
        ),
        neurotransmitter,
    )
    feather.write_feather(
        pa.table(
            {
                "src": pa.array([9_007_199_254_740_993], type=pa.uint64()),
                "dst": pa.array([2], type=pa.uint64()),
                "count": pa.array([6], type=pa.uint64()),
            }
        ),
        weights,
    )
    inspection = inspect_feather(annotation)
    assert inspection.row_count == 2
    assert inspection.columns == ("body", "type", "side")
    result = load_male_cns_v1(
        annotation,
        neurotransmitter,
        weights,
        MaleCNSV1ColumnMapping(
            annotation_body_id="body",
            edge_source_id="src",
            edge_target_id="dst",
            edge_weight="count",
            annotation_cell_type="type",
            annotation_side="side",
            neurotransmitter_prediction_columns=("prediction",),
            neurotransmitter_probability_columns=("probability",),
        ),
    )
    assert result.neuron_ids == ("2", "9007199254740993")
    assert result.edges[0].synapse_count == 6
    assert result.neurons[1].neurotransmitter == "GABA"
    assert ("prediction", "GABA") in result.neurons[1].metadata
    assert ("probability", "0.9") in result.neurons[1].metadata
