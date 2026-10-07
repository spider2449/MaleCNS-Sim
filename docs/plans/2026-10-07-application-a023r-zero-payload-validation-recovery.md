# A023-R — Zero-payload validation recovery

Authorization: **授權 A023-R**. Terminal classification:
**A023-R-B — ZERO-PAYLOAD ROUTE INCOMPLETE; ONE VALIDATION CLASSIFICATION GAP REMAINS.**
Overall **A023-B** remains; G16 is not satisfied. The bounded gap is an executable
validation route consistent with both all-Z0 execution and the retained execution
restrictions. No runtime contract defect or guard defect has been established.

## Starting custody and frozen fingerprints

Root derived by git rev-parse: D:/spider/working/MaleCNS-Sim.
HEAD, origin/master, and live origin refs/heads/master all equal
c5ad89377575592665344f6420126b16c29b4339. Exactly the five expected untracked
files; tracked diff/stat and staging empty, stash empty, version 0.3.0,
tracked workflows zero. Hashes captured before recovery edits:

- `src/malecns_sim/runtime.py`: `acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d`
- `src/malecns_sim/experimental/__init__.py`: `6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128`
- `src/malecns_sim/experimental/gpu.py`: `56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc`
- `tests/test_application_a023.py`: `81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579`
- `docs/plans/2026-10-07-application-a023-public-runtime-implementation.md`: `5d51c345263c5eeed3a2f16b8b96588ae51804059873296f7e240a0e3e723b99`

The four retained source/test files remain byte-identical. This report and the
append-only reference in the original report are the only recovery edits.
Original status --short grouped experimental/ as one untracked directory;
git ls-files --others --exclude-standard established the exact five-file list.

## Guard audit

Statically inspected scripts/a019c_firewall/validation_firewall.py,
sitecustomize.py, a006r_node.py, a007c_node.py, and R2 guard tests.
Registration denies repository data/, MALECNS_DATA_ROOT when supplied, and
male-cns-v1 / male-cns/v1.0 release spelling even outside data/.
The CPython open audit event covers ordinary builtins/io/pathlib opens.
Arrow wrappers cover native FeatherReader, memory_map, OSFile, input_stream,
Feather read_table/read_feather and Parquet read_table/read_schema/ParquetFile.
check resolves the path, logs blocked with before_content_read=true and raises
before calling the original reader. Metadata stat/is_file remains permitted.
Import/collection can attempt reads and therefore must be guarded from startup.
sitecustomize activates install with MALECNS_A019C_R2_FIREWALL=1; bootstrap
failure exits 78. Popen enforces mandatory Python child entry and only the exact
existing A006R/A007C Node contracts. No general pytest selection route or pytest
markers are configured in pyproject.toml. No guard semantics were changed.

The log records active and blocked events, not a separate accepted-read counter.
Zero accepted registered reads follows enforcement for the intercepted routes;
do not describe it as a directly emitted numeric counter or universal OS tracer.
Collection log: C:/TEMP/a023r-collection-20261007.jsonl.

## Original blocker and proven dependencies

Original historical node:
tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields.
DatasetCatalog.spec -> populations -> ProductionEngine.identities requires
registered annotation/neurotransmitter evidence. Its fixed member counts and
registered population identity assertions require that evidence. PAYLOAD-REQUIRED,
not a product regression. Prior Arrow denial preceded content access at
body-annotations-male-cns-v1.0-minconf-0.5.feather under data/raw/male-cns/v1.0/.
No ordinary execution was repeated to rediscover this denial.

Proven Z1 candidates (NOT RUN; no complete exclusion manifest is certified):

- tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity
- tests/test_application_a003.py::test_result_events_and_backend_export_routes
- tests/test_tracked_integrity.py::test_tracked_integrity_accepts_copy_and_rejects_corrupt_metadata
- tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance

The A003 nodes call the real catalog spec without replacing identities.
The integrity node copies every PINNED_SHA256 file, including protected data/;
copying those contents to temporary storage is forbidden by this authorization.
A018UJ calls git show on historical data/derived/task008-results.json; this is
registered historical content access, not an authorized alternative reader.
None imports the new A023 runtime facade. A023 adds four source/test files and
changes no historical production feature. These are candidate evidence, not a
claim that all other nodes are Z0 or that the inventory is complete.

## Guarded collection and route stop

Executed only collection with activation before imports:

    MALECNS_A019C_R2_FIREWALL=1
    PYTHONPATH=<absolute repository>/scripts/a019c_firewall
    MALECNS_A019C_R2_LOG=C:/TEMP/a023r-collection-20261007.jsonl
    uv run python -m pytest --collect-only -q

Result: **1503 collected**, one existing CUDA_PATH warning. Log contains one
active event and no blocked event. Accepted protected reads 0; denied reads 0
for collection. Raw output: C:/TEMP/a023r-collection-20261007.txt.
This is not an executable-suite pass. Z0/Z1/Z2 final counts and complete exact
node classification are NOT ESTABLISHED; only the five Z1 candidates above are
proven here. No selected executable suite or selection manifest was added.

A concrete payload-independent route conflict was identified before execution:
tests/test_application_a007b.py::test_full_sweep_and_retention_stress measures
full_sweep_seconds, comparison/playback/subgraph seconds, export_seconds and
result_construction_seconds using perf_counter, then prints
A007B_SYNTHETIC_MEASUREMENTS. All-Z0 execution includes this node, whereas the
current authorization forbids timing harnesses/performance data. It cannot
truthfully be excluded as REGISTERED-PAYLOAD-REQUIRED. No test was edited,
skipped, timed, or executed to resolve this conflict.

Also, tests/test_application_a011.py::test_http_ui_assets_and_commands launches
bare node with tests/js/application_a011.cjs. Static guard admission permits
only the exact A006R/A007C Node contracts, so the unchanged guard rejects it.
This is a child-route compatibility issue, not a proven guard defect or Z1 node.
No new child admission or replacement historical assertion was introduced.

The required integrity script independently reads data/provenance and
data/derived via Path.read_bytes, including male-cns-v1.0.json. The existing
guard denies these before content. An ordinary guarded integrity PASS is
therefore unavailable under this boundary. This was established statically;
the checker was NOT RUN, and its required assertions were not weakened.

## Gates and custody

G1–G15 retain the original recorded PASS dispositions; no new reconfirmation
execution is claimed. Prior A023 27 passed / isolated regressions 124 passed /
bootstrap 39 passed remain historical results. G16 NOT PASS.
ZERO-PAYLOAD FULL VALIDATION NOT RUN. Final executable pass/fail/skip/xfail and
read counts are N/A; collection counts must not be substituted for them.
Compileall, build and integrity NOT RUN in recovery because the prerequisite
zero-payload execution has not passed. git diff --check PASS before report edits;
final report diff verification is recorded in the user-facing custody result.

No benchmark, timing harness, profiler, full-real preparation/advance, Arena or
intervention execution, payload content access, downloads or archive writes.
No test weakening, hidden skips, guard bypass, commit, push, version bump, tag,
release or publication. Candidate 0.4.0; current package remains 0.3.0.

Exact next task: **A023-R2 — resolve the all-Z0 execution authorization conflict
for the existing synthetic timing test, define a certified A011 child route
without weakening safety, and adjudicate the required protected-metadata
integrity gate; then finish static classification and guarded validation.**
This report grants no authority for payload reads or performance execution.

## A023-R2 (2026-10-07): contract-violation stop

Authorization: **授權 A023-R2**. Terminal classification:
**A023-R2-CONTRACT-VIOLATION**. Overall **A023-B** remains; G16 NOT PASS.
The A023-B and A023-R-B history above remains unchanged.

Root was dynamically derived as D:/spider/working/MaleCNS-Sim. Starting local
HEAD, origin/master and live origin refs/heads/master were exactly
c5ad89377575592665344f6420126b16c29b4339. Baseline status had exactly the six
authorized untracked files, no tracked changes, empty staging and stash,
version 0.3.0 and zero tracked workflows. Starting SHA-256 fingerprints:

| File | SHA-256 |
| --- | --- |
| src/malecns_sim/runtime.py | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | 7c4d5f60f8077bfe064b8b3626e8f80f8e644c1d7469124d8e149f5e18ae3c58 |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 7db6e306227399eaea19dceef372c8a28f896d9e494e2c5452b05b823c95a5bd |

All four original runtime/test fingerprints match A023-R exactly. Before edits
or new tests, guarded ordinary collection again yielded **1503 nodes**. Startup
activation used MALECNS_A019C_R2_FIREWALL=1 and absolute firewall PYTHONPATH.
Collection output: C:/TEMP/a023r2-collection-20261007.txt; guard log:
C:/TEMP/a023r2-collection-20261007.jsonl. The log contains one active event and
no blocked events. Collection accepted registered reads 0 under the existing
interception contract; collection denied reads 0.

### Stop cause and accounting limitation

During subsequent static source inspection, a native `rg` command intended to
search tests returned repository-wide matches, including uv.lock, README.md
and historical plans. It was outside the Python guard. The command's output
was heavily truncated, so its complete read scope cannot be reconstructed
from the returned evidence. The repository .gitignore does not exclude
data/provenance; a broad search cannot therefore be certified payload-free.
This violates the task's fail-closed zero-content boundary. No registered
content is reproduced here. **Accepted registered reads for the entire R2
turn are UNKNOWN, not a certified zero.** The zero counters from guarded
collection must not be generalized to the unguarded search.

Work stopped immediately on recognizing this scope violation. No test-suite
execution, child launch, benchmark, profiler, real preparation/advance,
compileall, build, integrity checker, commit or push followed it. Only this
incident record and the implementation-report pointer were added.

### Findings established before stop; not route certification

- A007B test_full_sweep_and_retention_stress: **T0**, based on inspected source.
  Timing values are collected and printed but do not participate in acceptance
  assertions. Its assertions cover correctness, orchestration and retention.
  It was NOT RUN; no emitted timing was used as performance evidence.
- A011 test_http_ui_assets_and_commands: **C2**, based on inspected source.
  Its bare Node argv is not one of mandatory_child's exact A006R/A007C
  admitted contracts. guarded_command rejects the non-Python executable.
  The mandatory Python child entry does not supply an alternate Node admission.
  No child route was certified, no guard defect was proved, and no admission
  contract, historical test or assertion was changed. Tentative policy
  disposition is Z3-BLOCKED; safe exclusion was not established.
- I0: A023 source/test/doc additions are disjoint from protected evidence;
  their starting fingerprints were captured. Release-safe corruption checking
  was not implemented or certified.
- I1: check_tracked_integrity.check reads every PINNED_SHA256 entry, including
  four protected data/provenance or data/derived entries, then checks protected
  content relationships. Full protected integrity is explicitly **NOT RUN**.
- I2: Path.is_file and constant/schema inspection are metadata-only operations;
  the checker exposes no existing metadata-only or zero-payload mode. No
  sufficient split or acceptance policy was certified.

The five R1 Z1 candidates remain retained evidence, not a complete Z1 inventory.
No complete taxonomy manifest was produced: Z0/Z1/Z2/Z3 counts are NOT
ESTABLISHED. Unexamined nodes are not asserted Z0. No validation runner,
selection manifest, integrity mode or R2 tests were added. Final collection
remains the baseline 1503; executable selected/passed/failed/skipped/xfail,
Z1/Z3 exclusions and final-suite denial counts are N/A because no final suite
ran. ZERO-PAYLOAD RELEASE-SAFE VALIDATION **NOT RUN**.

G1-G15 retain prior PASS history only, without new R2 execution reconfirmation.
G16 NOT PASS. Compileall/build/zero-payload integrity NOT RUN. Protected-content
integrity NOT RUN; no partial check is represented as full integrity PASS.
No tests were weakened, hidden skips added, historical results rewritten,
production semantics changed, version bumped, tag/release/publication made,
or A019 performance work reopened. No reset/stash/discard was used.

Exact next task: bounded incident adjudication and fail-closed static-inspection
recovery before any further A023 validation. Do not start A024. This report
does not certify recovery or authorize protected content access.

## A023-R3 (2026-10-07): incident adjudication and static-inspection certification

Authorization: **授權 A023-R3**. Terminal classification:
**A023-R3-A — R2 INCIDENT ADJUDICATED; FAIL-CLOSED STATIC-INSPECTION ROUTE CERTIFIED.**
Overall **A023-B** remains; **G16 NOT PASS**. Preserve A023-R-B and
A023-R2-CONTRACT-VIOLATION. R4 has NOT started.

### Incoming custody and freeze

Repository root was dynamically derived by `git rev-parse --show-toplevel` as
D:/spider/working/MaleCNS-Sim. Starting HEAD, origin/master and live GitHub
refs/heads/master all equal `c5ad89377575592665344f6420126b16c29b4339`.
Metadata-only status established exactly the six incoming untracked files,
empty staging and stash, and no tracked changes. Existing additional detached
worktree .kilo/worktrees/clarity-mare is at the same SHA and was left untouched.
Explicit control-file inspection established version 0.3.0; tracked filename
inventory established zero .github/workflows entries.

SHA256 and byte lengths captured before R3 edits (content hashing was expressly
authorized for these six exact incoming paths):

| Incoming file | Bytes | SHA256 |
| --- | ---: | --- |
| src/malecns_sim/runtime.py | 11186 | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 86 | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 2349 | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 10879 | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | 9437 | 2b7b85b38a1a11358ed5b0509e79f708fcbb39402fbe9df87244c648a7af38c8 |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 13919 | d466cd99f653ba25b3220c5cc113e849b94834aa26ff5085f573418c5ae0600e |

All four source/test identities match the retained R1 record. Explicitly reading
the two reports confirmed retained R1/R2 recovery history; only their fingerprints
evolved from earlier custody records. No unrelated WIP exists. R3 never edits
the four source/test files or the original implementation report.

### R2 adjudication: IR3

**IR3 — ACTUAL PROTECTED READ UNKNOWN; ZERO-READ CERTIFICATION INVALID.**
The retained R2 report identifies a native `rg` command intended to inspect tests.
The exact argv is not recoverable from the evidence available in this run; no
command reconstruction is invented. Observed results included uv.lock, README.md
and historical plans outside the intended tests boundary. Native content search
must inspect file content to find content matches. Its returned output was
truncated and no complete file-open/read telemetry is retained. Matching output
does not identify every file opened, including files with no matches.

Correct incident wording: **native content-search scope escaped the intended
boundary; complete read scope is unavailable; therefore zero-read attestation
is invalid.** Protected paths can be proven neither included nor excluded.
Actual protected read occurrence = **UNKNOWN**; task-wide registered-payload
reads for R2 = **UNKNOWN**; zero-read attestation = **NOT CERTIFIABLE**.
This does not prove protected payload was read. R2 guarded collection separately
recorded accepted reads 0 and denied reads 0 under its interception contract;
those counters do not cover the native search. The incident invalidates R2
zero-read custody only, not independently guarded prior A023/A023-R results.

### Bootstrap and protected-path authority

PATH DISCOVERY is metadata-only: git status, rev-parse, ls-remote, ls-files,
ls-tree, worktree/stash inventory and filesystem stat metadata as appropriate.
Use git ls-files for filename inventory; it does not open file contents.
CONTENT INSPECTION is exact-path, preclassified, audited and fail-closed.

Bootstrap content access was explicitly limited to the six authorized fingerprint
targets, the two named reports, pyproject.toml, and the metadata-identified control
source scripts/a019c_firewall/validation_firewall.py. No references were followed.
The known-safe guard control has 7946 bytes and SHA256
170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af.
These explicit bootstrap reads and hashes are the pre-inspector audit inventory.
They included no registered payload. The guard control is the permitted reviewed
bootstrap exception; no payload was opened to learn registration.

The unchanged guard exposes `check(source)`: it resolves the path and applies
DENIED_ROOTS (repository data/ and optional MALECNS_DATA_ROOT) plus registered
release-name protections. The adapter calls that exact function on each canonical
regular-file target. SourceAccessDenied means PROTECTED; any other classification
exception means UNKNOWN; normal return on this validated path means SAFE under
the existing guard definition. There is no copied independent protection rule.
Existing check(), install(), interception and child-admission semantics are
unchanged. The helper never calls install(), imports pyarrow, or admits children.
The reviewed guard module's top-level execution loads only its control constants
and standard library; its import/reference functions are not followed.

### Inspector and operational protocol

Added validation infrastructure only:
scripts/a023_fail_closed_inspect.py and tests/test_a023_fail_closed_inspect.py.
The helper derives the root dynamically from the ancestor .git metadata marker,
then checks equality with the reused guard ROOT. It accepts explicit individual
relative paths only. Absolute paths, drives, wildcards, traversal, empty/dot
components, directories, symlinks and all Windows reparse points are rejected.
Hard-link ambiguity is also rejected. Canonical custody and file identity are
checked before open and rechecked after classification. UNKNOWN fails closed.
There are no child commands, shell searches, recursive requests, or automatic
import/include/reference discovery. Every additional target requires its own
explicit argument and ledger event.

Run only the reviewed helper under the base standard-library-only interpreter
mode `-I -S -B`. Its fixed guard bootstrap is exact-path, metadata-checked,
ledgered and SHA256-pinned; a changed guard identity stops the route. Its own
source is also fingerprinted through the reader. The interpreter necessarily
loads the exact named helper source at startup; this is a reviewed control-source
load, not discovered target content. For the isolated self-tests, the interpreter
loads exactly the named new test source, which explicitly loads the new helper.
Compileall is restricted to these same two new files. These authorized validation
control reads are distinct from canary target reads. The ledger records every
explicit content open performed by the helper, including bootstrap/control reads;
it is not universal OS read telemetry or a count of interpreter startup rereads.
All repository content paths opened in the canary are identified below.

Each event distinguishes metadata checking from content opening and records path,
canonical path, role, decision, outcome, byte length and SHA256 for successful
reads. Rejected targets remain events with content_opened=false. Contents are
never stored in the ledger. Optional --emit emits only exact accepted requested
files, never automatically emitted control sources. The external ledger must be
new, is reserved before repository reads and is finalized even on failure.

Operational requirement: future A023 recovery must use this mechanism for
repository content inspection and must NOT use uncontrolled native recursive
content search. Ban rg, grep, git grep, findstr, Select-String, IDE recursive
search, tests-only recursive content search, wildcard readers, git log -S/-G,
and equivalent uncontrolled file-opening searches. Do not pass a directory or
glob to a content reader. Metadata inventory may be filtered as strings without
opening the listed files. This mechanism does not control arbitrary commands
outside itself and does not claim an OS sandbox against concurrent hostile
replacement of workspace files. Keep custody stable while inspecting; any
ambiguous or changed identity must stop the route.

### Self-tests and small canary

Direct isolated unittest invocation (no pytest or repository-wide collection):

    <repo>/.venv/Scripts/python.exe -I -S -B tests/test_a023_fail_closed_inspect.py

**12 tests PASS; zero skips.** Coverage: exact safe content and length/hash ledger;
wildcards, directories, traversal, outside absolute paths; actual synthetic
symlink escape, synthetic reparse metadata and actual hard-link ambiguity;
PROTECTED and UNKNOWN before-open rejection; classification exceptions;
explicit multiple-file enumeration, no reference following and exact opened-file
ledger. Path.open sentinels prove rejected targets are never opened or counted
as opened content. Fixtures are temporary synthetic content only. No real guard
weakening was used. Unit-framework elapsed output is not performance evidence.

Compileall restricted to the new helper and new test: **PASS, exit 0**.
No A023 source compilation or broader validation was performed.

Canary command used the same isolated interpreter and helper with --emit,
--ledger C:/TEMP/a023r3-canary-20261007.json, followed by exactly these four
separately enumerated targets: the recovery report, tests/test_application_a011.py,
tests/test_application_a007b.py, and scripts/a019c_firewall/validation_firewall.py.
Each requested file classified SAFE before opening. Requested 4, accepted 4,
rejected 0; **PASS, exit 0**. No referenced dataset was opened. Content-output
truncation does not lose read scope: the independent ledger is complete.

Opened-content ledger, in event order:

| Role/path | Bytes | SHA256 |
| --- | ---: | --- |
| Bootstrap: scripts/a019c_firewall/validation_firewall.py | 7946 | 170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af |
| Control: scripts/a023_fail_closed_inspect.py | 7278 | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| Requested: docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 13919 | d466cd99f653ba25b3220c5cc113e849b94834aa26ff5085f573418c5ae0600e |
| Requested: tests/test_application_a011.py | 8292 | ae5ebc50a2a0331e6f8ca24ab75bc8159f6b0d3cc143bf200e236af6e13f3bd7 |
| Requested: tests/test_application_a007b.py | 22712 | f06b09b486c32f85e4671375844069f5dc78d2c02095f8c284ef25e7111317f0 |
| Requested: scripts/a019c_firewall/validation_firewall.py | 7946 | 170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af |

Ledger count: **6 explicit content-open events, 5 distinct repository paths**.
All SAFE. **Protected content opens = 0**. The report fingerprint is its incoming
pre-append snapshot, intentionally not the final report hash. The ledger resides
outside the repository and is also reproduced here without file contents.

### Closure and exact next task

Only the existing recovery report changed, plus the two new infrastructure files.
Final four original A023 runtime/test hashes remain equal to the incoming values;
the implementation report and existing guard remain byte-identical. Known-R3-file
whitespace/diff checks PASS: explicit `git diff --no-index --check` against
/dev/null emitted no whitespace-error diagnostics for each of the three R3
files (exit 1 denotes the untracked additions; LF/CRLF conversion warnings
are not whitespace-error findings). Final exact-path inspection also PASS;
ledger C:/TEMP/a023r3-final-inspection-20261007.json records five explicit
content-open events: guard bootstrap, helper control, and the three R3 files.
That report snapshot precedes this closure-detail append; no snapshot hash is
represented as a final-report self-hash. Final committed local/origin/live SHA remains
c5ad89377575592665344f6420126b16c29b4339. Worktree has exactly eight untracked
files: the six incoming files plus the helper and self-test. Tracked changes,
staging and stash remain empty. Existing worktrees are preserved. Version 0.3.0,
tracked workflows 0. No clean/reset/stash/discard/commit/push occurred.

R3 uncontrolled native repository content searches = 0. Simulations, A023 runtime
executions/tests, CPU/GPU correctness regressions, performance timing, profilers,
full-real preparations, real advances, downloads, archive writes, interventions
and Arena runs = 0. R3 registered payload content reads through this route = 0;
no other R3 payload-content access occurred. R2 actual protected-read occurrence
remains UNKNOWN. A007B/A011 were inspected only; neither was executed. Integrity,
full-suite pytest, taxonomy execution, build and G16 attempt were NOT RUN. No
version bump, tag, release or publication. No scientific experiment or claim.

Exact next task: **A023-R4 — use the certified fail-closed inspection route to
complete the full Z0/Z1/Z2/Z3 taxonomy, resolve A007B/A011/integrity dispositions,
construct the guarded release-safe validation route, and attempt G16; no
uncontrolled native content search.** Do NOT start R4 under R3 authorization.

## A023-R4 (2026-10-07): baseline collection mismatch stop

Authorization: **授權 A023-R4**. Terminal classification:
**A023-R4-B — ONE RELEASE-SAFE VALIDATION BLOCKER REMAINS.**
Overall **A023-B** remains. G16 NOT PASS. This is a collection-contract
blocker, not a proven runtime or validation/guard infrastructure defect.
The required 1503-node taxonomy cannot be certified against the actual
1515-node incoming collection without adjudicating baseline accounting.

### Custody and incoming fingerprints

Root dynamically derived with git rev-parse --show-toplevel:
D:/spider/working/MaleCNS-Sim. Local HEAD, origin/master and live GitHub master
all equal c5ad89377575592665344f6420126b16c29b4339. Exactly eight incoming
untracked files, no unrelated WIP, staging empty, stash empty, version 0.3.0,
tracked workflows zero. Existing detached clarity-mare worktree preserved.
All eight SHA256 fingerprints captured before report edits:

| File | SHA256 |
| --- | --- |
| src/malecns_sim/runtime.py | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | 2b7b85b38a1a11358ed5b0509e79f708fcbb39402fbe9df87244c648a7af38c8 |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | d19e4fdbab29c27096718d7f16473ced3cd2a33f621d00abfdb6ca5fc7c83af9 |
| scripts/a023_fail_closed_inspect.py | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| tests/test_a023_fail_closed_inspect.py | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |

Original four runtime/test hashes match retained R1/R3 identities. Inspector
hash matches the R3 report; inspector and test hashes both match external
C:/TEMP/a023r3-final-inspection-20261007.json. Guard bootstrap identity remains
170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af.
R3 route and guard unchanged. R1/R2/R3 history preserved. R2 remains IR3:
actual protected read occurrence UNKNOWN; R2 zero-read attestation INVALID.

### Guarded collection and mandatory stop

Startup configuration before imports/collection:
MALECNS_A019C_R2_FIREWALL=1; PYTHONPATH set to absolute repository
scripts/a019c_firewall; MALECNS_A019C_R2_LOG set to external collection log.
Executed uv run python -m pytest --collect-only -q, exit 0.
**1515 tests collected**, with 1515 distinct exact node IDs and zero duplicates.
Expected baseline: **1503**. No R4 tests were added.

Output: C:/Users/spider.tp/AppData/Local/Temp/a023r4-collection.txt.
Guard log: C:/Users/spider.tp/AppData/Local/Temp/a023r4-collection.jsonl.
One active event, no blocked events. Accepted registered reads 0 under the
unchanged guard interception contract; denied reads 0. This is not a separate
OS-level accepted-read counter or executable test-suite result.

Exactly 12 collected nodes belong to the incoming R3 self-test module:

- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_absolute_outside
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_classifier_exception_before_open
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_directory
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_exact_safe_content_and_ledger
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_explicit_multiple_no_following_exact_ledger
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_hardlink_ambiguity
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_protected_before_open
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_reparse_attribute_before_open
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_symlink_escape
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_traversal
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_unknown_before_open
- tests/test_a023_fail_closed_inspect.py::InspectorTests::test_wildcards

1515 minus these 12 equals 1503, explaining the numerical discrepancy. This
arithmetic does not certify historical exact-node set equivalence. No ignore,
subtraction, test relocation or alternate collection was used to satisfy the
frozen baseline. The explicit collection-drift STOP gate was honored.

### Inspection, policy findings and uncompleted gates

All repository target content inspection used the exact-path R3 inspector;
external ledgers are a023r4-initial-inspection.json,
a023r4-policy-inspection.json, a023r4-child-inspection.json and
a023r4-report-confirmation.json under the system temporary directory above.
All opened targets classified SAFE; protected content opens zero. The policy
inspection rejected the nonexistent mandatory_child.py target at metadata
checking before open; remaining targets were subsequently explicitly inspected
through a new ledger. No automatic references or uncontrolled native repository
content searches/reads occurred. The only native rg invocation searched the
external memory registry, not repository content; no memory finding was relied on.
Exact incoming-file hashing was the expressly requested custody operation.

A011 test_http_ui_assets_and_commands source and unchanged guard launch helpers
reconfirm **C2**: bare Node is outside the exact A006R/A007C contracts. No safe
A011 child route or justified terminal exclusion certified; final A011
RUN/NOT-RUN/BLOCKED disposition remains unestablished after the baseline STOP.
No child executed. No historical assertion or guard admission changed.
A007B retains historical tentative T0 only; no fresh R4 source reconfirmation
or execution occurred. Timing interpreted as performance evidence: No.

Complete Z0/Z1/Z2/Z3 counts, final exact Z1 inventory, terminal Z3 inventory,
A023-modified coverage mapping and integrity I0/I1/I2 split: **NOT ESTABLISHED**.
The five previously recorded Z1 candidates remain historical candidates,
not a complete R4 taxonomy. No unexamined node asserted Z0. Protected-content
integrity: **NOT RUN — REGISTERED-PAYLOAD-REQUIRED**. Unprotected/A023 integrity
and I2 certification: NOT RUN / NOT CERTIFIED. No integrity PASS claim.

Release-safe runner/manifest/integrity helper: not added. Route self-tests,
final route collection/execution, selected/excluded counts and executable
passed/failed/skipped/xfail/xpass: N/A; no test execution in R4.
ZERO-PAYLOAD RELEASE-SAFE VALIDATION: **NOT RUN**.
G1-G15 retain historical PASS records only, not R4 reconfirmation; G16 NOT PASS.
Targeted A023 and CPU/GPU correctness regressions NOT RUN in R4.
Compileall, uv build and integrity NOT RUN because the prerequisite failed.

### Closure and nonclaims

Only this append and an implementation-report stop pointer are R4 edits.
All source/test/guard bytes preserved. git diff --check and exact report
no-index whitespace checks PASS; cached diff check PASS, staging empty.
Final inventory remains the same eight untracked files. Local/origin/live SHA
unchanged; staging/stash empty; version 0.3.0; tracked workflows zero.
No tests weakened, hidden skips, history rewritten, guard bypass/weakening,
performance/profiler/A019 runs, full-real preparation/advance, Arena or
intervention execution, downloads, archive writes, commit, push, version bump,
tag, release or publication. No full pytest PASS or G16 PASS is claimed.

Exact next task: **adjudicate the A023-R4 baseline accounting contract:
1503 historical nodes plus 12 existing R3 self-test nodes versus the incoming
1515-node ordinary collection; freeze explicit baseline/infrastructure sets,
then resume the complete guarded taxonomy and policy-resolution work.**
Do NOT start A024.


## A023-R5 (2026-10-07): exact sets frozen; A011 policy stop

Authorization: **?? A023-R5**. Classification **A023-R5-B**; overall **A023-B**; G16 NOT PASS.
Exactly one named blocker: **A011 C2 has no certified guard-compatible execution route or certified regression-safe exclusion**. Phase 6 requires STOP for Z3-BLOCKED. No guard defect is claimed. R1-R4 history preserved.

Root dynamically derived: D:/spider/working/MaleCNS-Sim. Starting local HEAD, origin/master and live GitHub master all c5ad89377575592665344f6420126b16c29b4339. Exactly eight expected incoming untracked files; staging/stash empty; version 0.3.0; tracked workflows zero. Incoming SHA256:

| File | SHA256 |
| --- | --- |
| src/malecns_sim/runtime.py | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | ea29123e74757c82a618dd1f94a359c58884c454afc77309bafa47f810ae3ea0 |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 4667dd562e96bbb8b88dfabd52d7c2e982c7ff3ac5652d4cab14da0f2115c185 |
| scripts/a023_fail_closed_inspect.py | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| tests/test_a023_fail_closed_inspect.py | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |

Four original source/test identities match R1/R3/R4; inspector/test match retained R3 identities. None was edited. Implementation report unchanged because R5 closure was not reached.

### Exact collection accounting

Before any new tests, guard activation environment was set before imports: MALECNS_A019C_R2_FIREWALL=1, absolute scripts/a019c_firewall PYTHONPATH, external log. uv run python -m pytest --collect-only -q exited 0: **1515 distinct nodes, zero duplicates**. Output/log: C:/Users/spider.tp/AppData/Local/Temp/a023r5-collection.txt and a023r5-collection.jsonl. One active event, no blocked events.

Exact collected R3 module nodes define I. H is the authorized exact set difference. Sorted manifests: docs/manifests/a023-validation-baseline-h.txt (**1503**) and a023-validation-infrastructure-i.txt (**12**). N is the empty set (**0**). H/I/N pairwise disjoint, exact union equals observed collection, missing/extra zero. No tests added or changed after collection. This is the authorized R5 H definition, not proof of an independently reconstructed historical snapshot. Do not silently regenerate H. Manifest self-tests have not run.

### Policy evidence and mandatory stop

All repository target inspection used the R3 helper under python -I -S -B with fresh external ledgers a023r5-inspect-01.json through -04.json. Inspector 02 rejected nonexistent mandatory_child.py at metadata checking before open; actual functions were inspected in validation_firewall.py and exact a006r_node.py, a007c_node.py, guarded_child.py paths. No protected content opened; no uncontrolled repository content search/read. The external memory lookup produced no relevant finding and was not relied upon.

A007B: tests/test_application_a007b.py::test_full_sweep_and_retention_stress is **T0 / Z3-RUN** conditional on the eventual acceptance gate. Source reconfirms timing is printed but not compared in acceptance assertions. NOT RUN. Timing used as performance evidence: No.

A011: tests/test_application_a011.py::test_http_ui_assets_and_commands is **C2 / Z3-BLOCKED**. It runs HTTP/backend assertions then bare Node on tests/js/application_a011.cjs using synthetic arena.json and the static directory. The JS executes arena.js and asserts controls, revision handling and speed-clock behavior. guarded_command rejects non-Python executables except exact admitted contracts. A006R/A007C scripts, purposes, arguments and read grants differ; neither existing route preserves A011 semantics. guarded_child activates a Python guard but offers no alternate Node admission. No safe route certified, no child launched, no historical assertions changed. A safe exclusion has not been certified against a complete A023 coverage map. Phase 6 STOP occurred before final suite.

### Uncompleted gates and nonclaims

Persisted taxonomy a023-zero-payload-taxonomy.json explicitly says **INCOMPLETE - NOT ACCEPTED FOR EXECUTION**. Every H node appears once. Provisional Z0=0, Z1=0, Z2=1501, Z3=2 (RUN=1, BLOCKED=1, NOT-RUN=0). Z2 is unresolved, never asserted safe. Final Z1 inventory NOT ESTABLISHED; five historical candidates remain candidates, not final exclusions. No claim of zero payload-required nodes or unique-coverage adjudication. Complete taxonomy gate did not pass.

Integrity: I0 NOT RUN; I2 NOT CERTIFIED/NOT RUN; I1 **NOT RUN - REGISTERED-PAYLOAD-REQUIRED**. No full integrity PASS. Release-safe route/self-tests not implemented or run. Selected H execution/results, H final exclusions and I/N execution: NOT RUN / N/A. Mandatory infrastructure PASS requirement remains. ZERO-PAYLOAD RELEASE-SAFE VALIDATION **NOT RUN**. G1-G15 historical PASS only, not R5 reconfirmation; G16 NOT PASS. Compileall/build/integrity NOT RUN because prerequisites failed.

Accepted registered reads 0 under the inspected interception contract; collection denied reads 0. No separately emitted accepted-read counter or universal OS telemetry claimed. No tests weakened, history rewritten, guard bypass, performance/profiler/A019 activity, full-real preparation/advance, Arena/intervention execution, downloads or archive writes. No commit/push/version bump/tag/release/publication.

R5 changes: this report append plus the exact H/I manifests and provisional taxonomy. Final worktree inventory is these three new manifests plus the eight incoming files. No unrelated files. Final diff/cached checks and custody are reported in the final response.

Exact next task: **resolve A011 C2 terminal policy disposition against frozen H/I, then complete taxonomy, integrity split, mandatory manifest/route self-tests and guarded G16 recovery; record every added test as N**. No separate baseline-accounting task; do not start A024.

## A023-R6 (2026-10-07): execution-order contract-violation stop

Authorization: **授權 A023-R6**. Terminal classification:
**A023-R6-CONTRACT-VIOLATION**. Overall **A023-B** remains; **G16 NOT PASS**.
Preserve A023-B, A023-R-B, A023-R2-CONTRACT-VIOLATION, A023-R3-A,
A023-R4-B and A023-R5-B. No R6-A/B/C/D certification is substituted for
this execution-order incident.

### Starting custody and incoming fingerprints

Root dynamically derived with git rev-parse --show-toplevel:
D:/spider/working/MaleCNS-Sim. Starting local HEAD, origin/master and live
GitHub master all c5ad89377575592665344f6420126b16c29b4339.
Metadata-only Git inventory established exactly the eleven incoming untracked
files below, no tracked changes, empty staging and stash, and zero tracked
workflows. Exact inspected pyproject.toml reports version 0.3.0. The existing
detached clarity-mare worktree was preserved. No reset/stash/discard occurred.
All eleven incoming SHA256 fingerprints were captured before report edits:

| Incoming file | SHA256 |
| --- | --- |
| src/malecns_sim/runtime.py | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | ea29123e74757c82a618dd1f94a359c58884c454afc77309bafa47f810ae3ea0 |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | fc8dffc695380bae83aabadf6f3a0769d6e47e1811c2740c1ca607b22963f47e |
| scripts/a023_fail_closed_inspect.py | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| tests/test_a023_fail_closed_inspect.py | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |
| docs/manifests/a023-validation-baseline-h.txt | ec11f5ec29784519e315e8e551af5cf54f0583b4d147aff87d2ec7e09722048f |
| docs/manifests/a023-validation-infrastructure-i.txt | 3cd4f286f584873ba279a55c764c06f1df8b262c3b731f031955aafe9217d830 |
| docs/manifests/a023-zero-payload-taxonomy.json | a70af57bd719d7d544ef9a3caadf03060794f5143f2dc550e9743593e8832677 |

The four original A023 source/test identities match retained R1/R3/R4/R5
records. R3 inspector/test identities match their retained records. H and I
were inspected through the certified route, never regenerated, and retained
byte identity throughout this attempt.

### Initial exact H/I collection

Before adding any tests, startup activation was set before imports:
MALECNS_A019C_R2_FIREWALL=1; absolute scripts/a019c_firewall PYTHONPATH;
external MALECNS_A019C_R2_LOG. Guarded uv run python -m pytest --collect-only -q
exited 0. Observed **1515 distinct exact nodes**, zero duplicates:
H=1503, I=12, H intersection I empty; exact observed collection equals H union I;
missing/extra zero. N remains empty (0); no R6 tests were added.

External collection output/log:
C:/Users/spider.tp/AppData/Local/Temp/a023r6-collection.txt and
C:/Users/spider.tp/AppData/Local/Temp/a023r6-collection.jsonl.
Log: one active event, zero blocked events. This is collection evidence,
not an executable release-safe suite PASS.

### Inspection and preliminary A011 evidence

Repository content inspection used the unchanged R3 exact-path helper with
python -I -S -B and fresh external ledgers a023r6-inspect-01.json through
-09.json in the system temporary directory above. Requested repository files
were protection-classified before open and recorded in those ledgers. No
uncontrolled repository content search/read occurred. Metadata-only git ls-files
provided explicitly enumerated test paths for inspector 07. Subsequent AST
summaries and exact module views read only the external certified inspection
output, not repository paths. One external memory-registry search had no hits
and supplied no relied-upon memory fact. Incoming exact-path hashing was the
expressly authorized custody operation.

A011 historical command is bare Node with arguments:
node, tests/js/application_a011.cjs, a synthetic temporary arena.json,
src/malecns_sim/application/static. subprocess.run uses capture_output=True,
text=True, default shell=False, inherited environment and default handle policy.
The historical Python body starts a loopback HTTP server, asserts static assets,
authentication, one synthetic step, stale revision rejection and event output,
then invokes the JS. The JS reads the synthetic fixture and arena.js, evaluates
its controls in a VM context, and asserts control requests, revision handling
and render-speed clock behavior. No shell/wrapper or explicit inherited handle
is part of the historical command. Node is required for its JS assertions.
No protected registered payload was established as intrinsic to this command.

Exact C2 rejection: install replaces Popen.__init__; its child_init calls
original_init with guarded_command(args). guarded_command rejects Node because
it is neither an admitted exact A006R/A007C contract nor sys.executable, raising
SourceAccessDenied('unsupported A019 child executable') before original_init
and before child creation. It is not a child-registration or activation failure.
The audit hook also requires mandatory_child, but that is not the first rejection
for this bare command.

Existing A006R/A007C Node routes have different exact scripts, purposes,
arguments and filesystem read grants; neither preserves A011 semantics.
guarded_child installs a Python guard and provides no alternate Node admission.
No adequate existing compliant A011 route was found among the inspected routes.
No new child adapter, Node admission, guard weakening or historical test edit
was made. No child-route self-test or real A011 node execution occurred.

Preliminary independent-coverage evidence: the inspected A011 HTTP/UI path
uses the legacy lif runtime through server/Arena; inspected A023 tests directly
exercise the new CPU/GPU facades, independent states, preflight atomicity,
continuity, detached output, alias isolation and ordinary execution poisoning.
This supported investigating NOT RUN - CHILD-LAUNCH POLICY. It did **not**
complete a certified R6 terminal disposition. The commentary's statement that
the evidence supports Z3-NOT-RUN must not be read as certification. The persisted
A011 disposition remains **Z3-BLOCKED** in the unchanged provisional taxonomy.

### Actual execution-order incident and stop

While assessing the independent-coverage requirement, the agent ran:

    uv run python -m pytest -q tests/test_application_a023.py

under active startup guard, before certifying A011's terminal disposition and
before completing the R6 taxonomy/execution gate. Result: **27 passed, zero
failures/skips**, one existing CUDA_PATH warning. This included the bounded
synthetic GPU correctness test. External guard log:
C:/Users/spider.tp/AppData/Local/Temp/a023r6-a023.jsonl.
Log: one active event, zero blocked events.

The run was premature. General permission to run A023 correctness tests does
not waive R6's required execution order or certify the missing taxonomy gate.
The explicit terminal condition 'execution before taxonomy gate' therefore
requires **A023-R6-CONTRACT-VIOLATION**, even though the targeted tests passed
and the guard remained active. No release-safe PASS is inferred from this run.
The violation was recognized after further static inspection; no additional
test execution followed the targeted run. On recognition, task work stopped;
only this incident record, the implementation-report pointer and final custody
reporting followed. The R6 recovery objective is not achieved.

### Uncompleted gates and final nonclaims

A007B source was reconfirmed as **T0**: timing values are printed but do not
participate in acceptance assertions. Its tentative Z3-RUN is conditional on
the eventual taxonomy gate. A007B was **NOT RUN**. Incidental timing was not
used, compared or retained as performance evidence. Pytest framework elapsed
output is not performance evidence.

The taxonomy file remains byte-identical to incoming R5 and explicitly
INCOMPLETE - NOT ACCEPTED FOR EXECUTION: provisional Z0=0, Z1=0, Z2=1501,
Z3=2 (RUN=1, BLOCKED=1, NOT-RUN=0), total 1503. These are unresolved manifest
counts, not final scientific/payload classifications. Final Z1 inventory,
final terminal Z3 inventory and unique-A023-coverage adjudication are
**NOT CERTIFIED**. Additional inspected historical protected-content references
must be assessed in a later authorized recovery; no exclusion was manufactured.

I0 NOT RUN/NOT CERTIFIED; I2 NOT RUN/NOT CERTIFIED;
I1 **NOT RUN - REGISTERED-PAYLOAD-REQUIRED**. No helper or integrity split was
certified. N=0, no new infrastructure/tests. Initial exact collection remains
the only collection in R6; a final post-route collection was NOT RUN.
Route/self-tests, H-selected final execution, H final exclusions and mandatory
I/N execution: **NOT RUN / N/A**. The 27 targeted A023 passes belong to H but
are not a substitute for final H/I/N accounting.

Accepted registered reads **0 under the unchanged interception contract** for
the guarded collection and targeted run; denied reads **0** in both logs.
Certified inspection ledgers record zero protected content opens. This is not
a separately emitted accepted-read counter or universal OS-level tracing claim.
The incident is premature execution, not an established protected-content read.

ZERO-PAYLOAD RELEASE-SAFE VALIDATION **NOT RUN**. G1-G15 retain prior PASS
history only; all-gate R6 reconfirmation was not completed. G16 **NOT PASS**.
Compileall, uv build and release-safe integrity **NOT RUN**. No unconditional
full pytest/integrity PASS. No source/test/guard/manifests changed, historical
assertions weakened, hidden exclusions added or historical results rewritten.
No performance benchmark/profiler/A019 rerun, full-real preparation or real
advance, separate Arena/intervention experiment, download or archive write.
No commit/push/version bump/tag/release/publication.

R6 changes only the two existing untracked reports. Exact final untracked
inventory remains the eleven incoming paths listed above; no new file added.
Final Git diff checks, local/origin/live identity, original source/test/inspector/
manifest identity preservation, staging/stash and version/workflow custody are
reported in the final response after this append.

Next work requires a separately authorized adjudication of this premature
execution and a guarded continuation of the frozen H/I recovery. A024 is not
started or recommended as an eligible next task because R6-A was not reached.
# A023-R7 (2026-10-07): incident safety-scope stop

Authorization: **授權 A023-R7**. Terminal classification: **A023-R7-C — PREMATURE EXECUTION REVEALED A SAFETY-SCOPE PROBLEM**.
Incident classification: **PE3 — PREMATURE EXECUTION WITH UNKNOWN SAFETY SCOPE**.
Overall **A023-B**; **G16 NOT PASS**. All historical outcomes, including R6's contract violation, remain in force.

Starting and final committed custody: local HEAD, origin/master and live GitHub master equal `c5ad89377575592665344f6420126b16c29b4339`. Root derived dynamically: D:/spider/working/MaleCNS-Sim. Exactly eleven incoming untracked files; staging and stash empty. Detached clarity-mare worktree preserved. Version 0.3.0; tracked workflows zero.

## Eleven incoming SHA256 fingerprints, before edits

| File | SHA256 |
| --- | --- |
| src/malecns_sim/runtime.py | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | ed753c163eb9f975242f1a730a69720e41ef66a5d35935e100c214f55604be2b |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | b49f326fe282fd34a8d1f0a8ccfb83f8517737a0f53d0e1e333c2ccd22f8d70a |
| scripts/a023_fail_closed_inspect.py | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| tests/test_a023_fail_closed_inspect.py | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |
| docs/manifests/a023-validation-baseline-h.txt | ec11f5ec29784519e315e8e551af5cf54f0583b4d147aff87d2ec7e09722048f |
| docs/manifests/a023-validation-infrastructure-i.txt | 3cd4f286f584873ba279a55c764c06f1df8b262c3b731f031955aafe9217d830 |
| docs/manifests/a023-zero-payload-taxonomy.json | a70af57bd719d7d544ef9a3caadf03060794f5143f2dc550e9743593e8832677 |

Original four A023 source/test identities and R3 inspector/test identities match retained records. H/I match R5 custody: H=1503, I=12. No unrelated WIP. Incoming hashing is the authorized custody operation; repository inspection used only the unchanged certified inspector with Python -I -S -B and fresh external ledgers a023-r7-inspect-1.json through -5.json.

## Incident adjudication and evidence disposition

Retained R6 report recovers `uv run python -m pytest -q tests/test_application_a023.py`: 27 passed, zero failures/skips, one CUDA_PATH warning. The selected command names only A023 tests; importing helper modules does not establish execution of their test bodies. Retained report states the synthetic GPU test ran. No R7 repetition occurred.

The retained exact external log `C:/Users/spider.tp/AppData/Local/Temp/a023r6-a023.jsonl` was inspected: one active event, PID 9516, repository data denied root; no blocked events. Denied counter=0 events. Accepted registered reads=0 under the unchanged interception contract as retained in R6; no directly emitted accepted-read counter exists. Protected payload access is NOT PROVEN. This is not universal native/OS read telemetry.

The log has no general child-creation or file-write accounting. Absence of blocked events cannot establish that no child launched. Runtime state necessarily changed in the selected synthetic tests, but retained command/output does not attest whether all persistent effects were absent. R6 records unchanged production source/test/guard/manifests, supported by current retained byte identities and clean tracked status; this does not reconstruct transient writes. Pytest cache, bytecode, GPU-native cache and temporary-file creation/cleanup are not exhaustively inventoried in retained execution evidence. The current Git inventory excludes ignored artifacts and cannot prove their absence or origin. No complete execution-output file or incident before/after filesystem inventory was identified among metadata-discovered a023r6 external files. Thus child launch and residual/persistent artifact scope remain UNKNOWN. No actual protected-read breach is alleged. PE1 cannot be established from this evidence alone; PE3 prevents clean recovery certification.

The 27 PASS is frozen solely as **PREMATURE OBSERVATION — NOT ACCEPTANCE EVIDENCE**. It does not satisfy G15 or G16, replace later required A023 execution, count toward final release-safe selected-node totals, establish A011 disposition, or establish taxonomy completeness. It remains in history.

## Gate work withheld at the safety-scope terminal boundary

No gate/wrapper/test added, certified or invoked. No EXECUTION_AUTHORIZED or machine EXECUTION_DENIED result is claimed. Gate self-tests and compileall NOT RUN. Future gate must implement all twelve GATE-P1 through GATE-P12 prerequisites from the R7 authorization, default DENY on absent/malformed/provisional/drifting evidence, preserve mandatory zero-payload guarding, and expose no bypass/override. This is a pending requirement, not an implemented design certification.

Real blockers remain: taxonomy INCOMPLETE, Z2=1501, one Z3-BLOCKED/A011 C2, integrity I0/I2 unresolved, unique-A023 coverage not certified. A007B T0 was not executed. H/I unchanged; N7=0, exact node set empty. No H/I/N final execution, A023/A007B/A011/workload/regression execution, build, integrity checker, performance/profiler/full-real activity, guard change, uncontrolled repository content search, commit/push, version bump, tag/release/publication occurred in R7. Only this existing report changed; final eleven-file WIP inventory remains the incoming list above. Git diff --check passed before this report edit; final checks are reported separately.

Exact next task: separately authorize recovery of retained R6 child-launch and persistent-artifact evidence sufficient to resolve PE3, or an explicit adjudication of those evidence limits; then resume fail-closed validation-gate implementation and certification. **Do not start A023-R8 or attempt G16 while this safety-scope problem remains unresolved.** R8's taxonomy/A011/integrity/final-execution objective remains deferred.

## A023-R8 (2026-10-07): retained/static safety-scope adjudication

Authorization: **授權 A023-R8**. Terminal classification:
**A023-R8-C — R6 SAFETY SCOPE REMAINS UNRESOLVED AND CANNOT YET BE ISOLATED**.
Incident disposition: **PE3-UNRESOLVED**. Overall **A023-B**, implementation
partially complete; **G16 NOT PASS**. Preserve all R1-R7 history, specifically
A023-R6-CONTRACT-VIOLATION and A023-R7-C / historical PE3. No G16 recovery
or validation-gate certification followed this adjudication.

### Phase 1: incoming custody

Root dynamically derived by git rev-parse --show-toplevel:
D:/spider/working/MaleCNS-Sim. Local HEAD, origin/master and live GitHub master
all equal **c5ad89377575592665344f6420126b16c29b4339**, before inspection.
Exactly eleven untracked WIP files; no tracked changes, staging empty, stash
empty. Main master worktree and existing detached clarity-mare worktree at
that SHA were preserved. Package version 0.3.0, zero tracked workflows.
Incoming authorized SHA256/length capture preceded repository inspection:

| Exact incoming path | Bytes | SHA256 |
| --- | ---: | --- |
| src/malecns_sim/runtime.py | 11186 | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| src/malecns_sim/experimental/__init__.py | 86 | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 2349 | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| tests/test_application_a023.py | 10879 | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | 10727 | ed753c163eb9f975242f1a730a69720e41ef66a5d35935e100c214f55604be2b |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 58398 | fb367ca11c81ffe9d22070c25864f1da61e37f2477ee19ac3174fa28ccf89aa7 |
| scripts/a023_fail_closed_inspect.py | 7278 | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| tests/test_a023_fail_closed_inspect.py | 4680 | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |
| docs/manifests/a023-validation-baseline-h.txt | 119921 | ec11f5ec29784519e315e8e551af5cf54f0583b4d147aff87d2ec7e09722048f |
| docs/manifests/a023-validation-infrastructure-i.txt | 1004 | 3cd4f286f584873ba279a55c764c06f1df8b262c3b731f031955aafe9217d830 |
| docs/manifests/a023-zero-payload-taxonomy.json | 420766 | a70af57bd719d7d544ef9a3caadf03060794f5143f2dc550e9743593e8832677 |

Original four A023 runtime/test hashes match retained R1/R3/R6/R7 custody.
R3 inspector/test, H/I and taxonomy hashes match retained custody. The original
implementation report matches R7. Only this recovery report receives an append.
No new repository helper, production change or test change was necessary.

### Inspection protocol and exact evidence inventory

The existing inspector's help was invoked once without requested content; it
opened no requested repository content. Every subsequent repository inspection
used python -I -S -B scripts/a023_fail_closed_inspect.py, explicit individual
paths, pre-open classification and a fresh external ledger. No recursive or
uncontrolled repository content search/read occurred. Metadata discovery used
Git filename/status/worktree commands and exact filesystem metadata. An external
memory-registry query found no relevant A023 record and supplied no audit fact.
AST summaries read only external outputs already emitted by the certified route.
No repository AST reader or alternate inspection route was introduced.

External evidence directory: C:/Users/spider.tp/AppData/Local/Temp/.
Ledgers use the exact prefix a023-r8- and suffix -20261007.json:
report, test, graph1, graph2, control, graph3, infra, pytest, entry, graph4,
graph5, graph6, graph7, graph8, before; final report inspection uses after.
Graph3 through graph8 accepted output is retained in corresponding .txt files;
before/after retain certified report output. These are external inspection
artifacts created in R8, not reconstructed R6 telemetry.

Requested repository graph, following actual imports and selected helpers only:
- tests/test_application_a023.py; tests/test_task005.py (_projection/_signed);
  tests/test_application_a011.py (stimulus and module import effects).
- pyproject.toml; src/malecns_sim/__init__.py; runtime.py;
  experimental/__init__.py and experimental/gpu.py.
- dynamics/__init__.py, lif.py, stimulus.py, cuda.py and cache.py.
- data/__init__.py, model.py, normalize.py, neurotransmitter.py, io.py,
  male_cns_v1.py, provenance.py and shiu_v630.py.
- graph/__init__.py, signed.py, sparse.py and fingerprint.py; sign.py; homology.py.
- application/__init__.py, arena.py, errors.py, events.py, models.py,
  service.py, serialization.py and preparation.py.
- analysis/__init__.py, benchmark.py, task007.py, task007a.py, task007b.py,
  shiu_v630.py, task008.py, task008a.py, task011.py and task010.py.
- scripts/a023_fail_closed_inspect.py, scripts/a019c_firewall/validation_firewall.py
  and scripts/a019c_firewall/sitecustomize.py; named recovery report.

The analysis modules are imported through application.service when importing
application.arena for the A011 stimulus helper. Their workload functions were
inspected statically and never invoked. Protected path literals in control
source were not followed. No protected contents were inspected or hashed.

### Phases 2-3: child seams and infrastructure boundary

Exact premature command, never recreated in R8:

    uv run python -m pytest -q tests/test_application_a023.py

The 27 selected cases use bounded synthetic _projection/_signed and stimulus,
monkeypatch, CPU facade/engine and one experimental GPU facade test. The only
explicit requested pytest fixture is monkeypatch; no tmp_path, server fixture,
process pool, multiprocessing, os.system/popen, shell, browser, Node or child
pytest runner is called by these test bodies. pickle.dumps is a serialization
attempt that the opaque objects reject; it does not write a pickle file.

| Seam | Classification | Static/retained disposition |
| --- | --- | --- |
| Selected A023 Python bodies, _projection/_signed, stimulus, CPU facade/lif/event functions | CP0 | No process-launch call on these inspected paths. |
| A011 HTTP/Node test body | CP0 for this selection | Imported module defines it; selected A023 cases call only stimulus. Its local server/Node imports and execution remain inside the unselected function. |
| application.service Git identity subprocess.run calls; analysis.task010/task011 Git subprocess calls | CP0 for this selection | Dormant function bodies; not called by selected synthetic helpers or import-time constants. |
| Repository pytest configuration | CP0 for configured launch options | pyproject sets testpaths=tests and addopts=-ra; no configured plugin/worker/child runner. Metadata inventory finds no repository conftest.py, pytest.ini, setup.cfg or tox.ini. Exact ancestor conftest metadata probes find none. |
| GPUPreparedRuntime -> CuPy RawKernel(...).compile(); CuPy array/kernel operations and native CUDA initialization | CP3 | A reachable native/compiler seam, not proof a child actually launched. External compiler subprocess/native-helper capability and authority cannot be closed from the available permitted source evidence. |
| Installed pytest plugin/configuration/fixture internals, historical external plugin/environment injection | CP3 | No retained complete loaded-plugin list or historical environment identity; installed inspection was rejected as detailed below. |
| Any child actually created through the preceding CP3 dependency seams | CP2 conditional | Exact historical occurrence, argv, lifetime and guard/authority scope are not retained. Do not assert a child existed. |

No CP1 child was affirmatively identified. Retained R7 inspection of the R6 log
records one active event, PID 9516, no blocked events; it accounts for startup
activation of the Python pytest process under the inspected contract. It is
not a child census, descendant-lifetime report or native launch/write tracer.

The uv launcher and its Python pytest process are ordinary infrastructure.
Their existence is not itself a safety violation. The Python process startup
activation is retained; uv's environment preparation and any plugin/native
helpers do not gain universal guard accounting from that event. No retained
uv synchronization/dependency-write inventory or complete plugin inventory
establishes those historical boundaries. R8 did not execute uv or pytest.

Guard source remains SHA256
170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af.
Its Popen wrapper rejects shell children, routes ordinary Python argv through
mandatory guarded_child, and admits only exact existing child contracts.
This is useful enforcement evidence for intercepted Popen paths, not proof
that no native process launch or arbitrary write outside interception occurred.

Three explicit dependency inspection attempts failed CLOSED before requested
content open (metadata_checked=false, content_opened=false):
- .venv/Lib/site-packages/cupy/cuda/compiler.py (infra ledger);
- .venv/Lib/site-packages/_pytest/config/__init__.py (pytest ledger);
- .venv/Lib/site-packages/pytest-9.1.1.dist-info/entry_points.txt (entry ledger).

All failures are **hard-link protection identity UNKNOWN**. No hard-link
exception, dependency copy, alternate cache source or bypass was used. The
infra request contained other exact pytest/cache/temp/rewrite/entry-point paths,
but stopped at its first target; those later targets were NOT opened and are
NOT described as inspected. Filename-only dist-info inventory identifies
installed packages, not their historical plugin behavior. Installed dependency
and native closure therefore remains incomplete. This compliant rejection is
not A023-R8-CONTRACT-VIOLATION and is not evidence of protected access.

Answer to the direct launch questions: no direct child launch in inspected
selected A023 bodies/helpers; a transitive native/compiler launch cannot be
excluded. Repository-defined applicable fixture/plugin launches were not found;
external/installed pytest/plugin scope cannot be certified absent. No meaningful
unaccounted child's safety custody is claimed resolved.

### Phases 4-6: persistent effects and authoritative custody

| Potential class | PW disposition | Evidence and limits |
| --- | --- | --- |
| CPU state arrays, result tuples, synthetic projection, monkeypatch attributes | PW0 | Process-local mutation only on inspected selected paths; no file persistence call. |
| Explicit result/provenance/prepared-cache/event-journal writers in imported modules | PW0 for selection | Functions can write arbitrary caller paths if called, but selected A023 bodies/helpers/import constants do not invoke them. |
| Compiler/pytest temporary files and system TEMP/TMP | PW1 candidate / PW5 unresolved history | No historical exact destinations/cleanup inventory; cannot certify all were isolated ephemeral artifacts. |
| .pytest_cache and Python __pycache__ | PW2, repository-local PW3 location | Non-authoritative caches can affect later selection/import behavior if reused; no exact R6 creation/mutation attribution. |
| CuPy kernel cache and CUDA/native compiler/driver cache | PW2 candidate / PW5 unresolved destination/implementation scope | Reachable GPU compile path; native implementation and historical environment overrides not closed. Cached compiled code can affect future execution if reused. |
| uv package/environment/cache/config effects | PW5 for historical dependency custody | Committed source identity does not fingerprint .venv or user/cache configuration. Fresh Python alone can still consume altered dependency/config bytes. |
| Tracked source, A023 WIP, R3 infrastructure, H/I/taxonomy | PW3 potential target, current named custody accounted for | No explicit selected write path found; exact tracked status and named fingerprints supply the narrow current-byte evidence below. |
| Registered protected evidence or authoritative paths through unresolved native/plugin behavior | PW4 potential consequence / PW5 unresolved mechanism | No actual modification proved; no complete write trace or permitted before/after protected-content comparison establishes absence. |

Metadata finds .pytest_cache, tests/__pycache__, src/malecns_sim/__pycache__ and
C:/Users/spider.tp/.cupy/kernel_cache present. Their directory timestamps do not
establish which files R6 wrote or whether files were read subsequently. R6's
external a023r6-a023.jsonl exists (93 bytes); R7's retained log interpretation
is used narrowly. No cache contents were opened and no cache/temp was deleted.
Current TEMP/TMP are C:/Temp; no queried PYTEST_PLUGINS, PYTEST_ADDOPTS,
PYTHONPATH, CUPY_CACHE_DIR, CUPY_CACHE_IN_MEMORY, CUDA_CACHE_PATH or
MALECNS_DATA_ROOT override was displayed. Current environment absence is not
proof of R6's historical environment or plugin list.

Affirmatively preserved current authoritative identities:
- All four original A023 implementation/test byte hashes, matching original
  retained fingerprints before and after R6/R7.
- R3 inspector/test, frozen H/I and provisional taxonomy byte hashes.
- Original implementation-report byte hash matching incoming/R7 custody.
- No current tracked diff or staged changes; committed local/origin/live
  identity remains the expected SHA. This is Git tracked-state evidence,
  not an exhaustive independent SHA256 inventory of every protected/ignored
  artifact or proof of absence of transient historical writes.

No protected content fingerprint was taken. Finite matching hashes do not
prove all repository artifacts unchanged, nor seal installed dependencies,
ignored artifacts, user/profile paths or native caches. The actual historical
protected-read/write occurrence remains unproved. PE2 is NOT supported.

A future isolated pytest cache, dedicated temp root and fresh process can
neutralize ordinary pytest/temp reuse. Bytecode consumption also requires an
empty isolated PYTHONPYCACHEPREFIX or independently clean source import boundary:
PYTHONDONTWRITEBYTECODE alone stops writes, not existing-bytecode consumption.
GPU kernel and driver caches need dedicated fresh destinations and no historical
reuse, with dependency-specific controls reviewed before certification. Fresh
processes eliminate in-memory runtime states, but do not reseal dependencies or
prove an unaccounted historical child cannot still affect authoritative state.
No isolation boundary was executed or certified in R8.

### Phases 7-10: decision against the bounded-uncertainty test

| Requirement | R8 adjudication |
| --- | --- |
| B1 | Met: protected content access is not proven. |
| B2 | NOT ESTABLISHED: reachable native/compiler/plugin seams remain CP3 and their conditional children CP2; meaningful write/authority scope is unaccounted for. |
| B3 | Met for the required named A023/R3/H/I/taxonomy identities; matching fingerprints have this finite scope only. |
| B4 | NOT ESTABLISHED: unresolved effects cannot be restricted to non-authoritative cache/temp classes; dependency/config/native-write scope remains PW5. |
| B5 | Partial design only: ordinary caches/temp can be isolated, but historical native/plugin/dependency effects and potential surviving authority are not yet neutralized by a certified boundary. |
| B6 | Met: all 27 PASS results remain excluded from acceptance. |
| B7 | Named frozen H/I/WIP custody is available without trusting R6 results; restarting validation is NOT certified while B2/B4/B5 fail. |

**PE3-UNRESOLVED**, hence **A023-R8-C**, is required. PE1's affirmative high
bar is not met, and PE3-BOUNDED requires all B1-B7. This is a bounded failure
of available inspection/custody evidence, not an allegation that native helpers,
plugins or protected mutation actually occurred. Mere cache presence, elapsed
pytest output, missing telemetry or an ordinary uv->Python chain proves no breach.

Potential future requirements, DESIGN ONLY, not authorization to resume:
fresh exact interpreter/pytest process; mandatory guard active from startup
before import with fresh external activation log; exact H/I and eventually N
manifests; original WIP fingerprint checks; sanitized explicit plugin/config
inputs; isolated/disabled pytest cache; new dedicated TEMP/TMP and basetemp;
no previous temp/worker/server/runtime state; clean bytecode import boundary;
fresh reviewed CuPy/CUDA cache destinations; accounted-for child lifetime and
write authority; no acceptance of R6 output. These controls are necessary
considerations but do not presently establish a sufficient execution boundary.
No VM/container is prescribed absent a demonstrated need.

### Phases 11-12: validation limits, history and exact next task

The 27 PASS remains **PREMATURE OBSERVATION — NOT ACCEPTANCE EVIDENCE**.
It cannot satisfy G15 or G16, contribute to final H/I/N acceptance totals or
certify taxonomy/A011/integrity. No R6 result was promoted or erased.

R8 performed exact-path static inspection, explicit authorized incoming/final
custody hashes and metadata checks only. No workload/A023/A011/A007B/CPU-GPU
regression/H/I/final-validation execution, simulations, build, integrity checker,
compileall, benchmark, profiler, performance/full-real activity occurred. No
production/test/guard semantic change, protected content access, uncontrolled
repository search, cleanup/reset/stash/discard, commit/push, version bump,
tag/release/publication. Version remains 0.3.0; tracked workflows zero.

Starting Git diff --check and cached diff check passed. Because this report is
untracked, those checks alone do not validate its append. Certified before/after
output comparison and append whitespace checks are required for closure; final
custody results accompany the final response. Exactly the same eleven WIP paths
remain, with only this report's bytes intentionally changed. Staging/stash empty;
existing worktrees preserved; final committed SHA equals starting expected SHA.
Overall A023-B and G16 NOT PASS remain.

Exact next task (one bounded design task only):
**A023-R9-CUSTODY — design a bounded custody reset that reseals dependency/plugin
and authoritative/protected-state identities without protected-content access,
resolves safe inspectability of hard-linked dependency controls without weakening
R3, and specifies a closed child/write plus fresh cache/temp/import boundary.**
Deliver a reviewable design and its required authorization/evidence limits; no
workload execution, artifact deletion/replacement or G16/gate recovery in that
design task. Do not begin validation-gate certification until the custody gap
has actually been resolved. No next task was started automatically.
R8 closure verification: certified before/after report outputs preserve all
prior R1-R7 text and contain exactly one R8 section; appended whitespace check
PASS. All sixteen listed ledgers have protected_content_opens=0 and every
actual content-open event classified SAFE. The three dependency failures each
opened only the two safe controls, never their rejected requested target.
Final Git working/cached diff --check PASS; exactly eleven untracked paths,
no tracked/staged changes, empty stash, both worktrees preserved. All ten
non-recovery-report incoming files retain identical SHA256 and byte lengths.
Final local HEAD, origin/master and live GitHub master again equal
c5ad89377575592665344f6420126b16c29b4339. This closure paragraph changes only
this recovery report and grants no additional execution authority.

## A023-R9-CUSTODY (2026-10-07): clean validation custody reset design

Authorization: **?? A023-R9-CUSTODY**. DESIGN ONLY. Classification: **A023-R9-CUSTODY-A ? CLEAN VALIDATION CUSTODY RESET DESIGN READY**. Overall **A023-B**, implementation partially complete; **G16 NOT PASS**. Preserve A023-R2-CONTRACT-VIOLATION, A023-R3-A, A023-R4-B, A023-R5-B, A023-R6-CONTRACT-VIOLATION, A023-R7-C and A023-R8-C. R8 remains **PE3-UNRESOLVED**. R6 command `uv run python -m pytest -q tests/test_application_a023.py`, observed 27 passed, remains **PREMATURE OBSERVATION ? NOT ACCEPTANCE EVIDENCE**. Protected read NOT proven; PE2 NOT supported; historical child/dependency/plugin/native and persistent-write scope remains unreconstructable. This design makes that history irrelevant as validation authority, without proving harmlessness.

### Starting custody

Root dynamically derived: D:/spider/working/MaleCNS-Sim. HEAD, origin/master and live GitHub master all equal `c5ad89377575592665344f6420126b16c29b4339`. Exactly eleven untracked files, no tracked/staged changes, empty stash. Both main and existing detached .kilo/worktrees/clarity-mare worktrees preserved at that SHA. Version 0.3.0; tracked workflows zero. Incoming fingerprints before design edits:

| Exact path | Bytes | SHA256 |
| --- | ---: | --- |
| docs/manifests/a023-validation-baseline-h.txt | 119921 | ec11f5ec29784519e315e8e551af5cf54f0583b4d147aff87d2ec7e09722048f |
| docs/manifests/a023-validation-infrastructure-i.txt | 1004 | 3cd4f286f584873ba279a55c764c06f1df8b262c3b731f031955aafe9217d830 |
| docs/manifests/a023-zero-payload-taxonomy.json | 420766 | a70af57bd719d7d544ef9a3caadf03060794f5143f2dc550e9743593e8832677 |
| docs/plans/2026-10-07-application-a023-public-runtime-implementation.md | 10727 | ed753c163eb9f975242f1a730a69720e41ef66a5d35935e100c214f55604be2b |
| docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 77963 | 0603ebcc746d6ee499d47a6bfbc3ecfb611a4cdad6fdfccf9711a50fcc086f27 |
| scripts/a023_fail_closed_inspect.py | 7278 | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| src/malecns_sim/experimental/__init__.py | 86 | 6a50cd6c9c0d1778292513deeaeffe1fdf1419da72dc2a45fc6bbd4645e61128 |
| src/malecns_sim/experimental/gpu.py | 2349 | 56c0ec202306f84ed378c8439fe923f9292b8dc2432893ff2dc6e176ed68dfbc |
| src/malecns_sim/runtime.py | 11186 | acc6520c565f32b179faa20d1bf73dee0e898878c5eb4fdf5658a29dca188e3d |
| tests/test_a023_fail_closed_inspect.py | 4680 | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |
| tests/test_application_a023.py | 10879 | 81f704e167b07cfea3cdb3f0b29645b51d72ea1276b81951bb48557091cbc579 |


Original A023 source/test, R3 inspector/test, H/I/taxonomy and implementation-report identities match retained R8 custody. Only this recovery report evolves. Future transfer must freeze its final then-authorized hash, not reuse its incoming hash above.

Repository inspection used only the unchanged exact-path R3 inspector; initial help requested no content, subsequent invocations used Python -I -S -B. External ledgers: D:/spider/working/a023-r9-inspection-1.json, a023-r9-inspection-2.json, a023-r9-incoming-inspection.json, a023-r9-before-report.json. First ledger rejected missing .python-version before opening it; no fallback. Explicit authorized 11-file hashes were independently confirmed by certified incoming inspection. Site-packages directory labels were inventoried metadata-only; no installed content opened. External emitted-output parsing is not repository search. No relevant A023 memory entry supplied an audit/design fact.

Static metadata: pyproject.toml 910 bytes, SHA256 `00de0136d78559c96a5cd54c4f3004f51affa0f6dce1c2c4312f96f389baaf51`; Python >=3.12, no .python-version. uv.lock 91219 bytes, SHA256 `7523bec3c8947522d8eb80bda995696aba8941f143f7ef37c46afaece416ec02`, format 1/revision 3, Python/platform marker branches. Runtime numpy>=1.26, pandas>=2.1, pyarrow>=15.0, scipy>=1.11; test extra/dev pytest>=8.0; GPU cupy-cuda12x[ctk]==14.2.0. Pytest testpaths=tests/addopts=-ra, no declared external plugin. Metadata inventory finds no tracked conftest.py/pytest.ini/setup.cfg/tox.ini. Isolated stdlib-only current interpreter probe reports CPython 3.14.0, MSC v.1944 AMD64, .venv/Scripts/python.exe: observation only, not trusted binary identity. Installed dist-info labels match lock names/versions but do not certify installed metadata, historical plugins or file bytes.

### 1. Authoritative inputs A0-A10

Every accepted content input requires SAFE classification, canonical path/file identity, SHA256 and byte length. Unknown authority, alias/reparse/hardlink ambiguity, missing/extra inputs or drift fails closed. Location/run ID/time may vary only inside recorded confinement; semantic inputs cannot vary silently.

| Input | Authoritative fingerprint / variation and refusal |
| --- | --- |
| A0 committed source | Exact commit above; tracked path/mode/blob inventory; SAFE materialized source SHA256/length. Location varies, bytes/modes/commit cannot. Protected Git blobs excluded, never read. |
| A1 WIP | Exactly eleven current approved path/hash/length entries, including final recovery report. Authorized later changes require a new approved inventory; missing/extra/drift refuses. |
| A2 H | Frozen hash above; 1503 unique nonempty exact node IDs/order. No variation; not execution acceptance. |
| A3 I | Frozen hash above; 12 unique nonempty exact node IDs/order. No variation; not infrastructure PASS. |
| A4 taxonomy | Frozen provisional hash/status/all entries; Z0=0,Z1=0,Z2=1501,Z3=2, INCOMPLETE - NOT ACCEPTED FOR EXECUTION. Identity known, execution denied; later completion requires new approval. |
| A5 Python | CPython 3.14.0 Windows AMD64 exact build, verified independent artifact provenance and executable/stdlib/DLL inventory hashes. Current .venv not authority; version string alone insufficient. |
| A6 dependencies | pyproject/lock identities, resolved Windows CPython branch/groups/extras, artifact hashes and complete installed file/name/version inventory. Root varies; extra/missing/mutated packages refuse. |
| A7 pytest/plugins | pytest 9.1.1, pluggy 1.6.0, exact builtin plugin modules/files and explicit allowed external plugins, entry points and actual active census. Unexpected registration/config refuses. |
| A8 runtime/config | Exact environment/config JSON digest, cwd/argv/sys.path, native tools/DLL/driver identities, approved CPU/GPU configuration. Fresh confined root names vary; ambient variables/config/tool authority refuses. |
| A9 guard | R3 inspector/test hashes above; firewall 170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af; exact bootstrap/child controls and registration of original/execution/external protected roots; outer runner/OS policy hashes. No semantic weakening. |
| A10 N | Future exact selected-node manifest/hash/count linked to H/I/taxonomy/exclusions. Currently absent/unapproved means EXECUTION_DENIED; no R6 result or silent omissions. |

Native configuration/system platform are explicit inputs, not ambient authority. GPU presence alone grants nothing. Unidentified driver/compiler/DLL/config denies the relevant branch without changing assertions.

### 2. Dependency custody: DEP-C

Select **DEP-C**, fresh uv-managed reconstruction with frozen lock plus artifact and full installed inventories. DEP-A leaves mutable environment/plugin bytes; DEP-B alone describes potentially R6-mutated installed bytes. Never copy historical .venv, pyc, editable metadata or unverified cache. Independently verify exact uv executable and CPython artifact; record build/version/hash/provenance. Preparation is separate, frozen/offline, fresh cache, copy link mode (nlink=1), explicit test/dev plus GPU extras. No implicit uv synchronization during validation; use absolute new Python executable. Installation/build hooks require separate bounded authority in preparation. Seal final environment read-only; imports use approved src rather than a second project copy. No R9 downloads. Unavailable verified artifacts mean refusal, not reuse.

Exact lock versions to freeze, verifying marker applicability/artifact hashes against lock: colorama 0.4.6; cuda-pathfinder 1.8.2; cuda-toolkit 12.9.2.0; cupy-cuda12x 14.2.0; iniconfig 2.3.0; malecns-sim 0.3.0; numpy 2.5.3; nvidia-cublas-cu12 12.9.2.10; nvidia-cuda-nvrtc-cu12 12.9.86; nvidia-cuda-runtime-cu12 12.9.79; nvidia-cufft-cu12 11.4.1.4; nvidia-curand-cu12 10.3.10.19; nvidia-cusolver-cu12 11.7.5.82; nvidia-cusparse-cu12 12.5.10.65; nvidia-nvjitlink-cu12 12.9.86; packaging 26.3; pandas 3.0.6; pluggy 1.6.0; pyarrow 25.0.1; pygments 2.21.0; pytest 9.1.1; python-dateutil 2.9.0.post0; scipy 1.18.1; six 1.17.0; tzdata 2026.4. CuPy must be present for GPU validation, not accidental missing-dependency behavior. All transitive native distributions count even if not plugins.

These target versions/declarations and lock bytes are frozen NOW. Interpreter/uv/wheel/installed/DLL/driver hashes are NOT yet captured as clean inputs: R10 must establish independently verified artifacts and freeze them before CL6 PASS. No current installed inventory or active plugin set is certified by this design.

### 3. Safe dependency inspection

Keep R3 repository mode unchanged, including single-link rejection. R10 needs a separate **external-dependency exact-path mode**: explicit approved canonical fresh environment root outside protected roots/release spellings; exact individual target and SAFE authority before content open. No recursive source search or arbitrary site-packages crawling. Filename metadata identifies dist-info; inspect exact METADATA/WHEEL/RECORD/entry_points.txt only after independent classification. RECORD is untrusted: reject traversal/absolute/ambiguous paths, streams, reparse points, duplicates, out-of-root targets, unknown ownership/hash algorithms. It never grants authority to follow a path. Approve every record target separately; metadata-only path inventory detects extra files, never silently allows them. Hash full finite approved installed inventory. Named dependency source reads additionally require exact path and purpose.

Import-spec discovery must not execute parent packages/custom finders; prefer validated file-location metadata. Import-dependent discovery is allowed only later in the sealed process, never as inspection bypass. Fresh copy-mode files nlink=1; old hardlinked dependencies remain rejected. No relaxed R3 rule or laundering copies. Ledger each root/path/file ID/protection/open decision/hash/length/role/outcome; repeat handle identity checks. Unknown authority fails before open. Private sealed root closes concurrent replacement. Mode designed only, not implemented.

### 4. Pytest plugins: PLUGIN-A

Select **PLUGIN-A**: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, clear PYTEST_PLUGINS/PYTEST_ADDOPTS, initially empty external entry-point allowlist. Inventory entry points without loading. Freeze pytest 9.1.1 normal builtins from exact approved configuration source, names/module origins/file hashes, preserving fixtures/capture/assertion rewriting. Explicitly disable cacheprovider and record its exclusion; no lastfailed/stepwise selection. One fingerprinted custody observer may perform pre-collection active-plugin census and monitor subsequent registration; it gains no child/write privilege. Actual names/origins/distribution/version/hashes must equal frozen builtins plus observer and separately approved required plugins. Unexpected registration aborts before workload.

Explicit pyproject config preserves testpaths/-ra; approved tree-only conftest discovery, no ancestors/user config. Risk: an external-plugin/cacheprovider fixture requirement would alter tests. Static classification must detect it before selection, then deny pending explicit approved plugin/cache plan, never hidden skips/edits. No declared external requirement is not proof of all tests. Required monkeypatch/tmp_path/builtin behavior stays intact. R10 does not collect/run incomplete H/I to infer a plugin contract; census certification uses synthetic control fixtures.

### 5. Closed children: CHILD-C

Select **CHILD-C**, containment plus explicit command classes. CHILD-A cannot accommodate eventual A011; CHILD-B without OS containment leaves native seams. Only fingerprinted host launcher creates root. Existing guard admissions remain unchanged. Each future class declares caller, absolute executable/hash, exact argv/hash, script hash, cwd/env digest, bounded count/timeout, read/write authority. No shell/PATH/interpolation/breakaway/arbitrary argv. Windows serialized argv uses exact parsing/round-trip validation, not splitting.

Create root suspended with restricted token; assign Windows Job Object before resume, kill-on-close/no breakaway. Default active-process limit one; child phases permit only declared finite counts. Python children require mandatory guarded_child activation/handshake before imports; equivalent native OS restriction must precede first instruction. Job containment alone does not enforce executable/argv: OS process-creation/application policy and trusted broker must prevent direct native bypass, or fail closed. Intercepted Popen wrappers alone are insufficient. Native/compiler launch denied unless independently approved; CuPy needs proven in-process compilation or exact bounded compiler contract, never implicit allowance.

Job completion notifications plus PID/create-time/image/token/job census account for all creation/exits. Missing activation/accounting, undeclared child, timeout/orphan or abnormal control termination fails custody; terminate job, wait for zero descendants, record cleanup, no retry. No prior server/worker adoption. Unbounded network/service/IPC delegation denied so a process cannot launch outside job through an ambient service. All children inherit restricted environment/token/ACL and no protected authority. Unknown historical children need not be found or killed if excluded from new custody.

### 6. Writes and filesystem enforcement

| Class | Authority and proof |
| --- | --- |
| W-AUTH0 tracked files | Sealed execution tree read-only; original checkout inaccessible to validation identity; ACL/token proof and SAFE before/after hashes/file IDs. |
| W-AUTH1 eleven WIP | Same read-only copies and complete hash/length comparison. |
| W-AUTH2 protected evidence | No content read/write/delete/rename/create/ACL authority; no protected materialization; OS denial plus unchanged guard. |
| W-AUTH3 temp | Only fresh bounded per-run root writable; destination/output inventory ledgered. |
| W-AUTH4 pytest cache | Disabled, historical reads denied. |
| W-AUTH5 bytecode | Dedicated fresh prefix writable, input tree has no historical pyc. |
| W-AUTH6 GPU/native cache | Dedicated fresh roots only; reviewed controls; unknown destination denies relevant execution. |
| W-AUTH7 profile/global | Original profile/config inaccessible; approved system inputs read-only; fresh private profile under temp is W-AUTH3. |
| W-AUTH8 unknown | Default deny read/write/execute, no user-wide token authority. |

Select **FS-C**, OS ACL/sandbox/read-only enforcement with private execution tree. FS-A/B cannot bound native writes or surviving same-user processes; disposable location alone insufficient. ACLs cover delete-child/rename/create/WRITE_DAC/ownership, not merely ordinary file write. Non-admin validation token lacks owner/restore/debug/backup privileges and writable sealed-input handles. Host records DACL/SIDs/token/effective access and synthetic negative probes; protected content never probed. Native writes receive the same enforcement. Unknown external read/execute paths denied, approved runtime inputs finite. Host-owned records/logs not workload-editable. Claim enforced authority rather than universal file-open tracing if attempt telemetry incomplete.


### 7. Cache/temp reset and imports

| Cache/input | Classification and policy |
| --- | --- |
| pytest | RESET-D: cacheprovider disabled, no cache-based selection or old root reads. |
| Python __pycache__/pyc | RESET-R: empty PYTHONPYCACHEPREFIX under fresh root; no old bytecode copied. -B alone does not prevent historical bytecode consumption. |
| TMP/TEMP/pytest basetemp | RESET-R: fresh per-run explicit roots; no prior temp/server discovery. |
| uv | RESET-R: preparation-only fresh cache with independently verified artifacts; no uv during validation. Sealed installed inputs RESET-I after certification. |
| CuPy kernel | RESET-R: fresh CUPY_CACHE_DIR; exact dependency-supported controls reviewed before GPU execution. |
| CUDA driver/JIT | RESET-R: fresh CUDA_CACHE_PATH plus explicit reviewed enable/size configuration. |
| compiler/native | RESET-R for each required approved cache; unneeded optional caching RESET-D. Unidentified capable cache blocks, never accepted RESET-U. |
| Node/npm | RESET-R for eventual Node temp/profile/module-compile and authorized npm cache; npm/npx/install/network resolution disabled, no initial command authority. |
| application temp/cache | RESET-R: each applicable app/prepared/output location mapped to fresh writable roots; old prepared/evidence caches prohibited. |
| user config/HOME/APPDATA/LOCALAPPDATA | RESET-R: empty private profile; original profile inaccessible; explicit frozen config only. |

No historical deletion. No semantic cache may remain RESET-U at acceptance; unknown native destination/control fails CL10/12. Approved system driver/runtime files may be RESET-I only with independent provenance/hash/version and OS read-only protection; mutable user overrides excluded. GPU branch denied until closure; no changed tests to avoid this condition.

Fresh absolute Python process every phase, no interpreter reuse/sys.modules/monkeypatch/session inheritance. Explicit cwd=execution root; no ambient current-directory/ancestor imports/config. Pinned bootstrap starts isolated (-I -S), activates unchanged guard before third-party imports, then adds only approved stdlib/site-packages/src/guard paths and reviewed site initialization. No ambient .pth/sitecustomize execution; required behavior is a separately frozen explicit input. Inherited PYTHONPATH absent; bootstrap controls sys.path. Clear inherited environment and construct finite allowlist for OS loader, guard, cache and explicit configuration. Restricted PATH/DLL search paths; no startup/coverage/debugger/plugin/compiler injections. Every admitted child follows the same contract or explicit Node/native equivalent. No prior live ports/servers/workers/shared session state.

### 8. Reset comparison and selection

| Strategy | Isolation/determinism/authority/complexity and divergence |
| --- | --- |
| RSET-1 same checkout/fresh process | Eliminates module state and redirected cache reuse, but ignored artifacts/deps/old same-user writers remain. Lowest complexity; insufficient. |
| RSET-2 disposable Git worktree/WIP | Exact commit/WIP possible, but shared Git administration and protected checkout materialization risks; no native authority closure. Moderate complexity; insufficient alone. |
| RSET-3 fresh uv plus 1/2 | Closes dependency reconstruction with verified artifacts, still lacks old-child/native write confinement. Moderate complexity; insufficient alone. |
| RSET-4 private sealed SAFE execution tree/fresh uv/restricted token/OS policy/job | Isolates consumed bytes/config/caches and historical process access; closes new child/write authority. Additional Windows custody setup, selected minimum sufficient combination. |

Select **RSET-4**. Disposable Git worktree **not required**; disposable execution tree **required**; fresh uv environment **required**. VM/container not required. Materialize finite approved SAFE tracked paths only from exact committed Git objects through future certified exact Git-object inspection/materialization; never broad checkout/archive of protected files or protected Git blob reads. Record excluded protected paths metadata-only. Approve all H/I/N/import/config unprotected input closure first; unknown required file denies. Preserve modes/identities. Do not reuse existing detached worktree or writable live .git administration. Tests needing Git identity get a sealed read-only exact Git metadata input and bounded executable contract, or remain denied; never change commit/assertions to manufacture compatibility.

A surviving historical process under the same user could alter a merely fresh tree. Therefore create the private root under an **independent custody principal**, with DACL denying R6 user's token read/write/execute/ownership/WRITE_DAC. Validation principal gets only sealed-input reads and run-root writes; controller uses narrowly authenticated broker, no generic file/process authority. DACL inheritance disabled, materialization handles closed before resume; unpredictable root names alone insufficient. Custody owner must not share unrestricted R6 token. Verify copy through stable trusted handles and reject source drift; reconstruct dependencies from independently authenticated artifacts, not current .venv/cache. Old processes cannot modify new inputs/log/config, signal workers or inject network/IPC state. Host broker rejects unaccounted handles and privilege overrides.

Threat scope is ordinary historical user-process effects, not malicious administrator/kernel compromise. If R6-associated authority can override the private principal/ACL, or independent principal/application/process policy cannot be certified, fail CL11/12/18 and retain EXECUTION_DENIED; do not downgrade to wrappers. R10 provisioning must establish this capability, not presume it. No claim that unrelated historical principals cannot write original protected state globally. New validation cannot consume those contents and has no write authority, so their unknown history cannot affect its acceptance inputs.

### 9. Exact WIP transfer and before/after custody

Transfer exactly eleven named files; no recursive copy. Source canonical root/path, approved SHA256/length, stable file ID, nlink=1 and no reparse/stream alias required. Read via certified SAFE mechanism, transfer verified byte stream without line-ending transformation/edits. Destination is new regular single-link file at same relative path; recompute hash/length while private custody held. Missing/extra/duplicate/drift refuses. Original files remain untracked; execution overlay records uncommitted status without staging/commit or shared index. No R6 log/cache/output transfer. Preparation artifacts separate from source/WIP; later authorized runner files belong to distinct finite infrastructure inventory, never silently expand WIP.

BEFORE: all eleven WIP, every materialized SAFE tracked path/mode/blob/hash/length/file ID, guard/runner/manifests, dependencies and config; complete metadata-only tracked path inventory labels excluded protected paths. Match original SAFE tracked files to committed blobs as well as approved WIP. Git status --short/full untracked/staging inventories supplement hashes. AFTER: same exact SAFE hash/length and path-set comparison, new/removed-file detection, original status/untracked/staging checks. Original/execution inputs separately labeled. Protected content never hashed. Intentional validation outputs only dedicated authorized roots, excluded from WIP comparison but separately ledgered; unexpected source-tree artifacts fail. Matching final hashes alone do not prove no transient writes: read-only OS enforcement and handle custody supply that claim.

### 10. Protected identity without content

Record canonical registered paths/roots, existence, guard-permitted stat/file ID/reparse/link metadata, DACL/effective-access identity. Include committed control-manifest identity and already established historical archival hashes only with provenance and historical_hash_recomputed=false. No payload/protected Git blob opened for fresh hashes; unknown metadata authority refuses applicable claim.

Separate statements: protected content **NOT READ by new validation** under effective OS denial plus unchanged guard; protected paths **NOT WRITTEN by new validation** under OS authority denial; protected historical hashes **NOT RECOMPUTED**. Metadata equality supports limited continuity, not fresh byte integrity, historical harmlessness or absence of writes by unrelated principals. Original protected state never imported. ACL inspection is not integrity PASS or biological evidence.

### 11. Machine-readable clean-lineage start record

Define host-owned `a023-clean-validation-custody.json`, schema a023-clean-validation-custody-v1, UTF-8 canonical sorted-key compact JSON plus SHA256. Seal BEFORE workload. Required schema fields:

- schema/run_id/UTC timestamp/phase/status (EXECUTION_DENIED or READY), committed_head, original_root/execution_root/materializer_identity.
- wip[11]/tracked_safe_inputs[]: exact relative/canonical source/destination paths, bytes/sha256/file_id/protection, blob/mode where applicable.
- h/i: path/hash/length/count/uniqueness; taxonomy identity/status/counts; n identity/count or null plus blocking_reason.
- python implementation/version/build/arch/executable/runtime inventory hashes/artifact provenance; uv version/hash/config; lock/pyproject identities; selected markers/groups/extras; artifact/installed inventories and hashes; pytest identity.
- plugins: builtin/explicit allowed/discovered entry points/actual active census, origins/hashes/distribution versions, autoload=false, observer identity.
- guard inspector/test/firewall/bootstrap/child controls/config/registration and activation; runner identity/effective argv.
- environment exact nonsecret allowlist values/digest, cwd/sys.path/DLL/tool/driver identities; read-only external input policy.
- cache_temp roots/classifications/freshness; child_policy/job/token/principal/OS application policy; write_policy/DACL/effective-access proofs.
- protected_metadata and historical provenance only, historical_hash_recomputed=false; before_inventory digest.
- gates CL1-CL20 results/reasons/evidence refs; workload_authorized=false in R10; historical_results_reused=false; protected_content_reads=0.

Null unknowns carry failing gates, never invented PASS. Immutable start record and host append-only logs cannot be modified by workloads. After record references start digest and contains exits/descendants/cleanup, denials and after inventory. A DENIED start record certifies fail-closed machinery without any workload launch. No protected contents or reusable secrets in custody records.

### 12. Clean-lineage gates CL1-CL20

All PASS is necessary, not G16 execution authorization.

| Gate | PASS requirement |
| --- | --- |
| CL1 | Exact committed local/origin/live identity. |
| CL2 | Exact approved eleven WIP and destination transfer identities. |
| CL3 | H hash and 1503 unique exact IDs. |
| CL4 | I hash and 12 unique exact IDs. |
| CL5 | Taxonomy known, complete and accepted; current incomplete status fails. |
| CL6 | Independently verified Python/uv/artifacts plus fresh sealed full dependency inventory. |
| CL7 | Frozen pytest/plugin set/config and exact active census, autoload disabled. |
| CL8 | Pinned unchanged guard with certified startup/config/registration. |
| CL9 | Fresh process/import/environment boundary. |
| CL10 | All semantic temp/caches isolated or disabled, no RESET-U. |
| CL11 | OS-closed declared children/tree/activation/lifetime/cleanup. |
| CL12 | OS-closed write and external read/execute authority; old-process exclusion. |
| CL13 | Protected content read/write prohibited for entire new tree. |
| CL14 | Complete SAFE before inventories and read-only sealing. |
| CL15 | No R6 history/result/artifact reuse as validation authority. |
| CL16 | Fingerprinted approved runner/materializer/bootstrap/observer. |
| CL17 | Complete exact N linked to H/I/taxonomy. |
| CL18 | Independent custody principal/token/DACL/OS process policy with synthetic enforcement certification. |
| CL19 | Immutable pre-workload custody record and full evidence references. |
| CL20 | Explicit protected-claim boundaries and approved required A011/I0/I1/I2 dispositions. |

Current taxonomy/N/A011/integrity incompleteness must yield **EXECUTION_DENIED**, explicit reasons, zero workload activation. R10 may certify control machinery using dedicated synthetic fixtures only; no A023/H/I/A011/A007B execution or suite collection to fill missing gates. Static A011/taxonomy/integrity adjudication may later proceed within safe custody to establish dispositions: gates constrain workload recovery, not the ability to perform prerequisite static design. Complete gates plus separately explicit authorization are required before G16. Design-ready is not a current READY/CL PASS claim.

### 13. A011 and integrity

A011 NOT solved. Future custody prerequisites: independently verified exact Node executable/version/hash and tests/js/application_a011.cjs hash; declared caller/exact argv/cwd/env; bounded child count/timeout and loopback server endpoint; confinement active before first instruction; separately certified guard-compatible adapter without broader admission; isolated Node temp/profile/cache; no npm/npx/install; complete descendants/exits/orphan cleanup; permitted outputs only; zero protected read/write authority. Python server lifetime/port/cleanup separately declared, no prior server reuse. Node cannot merely log after launch and call that pre-activation. Assertions/semantics unchanged.

Integrity **I0**: content-check only explicitly SAFE A023/unprotected inputs. **I1**: protected content **NOT RUN**, never PASS via reset/metadata. **I2**: limited approved manifest/schema/path/metadata consistency. Full integrity checker NOT RUN. Custody proves frozen inputs/bounded authority, not protected byte integrity or a release requirement demanding I1. Future policy must explicitly retain/adjudicate that blocker, no weakened assertions or false full-integrity label.

### 14. Threats, nonclaims and bounded next implementation

Isolates stale pytest selection/temp/bytecode/GPU/native caches, old imported Python state, ambient plugins/config/env, dependency/WIP drift, historical servers/workers and unknown child influence over new private inputs. OS authority prevents new repository/protected writes, unknown native destinations and orphaned descendants. Independent artifact verification avoids a clean-looking copy of altered .venv. Unknown cache/tool/config/ACL override, file drift, plugin/child mismatch, missing handshake/log, orphan or incomplete taxonomy/N/disposition fails closed; no in-run repair/retry.

Does NOT reconstruct R6 opens/child tree/argv/lifetime/cache/dependency/persistent writes/protected mutation; does not support PE2 or prove R6 harmless. No biological/scientific claim, performance reproducibility/GPU speed/full-real completion, privileged hostile-host proof or fresh protected-content integrity. The 27 passed never contributes to acceptance. Unknown original historical effects need not be corrected to validate independent sealed inputs.

Exactly one next task, NOT STARTED:
**A023-R10-CUSTODY ? implement and certify the clean validation custody reset and fail-closed execution gate; prove current incomplete taxonomy/A011/integrity state remains EXECUTION_DENIED; no G16 workload execution.**

One bounded implementation includes external/Git-object exact inspection, private SAFE execution-tree/eleven-file transfer, independently verified fresh uv environment, OS principal/ACL/job/command policy, plugin/cache/import controls, immutable start/after records and before/after custody. Certification uses dedicated synthetic control fixtures/denied-launch cases, never scientific payload/A023/H/I/A011/A007B workloads. No production/test semantic edits, historical cleanup or guard weakening. Missing provisioning/artifact authority yields blocked certification, not conceptual PASS. Implementation and synthetic control certification may combine; actual workload/G16 certification is a separate later task. No micro-task cascade, no automatic R10 start.

### R9 closure scope

A023 tests=0; A011=0; A007B=0; H/I validation=0; simulations=0; build=0; integrity execution=0; performance=0; profiler=0; full-real preparation/advance=0; registered payload reads=0. No uncontrolled repository content search, installed source crawling, reset implementation/execution, cleanup/reset/stash/discard, commit/push, guard/implementation/test change, version bump, tag/release/publication. Only recovery report appended, prior history retained. Static closure verification follows.


R9 child-enforcement clarification: use Windows child-process creation mitigation (PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY with child creation restricted) on each workload worker, combined with the restricted token/job. A host-owned broker outside workload control creates only declared executable/argv classes suspended and assigns each to the same contained job before resume. Treat the broker supervisor plus all broker-created workers as the accounted validation process tree; no worker receives direct process-creation authority. OS executable allow policies supplement this restriction, not argv validation. The broker validates argv/environment/hash; workers cannot bypass it through direct native CreateProcess. Future infrastructure adapters must preserve existing guard admission decisions and use only approved broker classes; routes lacking a compatible adapter stay denied. This closes the native argv gap without pretending Job Objects or executable allowlists enforce argv. Any unsupported mitigation/broker bypass fails CL11/18.

R9 closure verification: certified before/after emitted report comparison preserved the complete R1-R8 prefix and exactly one R9 section. All appended lines passed trailing-whitespace checks. Five inspection ledgers recorded protected_content_opens=0; every actual content-open event was SAFE. Ten non-recovery-report incoming files retained identical SHA256 and byte lengths. Exactly the same eleven untracked paths remain; only this recovery report changed. Working/cached git diff --check PASS; no tracked or staged changes; stash empty; both worktrees preserved. Final HEAD/origin/master/live GitHub master equal c5ad89377575592665344f6420126b16c29b4339. Version 0.3.0/workflows zero unchanged. No workload/build/integrity/commit/push/tag/release/publication; G16 NOT PASS. This final paragraph is an append only and grants no R10 or execution authority.

## A023-R10B3-TRUSTROOT (2026-10-07): exact secondary guard closure

Authorization: **授權 A023-R10B3-TRUSTROOT**. Starting point:
**A023-R10B2-TRUSTROOT-B — EXTERNAL RUNTIME PROVENANCE ESTABLISHED;
ONE TRUST-ROOT CERTIFICATION GAP REMAINS**, as explicitly supplied in this
authorization. This report did not supply the R10B2 external run observations;
the authorization supplied them. Current admission and four-file identities
were freshly verified in this run.

Terminal classification:
**A023-R10B3-TRUSTROOT-A — SECONDARY GUARD DEPENDENCY CLOSED;
NON-CIRCULAR TRUST ROOT CERTIFIED; A023-TRUSTROOT-V1 ESTABLISHED.**

Overall remains **A023-B**, **G16 NOT PASS**, **PE3-UNRESOLVED**.
Preserve **A023-R10-CUSTODY-CONTRACT-VIOLATION**,
**A023-R10R-CUSTODY-C**, **A023-R10B-TRUSTROOT-CONTRACT-VIOLATION**, and
**A023-R10B2-TRUSTROOT-B**. None is rewritten as PASS. No invalid R10/R10B
observation supplies this trust lineage.

### Metadata-only admission and ORCH-0

Git metadata dynamically established root D:/spider/working/MaleCNS-Sim.
Starting HEAD = origin/master = live GitHub refs/heads/master =
c5ad89377575592665344f6420126b16c29b4339. Exactly the eleven authorized
untracked paths were present; no tracked changes, staging or stash; tracked
workflow filename count zero. Worktrees: authoritative root and
D:/spider/working/MaleCNS-Sim/.kilo/worktrees/clarity-mare, both at that SHA.
No repository content was opened before external bootstrap admission.

ORCH-0: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe.
Current executing host path and Resolve-Path agree. Length 492032 bytes,
PowerShell 5.1.19041.2673, NTFS volume serial 0xa43ae428 (-1539644376),
file ID 0x0000000000000000000100000000d566 (high/low 65536/54630).
All path ancestors and executable lack reparse attributes.
Hardlink inventory has exactly two Windows-system paths: the admitted
System32 path and
C:\Windows\WinSxS\amd64_microsoft-windows-powershell-exe_31bf3856ad364e35_10.0.19041.2913_none_dd8b6791b7a0eed5\powershell.exe.
Both are outside both Git worktrees, repo .venv, and observed external A023
execution trees. This system hardlink disposition is explicitly accounted
for, not treated as a single-link repository target. No PATH-selected,
unadmitted, repo-local or .venv runtime was executed. No Python was executed.

### External bootstrap V3 and source continuity

Version: **A023-EXTERNAL-BOOTSTRAP-V3**.
Run ID: malecns-a023-r10b3-c4d6a96ff34248e094c87fc685e3f43e.
Source generated directly from this authorization outside the repository:
C:\Temp\malecns-a023-r10b3-c4d6a96ff34248e094c87fc685e3f43e\bootstrap-v3.ps1.

The four initial repository opens used the original read-stage source:
5495 bytes, SHA256
7c82fcf49c2819a16ef299891517f43b90cdf7d6586649959a26f1b912ff5d03.
That byte-exact source is retained externally as bootstrap-v3-read-stage.ps1.
After those opens, only an exact B2 PostRead branch was added for the
authorized post-append identity capture. The inspection function and
four-entry allowlist remain byte-identical. Removing that branch and restoring
the mode declaration reproduces the original source hash/length exactly.
Final bootstrap-v3.ps1: 6104 bytes, SHA256
de84b933b194d5ea94598ddbd4776fa533d87fa06e043873772d5956d41de358.

Original and final sources each passed all eleven external synthetic cases:
exact allowed acceptance; nonallowlisted denial; wildcard denial; directory
denial; traversal denial; outside-root denial; actual junction/reparse denial;
actual hardlink ambiguity denial; malformed request denial; deterministic
hash/length; deterministic ledger. Final-source tests ran from a byte-identical
external verification-final copy with fresh synthetic fixtures.
A repeated test invocation against reused fixtures stopped at an existing
synthetic directory; no repository open occurred. Fresh-fixture rerun passed.
The PostRead array conversion was corrected before certification; initial
four-open ledger validation then passed. No security-regression case passed
through a denial gate; no repository read was added by these external repairs.

Exact allowlist, with no automatic reference/import expansion:

- B0: scripts/a023_fail_closed_inspect.py
- B1: tests/test_a023_fail_closed_inspect.py
- B2: docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md
- B3: scripts/a019c_firewall/validation_firewall.py

V3 rejects malformed/nonexact requests, wildcard/directory/traversal/outside
requests, every target/ancestor reparse point, and ambiguous hardlinks before
content open. Canonical full path and Resolve-Path must agree. Explicit
single-file reads produce deterministic SHA256/length and ordinal ledger.
No recursive request, reference following, repository import, or dynamic
dependency traversal is implemented. This is an operational exact-path
authority, not an OS sandbox against concurrent hostile file replacement.

### Initial four-file repository ledger and identities

External ledger:
C:\Temp\malecns-a023-r10b3-c4d6a96ff34248e094c87fc685e3f43e\repository-ledger.json.

| Ordinal | File | Bytes | SHA256 |
| --- | --- | ---: | --- |
| 1 / B0 | scripts/a023_fail_closed_inspect.py | 7278 | 374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e |
| 2 / B1 | tests/test_a023_fail_closed_inspect.py | 4680 | d650b183414870e0ca219ef7a7a439447022aa034fbc887581b277c86a97587b |
| 3 / B2 PRE-UPDATE | docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md | 112518 | 3461408ea34a22be55287c5a157cb5a5b738d3c4813b1df7f70d08d0c00c5070 |
| 4 / B3 | scripts/a019c_firewall/validation_firewall.py | 7946 | 170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af |

Each canonical path is the dynamically established root joined to that exact
relative path. Each has reparse=false and hardlinks=1. B3 canonical path:
D:\spider\working\MaleCNS-Sim\scripts\a019c_firewall\validation_firewall.py.
B0/B1 match R10B2 exactly; B2 matches its supplied pre-R10B3 identity exactly.
Four successful repository opens; four distinct files; B0/B1/B2/B3 once each.
No fifth repository file opened. Analysis thereafter used the already captured
external bytes only; no referenced file was opened.

### B3 static dependency audit: B3-CLOSED for the consumed classifier

Top-level imports: functools, json, os, pathlib.Path, sys; all Python stdlib.
Top-level execution computes ROOT, DENIED_ROOTS, optional environment root,
LOG, and CHILD_ENTRY/DIRECT_ENTRY path strings. Path.resolve is filesystem
metadata canonicalization, not a content read.

Deferred stdlib imports: ctypes, ctypes.wintypes, subprocess.
Deferred repository-local imports: a007c_node.admitted and a006r_node.admitted.
Deferred external imports: pyarrow, pyarrow.feather, pyarrow.parquet,
pyarrow._feather. These occur only in child-control/install functions.
B0 never calls install, mandatory_child, guarded_command, audit_argv,
direct_control or wrap; none of those deferred imports executes on B0's
bootstrap/check path. guarded_child.py and a014_direct_control.py are
top-level path constants only, not loaded content dependencies of check().
No dynamic import/importlib/__import__ or automatic reference following occurs
on the consumed path. B3's full install/child machinery is not certified here.

The only explicit B3 file open is record(): open(LOG, "a", encoding="utf-8").
It writes a blocked-event log; it does not read configuration or target content.
LOG comes from MALECNS_A019C_R2_LOG. In this run that variable is unset, so record
performs no open. Future secondary-authority use must keep it unset or separately
authorize an exact external log destination; an arbitrary repository log path
does not receive authority from B3. MALECNS_DATA_ROOT is also unset in this run.
If used later, its exact value and metadata-only resolution must be recorded
as classifier configuration, not discovered from a repository content file.

Other environment lookup, MALECNS_A019C_R2_FIREWALL, and inherited env checks
are confined to the unused child/install machinery. There are no config-file
reads, repository-relative content reads, recursive content searches or child
launches in module top-level initialization or check/record/category.
The classifier uses canonical path, ROOT/data, optional explicit data-root
environment input, registered release-name spelling, and optional external
log configuration. For fixed explicit inputs the classification is deterministic.
No fifth repository content file is needed for the behavior B0 consumes.
Classification: **B3-CLOSED**. This does not certify every dormant B3 function.

### Closed B0 -> B3 security-critical path

B0 bootstrap uses Inspector with a one-exact-control SAFE exception:
root / scripts/a019c_firewall/validation_firewall.py, otherwise UNKNOWN.
exact_target checks explicit lexical path, regular file, canonical custody,
reparse status and nlink=1 before the guard is opened. B3 content is ledgered
as reviewed-guard-bootstrap and pinned to B0.GUARD_SHA256, which equals the
current B3 SHA256. B0 creates types.ModuleType, sets __file__ to the exact
guard path, compiles/executes those bytes, and requires module.ROOT == root.
No module finder or dependency traversal loads another repository module.

The returned Inspector classifier calls module.check(canonical Path target).
SourceAccessDenied maps to PROTECTED; any other Exception maps to UNKNOWN;
normal return maps to SAFE. Inspector.inspect rejects every decision other
than SAFE before opening the requested target, repeats metadata/identity
checks after classification, then opens only the exact target and checks the
opened file identity. UNKNOWN and protected decisions deny before target open.
check() denial calls record/category and raises SourceAccessDenied. With LOG
unset this path has no additional open. Classification/log exceptions also
map to UNKNOWN and still deny before target open.

Finite consumed graph:
bootstrap -> Inspector.inspect(GUARD, expected hash) -> compile/exec(top-level)
-> ROOT equality -> classify -> B3.check -> optional record/category
-> SAFE/PROTECTED/UNKNOWN -> Inspector.inspect target pre-open gate.
B0 contains no recursive search or child spawn. B0 causes only the explicitly
authorized B3 bootstrap read plus separately authorized exact target reads.
B3 does not independently grant those target reads.

### Retained R3 evidence and BRIDGE-R3

Evidence recovered solely from B2's already read bytes:

- B2 pre-update lines 289-307 record the exact guard path, 7946 bytes and SHA256
  170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af,
  unchanged check() semantics, and top-level stdlib-only control initialization.
- Lines 298-305 record canonical check(source), DENIED_ROOTS/release-name rules,
  SourceAccessDenied -> PROTECTED, other exceptions -> UNKNOWN, normal return
  -> SAFE, and no install()/pyarrow/child admission by the helper.
- Lines 313-352 record exact-path/canonical/reparse/hardlink checks, pre-open
  UNKNOWN denial, pinned guard bootstrap and the operational custody limit.
- Lines 356-367 retain 12 isolated synthetic self-tests PASS, zero skips,
  including PROTECTED/UNKNOWN/classifier-exception sentinels before Path.open.
  These historical tests were not rerun in R10B3.
- Lines 372-394 retain the R3 canary ledger: guard bootstrap and requested guard
  both at the current B3 identity; helper control at the current B0 identity;
  six explicit successful opens, five distinct paths, all SAFE, protected opens
  zero. Those historical ledger facts are recovered as evidence, not repeated
  as current-run opens or authority to inspect the other canary files.
- Lines 398-418 record unchanged guard bytes and the R3 zero-read scope.

All five BRIDGE-R3 conditions pass: current B0 exactly matches retained R3
identity; current B3 exactly matches retained R3 classifier identity; current
B0/B3 mechanics match the retained security-critical semantics; B3-CLOSED for
the consumed path; no fifth repository dependency discovered.
**BRIDGE-R3**, not BRIDGE-NEW and not BRIDGE-NONE.
No external executable B0+B3 harness was run; no Python runtime was admitted
or executed, and no executable-certification claim is manufactured from a new
unadmitted runtime.

### Secondary authority and A023-TRUSTROOT-V1

The certified secondary authority is exactly the identity-pinned pair above:
B0 is the inspection entry point; B3 is its authorized protection-classification
dependency. B3 alone grants no general content-read authority. Neither file
may dynamically expand repository authority. Every future target requires
separate explicit task authority. Any change in either identity invalidates
the secondary authority until recertification. A future Python execution
requires separately admitted exact external runtime provenance; this task does
not admit PATH Python or the repository .venv. Keep logging unset or explicitly
external and record classifier environment inputs.

Trust chain:
this task authorization -> metadata-certified ORCH-0 ->
A023-EXTERNAL-BOOTSTRAP-V3 read-stage (and byte-continuous exact B2 post reader)
-> exact B0/B1/B2/B3 allowlist -> static consumed B0+B3 closure ->
BRIDGE-R3 -> certified B0+B3 secondary authority -> **A023-TRUSTROOT-V1**.

External trustroot-certificate.json was written after successful final-source
self-tests and ledger identity verification, before this report append.
R10/R10B invalid custody observations are excluded from the lineage.
Actual protected scientific payload content opens = **0**. Protected hashes
were not recalculated; protected integrity is not PASS.

### Authorized report append, final custody and exact next task

Only after trust establishment, this section is appended once to B2 with a
write-only append handle. All prior report bytes remain the prefix.
Exactly one further repository content open is authorized: B2 post-update,
using V3 PostRead. Its final SHA256/length and prefix equality are captured
externally and returned in the task final report, not inserted as a circular
self-hash into this report. Expected final ledger: five successful opens,
four distinct paths; B0/B1/B3 once each, B2 twice (pre/post).

No other repository file is modified. Expected final untracked inventory
remains exactly:

- docs/manifests/a023-validation-baseline-h.txt
- docs/manifests/a023-validation-infrastructure-i.txt
- docs/manifests/a023-zero-payload-taxonomy.json
- docs/plans/2026-10-07-application-a023-public-runtime-implementation.md
- docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md
- scripts/a023_fail_closed_inspect.py
- src/malecns_sim/experimental/__init__.py
- src/malecns_sim/experimental/gpu.py
- src/malecns_sim/runtime.py
- tests/test_a023_fail_closed_inspect.py
- tests/test_application_a023.py

Final metadata verification is performed after the single post-update read.
Committed SHA remains c5ad89377575592665344f6420126b16c29b4339; staging/stash
empty; both worktrees preserved. No commit/push, version bump, tag, release or
publication. Version 0.3.0 is retained historical B2 evidence only; no version
content source was reopened. Workflow count zero is freshly metadata verified.

A023 tests=0; A011=0; A007B=0; H/I workload=0; ordinary pytest=0; repository
test collection=0; simulation=0; build=0; integrity run=0; performance=0;
profiler=0; full-real=0. No uncontrolled content search. External synthetic
bootstrap activity only; no private execution tree, fresh uv environment,
PLUGIN-A, CHILD-C, FS-C or CL implementation, taxonomy completion or G16.
No clean/reset/stash/discard. Historical STOP/B/contract violations remain.

Exact next task, **NOT STARTED**:
**A023-R10C-CUSTODY — using the explicitly restated A023-TRUSTROOT-V1,
perform a fresh R9 custody implementation; certify clean custody and
fail-closed gate; require CUSTODY_READY=true and EXECUTION_AUTHORIZED=false;
no G16 workload.**
