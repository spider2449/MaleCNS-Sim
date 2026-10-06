# Application A019C-R9: validation/firewall integration adjudication

Authorization: `授權 A019C-R9`. Repository root derived using
`git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.

## Plan

1. Verify committed identities, staging, stash and all accumulated WIP.
2. Confirm the frozen bootstrap with its minimum complete regression.
3. Inspect the exact validation command, integrity inputs and build startup.
4. Admit tooling only with demonstrated payload separation and containment.
5. Record a bounded stop if the required separation cannot be established;
   withhold certification and commit/push rather than weaken the guard.

## Starting inventory

Local HEAD, origin/master and live GitHub master all matched
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Exactly 20 untracked files; no tracked modifications; staging and stash empty.
All belong to accumulated A019C work. No unrelated WIP was found.

```text
docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
docs/plans/2026-10-05-application-a019c-harness-contract.json
docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
docs/plans/2026-10-06-application-a019c-r7-live-process-tree-cleanup.md
docs/plans/2026-10-06-application-a019c-r8-obsolete-child-guard-regression.md
scripts/a019c_firewall/guarded_child.py
scripts/a019c_firewall/sitecustomize.py
scripts/a019c_firewall/validation_firewall.py
scripts/benchmark_application_a019.py
tests/fixtures/application-a019c-preparation-identity.json
tests/test_application_a019c.py
tests/test_application_a019c_r2_firewall.py
tests/test_application_a019c_r3_firewall.py
tests/test_application_a019c_r4_firewall.py
tests/test_application_a019c_r5_firewall.py
```

## Preserved chronology and bootstrap

Preserved: A19C-F, A19C-R-D, A19C-R2-C, A19C-R3-D,
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE,
A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE,
A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE,
A19C-R7-FIREWALL-METHOD-INVALID, A19C-R8-B.
R8's 39 bootstrap passes, 35 harness passes and fresh CLI success remain
historical evidence. Its broader validation was 15 passed, 1 failed,
4 deselected; integrity blocked provenance; isolated build exited 78.
These are not rewritten as complete certification.

R9 bootstrap, with activation 1, absolute firewall PYTHONPATH and log
`C:/TEMP/a019c-r9-bootstrap.jsonl`:

```text
.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest
  tests/test_application_a019c_r5_firewall.py
  tests/test_application_a019c_r4_firewall.py
  tests/test_application_a019c_r3_firewall.py
  tests/test_application_a019c_r2_firewall.py -q -x
39 passed in 5.19 s
```

Bootstrap certification preserved. No bootstrap implementation was edited.
Both live-tree cases, mandatory activation controls, bypass rejection,
Windows parsing, native Feather controls and cleanup remain covered by this
complete passing suite. Audit contains two live-tree cleanup records.

## Operation classes and exact Git adjudication

V0: source, scripts, tests, synthetic fixtures, plans and packaging metadata.
V1: repository tooling, subject to exact operation and input adjudication.
V2: build tooling, subject to active payload blocking and containment.
V3: registered scientific payload, including provenance and mapping: forbidden.
V4: ambiguous operation/input: fail closed.
A repository location or a Git invocation does not imply V0 status.

The exact A018UJ test invocation is NOT plain `git diff`:

```text
git diff d6fdb16e078bfca524214b9d1855ece3f8e9a7d7 -- src data pyproject.toml
```

It includes V3 paths. `git ls-files data` establishes that registered provenance,
mapping evidence and derived scientific results are tracked there without
opening their contents. The requested diff can examine their working-tree or
Git-object content. A clean current status does not prove a command family
will never read those contents. Replacing this assertion with a source-only
check would remove its data-immutability coverage and was not done.

Resolved executable discovery: `C:/Program Files/Git/cmd/git.exe`.
No executable exception was added. Existing Python identity checks and mandatory
entrypoint enforcement remain unchanged. A future native exception would need
exact resolved executable identity, exact arguments, controlled configuration,
and demonstrated payload/descendant restrictions. Identity alone is insufficient.

The current firewall uses Python audit hooks plus Arrow interception; native
Git does not execute those hooks. ProcessJob assigns suspended children to a
kill-on-close Job and prevents breakaway, but does not restrict filesystem reads
or authorize descendant commands. Neither a direct Git allowlist nor routing
Git through a Python launcher establishes the required native-read restriction.
No new OS sandbox or bootstrap redesign was attempted. Source-only tooling may
be adjudicable separately, but does not satisfy the exact existing test.

Temporary guarded probe `C:/TEMP/a019c-r9-probes.py` exited 0:
exact diff rejected; `git show HEAD:data/provenance/male-cns-v1.0.json` rejected;
shell-wrapped Git rejected; registered provenance and connectivity blocked
before content reads. An earlier inline probe failed with SyntaxError before
workload; it supplies no PASS evidence. No native Git validation child launched.
T1 is unresolved; T2/T3 negative probes PASS; T4/T7 are covered by bootstrap;
T5/T6 negative probes PASS. These are not a passing R9 integration suite.

## Integrity decision: I2

`check_tracked_integrity.py` validates nine frozen evidence hashes and linked
historical identities. Its input set includes four registered data files:
`data/provenance/male-cns-v1.0.json`,
`data/provenance/shiu-2024-v630.json`,
`data/provenance/task008a-preserved-task008.json`,
`data/derived/task008-results.json`.
It also links Task018 manifest identity and Task008 preservation to those
contents. This is mixed repository custody and prohibited payload validation.
Dropping those inputs would not validate the complete stated identity chain.
Default semantics were preserved; no partial mode was introduced.

I2: `uv run python scripts/check_tracked_integrity.py` NOT RUN as an R9 gate:
requires registered scientific provenance/data outside authorization.
All nine entries and their cross-checks are NOT CHECKED in R9, never PASS.
Source inspection alone is not integrity verification.

## Build investigation: disposition unresolved

`pyproject.toml` selects setuptools.build_meta with isolated requirement
`setuptools>=68`. Guard startup unconditionally imports pyarrow and exits 78
on any startup exception. Guarded-child activation failure also uses 78.

Safe diagnostic, with activation, absolute firewall PYTHONPATH and audit path
`C:/TEMP/a019c-r9-build.jsonl`: `uv build --offline`.
Result: build_sdist backend exit 78; no build audit file was created.
This establishes failure before recorded guard activation, not its precise
exception. Missing pyarrow in the setuptools-only isolated environment is a
plausible source-derived explanation, not a confirmed root cause.
No download occurred. No guard-off retry or successful build claim was made.
B1 not established; B2 necessity not established; B3 defect not established.
Selecting any would overstate the evidence. Secondary unresolved status:
A19C-R9-D. Final build gate NOT RUN after the tooling-policy stop.

## Validation manifest

S0 planned sets: A019C harness; A019A; selected A018UJ, A018UI, A018UR,
A018U, A018T, A018S, A018, A017, A016, A015, A014, A013; A011 and reference
LIF (`test_task005.py`); selected application A008/A007C/A007B/A007A,
A006R/A006/A005/A004/A003/A002. These are candidate synthetic selections
from R8, not a claim that every test in each file is S0.
Bootstrap is S0 and ran; negative R9 probes are S0 and ran.
S1 pending: exact A018UJ Git regression and isolated build startup; neither
was admitted. Source/config inspection and metadata-only Git inventory ran.
S2 exact exclusions, unchanged:

- test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- test_validate_and_run_requests_share_exact_spec_identity
- test_result_events_and_backend_export_routes
- test_independent_frozen_artifact_reconstruction_and_provenance (A018UJ)

S2 also includes the default integrity checker. N: real benchmark, GPU,
Arena execution, unfiltered full pytest and publication.
Full pytest NOT RUN — synthetic-only authorization; known S2 tests excluded.
No broader collection/run followed the unresolved policy gate. No hidden
additional deselections or substitutions were used. Manifest is a bounded-stop
manifest, not the completed success manifest required by R9-A.

## Accounting and final requested report

Bootstrap blocked 34 events: connectivity 8, annotation 4, neurotransmitter 4,
metadata 4, provenance 5, mapping 4, other 5. Of these, 33 are registered-path
probes and one is a synthetic deny-root sentinel. R9 explicit probes added
one provenance and one connectivity event: 36 blocked events total, 35
registered-path probes plus one sentinel. Accepted registered reads: all
seven counters 0, aggregate 0. No native tooling exception was granted.
Allowed external tooling operations were metadata inventory/status/identity,
source inspection, diff whitespace checking and the offline fail-closed build
startup diagnostic; these are separate from source-read counters.

| Requested fields | R9 result |
|---|---|
| 1-2 Verdict/classification | Bounded stop: A19C-R9-B — TOOLING SUBPROCESS POLICY UNRESOLVED |
| 3-7 Identity/inventory/history | Starting SHA above; 20 scoped files; full paths above; no unrelated WIP; all historical outcomes preserved |
| 8-9 Bootstrap | Preserved; 39 passed |
| 10-12 Classes/policy/identity | V0-V4 above; no new allowlist; resolved Git path recorded, no native identity exception |
| 13-19 Tooling questions | Exact diff not allowed; arbitrary Git not allowed; shell rejected; bypass still rejected; no permitted native tooling child; no payload authorization; Git regression not PASS |
| 20-21 Payload probes | Provenance and connectivity blocked before reads |
| 22-26 Integrity | Mixed custody/payload purpose; I2; command NOT RUN; all nine inputs/cross-checks NOT CHECKED |
| 27-31 Build | Exit 78 before logged activation; exact root cause unresolved; no B1/B2/B3 justified; no policy exception; no build PASS; no payload authorization |
| 32-37 Manifest | Candidate S0/S1/S2 sets and exact exclusions above; A003 exclusions preserved; A018UJ reconstruction remains S2; full pytest NOT RUN |
| 38-40 Test suites | Bootstrap 39 PASS; R9 negative probes PASS but T1 unresolved; A019C harness NOT RUN in R9 |
| 41-56 CLI and broader suites | All NOT RUN after unresolved policy gate; R8 harness/CLI results remain historical, not fresh R9 PASS |
| 57-60 Final checks | compileall NOT RUN; integrity I2 NOT RUN; git diff --check PASS; build diagnostic FAIL CLOSED, final build gate not satisfied |
| 61-68 Accepted reads | connectivity=0; annotation=0; neurotransmitter=0; metadata=0; provenance=0; mapping=0; other=0; aggregate=0 |
| 69-70 Probes/tooling | 36 blocked read events; tooling operations separately recorded above |
| 71 Forward harness | scripts/benchmark_application_a019.py |
| 72-82 Harness gates | No fresh R9 certification; R8 bounded route, fallback, G1-G6 and L3/L4 historical PASS preserved; merge block 16384; production default unchanged |
| 83-108 Replay structure | R9 NOT RUN. Preserved R8 evidence: 1 network, 1 runtime, 2 fresh states; no reset/recreation/B-from-A; each 2 warmup + 10 measured, final 240 ms; 24 calls, max 12/state; no continuous 480 ms; A released before B, no coexistence; schedule generated once, seed 1555062870, horizon 240 ms, events 948; identical windows and exact state/pending/output replay |
| 104 Fingerprint | Historical R8: 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a |
| 109-120 Timing/resources | Harness NOT RUN in R9; historical R8 timing, 600/30/1500 s timeouts, private/working-set caps 8589934592, forced stops/no-retry PASS preserved. R9 bootstrap containment/live-tree cleanup/no-orphan PASS |
| 121-133 Execution firewall | Full-real preparations 0; real advances 0; future attempt unconsumed; GPU No; Arena 0; scientific experiments 0; downloads 0; A013 unchanged; scientific semantics unchanged; Task016/Task017 unchanged, Task017 NOT_ROBUST; archive writes 0 |
| 134-135 Package/workflows | 0.3.0; zero active tracked workflows |
| 136-140 Commit/remote | No new commit; push not attempted; local/origin/live remain starting SHA |
| 141-142 Tree/publication | 21 scoped untracked files after this report; staging/stash empty; no tag/release/version change |
| 143-145 Readiness | Bootstrap remains certified; full forward harness certification withheld; next bounded task: resolve payload-safe exact diff validation and isolated build startup; A019D not recommended or executed |

No accumulated file was reset, restored, cleaned, stashed or discarded. R9's
only repository mutation is this report. No evidence commit was made because
the required validation remains incomplete. No biological interpretation.
