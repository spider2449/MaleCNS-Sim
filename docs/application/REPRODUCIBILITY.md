# Application reproducibility record

Package metadata: `malecns-sim` **0.3.0**. Current runtime implementation
acceptance is [A023-A](../plans/2026-10-07-application-a023-r11-closeout-result.md)
at commit `70d494b144162aff2e8918bf81e96508dea92a34`. This is not new-wheel
certification. For intended 0.4.0 artifact validation use the
[application/runtime gate](../runtime/RELEASE_GATE.md) and
[consumer examples](../runtime/USER_GUIDE.md).

Historical A008 application source baseline:
`257355c266e2a41d4b5af0bb4412dbca6e9aa07d`. A008 adds documentation and
certification checks to that baseline, with no product behavior changes.
Historical annotated `v0.3.0` peels to
`a1a6651163840a982799b1fa82c1904e67f84660`; it is not the later application source.

Python >=3.12 and uv are assumed. A008 checkout validation uses Python 3.14.0
and uv 0.11.8 on Windows; installed-wheel certification uses an isolated Python
3.12 environment. See [USER_GUIDE](USER_GUIDE.md) for tested checkout and
installed-wheel installation commands, optional GPU setup and the complete
operating workflow. Entry point: `malecns-workbench`, mapped to
`malecns_sim.application.server:main`. Normal checkout startup:
`uv run malecns-workbench` (loopback, automatic available port).

Dataset prerequisite: DatasetCatalog's `male-cns-v1` registered, provenance-pinned
Feather resources under the selected data root. Data is not packaged. Use
`MALECNS_DATA_ROOT` or the working directory's `data` root, as documented in
the user guide. Installed startup and data-unavailable API smoke require no data.
Real operation requires data; A008 performs no real simulation.
CUDA is optional and needs the `gpu` extra plus compatible hardware/environment;
CPU-only UI startup does not import CuPy. No broad numerical parity is claimed.

## Contract identity

| Contract | Version |
|---|---|
| Experiment | application-experiment-v1 |
| Result | application-result-v1 |
| Playback | application-playback-v1 |
| Comparison | application-comparison-v1 |
| Preparation variant | application-preparation-variant-v1 |
| Robustness | application-robustness-v1 |

Preset: `application-historical-variation-family-v1`.
Preset digest: `34de3189f0630c159fabe140892362ec65228487984224ef880702eb3fd8f139`.
Its definition provenance names source commit
`c02501e114b487a4c41926a4a04a950e06ce8b7c`; this differs from the current
application baseline deliberately. Canonical backend digests, export byte hashes,
and visualization data are distinct identities.

## Local validation and installed artifact

There are zero active tracked GitHub Actions workflows. Historical CI evidence
does not replace current local validation. From the checkout:

The following commands are generic development checks, not a guarded zero-payload
release route. Tests/integrity can read tracked scientific evidence. Current
release-safe validation requires the separately authorized candidate gate above,
with I1 reported separately as NOT RUN when protected inputs are excluded.

```powershell
uv sync --frozen --group dev
uv run pytest
uv run python -m compileall src scripts tests
uv run python scripts/check_tracked_integrity.py
git diff --check
uv build
```

The [A008 certification record](../plans/2026-10-02-application-a008-documentation-reproducibility.md)
records exact results and wheel SHA-256 after final validation.
Wheel filename: `malecns_sim-0.3.0-py3-none-any.whl`. Install the actual newly
built wheel, not an editable project. Certification runs outside the checkout,
records `malecns_sim.__file__` in installed site-packages, verifies CuPy absent,
installed entry point, HTML/CSS/JS including playback/compare/robustness,
protected API and automatic-port startup. No source checkout is required to
serve the UI. This certifies packaging/operation, not a release or scientific
data reproduction; it does not certify real-data preparation/runtime performance.

## Scientific boundary

Schematic layout is not anatomical geometry. Playback displays recorded output,
not reconstructed biological propagation. Comparisons are model-output deltas,
not biological causality, inhibition, necessity or behavior prediction.
Application R0–V7 evidence uses NO_AGGREGATE_RULE and yields no default
ROBUST/NOT_ROBUST verdict. Historical Task017 separately remains NOT_ROBUST;
Task017Q remains Q1 — KEEP_DEFERRED. Synthetic review fixtures have no scientific
result meaning. Historical artifacts and external archives are unchanged.
