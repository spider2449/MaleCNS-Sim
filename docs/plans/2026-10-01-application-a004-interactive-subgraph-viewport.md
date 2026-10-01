# Application A004: interactive subgraph viewport

Status: **A4-INTERACTIVE-VIEWPORT-CERTIFIED**. Starting HEAD: `a87f122e28202451f2967108528452d1cc5d2620`. User manual visual acceptance of this exact A004/A004R worktree: **PASS**.

## Source and contract

`SubgraphView` schema `application-subgraph-view-v1` derives only from the `EffectiveSignedProjection` prepared for the selected A002 run. It uses the same neuron indices, resolved directed edges, effective signed weights, and prepared graph fingerprint as simulation. Anatomical synapse counts are recovered from absolute effective weight divided by the reference anatomical synapse factor. The source does not expose neuron type/class or side, so those fields are marked unavailable in the inspector. It does not use unfiltered registered anatomical edges that the simulator excluded.

The response contains dataset manifest identity, prepared graph fingerprint, A002 run ID, spec digest, filter definition and SHA-256 identity, truncation counts, nodes, edges, source label, schematic warning, extraction seconds, and serialized byte estimate. Nodes contain body ID, label, role list, and activity availability. Edges contain source, target, anatomical weight, and effective sign. No browser-generated topology exists.

Display filters are direct outgoing neighbors of all frozen stimulus anchors, direct incoming neighbors of the target anchor, or their union. Combined context is a union for display; shared displayed context does not claim a bridge or pathway. Candidate neighbors rank by descending absolute effective weight, then ascending body ID. The rendered graph includes all relevant anchors and at most 80 or 160 nodes. Induced edges among rendered nodes rank by descending absolute effective weight, then ascending source and target body IDs; at most 1,200 edges render. Both node and edge truncation counts are visible. The GET route `/api/runs/{job}/subgraph?mode={stimulus|target|combined}&cap={80|160}` rejects every other parameter shape or unbounded cap and uses the existing local session protection. A failed run yields a failure state; preparation yields a graph pending state.

## Rendering and interpretation

Canvas 2D renders a deterministic schematic layout: stimulus nodes on a left radial group, target on the right, context in center rings. Coordinates are presentation only and are not CNS morphology. Pan, wheel zoom, Zoom In, Zoom Out, Fit, and pointer selection operate locally without re-running the model. A bounded keyboard-accessible node list and search expose every displayed node. The inspector reports identity, roles, displayed degree and anatomical weight sums, and activity only when recorded by A002. Target count and firing rate come from A002; an unrecorded node explicitly says activity was not recorded. The result strip says model simulation result. Active job, A002 run ID, spec digest, dataset, graph fingerprint, and filter identity are exposed. Switching jobs clears the prior graph before loading the new one, and API result/graph identities are checked.

No new biological verdict, pathway finding, candidate ranking, intervention screen, robustness run, Task017 execution, Task017Q execution, BANC work, motif work, raw-data download, or archive write is authorized. Historical scientific artifacts remain unchanged. Task017 `NOT_ROBUST` and Task017Q `Q1 / KEEP_DEFERRED` remain intact. A005 remains responsible for activity playback, if separately authorized.

## A004 viewport certification measurement

One registered-data CPU graph preparation, with no simulation trial, produced prepared fingerprint `ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`, 166,700 nodes, and 24,904,953 resolved edges in 286.373 s. This is the graph fingerprint of the successful A003R result. The six display views were generated from this prepared projection:

| View | Cap | Rendered nodes | Candidate nodes | Rendered edges | Induced edges before edge cap | Extraction seconds | JSON bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Stimulus | 80 | 80 | 460 | 1,200 | 2,042 | 0.707211 | 98,924 |
| Stimulus | 160 | 160 | 460 | 1,200 | 5,132 | 0.756798 | 108,039 |
| Target | 80 | 80 | 126 | 1,200 | 2,110 | 0.591120 | 97,982 |
| Target | 160 | 126 | 126 | 1,200 | 4,407 | 0.580536 | 103,958 |
| Combined | 80 | 80 | 582 | 1,200 | 1,861 | 0.790483 | 98,874 |
| Combined | 160 | 160 | 582 | 1,200 | 4,876 | 0.814503 | 108,211 |

These are measurements from one Windows machine, not a general benchmark. API payloads use the same canonical compact JSON representation; actual HTTP response sizes were not separately measured. Browser layout and render times remain unmeasured. Automated tests exercise deterministic selection, identity, bounded caps, roles, truncation, and activity availability on a synthetic prepared projection. No new scientific baseline run was used. No browser surface was available to Codex. The user manually reviewed the corrected viewport, including clipping, responsiveness, and pan/zoom/selection, and accepted this exact worktree: **PASS**.

## A004R long-identity overflow correction

The user's A004 manual review reported that all visual and interaction checks passed except one presentation issue. The screenshot showed the 64-character dataset manifest SHA-256 escaping the left Experiment setup column into the center panel, below the dataset name, AVAILABLE status, and manifest label.

The dataset, run inspector, result, filter label, and event timeline containers now share the `identity-value` class with `min-width:0`, `overflow-wrap:anywhere`, and `word-break:break-word`. This preserves the full text while allowing long unbroken values to wrap. The main grid children explicitly use `min-width:0`; the single-column breakpoint is 899 px, above the three-column grid's 870 px minimum. Existing right-side identities retain preformatted line breaks. No graph extraction, simulation, run identity, filtering, scientific result, viewport graph data, or Application Layer contract changed. Real MaleCNS runs for A004R: **0**; the prior A004 certification run remains valid.

A lightweight static regression verifies the shared class on identity-bearing containers, its CSS declarations, grid-child shrink rule, and the breakpoint. The user manually rechecked the corrected layout and confirmed **PASS** for this exact A004/A004R worktree. Final classification: **A4-INTERACTIVE-VIEWPORT-CERTIFIED**. No new scientific execution was performed for A004R; real MaleCNS runs: **0**. The original overflow defect record above is retained.
