"""Certification-only, layer-explicit preparation identity evidence. No execution."""
import hashlib
import json
from pathlib import Path

SCHEMA = "preparation-identity-v1"
RECORD = Path(__file__).resolve().parents[1] / "docs/plans/2026-10-05-application-a018uj-identity-contract.json"
FIELDS = ("dataset_provenance_identity", "preparation_config_identity",
          "unsigned_graph_digest", "effective_projection_fingerprint",
          "prepared_network_digest", "neurons", "edges")


def reconstruct_envelope(payload):
    """Recombine frozen hashes using the unchanged Task008 default serializer."""
    if set(payload) not in ({"graph", "unsigned", "signed", "effective"},
                            {"graph", "unsigned", "signed", "effective", "parameters"}):
        raise ValueError("explicit prepared-network envelope components required")
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(b"malecns-sim-task008-prepared-network-v1\0" + raw).hexdigest()


def expected_identity():
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if record["schema"] != SCHEMA or reconstruct_envelope(record["envelope_inputs"]) != record["expected"]["prepared_network_digest"]:
        raise ValueError("invalid adjudicated identity record")
    return record["expected"]


def observe_identity(prepared, files, config_identity):
    """Read scalar identities from an already prepared object; never mutate arrays."""
    projection = prepared.projection
    return dict(dataset_provenance_identity=dict(manifest_digest=files.manifest_digest,
                mapping_fingerprint=files.mapping_fingerprint),
                preparation_config_identity=config_identity,
                unsigned_graph_digest=projection.unsigned_graph_fingerprint,
                effective_projection_fingerprint=projection.fingerprint,
                prepared_network_digest=prepared.fingerprint,
                neurons=int(projection.neuron_ids.size),
                edges=int(projection.effective_weights_mV.size))


def compare_identity(observed, expected):
    """Reject legacy/unknown/missing fields and compare only identically named layers."""
    for value in (observed, expected):
        if set(value) != set(FIELDS):
            raise ValueError("layer-explicit fields required; prepared_digest is rejected")
        if value["effective_projection_fingerprint"] == value["prepared_network_digest"]:
            raise ValueError("effective fingerprint cannot serve as prepared-network digest")
    return {"G1": observed[FIELDS[0]] == expected[FIELDS[0]],
            "G2": observed[FIELDS[1]] == expected[FIELDS[1]],
            "G3": observed[FIELDS[2]] == expected[FIELDS[2]],
            "G4": observed[FIELDS[3]] == expected[FIELDS[3]],
            "G5": observed[FIELDS[4]] == expected[FIELDS[4]],
            "G6": all(observed[key] == expected[key] for key in ("neurons", "edges"))}
