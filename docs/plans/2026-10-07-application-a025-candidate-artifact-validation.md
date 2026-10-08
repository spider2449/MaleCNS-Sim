# A025 — Candidate and installed-artifact validation

Date: 2026-10-07. Authorization: continue A025; commit and push A024 first.

## Entry identity and preserved scope

A024 was committed and pushed as
`c32919d4f0228310401abce17d09d3d68cb76deb`. Local HEAD, origin/master and
live GitHub master agree. The ten A024 paths were staged explicitly and
`git diff --cached --check` passed. The sole remaining incoming WIP is
`docs/references/deep-research-report.md`; preserve and exclude it from all
candidate, transfer, build and commit inputs. Existing worktrees and stash
remain untouched. Package version remains 0.3.0.

## Plan and execution boundary

1. Review the historical provisioner, freezer, runner and protection route as
   ordinary text. Retain original H/I/N identities, numerical assertions,
   exclusions and historical dispositions.
2. Implement an A025-specific candidate contract and fail-closed route. Freeze
   exact approved ordinary inputs against the committed A024 source. Never
   overwrite historical A023 manifests or relabel their evidence.
3. Certify the route's synthetic controls before discovery, imports or builds.
   Establish task-wide protection, dependency/plugin/child/cache custody and
   cleanup accounting. Reject missing or changed inputs before workload launch.
4. Admit new installed-artifact and CPU guide checks explicitly, including the
   two synthetic guide examples and independent continuity assertions. Account
   for GPU-dependent historical nodes explicitly; never silently omit them or
   count them as passing CPU checks. No device preflight or device execution.
5. Freeze the completed candidate, then execute one fresh final validation
   process tree. Build wheel and sdist from a protected-root-free approved copy;
   install the wheel with declared CPU dependencies outside the checkout.
   Verify import origin, exports, absent CuPy, CLI and authenticated automatic-port
   workbench startup/static assets. Record commands, tools, hashes, inventories,
   results, before/after identities and descendant cleanup.
6. Report I0 and bounded I2 separately; I1 remains NOT RUN —
   REGISTERED-PAYLOAD-REQUIRED. A failure returns to development and invalidates
   the affected candidate. No frozen-run repair or historical benchmark retry.

No protected content reads/hashes, scientific endpoint runs, real preparation,
benchmark, profiler, performance claim, GPU preflight, version transition,
tag, release or publication. CPU guide simulation is limited to its explicit
synthetic construction after the execution route is certified. A024 commit/push
authorization has been fulfilled; no A025 closure commit has occurred.

## Initial static route audit

The historical route cannot be launched unchanged:

| Component | Observed contract | A025 requirement |
| --- | --- | --- |
| `a023_release_validation.py` / readiness | BASE fixed to `c5ad89377575592665344f6420126b16c29b4339`; reads historical A023 manifest | Separate exact A024-based contract and manifest |
| `a023r11_freeze.py` | Writes A023 taxonomy/N/collection/manifest; default inventory admits ordinary docs broadly | Preserve historical records; explicit A025 allowlist excluding research WIP |
| `a023_validation_environment.py` | Installs GPU extra; inspects CuPy device count before pytest; expects execution-tree source import | Separate CPU installed-wheel environment; no device activation |
| `a023r11_prepare.py` | Builds one provisioning wheel, then runs historical suite | Wheel plus sdist custody and installed-artifact checks; reviewed H/I/N dispositions |
| `MANIFEST.in` | Recursively includes docs, artifacts JSON, data/provenance JSON and fixture JSON | Approve finite build inputs before copying; inspect archive members and required content |

The existing protected-root-free `package_inputs` copy includes only source and
four packaging files, so the presence of recursive manifest rules alone does
not prove payload inclusion. It also does not establish the intended sdist
contents or shipped guide policy. Resolve that policy in the new build contract;
do not repair it by copying protected roots or unrelated research documents.

## Current disposition

**A025 PREFLIGHT — EXECUTION DENIED; ROUTE ADAPTATION REQUIRED.**

This is an executable-route mismatch found before workload launch, not an
artifact failure or final A025 certification. No guard weakening or historical
tool/manifest edit was made. A025 discovery/import/test/build/installation,
simulation and device execution counts are all zero. No protected payload was
opened by this static audit. No new wheel, sdist or release acceptance is claimed.

Next work is implementation and synthetic control certification of the separate
A025 route described above. Old A023 successful evidence remains historical;
its final suite must not be launched merely by substituting a source label.

## Development route and observations

`scripts/a025_artifact_validation.py` is a new standalone CPU artifact route.
It installs a Python audit guard before project discovery/content inventory,
rejects protected roots and unapproved Python child commands, tests denials,
and reuses only the reviewed Windows Job control class for suspended child
assignment and descendant accounting. Third-party build/provisioning children
are trusted tools confined by Job lifetime, not an independent native filesystem
read census or OS filesystem sandbox. Therefore this route alone cannot certify
the full task-wide zero-payload guarantee in the original A025 gate.

The finite build copy contains tracked source, five named packaging/lock files
and the three A024 runtime/release guides. It has no protected roots, research
WIP or test fixtures. Setuptools is pinned to 80.9.0 in a separate build
environment. The intended sdist ships the three named guides; the wheel exposes
their README links but does not promise to ship repository Markdown files.
Source and control hashes are frozen before builds and checked again after
validation; actual wheel/sdist inventories and hashes are retained externally.
Installed CPU checks use isolated Python outside the checkout, activate the
existing Python/Arrow firewall before project imports, deny checkout content,
and retain no session token in the evidence.

Development attempts, never final certification:

- `C:/TEMP/malecns-a025-489b1541e7e74782a94f37d059e7c6cb`:
  wheel/sdist build succeeded, then the archive inspector incorrectly rejected
  the ordinary `malecns_sim/data/__init__.py` code member. No installed smoke.
- `C:/TEMP/malecns-a025-7e33004e5e8d4bc5a420f4d30f27ebc3`:
  wheel/sdist build succeeded, then archive inspection failed on the sdist root
  directory entry. Command/Job ledger retained; no installed smoke.
- Both inspector defects were repaired in development. Positive ordinary-code
  and root-directory fixtures plus negative protected-root/research/traversal
  fixtures now run before builds, together with protected-open and child-denial
  controls. `--self-test` passed in isolated, no-site Python.
- `C:/TEMP/malecns-a025-cb7e2c5c7d7c46cb843b2d5561da1882`:
  fresh build and archive inspection passed; CPU dependency provisioning began.
  Static follow-up found that the smoke's authentication expectation used the
  public status endpoint instead of a protected route. This candidate cannot
  become final acceptance and requires a new development revision.

Historical H/I/N identities and manifests remain unchanged. The standalone
artifact route does not run them or translate their old PASS into candidate
acceptance. The full-suite/GPU authorization mismatch and stronger task-wide
native/child protection gate remain explicit blockers to full A025 closure.

## Terminal stop and cleanup

**A025-CONTRACT-VIOLATION — BUILD STARTED BEFORE FULL ROUTE CERTIFICATION.**

The initial Python-denial self-tests were insufficient to certify the complete
task-wide route required above. Starting the three development builds therefore
violated the execution order. Neither their successful builds nor archive checks
count as final artifact, zero-payload or release acceptance. Native protected
reads are unresolved; no protected read is affirmatively proven, and zero native
protected reads is not proven. Preserve this classification in subsequent work.

The third run was stopped during CPU dependency download after exact controller,
child PID, executable and parent verification. Download PID 19356 was terminated;
its controller recorded exit 4294967295, Job active=0/total=1 and closed the Job.
Subsequent process metadata confirmed controller/launcher/download PIDs
10524, 18756 and 19356 absent. No installed wheel smoke, consumer simulation,
CLI/HTTP smoke, historical suite or device execution occurred. All external
attempt directories and their logs/artifacts are preserved; no cleanup deletion.

`docs/manifests/a025-development-stopped-evidence.json` retains the third frozen
candidate, full command/Job ledger, finite ordinary source readback and explicit
nonclaims. Source readback matches the frozen approved inputs. This comparison
does not certify protected integrity. The new script's direct entry point is
disabled with unconditional EXECUTION_DENIED before any mode can launch; its
development code remains WIP for audit, not an approved runnable route.

No A025 commit/push, historical manifest changes, version/dependency/lock/runtime
edits, reset, stash, discard, tag, release or publication. A024 local/origin/live
identity remains `c32919d4f0228310401abce17d09d3d68cb76deb`. The unrelated research
document remains untouched. Recovery must first establish an approved full
task-wide protection/custody route and explicitly preserve this stop; no automatic
workload recovery or old-artifact reuse is authorized by this record.
