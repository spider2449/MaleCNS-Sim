"""Bounded display views over an authoritative prepared projection."""

from types import SimpleNamespace
import http.client
import json
import threading
from html.parser import HTMLParser
from pathlib import Path
import re

import numpy as np
import pytest

from malecns_sim.application.subgraph import EDGE_CAP, build_subgraph
from malecns_sim.application.server import LocalServer, RunRecord
from malecns_sim.application.workbench import DatasetCatalog


class _IdentityMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.classes[attributes["id"]] = attributes.get("class", "").split()


def test_long_identity_layout_has_shared_wrap_rule():
    static = Path(__file__).resolve().parents[1] / "src" / "malecns_sim" / "application" / "static"
    markup = _IdentityMarkup()
    markup.feed((static / "index.html").read_text(encoding="utf-8"))
    for element_id in ("dataset", "identity", "result", "filter-label", "events"):
        assert "identity-value" in markup.classes[element_id]

    css = (static / "style.css").read_text(encoding="utf-8")
    identity_rule = re.search(r"\.identity-value\s*\{([^}]*)\}", css)
    assert identity_rule is not None
    for declaration in ("min-width:0", "overflow-wrap:anywhere", "word-break:break-word"):
        assert declaration in identity_rule.group(1)
    assert re.search(r"main>\*\s*\{[^}]*min-width:0", css)
    assert "@media(max-width:899px)" in css


def fixture():
    ids = np.arange(1, 104, dtype=np.int64)
    source = np.array([1] * 100 + [3, 4, 5], dtype=np.int64) - 1
    target = np.array(list(range(3, 103)) + [103, 103, 2], dtype=np.int64) - 1
    weights = np.array([0.275 * (100 - i) for i in range(100)] + [2.75, -5.5, 0.275])
    projection = SimpleNamespace(neuron_ids=ids, source_positions=source, target_positions=target,
                                 effective_weights_mV=weights, synaptic_weight_mV=0.275, fingerprint="prepared-fingerprint")
    spec = SimpleNamespace(stimulus=SimpleNamespace(member_ids=(1,)), target=SimpleNamespace(neuron_id=103),
                           intervention=SimpleNamespace(target_ids=(103,)), dataset=SimpleNamespace(manifest_digest="manifest"), digest="spec-digest")
    return projection, spec


def test_view_determinism_identity_and_cap():
    projection, spec = fixture()
    first = build_subgraph(projection, spec, "stimulus", 80, run_id="run")
    second = build_subgraph(projection, spec, "stimulus", 80, run_id="run")
    for view in (first, second):
        view.pop("extraction_seconds")
        view.pop("serialized_bytes")
    assert first == second
    assert first["graph_fingerprint"] == "prepared-fingerprint"
    assert first["spec_digest"] == "spec-digest" and first["run_id"] == "run"
    assert first["rendered_node_count"] == 80
    assert first["total_candidate_nodes"] == 101 and first["truncated"]
    assert first["nodes"][0]["roles"] == ["stimulus"]
    assert first["nodes"][0]["activity"] == {"available": False, "spike_count": None}
    assert first["edges"][0]["anatomical_weight"] == 100


def test_target_and_combined_context():
    projection, spec = fixture()
    target = build_subgraph(projection, spec, "target", 80)
    combined = build_subgraph(projection, spec, "combined", 80)
    assert {n["neuron_id"] for n in target["nodes"]} == {3, 4, 103}
    assert next(n for n in target["nodes"] if n["neuron_id"] == 103)["roles"] == ["target", "intervention"]
    assert {1, 3, 4, 103}.issubset({n["neuron_id"] for n in combined["nodes"]})
    assert any("shared displayed context" in n["roles"] for n in combined["nodes"])
    assert combined["filter_definition"]["edge_cap"] == EDGE_CAP


@pytest.mark.parametrize("mode,cap", [("all", 80), ("stimulus", 0), ("target", 1000000)])
def test_rejects_unbounded_or_unknown_filter(mode, cap):
    projection, spec = fixture()
    with pytest.raises(ValueError):
        build_subgraph(projection, spec, mode, cap)


def test_subgraph_route_bounds_session_failure_and_pending(tmp_path):
    server = LocalServer(0, DatasetCatalog(tmp_path / "missing", engine=None), tmp_path)
    projection, spec = fixture()
    record = RunRecord("synthetic", spec)
    record.subgraphs[("stimulus", 80)] = build_subgraph(projection, spec, "stimulus", 80, run_id="run")
    server.manager.records[record.job_id] = record
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def get(path, token=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
        headers = {"X-Local-Session": token} if token else {}
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        status, payload = response.status, json.loads(response.read())
        connection.close()
        return status, payload
    try:
        path = "/api/runs/synthetic/subgraph?mode=stimulus&cap=80"
        assert get(path)[0] == 403
        assert get(path, server.token)[1]["graph_fingerprint"] == "prepared-fingerprint"
        assert get("/api/runs/synthetic/subgraph?mode=stimulus&cap=1000000", server.token)[0] == 400
        assert get("/api/runs/synthetic/subgraph?mode=stimulus&cap=80&extra=1", server.token)[0] == 400
        assert get("/api/runs/synthetic/subgraph?mode=target&cap=80", server.token)[0] == 409
        assert get("/api/runs/unknown/subgraph?mode=stimulus&cap=80", server.token)[0] == 404
        record.state = "FAILED"
        assert get(path, server.token)[1]["error"]["code"] == "RUN_FAILED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
