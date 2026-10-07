# Validation environment recovery

Date: 2026-10-07.

The user requested continuation after the fresh Phase C failure. Return to
development to repair provisioning, preserve the previous run and manifests,
verify targeted controls in a separate protected-payload-free environment,
then freeze a new candidate and execute one fresh Phase C. No repair or retry
is permitted inside that Phase C. No protected integrity, real-source workload,
release, publication, tag, version change, commit or push is authorized.

Retain scientific assertions and all H/I identities. Install the frozen gpu
extra rather than excluding the sixty failing GPU cases. Create an ordinary
local wheel from an independent temporary copy of frozen packaging/source
inputs with no protected roots, then install it without resolving dependencies.
This supplies genuine distribution metadata without writing generated build
files into the immutable execution source tree. This is validation provisioning,
not a release packaging certification. Record the wheel identity and verify the
installed project/runtime/dev/GPU dependency closure, source import location,
and device availability before test collection.

Keep the old infrastructure-only dependency checker and B0/B3 firewall unchanged.
Add dedicated environment controls and exact N identities. Development and final
processes activate the unchanged protected-payload firewall before imports or
collection. The source checkout's existing environment is not modified. Final
evidence must distinguish scoped protection counters from a universal native-read
census, and preserve all previous FAIL dispositions.

## Development evidence and new freeze boundary

The existing source checkout environment failed the new strict metadata census:
two malecns-sim distributions were discoverable. No change was made to that
environment and the census was not relaxed. Initial local controls: 20 passed,
one expected environment rejection; those results are development evidence only.

Independent development root:
C:/TEMP/a023-environment-development-547329159b454e949a4730444284535b.
The guarded snapshot excluded protected payload roots. Its separate provisioning
created one real local wheel and 25 exact lock-resolved installed distributions,
with Python 3.12.13 and one usable GPU. Source imports resolve to the independent
execution tree rather than the installed wheel. All 209 selected development
tests passed in 44.33 seconds, including every module that failed in the previous
final run, the public facade, completion race and environment authority controls.
Selected source/test identities match the current candidate. The development Job
ended with total=7, active=0, terminated=0. These results are NOT FINAL CERTIFICATION.

Final exact collection is H=1503, I=12, N=41, total=1556. The original H/I and
twenty N identities remain unchanged; ten earlier code-review cases and eleven
new environment controls are explicitly admitted. The previous candidate is
retained in docs/manifests/a023-before-environment-recovery-frozen-candidate.json,
SHA256 f47db1fbd8eb166526060041a2156270d4f4d26a2a4e1ffb1e1fcc2918b08e99.

Local HEAD, origin/master and live master all match
c5ad89377575592665344f6420126b16c29b4339. Staging/stash remain empty. B0/B3
remain unchanged. This plan is the final pre-freeze record. No source/test/runtime
edits will occur during Phase C; a separate post-run report will hold the result.
