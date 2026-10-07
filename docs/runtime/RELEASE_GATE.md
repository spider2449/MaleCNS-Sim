# Application/runtime candidate release gate

Status: **PREPARATION READY; ARTIFACT VALIDATION NOT RUN; PUBLICATION NOT AUTHORIZED**.
This gate concerns the intended 0.4.0 engineering release. Package version remains
0.3.0. It complements the [historical scientific gate](../MALECNS_RELEASE_GATE.md)
without rewriting scientific results or certifying protected payload integrity.

## Frozen scope

Stable CPU factory/opaque state/detached output, legacy compatibility and packaged
workbench; optional experimental GPU and engineered synthetic Arena. The
[consumer guide](USER_GUIDE.md) and [candidate notes](../releases/0.4.0-preparation.md)
define claims and exclusions. Task026 remains
NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY. No routine real-data preparation,
benchmark, GPU timing, scientific endpoint rerun or archive recovery.

## Required future evidence

| Gate | Acceptance requirement | Current disposition |
| --- | --- | --- |
| Candidate identity | Exact local/origin/live source SHA; complete dirty/staged/WIP inventory; frozen ordinary input/lock hashes | A024 starting SHA recorded; final candidate not yet frozen |
| Guarded validation | Approved task-wide guard before discovery/import; fresh sparse execution tree, environment, plugin/child/cache custody; preserve exact H/I/N and terminal exclusions | A023 historical PASS only; fresh candidate run NOT RUN |
| Changed validation inputs | Explicitly review additions and taxonomy; keep numerical oracles and all exclusions, never silently broaden grants | New example checks require admission; NOT RUN |
| Integrity split | I0 unprotected content; I2 bounded consistency; report I1 separately | Fresh checks NOT RUN; I1 NOT RUN — REGISTERED-PAYLOAD-REQUIRED |
| Build custody | Approved protected-root-free ordinary source tree; fresh wheel and sdist; source/lock/build-tool identities, logs, hashes and inventories | NOT RUN |
| Installed CPU artifact | Fresh outside-checkout environment with declared dependencies; actual wheel import location, runtime exports and absent CuPy | NOT RUN |
| Consumer examples | Run both guide CPU examples from installed artifact; retain assertions/output; independent continuity oracle for API regressions | Static review only |
| CLI/static assets | Installed malecns-sim and malecns-workbench help/startup, automatic-port authenticated API/static asset smoke without data | NOT RUN |
| Artifact exclusions | Inspect wheel/sdist contents; no raw inputs/caches/secrets/unrelated research WIP; document which guides/examples ship | NOT RUN |
| GPU optionality | CPU import/install without GPU; extra metadata/locked closure checked separately; no mandatory device execution | Static metadata review only |
| GPU claim | Fresh device certification only with separate explicit authority; fake-device/structural tests do not certify hardware | Experimental; historical EQ-B only |
| Version transition | Explicit authority to set version and synchronize metadata/lock/notes; freeze and validate resulting bytes | NOT AUTHORIZED |
| Publication | Exact tested artifact/source identity, final diff/scope/cleanup report, explicit tag/release/publication authority | NOT AUTHORIZED |

A023 counted H=1503, I=12, N=41 (1556 collected, 1544 passed, 12 NOT RUN).
The eleven protected prerequisites and one absent external baseline are explicit
terminal exclusions. They do not become passing tests when omitted. Keep original
H/I identities; review any new validation checks as N. Any source/metadata/version
change after freeze invalidates affected certification and requires a fresh
candidate, not relabeling the old evidence.

## Bounded validation route

Separately authorize A025 before execution. Review the A023 provisioner/freezer/
runner as ordinary text, adapt their approved frozen inputs to the actual candidate
and example/artifact checks, and certify the route before discovery or build.
Do not treat a bare checkout pytest or build as a zero-payload certification route.
Use the existing H/I/N/taxonomy/final evidence under docs/manifests as historical
authority; they are not commands to import unchanged and certify different bytes.

Freeze after development checks, then use one fresh final environment/process tree
with plugin census, exact child authority, before/after ordinary hashes and cleanup
accounting. Build only from explicitly approved ordinary inputs; install the actual
wheel outside the checkout with runtime dependencies. Record Python, OS, package
versions, command lines, source/lock/artifact hashes, import locations, entry points,
assets and complete results. CPU guide execution is synthetic simulation and must
be named in that authorization. Device preflight/example execution is separate.

If a failure requires repair, return to development, invalidate the candidate and
report the failure. Never patch a frozen run, weaken the firewall, compute protected
hashes to fill I1, or reuse an old wheel as current evidence. No retry of any consumed
historical real benchmark is authorized by this route.

Release-safe I0/I2 acceptance alone cannot satisfy a policy requiring full I1.
The release decision must explicitly retain/adjudicate that boundary; missing
protected integrity is a blocker under any full-integrity requirement. Similarly,
Python >=3.12 metadata is not evidence of every Python/platform combination.
A008's installed wheel and A023's provisioning wheel are historical evidence only;
A009 blind new-user acceptance remains uncertified.
