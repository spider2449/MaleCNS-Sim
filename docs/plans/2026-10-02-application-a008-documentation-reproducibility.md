# Application A008 — Documentation and reproducibility certification

Start gate PASS: dynamically derived repository root; local/origin/live master
257355c266e2a41d4b5af0bb4412dbca6e9aa07d; clean worktree, empty stash,
version 0.3.0, no tracked workflows. Historical v0.3.0 target:
a1a6651163840a982799b1fa82c1904e67f84660. A003–A007 and A006S certifications
verified in their closure records. Task017 NOT_ROBUST; Task017Q Q1 — KEEP_DEFERRED.

Scope: operating guide, reproducibility manifest, README links, narrow contract
checks and installed-wheel smoke certification. No product behavior changes.

Plan:
1. Cross-check production UI, catalog, playback, pairing and variant contracts.
2. Write guides and narrowly useful schema/asset documentation checks.
3. Verify documented commands, application regressions, full tests, compilation,
   offline integrity, whitespace and build.
4. Install the wheel in an external temporary CPU-only environment; verify import
   location, entry point, assets, protected API, automatic ports and shutdown.
5. Record evidence and exact wheel hash; commit/push only after certification.

Scientific execution boundary: real MaleCNS simulations, Task017 units,
Task017Q, downloads, archive writes and BANC all zero. Historical artifacts and
external archive unchanged. No tag, release, version bump or GitHub Actions.

## Certification evidence

Verdict: **A8-DOCUMENTATION-REPRODUCIBILITY-CERTIFIED**.
Classification: documentation and installed-artifact reproducibility; no new
product capability or scientific certification.

USER_GUIDE and REPRODUCIBILITY created; README links all three application
guides. Production HTML/JS, DatasetCatalog, result/playback/comparison contracts,
preparation preset and robustness manager were inspected. No product/document
mismatch was found. Historical architecture audit/pending records remain
historical and are superseded by their existing A007C closure.

- Frozen development sync executed successfully; CPU-only environment, Python
  3.14.0, uv 0.11.8. Optional GPU CLI flags, pyproject extra/group and check_gpu
  script inspected only; no GPU execution or parity certification.
- Final full pytest: **384 passed, 14 skipped**, 53.84 s. Skips: 13 CUDA checks
  and one opt-in real-data check. Includes all 139 application/session regression
  tests and two new documentation checks. Focused documentation run: 2 passed.
- compileall, tracked integrity (9 files/internal identities), diff check and
  uv build: PASS. No GitHub Actions invoked.
- Normal `uv run malecns-workbench`: startup/root HTTP PASS; explicitly fixed
  port 48765: PASS. Port 8765 was occupied and correctly rejected; existing
  server processes were not stopped. Test-owned process trees were stopped.
- New wheel: `malecns_sim-0.3.0-py3-none-any.whl`.
  SHA-256: `6d497b2ee0da30002c20c39f0520694b15a8180269e0207a9f03c6d221245843`.
- External temporary environment: system temporary directory,
  `malecns-a008-3ddc8f7df9d44e55be78cf10ca32f6c0/.venv`, CPython 3.12.13.
  Wheel copied there and installed with uv pip; no editable install. Commands
  ran there with PYTHONPATH removed for server children and no local dataset.
  Import location relative to that temporary directory:
  `.venv/Lib/site-packages/malecns_sim/__init__.py`. Source leakage: **No**.
- CuPy absent; installed malecns-workbench entry point starts two independent
  processes, each with a distinct available default port and instance ID.
  HTML, CSS, app/run-status/playback/compare/robustness JS packaged and served:
  PASS. Protected run/robustness GET rejects missing token (403), authenticated
  calls return 200. Authenticated validation POST reaches contract validation
  and rejects an empty spec (400), without submitting any run.
- Installed command controlled KeyboardInterrupt test calls server_close and
  prints clean stop message: PASS. Physical console Ctrl+C not exercised;
  smoke processes were terminated after checks. Session-refresh behavior is
  represented from existing A006S certification and inspected production JS.
- A supplementary unauthorized POST probe received a Windows connection reset
  on early rejection with an unread request body. The final smoke uses protected
  GET rejection and authenticated validation POST; no bypass or behavior change.

All documented CPU/install commands executed. GPU commands contract-checked
only. Exact wheel operation depends on packaged code and installed dependencies,
not source-tree files; real scientific operation still requires external data.
No absolute checkout paths or actual tokens introduced in tracked content.

Real MaleCNS simulations 0; Task017 units 0; Task017Q 0; raw-data downloads 0;
archive writes 0; BANC 0. Historical scientific artifacts unchanged (changed-file
scope restricted to README, these application docs/plan and the documentation
test). External archive untouched. Package 0.3.0 and historical tag unchanged.

Next recommended task: **Application Task A009 — Independent new-user operating
guide walkthrough**, using installed-package startup and synthetic/existing
evidence only, with a separately authorized scope. Do not start automatically.
