"""A007C production assets and synthetic evidence integration tests."""
from pathlib import Path
import importlib.util
import json
import subprocess
import threading
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/malecns_sim/application/static"

@pytest.fixture(scope="module")
def review():
    spec = importlib.util.spec_from_file_location("a007c_review", ROOT / "scripts/review_application_a007c.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    server, temporary, identity = module.start_review()
    yield server, identity
    server.shutdown(); server.server_close(); temporary.cleanup()


def test_synthetic_production_api_and_assets(review, tmp_path):
    server, identity = review
    base = f"http://127.0.0.1:{server.server_port}"
    def get(route):
        with urlopen(Request(base + route, headers={"X-Local-Session": server.token})) as response:
            return json.load(response)
    snapshot = get("/api/robustness/" + identity)
    assert [v["variant_id"] for v in snapshot["result"]["variants"]] == ["R0", "V1", "V2", "V3", "V4", "V5", "V6", "V7"]
    variants = snapshot["result"]["variants"]
    assert variants[0]["state"] == "REUSED"
    assert variants[0]["comparison"]["target"]["spike_count"]["warning"] == "ZERO_BASELINE"
    deltas = [v["comparison"]["target"]["spike_count"]["absolute_delta"] for v in variants]
    assert min(deltas) < 0 < max(deltas) and 0 in deltas
    assert variants[5]["schedule_evidence"]["input_amplitudes_mv"] == [50.0]
    partial = next(get("/api/robustness/" + item["robustness_id"]) for item in get("/api/robustness")["robustness"] if item["overall_state"] == "PARTIAL")
    assert partial["result"]["variants"][4]["state"] == "FAILED"
    assert partial["result"]["variants"][5]["state"] == "PENDING"
    assert partial["result"]["variants"][0]["comparison"]
    assert get("/api/datasets")["datasets"][0]["synthetic_review"] is True
    evidence = {}
    for variant in variants:
        route = "/api/robustness/" + identity + "/variants/" + variant["variant_id"]
        evidence[variant["variant_id"]] = {"variant":get(route),"comparison":get(route+"/comparison"),"playback":get(route+"/playback"),"subgraph":get(route+"/subgraph")}
    assert get("/api/robustness/" + identity + "/export")["result"] == snapshot["result"]
    for asset in ["robustness.js", "compare.js", "style.css"]:
        with urlopen(base + "/" + asset) as response: assert response.status == 200
    data = tmp_path / "evidence.json"
    data.write_text(json.dumps({"snapshot":snapshot,"partial":partial,"evidence":evidence}), encoding="utf-8")
    result = subprocess.run(["node",str(ROOT / "tests/js/application_a007c.cjs"),str(data),str(STATIC)],capture_output=True,text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout)


def test_authoritative_backend_firewall_and_packaging():
    js = (STATIC / "robustness.js").read_text(encoding="utf-8-sig")
    html = (STATIC / "index.html").read_text()
    css = (STATIC / "style.css").read_text(encoding="utf-8-sig")
    assert "metric?.absolute_delta" in js and "target.spike_count.absolute_delta" in js
    assert "intervention -" not in js and "baseline -" not in js
    assert "sha256" not in js and "Task016" not in js
    assert "No aggregate robustness verdict requested." in js
    assert "<script src=\"/robustness.js\" defer>" in html
    assert "overflow-wrap: anywhere" in css and "overflow-x: auto" in css
    assert "up to 16 scientific child runs" in html and "cooperative boundaries" in html
    assert "releasing removes" not in js.lower() or "this session's retained robustness evidence" in js
    assert "X-Local-Session" in js and "/export" in js
    assert "static/*" in (ROOT / "pyproject.toml").read_text()
