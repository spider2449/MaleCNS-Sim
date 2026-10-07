# Code review recovery: Phase C result

Date: 2026-10-07.

Terminal result: FINAL CERTIFICATION FAIL. G16 remains NOT PASS. This report is
post-run documentation, outside the frozen candidate input set. It does not
replace or alter the frozen plan, manifest, execution tree or historical runs.

## Frozen identity and execution

Candidate manifest SHA256:
f47db1fbd8eb166526060041a2156270d4f4d26a2a4e1ffb1e1fcc2918b08e99.
Candidate inputs: 432. Exact collection: 1545 = H 1503 + I 12 + N 30.
The former manifest is retained byte-for-byte as
docs/manifests/a023r11-before-code-review-frozen-candidate.json, SHA256
4b04b8ec50f8fdab7a99e2d33922d1ef8fdc639ab9de74c278b5b1525a4fb8d2.

Fresh run root:
C:/TEMP/malecns-a023r11-final-4db6e8bfab7b47798318d85b0e681434.
Base: c5ad89377575592665344f6420126b16c29b4339.
Python 3.12.13; pytest 9.1.1; exactly 13 lock-resolved runtime/dev distributions.
The source project and optional GPU extra were not installed by the existing
provisioner. Fresh process, environment, temp and caches were used. The builtin
plugin census accepted 41 registrations and exact final collection succeeded.
Exactly one final suite invocation ran; no repair or retry occurred in Phase C.

Suite result: 1423 passed, 96 failed, 14 skipped, 12 deselected, one warning;
291.40 seconds. Pytest exit=1; final runner exit=1. All ten code-review regression
cases passed, including the real builtin census and three completion paths.

## Failure evidence

Twenty-four failed reports directly raise PackageNotFoundError for malecns-sim.
RunIdentity.create requires installed distribution metadata, but the provisioner
uses --no-install-project. Twelve other failures occur in dependent A007B/A007C
workflows with failed/missing child results. Their relationship to the missing
metadata is an inference from the execution path; this run did not isolate or
repair those twelve failures independently.

Sixty failed reports raise RuntimeError: CuPy is not available. These retained
GPU tests do not all skip when the optional extra is absent. The runtime/dev-only
fresh environment therefore does not satisfy their execution prerequisites.
Assertions and taxonomy were not changed during the final run to bypass this.

Any future recovery must return to development, resolve project-metadata and
optional-GPU provisioning/taxonomy explicitly, verify the controls, freeze another
candidate and use a wholly fresh Phase C. No second run is authorized by or
performed within this completed one-run task.

## Integrity, protection and cleanup

I0=PASS for unprotected frozen content only. I1=NOT RUN —
REGISTERED-PAYLOAD-REQUIRED. I2=PASS for bounded manifest/collection consistency.
All 432 input hashes and the manifest matched before and after execution, and
were independently compared against the current checkout after the run. The
execution tree has neither data nor artifacts roots. B0/B3 pinned identities
were verified before freezing and are retained as candidate inputs.

Final parent counters: accepted protected checks=0, denied protected checks=63.
The final evidence records protected_payload_accepted_opens=0 and 75 blocked
firewall events. These are the runner's scoped process/check and firewall-log
observations, not an independent census of every native read. Expected denial
controls are included in blocked counts. No release-safe suite PASS is claimed.

Windows Job accounting: total=105, active=0, terminated=0 after suite exit.
The Job was closed. No active contained descendants remained. The fresh failed
tree and previous worktrees/evidence are preserved.

Evidence SHA256:

- environment.json: 129574f349ecd3f2e327598ce8ae765f361654dcefce7deb09e42212273134b6
- final-validation.json: 06fcd8f09014c883269f2425775d6aa26742d76aa2d0f8258606ce7876ef5c01
- suite-output.txt: 894b4ab3096aa68de9ef1f4e9961648a19cb7c524f824ff8b558a5061987f771

Local HEAD and origin/master remain the base SHA; live master matched before
freezing. Staging/stash remained empty. Existing WIP was preserved. No protected
hashes were recomputed, no full protected integrity or packaging PASS is claimed,
and no reset, stash, discard, commit, push, release, tag or version change ran.
