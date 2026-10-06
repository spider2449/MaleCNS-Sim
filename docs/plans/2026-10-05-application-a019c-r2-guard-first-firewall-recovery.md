# A019C-R2 guard-first firewall recovery

Authorization: `授權 A019C-R2`, exactly one bounded recovery task.

Verdict: STOP. **A19C-R2-C — FIREWALL COVERAGE INCOMPLETE**.
Stop identifier: `A19C-R2-FIREWALL-BOOTSTRAP-FAILED`.
No superseding forward-harness certification is issued. A019D is not recommended
and its real attempt remains unconsumed. No commit or push was made.

## Starting identity and preservation

Root was derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`.
Starting local HEAD, origin/master and live GitHub master:
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Version 0.3.0; empty stash; zero tracked workflow filenames.
Exactly six untracked WIP files were present, with no unrelated WIP:

1. `docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md`
2. `docs/plans/2026-10-05-application-a019c-harness-contract.json`
3. `docs/plans/2026-10-05-application-a019c-synthetic-evidence.json`
4. `scripts/benchmark_application_a019.py`
5. `tests/fixtures/application-a019c-preparation-identity.json`
6. `tests/test_application_a019c.py`

All six remain preserved. Only the plan chronology and machine-readable evidence
receive additive R2 stop records. Harness, contract, identity fixture and original
tests are not rebuilt or modified. No reset, clean, restore, checkout or stash.

Historical **A19C-F — REAL-DATA FIREWALL VIOLATED** remains a stop.
Historical **A19C-R-D — REAL-DATA FIREWALL VIOLATED AGAIN** remains a stop:
the earlier recovery searched the contents of
`data/provenance/male-cns-v1.0.json` and
`data/provenance/task007-mapping-summary.json` before installing a guard.
Neither historical disposition is rewritten as PASS.

## Bootstrap and activation boundary

Before bootstrap, operations were Git metadata, package metadata, source-code
inspection under src/scripts/tests, and permitted WIP plan/evidence inspection.
No data payload was opened or searched. Loader implementation is source code;
invoking a loader on registered payloads is a different operation and was not done.

New validation-only files:
`scripts/a019c_firewall/sitecustomize.py`,
`scripts/a019c_firewall/validation_firewall.py`, and
`tests/test_application_a019c_r2_firewall.py`.
Production entrypoints do not import these files. Inactive behavior is unchanged.

The exact activation boundary was the first bootstrap invocation:

```powershell
$env:MALECNS_A019C_R2_FIREWALL='1'
$env:PYTHONPATH=(Join-Path (git rev-parse --show-toplevel) 'scripts/a019c_firewall')
$env:MALECNS_A019C_R2_LOG=Join-Path $env:TEMP 'a019c-r2-firewall-session.jsonl'
uv run python -m pytest tests/test_application_a019c_r2_firewall.py -q
```

Python startup executes sitecustomize before pytest collection. `install()` adds
the open/subprocess audit hook before importing PyArrow, wraps public Arrow
readers, sets ACTIVE, and logs activation. Bootstrap import failures terminate
with exit 78 rather than Python's usual ignored sitecustomize exception.
No validation ran before this boundary. The same environment was explicitly set
for both bootstrap invocations. No broader validation was launched.

The intended deny scope is all repository data/, the configured MALECNS_DATA_ROOT,
and relocated registered MaleCNS release names. Categories are REAL_CONNECTIVITY,
REAL_ANNOTATION, REAL_NEUROTRANSMITTER, REAL_NEURON_METADATA, REAL_PROVENANCE,
REAL_MAPPING, and REAL_OTHER_REGISTERED_DATA. Unknown sources under denied roots
are denied. Public Feather/Parquet/Arrow readers and Python opens are guarded.
Python subprocess inheritance and rejection of guard-removing environments pass.
These facts do not establish a firewall over every native or non-Python child.

## Bootstrap results and mandatory stop

First invocation: 10 passed in 1.30 seconds.
Coverage review added a native FeatherReader probe using a generated temporary
synthetic sentinel, with its temporary directory added to the test deny roots.
No registered real payload was used for that probe.
Second invocation: **10 passed, 1 failed in 1.10 seconds**.

The failure is in `test_native_reader_denies_synthetic_sentinel`:
`TypeError: __cinit__() takes exactly 3 positional arguments (2 given)`.
The probe used an incorrect native constructor signature. This is an invalid
coverage probe, not proof that a native read succeeded or was blocked.
It does not prove SourceAccessDenied before content read. Native coverage and
task-wide process-tree coverage remain incomplete. Per the explicit bootstrap
failure gate, no correction/rerun or broader validation follows this failure.
The failed test is retained as stop evidence, not a passing regression.

## Access accounting and deliberate probes

The bootstrap log records parent PIDs 8200 and 11888 and child PIDs 10200 and
20144. There are **30 deliberate blocked real-source probes**: two parent
reader probes for each of seven categories in each invocation, plus one child
provenance probe per invocation. Each logged rejection occurred before content
read and is expected. Two child-environment rejections are not source probes.
The invalid native probe is a separate synthetic coverage attempt, not a blocked
real-source probe. Its expected rejection was not established.

| Category | Identifier relative to data/ | Parent probes | Child probes | Before content read | Expected rejection |
|---|---|---:|---:|---|---|
| REAL_CONNECTIVITY | raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather | 4 | 0 | Yes | SourceAccessDenied |
| REAL_ANNOTATION | raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather | 4 | 0 | Yes | SourceAccessDenied |
| REAL_NEUROTRANSMITTER | raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather | 4 | 0 | Yes | SourceAccessDenied |
| REAL_NEURON_METADATA | raw/neuron-metadata.json | 4 | 0 | Yes | SourceAccessDenied |
| REAL_PROVENANCE | provenance/male-cns-v1.0.json | 4 | 2 | Yes | SourceAccessDenied |
| REAL_MAPPING | provenance/task007-mapping-summary.json | 4 | 0 | Yes | SourceAccessDenied |
| REAL_OTHER_REGISTERED_DATA | unknown-registered-source.bin | 4 | 0 | Yes | SourceAccessDenied |

For this bounded execution: accepted_real_connectivity_reads=0,
accepted_real_annotation_reads=0, accepted_real_neurotransmitter_reads=0,
accepted_real_metadata_reads=0, accepted_real_provenance_reads=0,
accepted_real_mapping_reads=0, accepted_other_registered_reads=0;
**accepted_registered_real_source_reads=0**. All executed payload operations were
generated temporary synthetic writes/reads or explicitly rejected source probes.
These execution counters are not a certification of complete interception
coverage. No task-wide certified-zero-source-access status is issued.

## Validation manifest and exclusions

S0 executed: only the targeted bootstrap file. Generated Feather fixture, ordinary
temp text, and source-code reads pass. S1 executed: none. No S2 test executed.
Candidate manifest construction is halted; uninspected candidates are not
classified as demonstrably synthetic merely because of their names.

Direct S2 exclusions, without execution:

- `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields`
- `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity`
- `tests/test_application_a003.py::test_result_events_and_backend_export_routes`
- `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance`:
  source invokes git show on data/derived/task008-results.json; conservatively
  excluded from this synthetic-only scope. Historical Git blobs also return
  payload contents; Python path interception alone does not guard git show.
- `scripts/check_tracked_integrity.py`: code explicitly reads provenance manifests
  and derived data. NOT RUN — authorization boundary; no weakened checker added.

Full pytest: **NOT RUN — synthetic-only authorization; known S2 tests excluded**.
This policy exclusion is not itself a validation failure.
All requested downstream validation sets, compileall, diff validation and build
are NOT RUN after the bootstrap failure. No test is globally skipped or weakened.

## Preserved forward contract, not recertified

Source inspection confirms the preserved harness explicitly scopes bounded_route
around one prepare call and exposes the A015/A016/A017/A018/A018T/A018U/A018UJ
route, enabled flag, merge block 16384 and fallback field. Its production default
is unchanged. Existing G1-G6 and cross-layer tests, two-state tests, schedule tests,
replay tests, deadline/resource/containment tests and no-retry tests remain WIP.
They are **NOT RUN in R2** and receive no new PASS claim.

The preserved A019C evidence records the schedule fingerprint
`6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`,
seed 1555062870, horizon 240 ms, 948 events; one network/runtime, two states,
2 warmups and 10 measured 20-ms advances per state, 24 calls total, 12 consecutive
per state, and exact replay. This is historical worker evidence only, not R2
execution or superseding certification. The timing helper and limits remain
unchanged: 600/30/1500 seconds and both caps 8589934592 bytes.

## Final report fields

Numbers correspond to the requested final-report checklist. NR means NOT RUN in
R2 after bootstrap failure; historical means preserved WIP, not current PASS.

| Items | Result |
|---|---|
| 1–3 Verdict / classification / starting HEAD | STOP; A19C-R2-C; 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4–6 Initial WIP count / names / unrelated WIP | 6; listed above; No |
| 7–8 Historical A19C-F / A19C-R-D preserved | Yes / Yes |
| 9–11 Guard-first / activation / mechanism | Yes before tests and real probes; boundary above; opt-in startup/audit/public-reader guard |
| 12 Parent guarded | Python pytest parent Yes; shell/uv native coverage not certified |
| 13 Subprocesses guarded | Exercised Python children Yes; entire process tree not certified |
| 14 Fail-closed | Bootstrap import failure and tested public access Yes; complete coverage not certified |
| 15–21 Seven payload categories guarded | Tested Python/public-Arrow paths Yes; complete native coverage not certified |
| 22 Deliberate blocked probes | 30 |
| 23–27 Edge / annotation / neurotransmitter / provenance / mapping probes | PASS for tested paths |
| 28–29 Synthetic fixture / temp fixture allowed | Yes / Yes |
| 30–37 Accepted reads by seven categories / aggregate | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0; coverage caveat above |
| 38–40 S0 / S1 / S2 sets | Bootstrap only / none executed / exclusions above |
| 41 Known A003 S2 tests excluded | Yes |
| 42–43 Full pytest run / status | No; NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 44 WIP reconciled | Preserved; synthetic recertification incomplete |
| 45 Harness | scripts/benchmark_application_a019.py |
| 46 Explicit bounded route selected | Present in WIP; NR |
| 47 Production default changed | No |
| 48–49 Route observable / block size | Present in WIP; executable evidence NR / 16384 in source |
| 50 Fallback hard-stop | NR |
| 51 preparation-identity-v1 loaded | NR in R2 |
| 52–58 G1/G2/G3/G4/G5/G6 / wrong-layer | All NR |
| 59 application-stateful-benchmark-v1 loaded | NR in R2 |
| 60–64 Network/runtime/state counts / A/B fresh | R2 harness not run; actual counts 0/0/0; A/B NR; historical contract 1/1/2 |
| 65–68 Reset / recreation / A from B / B from A | No operations; contract tests NR |
| 69–74 A/B warmup/measured / horizons / calls / consecutive | R2 none; historical contract 2/10 each, 240 ms each, 24 total, 12 max |
| 75–77 Continuous 480 ms / A release / coexistence | No execution / NR / no execution |
| 78–82 Schedule generation/seed/horizon/events/fingerprint | R2 generation 0; historical 1 / 1555062870 / 240 ms / 948 / fingerprint above |
| 83–87 Windows/state/pending/output equality / timing | All NR; implementation unchanged |
| 88–92 Preparation/advance/worker deadlines / private/working caps | Preserved wiring; NR |
| 93–97 Containment / timeout / memory / cleanup / no-retry | All NR for harness; only bootstrap subprocess checks executed |
| 98 Attempt-start boundary | Unchanged; first bounded full-real edge-source access |
| 99 Future A019D attempt consumed | No |
| 100–105 Full-real preparations / real advances / GPU / real Arena / experiments / downloads | 0 / 0 / No / 0 / 0 / 0 |
| 106–109 Scientific / A013 / Task016 / Task017 changed | No / No / No / No |
| 110 Task017 classification | Unchanged / NOT_ROBUST |
| 111–112 Archive writes / B archive changed | 0 / No |
| 113 Targeted firewall tests | First 10 pass; final 10 pass, 1 fail; bootstrap STOP |
| 114–129 A019C, A019A, A018UJ/UI/UR/U/T/S/018, A017/016/015/014/013, stateful/A011, application regressions | Every set NR — bootstrap failure |
| 130 Excluded real-data tests | S2 manifest above; all remaining candidates halted before execution |
| 131 Full pytest status | NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 132 compileall | NR — bootstrap failure |
| 133 Tracked integrity | NR — authorization boundary; source reads prohibited payloads |
| 134 Diff check | NR — bootstrap failure; no passing validation claim |
| 135 Build | NR — bootstrap failure; build-hook process coverage not certified |
| 136–137 Version / tracked workflows | 0.3.0 / 0 |
| 138–142 Commit / push / local / origin / live | No new commit; not pushed; all remain starting SHA |
| 143 Worktree / stash | Intended WIP and bootstrap/stop additions remain dirty; stash empty |
| 144 Tag/release/version mutation | No |
| 145 Superseding status | None |
| 146 Exact next task | Separately authorized firewall-bootstrap repair and complete coverage verification; no automatic continuation |
| 147 A019D recommended | No |

No biological interpretation. Task017 new units=0; Task017Q=0. Historical
Task016/Task017 and B archive unchanged. No production source, package metadata,
workflow, scientific semantics, global watchdog or dataset registration change.
