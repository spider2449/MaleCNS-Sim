# Validation environment recovery: final result

Date: 2026-10-07.

Terminal result: ZERO-PAYLOAD RELEASE-SAFE VALIDATION PASS for this fresh final
run only. The prior certification failures remain historical failures. This
post-run report is outside the frozen candidate and does not modify its inputs.
Full protected-content integrity and release certification remain unclaimed;
the historical full G16 gate is not promoted to PASS by this narrower result.

## Change and development evidence

The provisioner now installs the locked runtime/dev/GPU dependency closure and
one genuine malecns-sim distribution. A local wheel is built from a separate
temporary copy of ordinary source/packaging inputs, without data or artifacts
roots, then installed without dependency resolution. Build products never enter
the immutable execution source tree. Imports during validation still resolve to
that frozen source tree. This local installation supplies metadata and is not
release packaging certification. This recovery changes validation provisioning
only; the prior runtime/run-manager fixes are retained. Project version,
scientific equations and production defaults remain unchanged. Original H/I
assertions, frozen scientific fixtures and tolerances
remain intact; GPU tests were supplied their prerequisites rather than excluded.

The environment checker verifies project/runtime/dev/nested-GPU extras and
rejects missing, duplicate, additional or drifted distributions, wrong source
imports and absent GPU availability before collection. The historical
infrastructure-only checker and pinned B0/B3 firewall remain unchanged.

Development-only evidence: 209 selected tests passed in a wholly separate
environment, including every previously failing module and eleven new
environment controls. No development pytest result, environment or cache was
reused as final evidence. Existing checkout environment/WIP remained preserved.

## Frozen identity and final run

Candidate manifest SHA256:
c36fc228349bb5f7c8a2f17b709f2f5a5d803547f4c1008c9f236ddba3ccdcf5.
Frozen ordinary inputs: 437. Exact collection: 1556 = H 1503 + I 12 + N 41.
Taxonomy: Z0=1467, Z1=11, Z2=0, Z3=25, Z3-BLOCKED=0. The original twenty N
identities, ten earlier review controls and eleven environment controls are
explicitly retained/admitted. Twelve historical nodes are explicitly NOT RUN:
eleven require registered protected payload; one requires an absent external
starting-SHA fixture. They are deselected, not silently counted as passes.

Fresh run root:
C:/TEMP/malecns-a023r11-final-dcdeef88bc624893a8bc4160249e6c67.
Base: c5ad89377575592665344f6420126b16c29b4339.
Python 3.12.13; pytest 9.1.1; 25 installed distributions exactly match the frozen
project/runtime/dev/GPU lock closure. One usable GPU; 41 accepted builtin/plugin
registrations. Fresh execution tree, environment, process, TEMP/TMP and caches.
Source origin is execution/src/malecns_sim/__init__.py under the fresh run root.

Exactly one final suite invocation ran. Result: 1544 passed, 12 deselected,
zero failed, zero skipped, one warning, 314.25 seconds. The warning is the retained
negative Feather V1 fixture's deprecation warning. Both pytest and runner exit=0.
No source/test/runtime repair or retry occurred during Phase C. No performance,
full-real CPU/GPU speed, biological or new scientific conclusion is inferred.

Installed local wheel SHA256:
235b151ef558a073d28d1f18b0a8e3016d28bbe76d1794a23c3ce1852b330cd8.
Its path and exact packaging/source input hashes are in environment.json.

## Integrity, protection and cleanup

I0=PASS for unprotected frozen content only. I1=NOT RUN —
REGISTERED-PAYLOAD-REQUIRED. I2=PASS for bounded manifest/collection consistency.
All 437 hashes and the manifest match before/after execution. Independent
post-run comparison also verified current-checkout and execution-tree bytes,
manifest identity and the installed wheel artifact hash. Neither data nor
artifacts roots exist in the execution tree. Protected hashes were not recomputed.

Final parent counters: accepted protected checks=0, denied protected checks=63.
The runner records protected_payload_accepted_opens=0 and 75 blocked firewall
events, including expected negative controls. These are the fresh runner's
scoped parent check/wrapped-reader and child-firewall observations, not an
independent census of every native read or a task-history zero-payload claim.

Windows Job accounting: total=106, active=0, terminated=0 after suite exit.
The Job was closed and no active contained descendants remained. All historical
and new failed/successful execution trees and evidence remain preserved.

Evidence SHA256:

- environment.json: b36e0a13a8f5569740250a972d868bcead9f9d846da3b63c8d0c8847b6d84fc9
- final-validation.json: 874d63de386e984642b879d39e141fce2a1202ac39b6f2cc451e89e32c423c3f
- suite-output.txt: 23d2cae12815d442a2807d62a19f0b89198db7606649a798c250eebc5b67c81e

## Scope and Git custody

This clears the metadata/GPU prerequisites and the guarded final suite blocker
for the scoped route. It does not certify the twelve excluded nodes, full
protected integrity, restored historical payload, release packaging or release
readiness. The historical full G16/A023 disposition is not silently rewritten.

Local HEAD, origin/master and live master all remain
c5ad89377575592665344f6420126b16c29b4339. Staging/stash remain empty. Existing
WIP and worktrees are preserved. No reset, stash, discard, commit, push, release,
publication, tag or version change occurred.
