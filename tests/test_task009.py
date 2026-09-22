import ast
from pathlib import Path

import numpy as np

from malecns_sim.analysis.task009 import (
    MN9_L,
    MN9_R,
    NodeMetadata,
    StructuralGraph,
    analyze_graph,
    classify_dimorphism,
    first_hop_partition_records,
    freeze_candidate_list,
    identify_homolog_pairs,
    incoming_neighborhood,
    rank_intermediates,
    source_normalization,
    two_hop_route,
)


def _graph(edges, *, threshold=0):
    source = np.asarray([row[0] for row in edges], dtype=np.int64)
    target = np.asarray([row[1] for row in edges], dtype=np.int64)
    weight = np.asarray([row[2] for row in edges], dtype=np.int64)
    signs = np.asarray([row[3] for row in edges], dtype=np.int8)
    return StructuralGraph(
        neuron_ids=np.asarray([1, 2, 3, 4, 5, 6, 7, 10331, 16949], dtype=np.int64),
        source_ids=source,
        target_ids=target,
        anatomical_weights=weight,
        edge_signs=signs,
        threshold=threshold,
        unsigned_fingerprint="unsigned-test",
        signed_fingerprint="signed-test",
    )


def _fixture():
    graph = _graph(
        (
            (1, 5, 2, 1),
            (2, 5, 3, 1),
            (3, 5, 4, -1),
            (4, 6, 4, 1),
            (1, 7, 1, 1),
            (5, 10331, 5, 1),
            (5, 16949, 2, -1),
            (6, 10331, 6, -1),
            (6, 16949, 3, 1),
            (7, 10331, 7, 2),
        )
    )
    metadata = {
        str(index): NodeMetadata(
            body_id=str(index),
            type=f"T{index}",
            instance=f"T{index}_L" if index in {5, 10331} else None,
            side="L" if index in {1, 2, 5, 7, 10331} else "R",
            superclass="cb_intermediate",
            cell_class="interneuron",
            neurotransmitter="acetylcholine" if index in {1, 2, 4, 5, 6, 16949} else "gaba",
            dimorphism=None,
        )
        for index in (1, 2, 3, 4, 5, 6, 7, 10331, 16949)
    }
    return graph, metadata


def test_incoming_neighborhood_decomposition_preserves_unsigned_and_signed_views():
    graph, metadata = _fixture()
    result = incoming_neighborhood(graph, MN9_L, metadata)
    assert result.total_presynaptic_neuron_count == 3
    assert result.total_input_edge_count == 3
    assert result.total_anatomical_weight == 18
    assert result.excitatory_presynaptic_count == 1
    assert result.inhibitory_presynaptic_count == 1
    assert result.unresolved_presynaptic_count == 1
    assert result.excitatory_anatomical_weight == 5
    assert result.inhibitory_anatomical_weight == 6
    assert result.unresolved_anatomical_weight == 7
    assert dict(result.normalized_fractions)["unresolved_weight"] == 7 / 18


def test_first_hop_partition_reports_shared_and_side_only_weights():
    graph, _ = _fixture()
    records = first_hop_partition_records(graph, (1, 2), (3, 4))
    by_key = {(item.side, item.target_category): item for item in records}
    assert by_key["L", "shared"].target_count == 1
    assert by_key["L", "shared"].resolved_target_count == 1
    assert by_key["L", "shared"].anatomical_weight == 5
    assert by_key["R", "shared"].anatomical_weight == 4
    assert by_key["L", "left_only"].target_count == 1
    assert by_key["L", "left_only"].anatomical_weight == 1
    assert by_key["R", "right_only"].target_count == 1
    assert by_key["R", "right_only"].anatomical_weight == 4


def test_two_hop_aggregation_and_all_structural_proxies():
    graph, metadata = _fixture()
    route = two_hop_route(graph, (1, 2), MN9_L, source_side="L", metadata=metadata)
    assert route.intermediate_count == 2
    assert route.path_count == 3
    assert route.resolved_path_count == 2
    assert route.unresolved_path_count == 1
    assert route.positive_path_count == 2
    assert route.negative_path_count == 0
    assert route.ee_path_count == 2
    assert route.ei_path_count == 0
    assert route.ie_path_count == 0
    assert route.ii_path_count == 0
    assert route.bottleneck_proxy == 2 + 3 + 1
    assert route.multiplicative_anatomical_proxy == 2 * 5 + 3 * 5 + 1 * 7
    assert route.signed_multiplicative_proxy == 25
    assert source_normalization(route)[0][0] == "per_sugar_neuron:bottleneck_proxy"


def test_path_sign_classification_and_signed_route_to_mn9_r():
    graph, metadata = _fixture()
    route = two_hop_route(graph, (1, 2), MN9_R, source_side="L", metadata=metadata)
    assert route.path_count == 2
    assert route.positive_path_count == 0
    assert route.negative_path_count == 2
    assert route.ei_path_count == 2
    assert route.signed_multiplicative_proxy == -10


def test_deterministic_ranking_uses_body_id_tie_breaker():
    graph, metadata = _fixture()
    route = two_hop_route(graph, (1, 2), MN9_L, source_side="L", metadata=metadata)
    assert tuple(item.intermediate_id for item in rank_intermediates(route, "bottleneck_proxy")) == ("5", "7")
    assert tuple(item.intermediate_id for item in rank_intermediates(route, "signed_multiplicative_proxy")) == ("5", "7")


def test_homolog_pairs_require_explicit_unique_instance_suffixes():
    metadata = {
        "1": NodeMetadata("1", type="A", instance="A_L", superclass="x", cell_class="y"),
        "2": NodeMetadata("2", type="A", instance="A_R", superclass="x", cell_class="y"),
        "3": NodeMetadata("3", type="A", instance="B_L", superclass="x", cell_class="y"),
        "4": NodeMetadata("4", type="A", instance="B_R", superclass="x", cell_class="z"),
    }
    assert identify_homolog_pairs(metadata) == (("1", "2", "A", "A"),)


def test_threshold_sensitivity_and_candidate_list_freezing_are_structural():
    graph, metadata = _fixture()
    routes = tuple(
        two_hop_route(graph, sugar, target, source_side=side, metadata=metadata)
        for side, sugar in (("L", (1, 2)), ("R", (3, 4)))
        for target in (MN9_L, MN9_R)
    )
    candidates = freeze_candidate_list(routes, support_limit=1, inhibition_limit=1)
    assert candidates
    assert all(item.body_id.isdigit() for item in candidates)
    analysis = analyze_graph(graph, metadata, (1, 2), (3, 4))
    assert analysis["threshold"] == 0
    threshold_edges = [edge for edge in zip(graph.source_ids, graph.target_ids, graph.anatomical_weights, graph.edge_signs) if edge[2] >= 5]
    threshold = _graph(tuple(tuple(int(value) for value in edge) for edge in threshold_edges), threshold=5)
    threshold_analysis = analyze_graph(threshold, metadata, (1, 2), (3, 4))
    assert threshold_analysis["threshold"] == 5
    assert threshold_analysis["routes"][0].path_count < analysis["routes"][0].path_count


def test_dimorphism_classification_is_explicit_and_conservative():
    assert classify_dimorphism("isomorphic") == "isomorphic"
    assert classify_dimorphism("dimorphic") == "dimorphic"
    assert classify_dimorphism("male-specific") == "male-specific"
    assert classify_dimorphism(None) == "unresolved"


def test_task009_source_has_no_dynamics_import():
    path = Path("src/malecns_sim/analysis/task009.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any("dynamics" in name for name in imported)


def test_candidate_list_is_frozen_from_route_values_not_simulation_results():
    graph, metadata = _fixture()
    routes = (two_hop_route(graph, (1, 2), MN9_L, source_side="L", metadata=metadata),)
    first = freeze_candidate_list(routes)
    second = freeze_candidate_list(routes)
    assert first == second
