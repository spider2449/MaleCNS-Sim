"""Synthetic one-shot wiring, fallback stops, identity checks and cleanup."""
import ast
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch

import pyarrow as pa
import pyarrow.feather as feather
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("a018r", SCRIPTS / "certify_application_a018r.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
from investigate_application_a014 import synthetic_files
from malecns_sim.application.service import DatasetFiles, ProductionEngine
from malecns_sim.analysis import task008
from malecns_sim.dynamics.lif import PreparedRuntime


def files_and_expected(tmp_path):
    paths = synthetic_files(tmp_path, 2000, 100)
    feather.write_feather(feather.read_table(paths[2]), paths[2], chunksize=512)
    files = DatasetFiles(*paths, "synthetic", "synthetic")
    original = ProductionEngine().prepare(files, "cpu_reference")
    from preparation_identity_contract import observe_identity
    expected = observe_identity(original, files, harness.CONFIG_ID)
    return files, expected


def test_success_exact_identity_no_advance_default_restored(tmp_path):
    files, expected = files_and_expected(tmp_path)
    loader = task008.load_male_cns_v1_numeric
    events = []
    with patch.object(PreparedRuntime, "advance", side_effect=AssertionError("advance forbidden")), \
         patch.object(PreparedRuntime, "initial_state", side_effect=AssertionError("state forbidden")), \
         patch("malecns_sim.dynamics.lif.simulate_lif", side_effect=AssertionError("simulation forbidden")):
        result = harness.prepare_only(files, lambda kind, **fields: events.append((kind, fields)), expected)
    assert result["classification"] == "A018R-PREPARATION-CERTIFIED", result
    assert result["observed"] == expected
    assert result["finite"] and result["completed"]
    assert result["metrics"]["max_active_input_runs"] == 2
    assert "source_iteration" in result["metrics"]["timings"]
    assert "staged_merge" in result["metrics"]["timings"]
    assert any(kind == "source_access" for kind, _ in events)
    assert events[-1][0] == "cleanup"
    assert task008.load_male_cns_v1_numeric is loader
    assert ProductionEngine().prepare(files, "cpu_reference").fingerprint == expected["prepared_network_digest"]


def test_identity_mismatch_stops_and_cleans(tmp_path):
    files, expected = files_and_expected(tmp_path)
    expected["prepared_network_digest"] = "incorrect"
    events = []
    result = harness.prepare_only(files, lambda kind, **fields: events.append(kind), expected)
    assert result["classification"] == "A018R-GRAPH-IDENTITY-MISMATCH"
    assert not result["exact_identity_match"]
    assert events[-1] == "cleanup"


@pytest.mark.parametrize("mode", ["negative", "overflow", "invalid"])
def test_failure_cleanup_and_fallback_prevented(tmp_path, mode):
    files, _ = files_and_expected(tmp_path)
    values = {"negative": ([-1], [1], [1]), "overflow": ([1, 1], [2, 2], [2**63-1, 1]),
              "invalid": ([1], [2], [-1])}[mode]
    feather.write_feather(pa.table(dict(zip(("body_pre", "body_post", "weight"), values))), files.weights)
    events = []
    result = harness.prepare_only(files, lambda kind, **fields: events.append(kind))
    assert result["classification"] == ("A018R-PREPARATION-ERROR" if mode == "invalid" else "A018R-BOUNDED-PATH-FALLBACK"), result
    if mode != "invalid":
        assert result["fallback"] == ("negative_endpoint_reference" if mode == "negative" else "int64_overflow_reference")
    assert not result["completed"]
    assert events[-1] == "cleanup"


def test_exact_frozen_constants_and_no_execution_entrypoints():
    assert harness.MEMORY_CAP == 8589934592
    assert harness.PREPARATION_CAP == 600.0
    assert harness.BATCH_ROWS == 65536
    tree = ast.parse((SCRIPTS / "certify_application_a018r.py").read_text(encoding="utf-8"))
    called = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
              for node in ast.walk(tree) if isinstance(node, ast.Call)
              and isinstance(node.func, (ast.Attribute, ast.Name))}
    assert not called & {"advance", "initial_state", "simulate_lif", "simulate_cuda", "download", "urlopen", "generate"}


@pytest.mark.skipif(sys.platform != "win32", reason="Windows contained process tree")
def test_supervisor_time_failure_cleans_without_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(harness, "PREPARATION_CAP", 0.15)
    code = 'import json,os,time; print(json.dumps(dict(kind="prepare_start",pid=os.getpid(),started_ns=time.perf_counter_ns(),clock_ns=time.perf_counter_ns(),stage="synthetic")),flush=True); time.sleep(5)'
    result = harness.supervise([sys.executable, "-c", code], tmp_path / "result.json")
    assert result["classification"] == "A018R-TIME-LIMIT", result
    assert result["attempts"] == 0
    assert result["orphans"] == []


@pytest.mark.skipif(sys.platform != "win32", reason="Windows contained process tree")
def test_supervisor_success_boundary_handshake(tmp_path):
    output = tmp_path / "result.json"
    acknowledgement = str(output.with_suffix(".prepared-captured"))
    code = f'''import json,os,time,pathlib
def emit(kind, **fields):
 print(json.dumps(dict(kind=kind,pid=os.getpid(),clock_ns=time.perf_counter_ns(),**fields)),flush=True)
emit("prepare_start",started_ns=time.perf_counter_ns(),stage="synthetic")
emit("prepare_done",preparation_seconds=0.001,stage="prepared_resident")
while not pathlib.Path({acknowledgement!r}).exists(): time.sleep(0.01)
emit("cleanup",stage="released")
emit("result",result=dict(classification="A018R-PREPARATION-CERTIFIED",completed=True))
time.sleep(5)
'''
    result = harness.supervise([sys.executable, "-c", code], output)
    assert result["classification"] == "A018R-PREPARATION-CERTIFIED", result
    assert result["orphans"] == []
    assert any(sample["stage"] == "prepared_resident" for sample in result["samples"])
