# Code review recovery: fresh Phase C

Date: 2026-10-07.

The user explicitly authorized a new frozen candidate and a fresh Phase C run,
including synthetic regression workloads without protected scientific payload.
Preserve existing WIP and historical certification failures. No release, tag,
version change, commit or push is authorized by this validation task.

Before freezing, admit the ten reviewed mock/plugin regression identities in
addition to the original twenty N identities, collect exact H/I/N under the
active payload firewall, and verify the targeted controls in development.
Preserve the previous frozen manifest separately. Freeze source/test/runtime
only after those checks pass. Execute the final suite once in a new exact-base
tree, environment, process and cache with containment and payload protection.
Do not repair or retry during Phase C. Record terminal evidence separately.

## Pre-freeze development evidence

Thirty targeted controls passed with the payload firewall active before pytest
import. Full development collection contains exactly H=1503, I=12, N=30,
total=1545, with no duplicate or additional identities. Collection only did
not execute workloads. The original twenty N identities are retained from the
SHA256-pinned historical manifest; ten exact reviewed identities are added.
The freeze tool rejects any other N identity. Historical manifest bytes are
preserved in docs/manifests/a023r11-before-code-review-frozen-candidate.json.

Local HEAD, origin/master and live master all equal
c5ad89377575592665344f6420126b16c29b4339. Staging and stash are empty.
Existing worktrees remain retained. Git diff whitespace validation passed.
All development evidence is NOT FINAL CERTIFICATION.

The first pre-freeze attempt was rejected by the unchanged payload firewall
when the freeze tool tried to spawn Git for its metadata-only inventory. No
Phase C started. H/I/N files were written, but the candidate manifest was not.
The controller now supplies the exact Git metadata inventory as an explicit
file so the guarded freeze process does not need a child-process exception.

This plan is part of the frozen candidate. Terminal run evidence will be
recorded in the dedicated fresh run directory and a separate post-run report,
without modifying this frozen input or repairing product/tests during Phase C.
