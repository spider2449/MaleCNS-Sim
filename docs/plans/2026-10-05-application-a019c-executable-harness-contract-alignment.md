# A019C executable harness contract alignment

Authorization: `授權 A019C`, bounded executable alignment and synthetic certification only.
Starting local/origin/live SHA: `60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Clean worktree, empty stash, version 0.3.0, zero tracked active workflows verified.

Prior gates: A18UJ-A / R-A; A018UR-IDENTITY-ADJUDICATED-CERTIFIED; A19A-A / C1.
A019B remains A19B-BENCHMARK-CONTRACT-MISMATCH with zero real attempts.
Historical A013 correctly uses its production-default preparation contract.
Forward A019 requires the subsequently certified bounded architecture. A013 is
not modified. No production default or scientific semantics will change.

Implementation plan:
1. Add a distinct A019 harness loading A019A and preparation-identity-v1 metadata.
2. Reuse A018UR scoped bounded route and corrected G1-G6 helpers before runtime.
3. Reuse historical timing/replay sequence helper without calling its real worker.
4. Certify small Feather fixtures, full 24-call structure, lifetime, failure gates,
   frozen schedule, contained-tree watchdog, resource limits and no retry.
5. Run requested synthetic regressions and repository validation, document results,
   commit and push only after successful certification. No A019D execution.

## STOP disposition

**Task classification: A19C-F — REAL-DATA FIREWALL VIOLATED.**
Primary stop: `A019C-REAL-DATA-FIREWALL-VIOLATION`.

The synthetic harness itself completed its 44-neuron, 1248-edge bounded fixture:
35 final targeted A019C tests passed in 6.89 s. Persisted synthetic worker evidence
records one preparation/network/runtime, two fresh states, 24 calls, twelve
consecutive calls/state, 240 ms/state, exact state/pending/output replay, one
948-event schedule and zero real accesses within that worker. Those worker-only
zeros MUST NOT be read as task-wide firewall evidence.

The requested full pytest was launched without a task-wide real-source read
guard. Existing `tests/test_application_a003.py` local-catalog tests use the
available registered dataset: `DatasetCatalog.local()` -> `catalog.spec()` ->
`catalog.populations()` -> `ProductionEngine.identities()` ->
`load_task008_identities(annotation, neurotransmitter)`. The full run passed
these tests, hence real annotation/neurotransmitter access occurred. This was
outside A019C authorization. Exact read count was not instrumented and cannot
be claimed to be zero. The full suite was terminated on discovery (partial
progress reached 16%; no completed full-suite result). No real edge preparation,
real runtime construction or real advance was invoked. No real benchmark attempt
was consumed. No GPU, Arena, download, experiment or archive operation was invoked.

Earlier expanded targeted run: 891 passed, 1 failed, one expected Feather V1
warning, 139.25 s. Failure exposed a configurable completed-call deadline gap;
the final harness checks advance -> verification transition outside timers.
The final 35-test A019C suite passes, including deadline regression, actual Job
Object forced preparation/advance/worker timeouts, aggregate child memory stop,
instrumentation stop, no retry and empty contained-tree cleanup. The earlier
combined run is not a passing final validation result. Full pytest, compileall,
tracked integrity, diff check and build certification remain incomplete. No
commit or push is permitted for this stopped task; changes remain uncommitted.

Harness: `scripts/benchmark_application_a019.py`.
Synthetic entrypoint:
`uv run python scripts/benchmark_application_a019.py --synthetic --output <new-path.json>`.
The CLI exposes only generated synthetic sources. Future real execution requires
separate authorization, canonical identity, contained-watchdog proof and available
memory preflight in `run_forward`; no real CLI was added. The forward API uses
`with bounded_route(metrics, route_event)` around exactly one production-engine
preparation, with batch rows 65536 and fixed merge block 16384. Both negative-endpoint
and overflow fallbacks raise PREPARATION_FALLBACK before runtime. G1-G6 use the
unchanged layer-explicit helper and the canonical tracked identity record; the
synthetic record was independently generated through reference preparation.
Cross-layer effective/prepared digest substitutions are rejected.

The sequence helper is reused from historical A013 without modification, preserving
its timing brackets and complete compact replay fields. A wrapper checks canonical
initial state, weak-reference array release before B, one runtime and two states.
No reset, recreation or state derivation; all schedule windows are frozen once.
Schedule fingerprint:
`6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.
Synthetic aggregate replay fingerprint:
`a9f5af0c2ea0b8d1932f932bfea68b8fe8fbfa2c7424bf56f4ca39456b229ec1`.

Timing: slicing outside timers; packing inside encode/total; output assembly inside
advance; readout inside total; heavyweight digests/checks outside timers; warmups
recorded individually and excluded from distributions. Limits: preparation 600 s,
advance 30 s, worker 1500 s, private and working-set caps each 8589934592 bytes.
Watchdog uses unchanged corrected A014 suspended-launch Windows Job Object, tree
sampling and verified empty inventory on close. Sampling cannot catch every
between-sample transient peak. One launch, no automatic retry, no evidence overwrite.
Real attempt boundary is the bounded edge-batch source-access notification.
Schema: `application-stateful-benchmark-evidence-v1`; P1/P2 null for synthetic runs.

Production source, production default, scientific model/configuration/graph/sign/
weight/threshold/dt/delay/stimulus semantics, historical A013, A019B stop, Task016,
Task017 and archives were not modified. Task017 remains NOT_ROBUST. No tag, release
or version bump. Version remains 0.3.0; zero tracked workflows.

Exact next task: **A019C-R — Validation Source-Access Firewall Correction**.
Bounded objective: install and verify a task-wide guard for registered real source
reads, route metadata regressions to synthetic fixtures or explicit guarded skips,
then rerun synthetic certification and requested validation. No real execution.
A019D is not recommended from this failed task.

## A019C-R / A019C-R2 chronology

Historical A019C-R disposition: **A19C-R-D — REAL-DATA FIREWALL VIOLATED AGAIN**.
Content searches of data/provenance/male-cns-v1.0.json and
data/provenance/task007-mapping-summary.json preceded guard installation.
This historical stop remains unchanged and is not PASS.

Authorized A019C-R2 installed an opt-in validation bootstrap before tests or
prohibited-content probes. Its final targeted bootstrap result was 10 passed,
1 failed: the native FeatherReader coverage probe used an invalid constructor
signature and did not establish rejection before content read. Required stop:
`A19C-R2-FIREWALL-BOOTSTRAP-FAILED`; classification **A19C-R2-C — FIREWALL
COVERAGE INCOMPLETE**. No broader validation, harness execution, commit or push.
No superseding certification; A019D remains unconsumed and not recommended.
See 2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md for accounting,
preserved WIP, exclusions and the final checklist. A19C-F also remains unchanged.
