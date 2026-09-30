# Task 018B — MN9 Anatomical-Asymmetry Scientific Closure

Date: 2026-09-30. Decision: **A — V0.3 SCIENTIFIC SCOPE COMPLETE — RELEASE PREPARATION**.

## Starting checkpoint and frozen identities

Local `HEAD`, `origin/master`, and live GitHub `master` were all `2ba3ca303fb08a5f8bcdc6095f69f9c3761ce785`. The worktree was clean and the stash empty. Task 018 preregistration commit: `abb7cc8d385c6a1daa9e9bb87f7488ab5685783b`; exact document SHA-256: `4f767ab2bfcbf5e5773a803ee6fdb601e39d5521d7f30a12d35a3a5506de5bb4`. Task 018A execution commit: `2ba3ca303fb08a5f8bcdc6095f69f9c3761ce785`.

Dataset: MaleCNS v1.0; manifest SHA-256 `e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631`. The side-resolved identities are `MN9_L=10331` and `MN9_R=16949`. The existing ignored `data/derived/task018-results.json` has byte SHA-256 `b112712fc747c41332ebd5772c4ba24839f1c2f771e04533e34fdc24ca490e89`; its stored and independently recomputed canonical result digest both equal `270c931a2420df475ff54ea185e7e7d03da1a868af8a35f7f68e38ebbf98f9f4`. It was read, not regenerated.

## Closed confirmatory result

The preregistered **primary** result on the full frozen curated graph is **`SHARED_PARTNER_DIFFERENCE_LARGEST`**. Incoming synapse-count weight is `W_L=6012`, `W_R=556`, and `W_L-W_R=5456`. The signed partition is shared-partner difference `+4281`, LEFT-only input `+1315`, and RIGHT-only input `-140`. Exact verification: `4281 + 1315 - 140 = 5456`. Partner counts are LEFT `278`, RIGHT `137`, shared `65`, LEFT-only `213`, and RIGHT-only `72`.

The separately preregistered `min_synapses=5` **sensitivity** result is `LEFT_ONLY_INPUT_LARGEST`: `W_L=5699`, `W_R=386`, gap `5313`; shared `+2032`, LEFT-only `+3322`, RIGHT-only `-41`. Exact verification: `2032 + 3322 - 41 = 5313`. Partner counts are LEFT `93`, RIGHT `27`, shared `22`, LEFT-only `71`, and RIGHT-only `5`.

The largest-component label changes under the preregistered removal of low-count connectivity. This is relevant to interpretation of the component accounting at these two specified graph definitions. The sensitivity label does not replace, average with, vote against, or retroactively weaken the formal primary classification. No other threshold or decomposition was examined here.

This establishes an anatomical/connectomic decomposition in the frozen MaleCNS representation only. It establishes no biological causality; functional, behavioral, or physiological asymmetry; developmental mechanism; direct inhibition; network redistribution; biological explanation for the LEFT/RIGHT difference; or generality beyond this connectome representation. It is not joined with Task 017 dynamics into a stronger biological mechanism claim. Task 017 remains **`NOT_ROBUST`** under its frozen criteria; Task 018A neither rescues nor reverses it.

## Post-018A exploratory quarantine

The following became visible from Task 018A results and are post-result observations: shared-partner difference is the largest primary component; LEFT-only input is the largest threshold-5 component; the largest-component label changes between the two preregistered graphs; the primary graph has `65` shared, `213` LEFT-only, and `72` RIGHT-only partners; and the label change may suggest a role for low-count edges. The last suggestion is not a measured edge-level conclusion. None automatically becomes a confirmatory hypothesis. Any investigation requires a new prospective preregistration; Task 018B performs none.

## Audit of questions recorded before Task 018A

Task 015, committed before Task 017 and Task 018 outcomes, records four directions. The earlier research checkpoint also asks about anatomical origin, recurrent motifs, external observations, and model robustness. Task 017N independently assessed the roadmap before Task 018A and selected the anatomical question for Task 018 design. The Task 018 preregistration narrowed that question to the exact shared/unique presynaptic partition; Task 018A answered that registered question. The broader causal or annotation-based meaning of anatomical origin was not registered as an additional endpoint.

| Candidate question | Provenance | Current assessment |
| --- | --- | --- |
| Robustness of Task 010/011 model effects and compatibility labels | PRE-018A INDEPENDENT; ALREADY ANSWERED | Task 016/017 closed it as `NOT_ROBUST`; no immediate repeat is justified. |
| Anatomical organization of the MN9 incoming-weight gap | PRE-018A INDEPENDENT; ALREADY ANSWERED within the registered Task 018 partition | Task 018A completed the bounded descriptive question. Task 015's other possible annotations and decompositions were examples, not independent registered endpoints. |
| Reproducible network redistribution motifs in Task 011 traces | PRE-018A INDEPENDENT; INSUFFICIENTLY DEFINED | Scientifically motivated and distinct, with graph/traces in principle available, but Task 015 explicitly deferred it pending an independently fixed motif ontology, null model, windows, and replication rule. It does not warrant immediate preregistration from current evidence. |
| Comparison with independent anatomy, electrophysiology, or behavior | PRE-018A INDEPENDENT; INSUFFICIENTLY DEFINED | Distinct and potentially valuable, but no selected independent dataset, valid mapping, or comparison protocol is established. Behavioral comparison also lacks a behavioral model. It does not warrant immediate preregistration from current evidence. |
| Shared-versus-LEFT-only dominance, label change, partner-count pattern, or low-count-edge explanation | POST-018A DERIVED | Quarantined as exploratory observations, not pre-existing independent questions. |

The Task 017M candidate/variant patterns are likewise post-Task-017 exploratory observations, not a reason to restart Task 016 or to reinterpret Task 018. Task 017Q remains **DEFERRED** as a portability matter, not an open scientific endpoint.

## Decision and authorization boundary

**Decision A.** Task 016/017 and Task 018/018A are scientifically closed. The two independently documented remaining directions are insufficiently specified for immediate prospective preregistration, and follow-up on Task 018A's new patterns would be result-driven. Freeze current v0.3 science. The recommended next task is **v0.3 release preparation**, with its own authorization and release gate. This decision starts no release task, tag, publication, simulation, scoring, Task 017Q work, or additional scientific analysis. Scientific executions during Task 018B: **0**; Task 017 and Task 018A were not rerun; no result artifact was generated.

## Sealed-state integrity and validation

The read-only Task 017 checkpoint audit passed before and after these documentation edits. Each audit reported `3168` completed, `0` pending, and R0 plus V1–V7 each `396/396`. The before/after checkpoint fingerprint was `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`; complete-matrix digest `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028`; journal SHA-256 `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e`; and sidecar inventory SHA-256 `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553`.

Task 016 fingerprint remained `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`. `artifacts/task017/robustness-scoring.json` remained byte-identical at SHA-256 `06aa2febc33ae294bbd8ef3d302f5caea52ab3a8d96945944b5abfb175240142`. The Task 018 preregistration and ignored result artifact retained the SHA-256 identities above; the artifact canonical digest was recomputed without execution. `uv run pytest`: 255 passed, 1 established opt-in skip. `uv run python -m compileall src scripts tests`: passed. `git diff --check`: passed. No tag or release was made.
