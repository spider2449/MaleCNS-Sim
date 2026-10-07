# A023-R10C2-LOCAL-REPRO: Trusted-host validation infrastructure

Date: 2026-10-07. Authorized scope: fresh local reproducibility infrastructure
and synthetic infrastructure tests only. No commit, push or workload execution.

## Trust-model revision

Adopt **TRUSTED-HOST-REPRO-V1**. Trust the human developer, current Windows host,
administrator account, Git, Codex CLI, uv, Python and normal OS infrastructure.
Malicious host administration, hostile ownership, adversarial hypervisors and
intentional administrator tampering are outside this model.

Retire from the active clean-lineage gate: external machine/VM independence,
separate custody administrator, malecns-runner, resistance to SeDebugPrivilege,
administrator DACL override and proof that the owner cannot modify files.
The R10C1 external provisioning specification remains a valid stronger model.
This is a scoped contract revision, not retrospective acceptance.

Preserve A023-B, G16 NOT PASS, PE3-UNRESOLVED, A023-R10C-CUSTODY STOP and
A023-R10C1-PRINCIPAL-SPEC-A. R6's 27 passed remains PREMATURE OBSERVATION —
NOT ACCEPTANCE EVIDENCE. Previous inspection violations remain historical.

Protect against stale process/Python/pytest/cache state, R6-result reuse,
ambient plugins, accidental protected reads, uncontrolled test writes/children,
hidden environment/config drift and incorrect evidence accounting.

## Plan and implementation boundary

1. Verify local/origin/live master, exact 11 original WIP paths, staging/stash,
   worktrees and workflow count without uncontrolled content search.
2. Preserve A023-TRUSTROOT-V1: verify existing V3/B0/B3/B2 identities; reuse the
   certified bridge rather than repeating R10B-series certification.
3. Use B0/B3 exact-path pre-open classification and ledgered inspection.
4. Create a fresh detached sparse tree at
   c5ad89377575592665344f6420126b16c29b4339. Exclude classified protected data
   paths before checkout; do not read or materialize their Git blob contents.
5. Overlay exactly 11 independently verified WIP identities. Add the new
   infrastructure script separately, without changing the frozen H/I sets.
6. Use fresh uv sync --frozen --group dev --no-install-project --no-config
   with an admitted external Python and fresh cache. Skip project installation
   to avoid a build; explicitly control source import paths. Allow retrieval
   of exact lock-controlled artifacts; no upgrades or lock rewrite.
7. Construct a fresh explicit environment and dedicated temp/cache/output
   roots. Disable user-site imports and bytecode writes. Record uv-launcher
   PYTHONHOME state explicitly. Do not inherit project variables or secrets.
8. Install the unchanged full B3 firewall before pytest import/collection.
   Add stricter supported Windows long-path normalization and reject unknown
   device paths in the infrastructure adapter; do not weaken the guard.
9. Apply FS-REPRO-V1: immutable validation inputs, explicit writable roots,
   protected denial and complete pre/post input fingerprints. This Python
   audit policy is operational hygiene, not an OS security sandbox or a
   certification of arbitrary native code. Existing Arrow native readers are
   guarded and tested; future workloads still require explicit adjudication.
10. Disable pytest third-party autoload. Census both configuration and actual
    synthetic-session plugins; admit builtins plus one exact infrastructure
    census observer. Unknown plugins deny before collection.
11. Admit only fixed synthetic Python child classes. Record executable/argv,
    controlled environment, suspended job assignment before activation,
    nested lifetime, timeout termination and zero active job processes.
12. Exercise synthetic infrastructure checks, schema/missing/drift denials,
    immutable writes and protected Python/native Arrow denial. No repository
    test collection. Write a complete external validation record and evaluate
    20 adapted clean-lineage gates separately from execution readiness.

Two new infrastructure files are necessary and explicitly declared:

- scripts/a023_local_repro.py: standalone certification with embedded synthetic
  checks; it has no workload dispatch.
- This dated plan: records the active contract revision without changing the
  frozen B2 report or retroactively rewriting historical results.

The original 11 WIP remain byte-frozen. The new script and plan are additional
infrastructure, not members silently added to the original overlay or H/I.
Final N remains unfrozen and is deferred to R11.

## Frozen trust identities

| Control | SHA256 |
| --- | --- |
| Bootstrap V3 | de84b933b194d5ea94598ddbd4776fa533d87fa06e043873772d5956d41de358 |
| B0 | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| B3 | 170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af |
| B2 post-R10B3 | 96c9bd17e721a2697480da155e31f16e9ac4ddea9ab7450601a7d9d38c870607 |

ORCH-0 is the exact system Windows PowerShell executable with retained
provenance: 492032 bytes, PowerShell 5.1.19041.2673, file index high/low
65536/54630 and system-only hardlinks. File product-version text is distinct
from the PowerShell engine version. No identity mismatch was observed.

## Gate map

| Gate | Required evidence |
| --- | --- |
| CL01 | Exact committed base and metadata custody |
| CL02 | Exactly 11 verified original overlay identities |
| CL03 | H identity and 1503 nodes |
| CL04 | I identity and 12 nodes |
| CL05 | Frozen taxonomy identity, independently denied readiness |
| CL06 | Fresh isolated execution tree, no transferred runtime state |
| CL07 | Fresh environment and exact runtime/dev lock dependency closure |
| CL08 | Autoload disabled and actual controlled plugin census |
| CL09 | Exact explicit environment fingerprint |
| CL10 | Fresh dedicated temp/cache roots |
| CL11 | Unchanged B3 and synthetic protected Python/Arrow denials |
| CL12 | Known contained children, cleanup and orphan accounting |
| CL13 | Actual immutable/outside-output write denials |
| CL14 | Protected inputs absent from checkout and prohibited |
| CL15 | Complete pre-execution input fingerprints |
| CL16 | Fresh lineage, no R6 observations reused |
| CL17 | Preserved trust root and admitted controller provenance |
| CL18 | Infrastructure identity and actual self-test evidence |
| CL19 | Complete post-run input mutation accounting |
| CL20 | Exact inspection ledger with zero accepted protected opens |

Missing, malformed, extra or non-PASS gate evidence denies custody. The record
schema also rejects missing fields and fingerprint/overlay inconsistencies.
The certification entry point never authorizes a workload, even if presented
with fabricated readiness input.

## Execution gate and stop

Expected CUSTODY_READY=true and EXECUTION_AUTHORIZED=false after successful
certification. Blockers remain taxonomy incomplete, Z2=1501, A011 Z3-BLOCKED,
integrity split unresolved, unique A023 validation coverage unresolved and
final N not frozen. Do not repair those blockers in this task.

NOT RUN: tests/test_application_a023.py, A011, A007B, H regression workload,
final H/I/N suite, ordinary full pytest, simulation, preparation/advance,
benchmark, profiler, G16, release build and protected-content integrity.
Do not recompute protected hashes. No account/VM/host security changes.

## Certification result

**A023-R10C2-LOCAL-REPRO-A — TRUSTED-HOST REPRODUCIBILITY MODEL CERTIFIED;
CLEAN LOCAL VALIDATION HARNESS READY; CURRENT PROJECT STATE EXECUTION_DENIED.**

Final accepted run ID: malecns-a023-r10c2-33fe5219f73d4ce8acbf8d2885fde416.
The execution tree is the detached `execution` worktree under this external
run root. The record is `evidence/validation-record.json` under the same root.
No machine-specific original checkout path is required by this contract.

Validation-record SHA256:
245fd3adb735abaab3e247ce07563ff128439e10872cd1d80cc3435f1abb691f.

Infrastructure source SHA256:
9bb4841bed622b904f36fc40f183f4309d735067e35309d43b7e8de047c599d2.

Lock SHA256:
22d391ac12c2340ff5b668f1d89ac8534bf224a8a5543a5c0b588a6e90884828.

Original source checkout lock SHA256:
7523bec3c8947522d8eb80bda995696aba8941f143f7ef37c46afaece416ec02.
The original checkout uses CRLF and the fresh Git checkout uses LF. Final
exact-path readback verified unchanged original bytes against the admitted
source snapshot, unchanged execution bytes before/after, and identical
normalized content across checkouts. This is Git line-ending conversion, not
a lockfile rewrite or dependency drift.

The final run recreated tree, environment, temp/cache and evidence from scratch
after freezing the infrastructure source. Original overlay source/destination
verification passed for all 11 WIP. All 20 adapted clean-lineage gates passed.
CUSTODY_READY=true; EXECUTION_AUTHORIZED=false with all six stated blockers.

Actual tests: 45 synthetic infrastructure checks and one explicitly selected
external synthetic pytest case (1 passed). These include real write denials,
Python/Arrow protected-open denials including Windows long-path spelling,
UNKNOWN/classifier-error denial, plugin injection denial, gate/schema malformed
and missing evidence denial, fingerprint drift, exact runtime/dev dependency
closure, and normal/nested/timeout child accounting. No repository tests were
collected or run. Configuration census: 33 pytest builtin registrations.
Actual synthetic session: 41 registrations including one explicitly admitted
infrastructure census observer; third-party autoload disabled and no ambient
third-party plugins admitted.

Python 3.12.13 x64; uv 0.11.8. Frozen installed dependencies: colorama 0.4.6,
iniconfig 2.3.0, numpy 2.5.3, packaging 26.3, pandas 3.0.6, pluggy 1.6.0,
pyarrow 25.0.1, Pygments 2.21.0, pytest 9.1.1, python-dateutil 2.9.0.post0,
scipy 1.18.1, six 1.17.0 and tzdata 2026.4. No optional GPU/Node installation.

Normal/nested/timeout Job totals were 2/4/2, including uv Windows launcher
processes. Nested accounting equals the observed normal parent component plus
the independently recorded nested child component. All active Job counts were
zero after cleanup; timeout termination exit code was 79 and readiness output
proved the timeout child activated before termination. Child command and
environment inheritance were verified.

All 418 admitted immutable input fingerprints remained equal before/after.
Protected payload opens=0; protected hashes were not recomputed. No uncontrolled
repository content search in this task. Sparse checkout excluded 11 protected
base paths before materialization. A023-TRUSTROOT-V1 and frozen B0/B3/B2 bytes
remain unchanged; full B3 installation receives a supplementary stricter path
normalization adapter, not a source modification or weakened denial.

Development attempts are not acceptance evidence. They exposed an unpopulated
no-checkout tree, uv-added Python environment keys, pytest default device/log
paths, Windows long-path spelling, plugin class/module census representation,
and an incorrect assumption of two total processes for the nested uv-launcher
topology. Those infrastructure issues were corrected before the final fresh
complete run. An earlier fresh candidate failed the topology assertion and is
retained as failed evidence, not PASS. No scientific assertion was changed.

Only the new infrastructure script and this new plan were added to the source
repository. All original 11 WIP bytes, production files, guard bytes, taxonomy,
H and I remain unchanged. There is no commit/push/tag/version/release, no account
or VM provisioning, and no R11 execution. Existing and disposable worktrees are
retained with staging/stash empty; failed/development trees are not acceptance
inputs. The stronger R10C1 specification remains valid outside the repository.

Exact next task after success: A023-R11, resolve A011/A007B/taxonomy/integrity/N,
satisfy execution readiness, run exactly one zero-payload release-safe
validation and attempt G16. R11 is NOT STARTED.
