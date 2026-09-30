"""Verify frozen inputs and execute the single Task 018 anatomical analysis."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow
import pyarrow.feather as feather

from malecns_sim.analysis.task018 import LEFT, RIGHT, SCHEMA, canonical_json, partition, result_digest, sensitivity
from malecns_sim.data.male_cns_v1 import (
    ADAPTER_SCHEMA_VERSION,
    load_male_cns_v1_numeric,
    official_v1_mapping,
    project_numeric_connectome,
    select_publication_neuron_ids,
    threshold_curated_projection,
)
from malecns_sim.graph.fingerprint import graph_fingerprint
from malecns_sim.graph.sparse import SparseDirectedGraph


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs/plans/2026-09-30-task-018-mn9-anatomical-asymmetry-preregistration.md"
PREREG_SHA = "4f767ab2bfcbf5e5773a803ee6fdb601e39d5521d7f30a12d35a3a5506de5bb4"
MANIFEST = ROOT / "data/provenance/male-cns-v1.0.json"
RAW_DIR = ROOT / "data/raw/male-cns/v1.0"
OUTPUT = ROOT / "data/derived/task018-results.json"
REPORT = ROOT / "data/derived/task018-report.md"
ERROR = ROOT / "data/derived/task018-error.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_inputs() -> tuple[dict[str, object], dict[str, Path]]:
    if sha256(PREREG) != PREREG_SHA:
        raise ValueError("preregistration_fingerprint_mismatch")
    committed = subprocess.check_output(["git", "show", f"HEAD:{PREREG.relative_to(ROOT).as_posix()}"], cwd=ROOT)
    if committed != PREREG.read_bytes():
        raise ValueError("preregistration_not_committed_head")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("dataset_name") != "MaleCNS" or manifest.get("release") != "v1.0" or manifest.get("adapter_schema_version") != ADAPTER_SCHEMA_VERSION:
        raise ValueError("manifest_identity_mismatch")
    expected = {
        "body-annotations-male-cns-v1.0-minconf-0.5.feather": "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2",
        "body-neurotransmitters-male-cns-v1.0.feather": "95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621",
        "connectome-weights-male-cns-v1.0-minconf-0.5.feather": "e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1",
    }
    listed = {item["local_filename"]: item for item in manifest["files"]}
    if set(listed) != set(expected):
        raise ValueError("manifest_file_set_mismatch")
    paths = {name: RAW_DIR / name for name in expected}
    for name, fingerprint in expected.items():
        if listed[name]["sha256"] != fingerprint or paths[name].stat().st_size != listed[name]["byte_size"] or sha256(paths[name]) != fingerprint:
            raise ValueError(f"raw_file_identity_mismatch:{name}")
    return manifest, paths


def graph_details(projection, expected_edges: int, expected_weight: int) -> dict[str, object]:
    graph = projection.connectome
    weight = int(graph.synapse_counts.sum(dtype=np.int64))
    if graph.neuron_count != 166700 or graph.edge_count != expected_edges or weight != expected_weight:
        raise ValueError("projection_identity_mismatch")
    if np.any(graph.synapse_counts <= 0) or np.any(graph.source_ids[1:] < graph.source_ids[:-1]):
        raise ValueError("projection_integer_or_order_failure")
    return {
        "node_count": graph.neuron_count,
        "edge_count": graph.edge_count,
        "total_synapses": weight,
        "unsigned_graph_fingerprint": graph_fingerprint(SparseDirectedGraph.from_curated_projection(projection)),
    }


def incoming_edges(projection):
    graph = projection.connectome
    selected = (graph.target_ids == LEFT) | (graph.target_ids == RIGHT)
    return [(int(a), int(b), int(c)) for a, b, c in zip(graph.source_ids[selected], graph.target_ids[selected], graph.synapse_counts[selected])]


def execute() -> dict[str, object]:
    manifest, paths = verify_inputs()
    annotation = paths["body-annotations-male-cns-v1.0-minconf-0.5.feather"]
    nt = paths["body-neurotransmitters-male-cns-v1.0.feather"]
    weights = paths["connectome-weights-male-cns-v1.0-minconf-0.5.feather"]
    rows = feather.read_table(annotation, columns=["bodyId", "superclass", "status", "type", "instance", "somaSide"]).to_pylist()
    selection = select_publication_neuron_ids(rows)
    if selection.retained_count != 166700 or not {LEFT, RIGHT}.issubset(set(selection.neuron_ids.tolist())):
        raise ValueError("curated_mn9_identity_failure")
    mn9 = {int(row["bodyId"]): row for row in rows if row["bodyId"] in (LEFT, RIGHT)}
    identity = {}
    for body, instance, side in ((LEFT, "MN9_L", "L"), (RIGHT, "MN9_R", "R")):
        row = mn9.get(body)
        if row is None or (row["type"], row["instance"], row["somaSide"]) != ("MN9", instance, side):
            raise ValueError(f"mn9_annotation_identity_failure:{body}")
        identity[str(body)] = {"type": row["type"], "instance": row["instance"], "somaSide": row["somaSide"]}
    numeric = load_male_cns_v1_numeric(annotation, nt, weights, official_v1_mapping())
    full = project_numeric_connectome(numeric, selection)
    full_graph = graph_details(full, 25582938, 124177617)
    primary_edges = incoming_edges(full)
    primary = partition(primary_edges)
    repeat = partition(reversed(primary_edges))
    if primary != repeat or primary["integrity_status"] != "PASS":
        raise ValueError("primary_partition_or_repeat_failure")
    filtered = threshold_curated_projection(full, min_synapses=5)
    filtered_graph = graph_details(filtered, 6242118, 89860280)
    filtered_edges = incoming_edges(filtered)
    fixed = sensitivity(primary_edges)
    repeated_fixed = sensitivity(reversed(primary_edges))
    direct = partition(filtered_edges)
    if fixed != repeated_fixed or {key: value for key, value in fixed.items() if key != "label"} != direct or fixed["integrity_status"] != "PASS":
        raise ValueError("sensitivity_projection_or_repeat_failure")
    payload = {
        "schema": SCHEMA,
        "preregistration_sha256": PREREG_SHA,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "manifest_sha256": sha256(MANIFEST),
        "raw_file_sha256": {name: item["sha256"] for name, item in sorted({entry["local_filename"]: entry for entry in manifest["files"]}.items())},
        "dataset": {"name": "MaleCNS", "release": "v1.0"},
        "adapter_schema": ADAPTER_SCHEMA_VERSION,
        "graph_definition": "full curated directed publication-superclass neuron projection; positive integer synapse counts; duplicate pairs aggregated; autapses retained",
        "graphs": {"primary": full_graph, "sensitivity_min_synapses_5": filtered_graph},
        "mn9": {"left_body": LEFT, "right_body": RIGHT, "status": "SIDE_RESOLVED", "checked_annotations": identity},
        "primary": primary,
        "sensitivity": fixed,
        "sensitivity_changes_primary_classification": False,
        "integrity_status": "PASS",
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "software_versions": {"python": platform.python_version(), "numpy": np.__version__, "pyarrow": pyarrow.__version__},
    }
    payload["result_digest"] = result_digest(payload)
    return payload


def publish(payload: dict[str, object]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result_bytes = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False).encode("utf-8") + b"\n"
    report_bytes = ("# Task 018 local execution record\n\nResult digest: `" + str(payload["result_digest"]) + "`\n\n" + json.dumps({"primary": payload["primary"], "sensitivity": payload["sensitivity"]}, indent=2, sort_keys=True) + "\n").encode("utf-8")
    staged = []
    try:
        for target, content in ((OUTPUT, result_bytes), (REPORT, report_bytes)):
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".task018-", delete=False) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                staged.append((Path(handle.name), target))
        for source, target in staged:
            os.replace(source, target)
    except Exception:
        for source, target in staged:
            source.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
        raise


def main() -> None:
    if OUTPUT.exists() or REPORT.exists():
        raise RuntimeError("Task 018 final output already exists")
    try:
        payload = execute()
        publish(payload)
    except Exception as exc:
        ERROR.parent.mkdir(parents=True, exist_ok=True)
        ERROR.write_text(json.dumps({"status": "INCOMPLETE", "error": str(exc)}, sort_keys=True) + "\n", encoding="utf-8")
        raise
    ERROR.unlink(missing_ok=True)
    print(json.dumps({"result": OUTPUT.relative_to(ROOT).as_posix(), "digest": payload["result_digest"], "primary": payload["primary"], "sensitivity": payload["sensitivity"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
