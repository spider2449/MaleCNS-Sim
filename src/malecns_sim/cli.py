"""Narrow command-line inspection and benchmark entry points."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from malecns_sim.analysis.benchmark import benchmark_connectome
from malecns_sim.data.fetch import fetch_and_write_manifest
from malecns_sim.data.io import load_connectome
from malecns_sim.data.male_cns_v1 import inspect_feather
from malecns_sim.data.normalize import EdgeColumns, NeuronColumns
from malecns_sim.data.provenance import read_manifest, verify_file
from malecns_sim.graph.sparse import SparseDirectedGraph


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="malecns-sim")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "benchmark"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--neurons", required=True, type=Path)
        command_parser.add_argument("--edges", required=True, type=Path)
        command_parser.add_argument("--min-synapses", type=int, default=5)
        command_parser.add_argument("--neuron-id-column", default="neuron_id")
        command_parser.add_argument("--source-column", default="source_id")
        command_parser.add_argument("--target-column", default="target_id")
        command_parser.add_argument("--synapse-column", default="synapse_count")
        command_parser.add_argument("--cell-type-column", default="cell_type")
        command_parser.add_argument("--neurotransmitter-column", default="neurotransmitter")
        command_parser.add_argument("--ascending-column", default="ascending")
        command_parser.add_argument("--descending-column", default="descending")
        command_parser.add_argument("--sensory-column", default="sensory")
        command_parser.add_argument("--motor-related-column", default="motor_related")
    data_parser = subparsers.add_parser("data")
    data_subparsers = data_parser.add_subparsers(dest="data_command", required=True)
    fetch_parser = data_subparsers.add_parser("fetch")
    fetch_parser.add_argument("--release", choices=("v1.0",), default="v1.0")
    fetch_parser.add_argument("--output-dir", type=Path, default=Path("data/raw/male-cns/v1.0"))
    fetch_parser.add_argument("--manifest", type=Path, default=Path("data/provenance/male-cns-v1.0.json"))
    verify_parser = data_subparsers.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--root", type=Path, default=Path("data/raw/male-cns/v1.0"))
    feather_parser = data_subparsers.add_parser("inspect-feather")
    feather_parser.add_argument("--path", type=Path, required=True)
    feather_parser.add_argument("--sample-rows", type=int, default=5)
    return parser


def _load(args: argparse.Namespace):
    neurons = NeuronColumns(
        neuron_id=args.neuron_id_column,
        cell_type=args.cell_type_column,
        neurotransmitter=args.neurotransmitter_column,
        ascending=args.ascending_column,
        descending=args.descending_column,
        sensory=args.sensory_column,
        motor_related=args.motor_related_column,
    )
    edges = EdgeColumns(args.source_column, args.target_column, args.synapse_column)
    return load_connectome(args.neurons, args.edges, neuron_columns=neurons, edge_columns=edges)


def _summary_dict(summary) -> dict[str, int | float | None]:
    return {
        "neuron_count": summary.neuron_count,
        "edge_count": summary.edge_count,
        "total_synapses": summary.total_synapses,
        "min_synapses": summary.min_synapses,
        "max_synapses": summary.max_synapses,
        "mean_out_degree": summary.mean_out_degree,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "data":
        if args.data_command == "fetch":
            provenance = fetch_and_write_manifest(args.output_dir, args.manifest)
            print(json.dumps({"files": [asdict(file) for file in provenance.files]}, indent=2))
            return 0
        if args.data_command == "inspect-feather":
            inspection = inspect_feather(args.path, sample_rows=args.sample_rows)
            print(json.dumps(asdict(inspection), indent=2, default=str))
            return 0
        provenance = read_manifest(args.manifest)
        root = args.root or args.manifest.parent
        results = [verify_file(root / file.local_filename, file) for file in provenance.files]
        print(json.dumps(results, indent=2))
        return 0 if all(result["valid"] for result in results) else 1
    connectome = _load(args)
    if args.command == "benchmark":
        print(json.dumps(benchmark_connectome(connectome, min_synapses=args.min_synapses).as_dict(), indent=2))
        return 0
    full = SparseDirectedGraph.from_connectome(connectome)
    filtered = SparseDirectedGraph.from_connectome(connectome, min_synapses=args.min_synapses)
    result = {
        "neuron_count": len(connectome.neurons),
        "edge_count": full.summary.edge_count,
        "filtered_edge_count": filtered.summary.edge_count,
        "min_synapses": args.min_synapses,
        "full_graph_summary": _summary_dict(full.summary),
        "filtered_graph_summary": _summary_dict(filtered.summary),
        "full_sparse_storage_bytes_measured": full.sparse_storage_bytes,
        "filtered_sparse_storage_bytes_measured": filtered.sparse_storage_bytes,
    }
    print(json.dumps(result, indent=2))
    return 0
