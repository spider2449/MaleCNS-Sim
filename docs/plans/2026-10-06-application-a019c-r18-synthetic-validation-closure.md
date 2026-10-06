# A019C-R18 synthetic validation closure batch

Authorization: consecutive bounded S0/S1 closure and conditional commit/push. Starting local/origin/live master: `60c900b0c8e5a02ea95efc7340fd190193edf7e9`. Initial inventory: 43 scoped paths (the R17 final inventory), staging/stash empty, version 0.3.0, tracked workflows 0. Preserve R2-R17 WIP and all historical STOP records.

Plan: inventory; reproduce A002 alone; establish historical semantics; prefer fixture-only corrections; run targeted/local/application and remaining admitted S0/S1 manifest; bootstrap; forward harness; fresh contained CLI; affected stateful/reference controls; guarded compileall; diff review/check; conditional coherent commit/push and identity verification. Hard stops and S2/N exclusions follow the user contract.

A002 `test_optional_git_provenance`: reproduced 1 FAIL. Git exists at `C:/Program Files/Git/cmd/git.exe`. Production first attempts bare `git rev-parse --show-toplevel` from service source parent; guard rejects executable before process creation. Production catches OSError and returns both values None. Later operations are `rev-parse HEAD` and `status --porcelain` from verified repository root. Environment sanitization does not cause the first rejection; repository detection is not reached. Historical test checks available commit and missing-Git fallback. Classification: fixture integration, not established production regression.

Correction: guarded-context-only exact metadata fixture checks all three argv/cwd/options, actual source/repository samefile detection, commit parsing and dirty parsing; missing-Git fallback retained. Unguarded branch unchanged. Production code changed: no. Admission changed: no. Git status/diff/arbitrary Git/shell remain rejected. No outside-guard production Git invocation executed because it includes status. Local A002: 19 PASS. No child spawned by provenance fixture; no process cleanup needed. Registered accepted reads zero under fail-closed accounting, not independent native byte telemetry.

J2/I2/B2 and all S2 remain NOT RUN. Full-real preparations/real advances 0; A019D attempt consumed No.

## Second blocker and correction

`tests/test_application_a018ui.py::test_historical_current_components_exact[False-mixed]`: remaining selection reached 791 PASS, 1 FAIL, stopping at guarded rejection of `git show f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e:src/malecns_sim/dynamics/lif.py`. Historical semantic: an independent old projection/serializer/preparation oracle and byte comparison of unchanged scientific source. Classification: validation helper source-transport integration. Production code changed: no. Admission changed: no.

Smallest correction preserving the independent oracle: fixed fixture of the seven exact historical code blobs already named by this test, copied byte-for-byte from the two pinned revisions. Retrieval used resolved Git, exact repository cwd, and those literal source-code object names only; no data object, arbitrary revision/pathspec, diff, shell-wrapped Git, or child admission. The fixture records SHA256; the test pins and checks every expected hash and the exact key set. The original unguarded Git route remains. Files changed: `tests/test_application_a018ui.py`, `tests/fixtures/application-a019c-historical-code.json`, and R18 negative controls.

Single reproduced node after correction: 1 PASS. A018UI local subset: 11 PASS. Remaining tail: 40 PASS, including Node controls and three R18 controls. Unknown historical path, alternate revision, altered source bytes, arbitrary Git/status/diff/cat-file and shell/wrong-cwd execution are rejected. An observational control confirms production provenance attempted exactly the first command, then correctly returned optional None values after guard rejection. No executable/admission change; no production regression established. Historical source collection exited normally with streams/process handles released; guarded helper spawns no Git child. Final scoped process scan found no task child/orphan.

## Final validation

| Gate | Current R18 result |
|---|---|
| Application A008 through A002 selection | 134 PASS |
| All admitted application cases, across closure selections | 958 distinct PASS, no unresolved failure |
| A013 / A014 admitted controls | 17 PASS / 12 application + 7 direct-admission controls PASS |
| Complete bootstrap, final recertification | 39 PASS |
| A019C forward harness, final recertification | 35 PASS |
| Fresh contained synthetic CLI, final recertification | exit 0, A19C-A |
| Stateful/A011/reference-LIF | 27 PASS; no Arena cases |
| R18 targeted negative controls | 3 PASS within the 40-PASS tail |
| `uv run python -m compileall src scripts tests` | PASS, exit 0 |
| `git diff --check` | PASS |

The two original failures remain recorded as reproductions; final outcomes use corrected targeted/local/tail evidence. The remaining broad synthetic selection's 791 PASS is combined with its corrected tail, rather than falsely reporting that stopped invocation as green. Parameterized case identities are deduplicated. Every R17 required S0/S1 function is covered by current passing JUnit evidence. No unfiltered full pytest, J2 data diff, default integrity checker, or build was run.

Final per-node manifest: `2026-10-06-application-a019c-r18-validation-manifest.json`: S0 215 functions PASS; S1 20 functions PASS (includes R12/R18 controls); S2 5 functions NOT RUN; N 5 Arena functions NOT RUN. Tooling S1: bootstrap/CLI/compileall/diff/metadata review PASS; B2 remains explicitly NOT RUN under its frozen disposition. I2/J2 and full pytest remain NOT RUN. Full-real/GPU/Arena/scientific experiment/download/archive/tag/release/version actions N NOT EXECUTED. Conditional commit/push authorized only on this success. Historical R2-R17 adjudications and STOP records unchanged.

## Accounting and forward contract

All seven counters are 0: `accepted_real_connectivity_reads`, `accepted_real_annotation_reads`, `accepted_real_neurotransmitter_reads`, `accepted_real_metadata_reads`, `accepted_real_provenance_reads`, `accepted_real_mapping_reads`, `accepted_other_registered_reads`. This is fail-closed guarded execution/source-access accounting, **not independent native byte telemetry**. Exact historical source-code Git reads are not registered scientific payload reads. Deliberate registered probes were rejected before content reads; no accepted registered read observed.

Final fresh evidence: `2026-10-06-application-a019c-r18-synthetic-evidence.json`. Bounded A015/A016/A017/A018/A018T/A018U/A018UJ route PASS; batch 65,536, merge block 16,384; production default unchanged; fallback hard stop PASS. G1-G6 and L3/L4 wrong-layer rejection PASS. One PreparedNetwork, one PreparedRuntime, two SimulationStates; A and B each fresh, 2 warmup + 10 measured advances at 20 ms, final 240 ms. Total 24 calls; maximum consecutive 12; no continuous 480-ms trajectory or runtime recreation/reset. A released before B; no coexistence; exact state/pending/output replay PASS.

LEFT sugar 42, 100 Hz; RIGHT 0; seed 1555062870; impulse 68.75 mV; horizon 240 ms; 948 events. Fingerprint `6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`. Preparation/advance/worker limits 600/30/1500 s; private and working-set caps each 8,589,934,592 bytes. Timeout/memory/containment/cleanup/no-orphan/no-retry controls PASS. Final CLI one launch, orphan list empty, cleanup released. Production scientific/model semantics unchanged.

Full-real preparations 0; real advances 0; A019D attempt consumed **No**.

**A19C-R18-A — SYNTHETIC VALIDATION CLOSURE COMPLETE; A019C FORWARD HARNESS SYNTHETICALLY CERTIFIED.**

`A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED`

## Publication gate

Full accumulated source/test/fixture/document scope reviewed: 50 A019C paths; no unrelated WIP. Initial 43-path inventory is preserved by the R17 record; R18 adds its report, evidence, manifest, historical code fixture and controls and changes only A002/A018UI test behavior. Staging exposed extra EOF blank lines in R15/R16 documents; those blank lines alone were removed, preserving historical record content. Staged and working diff checks then PASS. Commit message: `test: certify stateful benchmark synthetic harness`. No tag, release or version bump. Exact commit/push and final local/origin/live identity are verified and reported in the delivery response after publication; package 0.3.0, workflows 0, empty stash required.

Exact next task, only after successful commit/push: **A019D — Full-Real Stateful Advance Benchmark Execution**. Not executed by R18.
