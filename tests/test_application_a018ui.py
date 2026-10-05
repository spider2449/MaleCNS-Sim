"""Bounded historical identity forensics, with no real-data access or advance."""
import ast
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from malecns_sim.analysis.task008 import _digest
from malecns_sim.analysis import task008
from malecns_sim.dynamics import lif
from test_application_a018u import a018u

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = "f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e"
spec = importlib.util.spec_from_file_location("a018ui", ROOT / "scripts/audit_application_a018ui.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def historical_source(path):
    return subprocess.check_output(["git", "show", f"{HISTORICAL}:{path}"], cwd=ROOT).decode("utf-8")


def historical_projection():
    tree = ast.parse(historical_source("src/malecns_sim/dynamics/lif.py"))
    node = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                and node.name == "EffectiveSignedProjection")
    namespace = dict(vars(lif))
    exec(compile(ast.Module(body=[node], type_ignores=[]), "historical_projection", "exec"), namespace)
    return namespace["EffectiveSignedProjection"]


def test_historical_identity_layer_reconstruction():
    payload = dict(graph="full",
        unsigned="fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4",
        signed="861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25",
        effective="ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f")
    observed = "d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495"
    assert _digest("malecns-sim-task008-prepared-network-v1", payload) == observed
    assert observed != payload["effective"]
    tree = ast.parse(historical_source("src/malecns_sim/analysis/task008.py"))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_digest")
    namespace = dict(json=json, hashlib=hashlib)
    exec(compile(ast.Module(body=[node], type_ignores=[]), "historical_digest", "exec"), namespace)
    assert namespace["_digest"]("malecns-sim-task008-prepared-network-v1", payload) == observed


@pytest.mark.parametrize("shape", ["mixed", "random", "all_exc"])
@pytest.mark.parametrize("conservative", [False, True])
def test_historical_current_components_exact(tmp_path, shape, conservative):
    files, numeric = a018u.fixture(tmp_path, 10, 80, shape)
    prepared, _, _, _ = a018u.run(files, numeric, conservative=conservative)
    old = historical_projection().from_signed_connectome(prepared.signed_connectome)
    current = prepared.projection
    for name in current.__dataclass_fields__:
        left, right = getattr(old, name), getattr(current, name)
        if isinstance(left, np.ndarray):
            assert left.dtype == right.dtype and left.shape == right.shape
            assert left.tobytes() == right.tobytes()
        else:
            assert left == right
    first = audit.components(prepared, parameters=lif.LIFParameters())
    assert first == audit.components(prepared, parameters=lif.LIFParameters())
    assert first["effective_weights"] == first["outgoing_data"]
    assert first["outgoing_indices"]["sha256"] == audit.fingerprint(current.target_positions)["sha256"]
    graph = prepared.signed_connectome
    mask = graph.signed_edge_mask
    weights = graph.connectome.synapse_counts[mask].astype(np.float64) * graph.presynaptic_signs[mask] * 0.275
    permutation = np.lexsort((np.searchsorted(current.neuron_ids, graph.connectome.target_ids[mask]),
                              np.searchsorted(current.neuron_ids, graph.connectome.source_ids[mask])))
    assert weights[permutation].tobytes() == current.effective_weights_mV.tobytes()
    for path in ("src/malecns_sim/graph/signed.py", "src/malecns_sim/graph/fingerprint.py",
                 "src/malecns_sim/sign.py", "src/malecns_sim/data/neurotransmitter.py"):
        assert historical_source(path).replace("\r\n", "\n") == (ROOT / path).read_text().replace("\r\n", "\n")


def test_metadata_and_diagnostic_bytes():
    assert audit.metadata_bytes(dict(z=None, a="\u03b3")) == b'{"a":"\\u03b3","z":null}'
    assert audit.metadata_bytes(dict(b=2, a=1)) == audit.metadata_bytes(dict(a=1, b=2))
    assert audit.fingerprint(np.array([0.0])) != audit.fingerprint(np.array([-0.0]))
    assert audit.fingerprint(np.array([1, 2])) != audit.fingerprint(np.array([2, 1]))
    assert _digest("domain", dict(a=1)) == hashlib.sha256(b'domain\0{"a":1}').hexdigest()


def test_effective_digest_field_order(tmp_path):
    files, numeric = a018u.fixture(tmp_path, 10, 80, "mixed")
    prepared, _, _, _ = a018u.run(files, numeric)
    projection = prepared.projection
    digest = hashlib.sha256(b"malecns-sim-effective-signed-projection-v1")
    for value in (projection.sign_policy_id, projection.resolution_policy_id,
                  str(projection.synaptic_weight_mV), projection.signed_policy_fingerprint):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "little"))
        digest.update(encoded)
    for array in (projection.neuron_ids, projection.source_positions, projection.target_positions,
                  projection.effective_weights_mV, projection.outgoing_indptr):
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    assert digest.hexdigest() == projection.fingerprint


def test_historical_preparation_and_committed_fingerprints(tmp_path):
    tree = ast.parse(historical_source("src/malecns_sim/analysis/task008.py"))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                and node.name == "prepare_network")
    files, numeric = a018u.fixture(tmp_path, 10, 80, "mixed")
    namespace = dict(vars(task008))
    namespace["load_male_cns_v1_numeric"] = lambda *args: numeric
    namespace["EffectiveSignedProjection"] = historical_projection()
    exec(compile(ast.Module(body=[node], type_ignores=[]), "historical_prepare", "exec"), namespace)
    historical = namespace["prepare_network"](*files)
    with patch.object(task008, "load_male_cns_v1_numeric", lambda *args: numeric):
        current = task008.prepare_network(*files)
    left = audit.components(historical, parameters=lif.LIFParameters())
    right = audit.components(current, parameters=lif.LIFParameters())
    assert left == right and historical.fingerprint == current.fingerprint
    payload = dict(graph=current.graph_name, unsigned=current.projection.unsigned_graph_fingerprint,
                   signed=current.projection.signed_policy_fingerprint, effective=current.projection.fingerprint)
    assert right["canonical_metadata"] == audit.fingerprint(audit.metadata_bytes(payload))
    recorded = json.loads((ROOT / "docs/plans/2026-10-05-application-a018ui-components.json").read_text())
    assert recorded["effective_digest"] == current.projection.fingerprint
    assert recorded["prepared_digest"] == current.fingerprint
    assert {key: value["current"] for key, value in recorded["components"].items()} == right


def test_production_default_and_frozen_expectation_unchanged():
    source = (ROOT / "scripts/certify_application_a018ur.py").read_text()
    assert "prepared_digest=prepared.fingerprint" in source
    assert 'PREPARED_ID = "ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f"' in source
    tree = ast.parse((ROOT / "src/malecns_sim/application/service.py").read_text())
    engine = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ProductionEngine")
    prepare = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "prepare")
    assert "bounded_route" not in ast.unparse(prepare)
