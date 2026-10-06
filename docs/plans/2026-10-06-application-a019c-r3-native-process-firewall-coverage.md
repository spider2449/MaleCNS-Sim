# A019C-R3 native/process firewall coverage correction

Authorization: `授權 A019C-R3`, one bounded correction; synthetic harness resumption only after complete bootstrap certification.

**STOP: A19C-R3-D — PROCESS-TREE FIREWALL COVERAGE INCOMPLETE.**
Stop identifier: `A19C-R3-PROCESS-COVERAGE-INCOMPLETE`.
Bootstrap: **3 passed, 1 failed**, 1.07 seconds, first failure stops execution.
No further bootstrap corrections, probes, tests, harness, compile, integrity, build, commit or push follow this failure. Only stop documentation and Git metadata inventory follow.

## Starting state and bounded plan

Root derived dynamically: `D:/spider/working/MaleCNS-Sim`.
Local HEAD = origin/master = live GitHub master = `60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Package version 0.3.0; zero tracked workflow files; stash empty.
Initial worktree: 10 untracked files, no modified tracked files, no staged files. Git's short status collapses the firewall directory to one entry; the expanded inventory establishes the actual file count.
No unrelated WIP found. Original six A019C files and four R2 additions preserved:

| Initial path | Ownership |
|---|---|
| docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md | A019C/R chronology |
| docs/plans/2026-10-05-application-a019c-harness-contract.json | A019C |
| docs/plans/2026-10-05-application-a019c-synthetic-evidence.json | A019C/R/R2 evidence |
| scripts/benchmark_application_a019.py | A019C |
| tests/fixtures/application-a019c-preparation-identity.json | A019C |
| tests/test_application_a019c.py | A019C |
| docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md | R2 |
| scripts/a019c_firewall/sitecustomize.py | R2 |
| scripts/a019c_firewall/validation_firewall.py | R2 |
| tests/test_application_a019c_r2_firewall.py | R2 |

Plan: inventory; inspect source; identify installed API; add native boundary wrapper; run ordered synthetic control, blocked parent native probe, guarded child native probe, missing-guard child control; stop on first bootstrap failure; complete remaining matrix and resume S0/S1 only if all bootstrap requirements pass.

Historical dispositions remain exactly:

- A19C-F — REAL-DATA FIREWALL VIOLATED
- A19C-R-D — REAL-DATA FIREWALL VIOLATED AGAIN
- A19C-R2-C — FIREWALL COVERAGE INCOMPLETE

R2 remains 10 passed / 1 failed. Its native constructor call omitted required `use_threads`, producing `TypeError: __cinit__() takes exactly 3 positional arguments (2 given)`. Neither R2's test nor its stop record is rewritten as PASS.

## Pre-change coverage inspection

R2 installs a CPython audit hook for `open`, covering builtins.open, pathlib.open/read_bytes/read_text and repository loaders that reach those operations. It wraps pyarrow.memory_map, OSFile, input_stream; public Feather read_table/read_feather; Parquet read_table/read_schema/ParquetFile. It does not wrap native FeatherReader before R3.

Denied paths include repository data/, configured MALECNS_DATA_ROOT and relocated release-name matches. The registration JSON itself cannot be inspected within this authorization. DatasetCatalog/registry resolution is not independently intercepted: its Python payload opens are denied. Loader-level seams are not globally replaced. No complete registry-coverage claim is made.

sitecustomize installs only when MALECNS_A019C_R2_FIREWALL=1, terminating exit 78 on installation exception. The subprocess audit checks explicit replacement environments and exact -S/-I/-E arguments. It does not validate the inherited environment when subprocess receives env=None. Python startup activation is observable through ACTIVE and JSONL activation records.

Actual harness ProcessJob is defined in scripts/investigate_application_a014.py and uses subprocess.Popen with CREATE_SUSPENDED, assigns a Windows Job, then resumes. It shares the same subprocess audit boundary. Its startup activation is NOT executed/certified in R3 because the earlier missing-guard control fails. No harness import or execution occurred.

## Installed native API and correction

PyArrow **25.0.1**, inspected from installed Python package source and introspection, without real payload access. No internet or real-file API discovery was used.
Native class: `pyarrow._feather.FeatherReader`.
Exact valid invocation:

```python
native.FeatherReader(str(source), use_memory_map=False, use_threads=True).read()
```

The equivalent positional constructor is `FeatherReader(source, False, True)`.
Installed pyarrow.feather._read_table_internal uses this three-argument constructor and calls read(), read_indices() or read_names(). The class is constructible from Python. It has read(), not read_all(); an initial introspection request for read_all raised AttributeError after reporting the version. That source/API inspection error was not a bootstrap validation failure or payload operation.

R3 adds a validation-only wrapper to the native module's FeatherReader binding. check(source) executes before invoking the original extension constructor. Generated temp Feather control writes `{sentinel: [19]}` and reads the exact same table through the original native constructor behind the wrapper: PASS.

Parent connectivity native probe and inherited guarded Python child's connectivity native probe: PASS. Both reject at validation_firewall.check before the original FeatherReader constructor; OS/native open is not reached and no payload bytes are returned. The wrapper also intercepts FeatherDataset/internal public paths resolving that module binding. This is a tested Python binding boundary, not an OS sandbox or coverage of arbitrary ctypes/native file APIs.

## Bootstrap execution and mandatory process stop

Command environment was explicitly set before Python startup:

```powershell
$env:MALECNS_A019C_R2_FIREWALL='1'
$env:PYTHONPATH=Join-Path (git rev-parse --show-toplevel) 'scripts/a019c_firewall'
$env:MALECNS_A019C_R2_LOG=Join-Path $env:TEMP 'a019c-r3-firewall-bootstrap.jsonl'
uv run python -m pytest tests/test_application_a019c_r3_firewall.py -q -x
```

Log nonexistence was checked before launching; no old log was overwritten.
Ordered results:

1. Synthetic native Feather constructor/read: PASS.
2. Parent known real connectivity native constructor rejection: PASS.
3. Python child ACTIVE and native rejection before constructor: PASS.
4. Missing inherited activation variable: FAIL, expected SourceAccessDenied was not raised. The test temporarily removes the activation variable from os.environ and launches with env=None. A harmless child prints `UNGUARDED CHILD EXECUTED`; no registered path is supplied to this child.

This proves an inherited environment is insufficient and the child can silently execute unguarded. The pytest monkeypatch restores the variable during teardown. No accepted payload operation occurred in the unguarded child. Per the hard gate, execution stops immediately with no repair/rerun after this failure.

## Incomplete process/source matrix

| Mechanism | Parent | Python child | Actual ProcessJob worker |
|---|---|---|---|
| Python open/pathlib | R2 boundary inspected; R3 category tests NOT RUN | NOT RUN in R3 | NOT RUN |
| Repository loader | Source inspected; no loader invoked | NOT RUN | NOT RUN |
| Public Feather | Generated write only; native common binding identified | Native probe only, separate public probe NOT RUN | NOT RUN |
| Corrected native Feather | Synthetic control and connectivity rejection PASS | Connectivity rejection PASS with activation inherited | NOT RUN |
| Missing guard | Parent active | FAIL: env=None bypass after activation variable removal | Same Popen boundary; execution NOT RUN |

| Source category | R3 native parent/child blocked probes | Remaining category/mechanism cells |
|---|---|---|
| Connectivity | 1 parent + 1 child, PASS | NOT RUN after process failure |
| Annotation | 0 | NOT RUN |
| Neurotransmitter | 0 | NOT RUN |
| Metadata | 0 | NOT RUN |
| Provenance | 0 | NOT RUN |
| Mapping | 0 | NOT RUN |
| Other registered source | 0 | NOT RUN |

Omitted cells are unresolved coverage gaps caused by the mandatory stop, not claims of transitive certification. Existing check(source) is the identified common path rejection boundary, but an inactive child never installs it. A complete matrix cannot be certified.

Executed log records:

- active PID 17128, repository data root denied;
- blocked PID 17128, REAL_CONNECTIVITY, before_content_read=true;
- active PID 19220, repository data root denied;
- blocked PID 19220, REAL_CONNECTIVITY, before_content_read=true.

blocked_probe_attempts=2, separately from accepted reads.
accepted_real_connectivity_reads=0; accepted_real_annotation_reads=0;
accepted_real_neurotransmitter_reads=0; accepted_real_metadata_reads=0;
accepted_real_provenance_reads=0; accepted_real_mapping_reads=0;
accepted_other_registered_reads=0; aggregate accepted registered reads=0.
These are counters for this execution, not certification of complete coverage.

## Validation manifest and final requested report

NR means NOT RUN in R3 after bootstrap failure; values described as source/contract evidence are not newly certified. S0 executed only tests/test_application_a019c_r3_firewall.py; S1 none. Remaining candidate S0/S1 manifest inspection is stopped. No command with unresolved payload safety was launched.

| Requested items | Result |
|---|---|
| 1–3 Verdict/classification/starting SHA | STOP / A19C-R3-D / 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4–6 Initial count/paths/unrelated WIP | 10 actual files; inventory above; No |
| 7–9 Historical A19C-F/A19C-R-D/A19C-R2-C | All preserved exactly |
| 10–13 PyArrow/error/API/invocation | 25.0.1 / reconstructed / identified / exact invocation above |
| 14–19 Native control/parent native block/parent/Python child/PyArrow child/native child | PASS / PASS / active / active with inherited variable only / separate public test NR / native PASS |
| 20–21 Actual harness worker/missing-guard fail-closed | NR / FAIL |
| 22–29 Connectivity/annotation/NT/metadata/provenance/mapping/other/full matrix | Connectivity native tested PASS; remaining categories not certified in R3; matrix incomplete |
| 30 Deliberate blocked probes | 2 connectivity native probes, parent and child |
| 31–38 Accepted category and aggregate counters | All seven categories 0; aggregate 0, execution scope only |
| 39–41 Bootstrap/resumption/WIP reconciliation | Not certified / No / preserved and inventoried; harness recertification incomplete |
| 42–47 Harness/explicit route/default/observable route/block/fallback | scripts/benchmark_application_a019.py / explicit in source / No default change / fields present, execution NR / 16,384 in source / NR |
| 48–54 G1/G2/G3/G4/G5/G6/L3-L4 | All NR |
| 55–59 Network/runtime/state counts/A fresh/B fresh | R3 actual 0/0/0; required 1/1/2 unvalidated; A/B NR |
| 60–63 Runtime reset/recreated/A from B/B from A | No R3 operations; required No values not recertified |
| 64–69 A/B structure/horizons/calls/max consecutive | Required each 2 warmup + 10 measured, 20 ms/call, each 240 ms, 24 calls, max 12; all NR in R3 |
| 70–72 Continuous 480 ms/A released before B/coexistence | No execution / NR / no execution; structure NR |
| 73–78 Schedule count/seed/horizon/events/fingerprint/windows | R3 count 0; historical contract 1/1555062870/240 ms/948/6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a; windows NR |
| 79–82 State/pending/output/timing | All NR |
| 83–87 Preparation/advance/worker timeouts/private/working caps | Source 600 s/30 s/1500 s/8,589,934,592/8,589,934,592; certification NR |
| 88–92 Forced timeout/memory/containment/no orphan/no retry | All NR for harness |
| 93–99 Future attempt/preparations/advances/GPU/Arena/experiments/downloads | No / 0 / 0 / No / 0 / 0 / 0 |
| 100–106 A013/scientific/Task016/Task017/classification/archive/B archive | No change / No change / No change / No change / NOT_ROBUST unchanged / 0 writes / No change |
| 107–110 S0/S1/S2/A003 exclusions | R3 bootstrap only / none / exclusions below / Yes |
| 111 Full pytest | NOT RUN — synthetic-only authorization; known S2 real-data tests excluded |
| 112 Targeted R3 firewall | 3 passed, 1 failed; stopped with -x |
| 113–128 A019C/A019A/A018UJ/UI/UR/U/T/S/018/A017/016/015/014/013/A011/application | Every set NR — bootstrap failure |
| 129–132 compileall/integrity/diff check/build | Every command NR — bootstrap failure |
| 133–134 Version/workflows | 0.3.0 / 0 |
| 135–139 Commit/push/final local/origin/live | No new commit / NOT RUN / all three starting SHA |
| 140–141 Worktree/stash/tag-release-version | Dirty intended WIP + R3 additions; stash empty / No mutations |
| 142–144 Superseding status/next task/A019D | None / separately authorized inherited-child fail-closed repair and full bootstrap matrix certification / Not recommended |

Known S2 tests excluded without execution:

- tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity
- tests/test_application_a003.py::test_result_events_and_backend_export_routes
- tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance (R2 source inspection identifies git show of derived payload)
- scripts/check_tracked_integrity.py (R2 source inspection identifies real provenance/derived reads; never waived)

No production source, historical A013, scientific semantics, preparation default, archive, Task016 or Task017 changed. Task017 new units=0; Task017Q=0; real benchmark attempts=0. Future real attempt remains unconsumed. No biological interpretation. No A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED status issued. A019D is not executed or recommended. No commit, push, tag, release or version bump.
