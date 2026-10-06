# A019C-R4 inherited-child fail-closed repair

Authorization: user explicitly authorized `授權 A019C-R4`, one bounded repair;
synthetic harness certification only after complete firewall bootstrap.

**STOP: A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE.**

## Starting inventory

Repository dynamically derived by `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`.
Starting local HEAD, origin/master and live GitHub master:
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Metadata-only inventory preceded source inspection and mutation.
Initial dirty count: 12 actual files (11 short-status entries because the firewall
directory was collapsed). All untracked; staged state empty; diff stat empty;
stash empty; unrelated WIP absent.

Initial paths:

1. docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
2. docs/plans/2026-10-05-application-a019c-harness-contract.json
3. docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
4. docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
5. docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
6. scripts/a019c_firewall/sitecustomize.py
7. scripts/a019c_firewall/validation_firewall.py
8. scripts/benchmark_application_a019.py
9. tests/fixtures/application-a019c-preparation-identity.json
10. tests/test_application_a019c.py
11. tests/test_application_a019c_r2_firewall.py
12. tests/test_application_a019c_r3_firewall.py

All belong to accumulated A019C/R2/R3 work. Existing historical evidence files,
fixtures and tests were not rewritten. No reset, restore, checkout, clean or stash.

## Historical stops

Preserved unchanged:

- A19C-F — REAL-DATA FIREWALL VIOLATED
- A19C-R-D — REAL-DATA FIREWALL VIOLATED AGAIN
- A19C-R2-C — FIREWALL COVERAGE INCOMPLETE
- A19C-R3-D — PROCESS-TREE FIREWALL COVERAGE INCOMPLETE

R3's 3 passed / 1 failed and PyArrow 25.0.1 native API findings remain established.

## Reconstructed defect and attempted architecture

R3 test 04 removed `MALECNS_A019C_R2_FIREWALL` from the parent environment and
called `subprocess.run([sys.executable, '-c', harmless_code])` without explicit
env. The audit inspected activation only when env was not None. Thus env=None
bypassed validation. Child sitecustomize installed only when activation equaled
`1`; absent activation silently allowed workload startup.

Added `scripts/a019c_firewall/guarded_child.py`: mandatory enforcement represented
by an absolute child entrypoint in argv, independent of activation environment.
Activation remains `MALECNS_A019C_R2_FIREWALL=1`. Entry rejects missing/corrupt
activation with exit 78 and `FIREWALL_REQUIRED_BUT_NOT_ACTIVE`, then installs and
verifies the firewall before importing runpy or executing workload.

Validation firewall wraps Popen initialization to route Python descendants through
this entrypoint. Unsupported executables/shell children are rejected. Parent audit
also checks mandatory entrypoint. Actual A019 script received a pre-workload
activation/install check and a synthetic startup-only probe. Its supervisor uses
the existing ProcessJob Popen mechanism; no historical A014/A013 code changed.

This is an attempted narrow A019 contract, not a universal OS sandbox.

## Bootstrap execution and immediate stop

Only executed validation command:

```powershell
$env:MALECNS_A019C_R2_FIREWALL='1'
$env:PYTHONPATH="$((Get-Location).Path)\scripts\a019c_firewall"
$env:MALECNS_A019C_R2_LOG="$env:TEMP\a019c-r4-bootstrap.jsonl"
uv run python scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r4_firewall.py -q -x
```

Result: **1 passed, 1 failed**. Exit 1. Stopped immediately; no repair iteration,
additional bootstrap execution or broader validation followed.

Passing first test: parent active; PyArrow 25.0.1; generated native Feather control
PASS using unchanged `FeatherReader(source, use_memory_map=False,
use_threads=True).read()`; seven representative categories blocked by both
Python read_bytes and native constructor interception. 14 deliberate blocked
probes, all before content read. Categories use code-defined paths under data/;
no registered taxonomy payload opened.

Failure: negative missing-activation test constructed mandatory child argv, removed
activation and PYTHONPATH, and attempted launch. On Windows the subprocess audit
event supplies a serialized command-line string, not the list expected by the new
audit check. Parent raised SourceAccessDenied('child lacks mandatory firewall
entrypoint') before starting child. No workload executed, but the required child
exit classification was not observed. This implementation assumption caused the
failure; it is not a Feather API defect. Child enforcement remains uncertified.

Remaining negative variants, positive child, native/public child, actual worker,
and inherited-removal test were NOT RUN after -x. The actual worker startup test
was authored but never executed. ProcessJob startup matrix remains incomplete.

## Accounting and certification

Accepted connectivity, annotation, neurotransmitter, metadata, provenance,
mapping and other registered reads: each 0; aggregate 0 within executed scope.
The execution log records one active parent and 14 blocked events; no child
started in the failed test. No claim that this is a universal acceptance monitor.

FIREWALL_BOOTSTRAP_CERTIFIED: **No**. Broader validation resumed: **No**.
A019C forward harness synthetic certification: **NOT RUN**, hard bootstrap gate.
Accumulated WIP preserved; reconciliation/certification incomplete.

Source-only forward harness properties remain unvalidated in R4: explicit
A015/A016/A017/A018/A018T/A018U/A018UJ route, opt-in bounded route, merge block
16,384, fallback hard stop, G1-G6, cross-layer rejection, one prepared network,
one runtime, two fresh states, each 2 warmups + 10 measured calls at 20 ms,
240 ms each, 24 total calls/max 12 consecutive, exact replay and state release.
Schedule contract: generated once, seed 1555062870, horizon 240 ms, 948 events,
fingerprint 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a.
Limits in source: 600/30/1500 seconds, private/working caps 8,589,934,592 each.
None of these harness results are claimed certified by R4.

Targeted A019C, A019A, A018UJ/UI/UR/U/T/S/018, A017/016/015/014/013,
A011/reference-LIF, application regressions, compileall, tracked integrity,
diff check and build: **NOT RUN — bootstrap failure**.
Tracked integrity additionally contains registered provenance payload reads;
current authorization does not permit those reads.
Full pytest: **NOT RUN — synthetic-only authorization; known S2 tests excluded**.

S2 exclusions preserved:

- test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- test_validate_and_run_requests_share_exact_spec_identity
- test_result_events_and_backend_export_routes
- A018UJ test_independent_frozen_artifact_reconstruction_and_provenance

## Final disposition

No success commit or bounded-stop commit. No push. Final local HEAD,
origin/master and live GitHub master remain the starting SHA (verified after
bootstrap failure). Worktree dirty intended accumulated WIP plus R4 edits;
stash empty. Version 0.3.0; tracked workflows 0. No tag/release/version change.

Full-real preparations 0; real advances 0; real benchmark attempts 0; future
A019D attempt unconsumed; GPU 0; Arena 0; scientific experiments 0; downloads 0;
archive writes 0. Production preparation default unchanged; historical A013
behavior and scientific semantics unchanged; Task016 unchanged; Task017 unchanged
and NOT_ROBUST. No biological interpretation.

No superseding A019C readiness status issued. A019D not recommended or executed.
Next task requires separate authorization for the Windows mandatory-child audit
representation repair and complete bootstrap matrix, before harness certification.
