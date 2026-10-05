"""Frozen evidence reconstruction and fail-closed layer gates; no real execution."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import preparation_identity_contract as contract
from malecns_sim.analysis.task008 import _digest


def historical(path):
    return subprocess.check_output(["git", "show", "f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e:" + path], cwd=ROOT).decode()


def test_independent_frozen_artifact_reconstruction_and_provenance():
    old = json.loads(historical("data/derived/task008-results.json"))["full_prepared"]
    payload = dict(graph=old["graph_name"], unsigned=old["unsigned_graph_fingerprint"],
                   signed=old["signed_policy_fingerprint"], effective=old["effective_projection_fingerprint"])
    record = json.loads(contract.RECORD.read_text())
    assert record["envelope_inputs"] == payload
    digest = contract.reconstruct_envelope(payload)
    assert digest == old["fingerprint"] == contract.expected_identity()["prepared_network_digest"]
    assert digest == "d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495"
    assert payload["effective"] == "ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f"
    assert len({payload["unsigned"], payload["effective"], digest}) == 3
    assert "E3 derived historical" in record["provenance"]["prepared_network_digest"]
    assert "full_prepared.effective_projection_fingerprint" in record["provenance"]["effective_projection_fingerprint"]
    assert record["generating_clean_sha"] is None
    assert contract.reconstruct_envelope(dict(reversed(list(payload.items())))) == digest
    assert _digest(record["serializer"], payload) == digest
    node = next(n for n in ast.parse(historical("src/malecns_sim/analysis/task008.py")).body
                if isinstance(n, ast.FunctionDef) and n.name == "_digest")
    namespace = dict(json=json, hashlib=hashlib)
    exec(compile(ast.Module(body=[node], type_ignores=[]), "frozen_serializer", "exec"), namespace)
    assert namespace["_digest"](record["serializer"], payload) == digest


@pytest.mark.parametrize("field,gate", list(zip(contract.FIELDS, ("G1", "G2", "G3", "G4", "G5", "G6", "G6"))))
def test_each_mandatory_layer_mismatch_fails(field, gate):
    expected = contract.expected_identity()
    observed = copy.deepcopy(expected)
    observed[field] = {} if field == "dataset_provenance_identity" else "incorrect"
    gates = contract.compare_identity(observed, expected)
    assert not gates[gate] and sum(not value for value in gates.values()) == 1


def test_correct_tuple_and_cross_layer_rejection():
    expected = contract.expected_identity()
    assert all(contract.compare_identity(expected, expected).values())
    for field in ("prepared_network_digest", "effective_projection_fingerprint"):
        wrong = dict(expected)
        other = "effective_projection_fingerprint" if field == "prepared_network_digest" else "prepared_network_digest"
        wrong[field] = wrong[other]
        with pytest.raises(ValueError, match="cannot serve"):
            contract.compare_identity(wrong, expected)
    swapped = dict(expected)
    swapped["prepared_network_digest"], swapped["effective_projection_fingerprint"] = swapped["effective_projection_fingerprint"], swapped["prepared_network_digest"]
    assert not contract.compare_identity(swapped, expected)["G4"]
    assert not contract.compare_identity(swapped, expected)["G5"]


@pytest.mark.parametrize("field", ["prepared_digest", "unsigned_digest", "fingerprint"])
def test_ambiguous_legacy_fields_rejected(field):
    wrong = dict(contract.expected_identity(), **{field: "legacy"})
    with pytest.raises(ValueError, match="layer-explicit"):
        contract.compare_identity(wrong, contract.expected_identity())


def test_no_real_execution_and_scientific_default_unchanged(tmp_path):
    from test_application_a018ur import files_and_expected
    from malecns_sim.application.service import ProductionEngine
    from malecns_sim.application.preparation import REFERENCE_CONFIG
    from malecns_sim.dynamics.lif import PreparedRuntime
    files, _ = files_and_expected(tmp_path)
    prepared = ProductionEngine().prepare(files, "cpu_reference")
    before = {name: value.tobytes() for name, value in vars(prepared.projection).items()
              if hasattr(value, "tobytes")} if hasattr(prepared.projection, "__dict__") else {
                  name: getattr(prepared.projection, name).tobytes()
                  for name in prepared.projection.__dataclass_fields__
                  if hasattr(getattr(prepared.projection, name), "tobytes")}
    with patch.object(ProductionEngine, "prepare", side_effect=AssertionError("prepare forbidden")), \
         patch.object(PreparedRuntime, "advance", side_effect=AssertionError("advance forbidden")):
        observed = contract.observe_identity(prepared, files, REFERENCE_CONFIG.digest)
        assert all(contract.compare_identity(observed, observed).values())
        contract.expected_identity()
    assert all(getattr(prepared.projection, name).tobytes() == raw for name, raw in before.items())
    assert not subprocess.check_output(["git", "diff", "d6fdb16e078bfca524214b9d1855ece3f8e9a7d7", "--", "src", "data", "pyproject.toml"], cwd=ROOT)
    assert REFERENCE_CONFIG.digest == contract.expected_identity()["preparation_config_identity"]
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
             for node in ast.walk(ast.parse((ROOT / "scripts/preparation_identity_contract.py").read_text()))
             if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))}
    assert not calls & {"prepare", "advance", "simulate_lif", "simulate_cuda", "download", "edge_batches"}
