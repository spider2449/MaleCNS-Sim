# A007A configurable preparation and variant contract

Date: 2026-10-02. Starting HEAD: c02501e114b487a4c41926a4a04a950e06ce8b7c.

The original A007 audit remains A7-CONTRACT-GAP. This prerequisite adds backend infrastructure only; no robustness matrix, UI, scoring, or historical execution is authorized.

## Implementation plan

1. Preserve application-experiment-v1 bytes and ordinary run identities. Introduce a separate preset-owned variant experiment envelope and domain-separated identity.
2. Add immutable resolved preparation configuration and literal R0-V7 definitions. V5 derives direct input from weight times 250. V7 uses an explicit sign-policy allowlist.
3. Pass resolved configuration to shared preparation and existing CPU/CUDA simulation primitives. Retain the no-config call path.
4. Extend strict A006 pairing with variant identity equality. Add bounded session/parent-owned child retention independent of eight-entry Recent Runs.
5. Prove all definitions and synthetic execution, historical identity preservation, pairing, and sixteen-child retention. Run required regressions, integrity, build, and fresh-wheel startup.
6. Record evidence and remaining A007 work. Commit/push only after certification and an unrelated-change audit.


## Audited production boundary and reference configuration

Application DatasetCatalog.spec freezes normal LIFParameters and Shiu2024SignPolicy. Service._schedule generates explicit Poisson schedules using weight_factor times the declared anatomical weight. ProductionEngine.prepare delegates to Task008.prepare_network, which loads and curates the unsigned projection, resolves neurotransmitter evidence using MaleCNSV1ConsensusThenPredictedThenCelltype, assigns signs, and creates EffectiveSignedProjection. Previously signing and effective weight were hard-coded defaults there. ProductionEngine.simulate passes LIFParameters to simulate_lif or lazily imported simulate_cuda. Time constants, delay, rest/reset, refractory period, and threshold control the existing simulator, while anatomical weight controls both the prepared projection and direct stimulus generation.

PreparationConfig is a frozen slots dataclass containing frozen LIFParameters, an allowlisted sign_policy_id, the fixed resolution_policy_id, direct_input_weight_factor, and a versioned derived-input rule. All physical numbers use finite validated LIFParameters; factor is fixed at 250, and derived amplitude must remain finite. Configuration serialization uses canonical finite JSON and a domain-separated SHA-256 digest. The lower engine receives resolved parameters and a policy object; it knows no R0-V7 switches. Client decoding accepts only preset_id and variant_id. There are no dynamic imports or client-supplied class names. There is no free-form parameter API.

R0 exactly matches production defaults: rest/reset -52 mV, threshold -45 mV, tau_membrane 20 ms, tau_synapse 5 ms, refractory period 2.2 ms, delay 1.8 ms, anatomical weight 0.275 mV, Shiu2024SignPolicy, reference neurotransmitter resolution, factor 250, direct-input amplitude 68.75 mV. Normal no-config preparation retains its historical fingerprint payload and default graph behavior.

## Literal preset and identity

Preset: application-historical-variation-family-v1. Variant schema: application-preparation-variant-v1. Each immutable member binds schema, preset ID/digest, variant ID, reference configuration digest, exact ordered override set, full resolved configuration, and source provenance at the starting commit. R0 is the predecessor/reference configuration; variants cannot supply additional overrides. Historical Task016 and Task017 definitions were read as evidence only. No historical runner is imported by production Application modules.

| Member | Exact override | Derived direct-input amplitude |
| --- | --- | --- |
| R0 | None | 68.75 mV |
| V1 | tau_membrane_ms = 10 | 68.75 mV |
| V2 | tau_membrane_ms = 30 | 68.75 mV |
| V3 | tau_synapse_ms = 2.5 | 68.75 mV |
| V4 | synaptic_delay_ms = 1 | 68.75 mV |
| V5 | synaptic_weight_per_anatomical_synapse_mV = 0.200 | 50 mV |
| V6 | v_threshold_mV = -44 | 68.75 mV |
| V7 | sign_policy_id = ConservativeSignPolicy | 68.75 mV |

V5 amplitude is derived from weight times the fixed factor 250, not independently overridden. Task017.VariantConfiguration.parameters and frozen_specification's direct_input record prove this relationship. V7 resolves through an explicit two-policy allowlist: Shiu2024SignPolicy and ConservativeSignPolicy. Conservative signing assigns acetylcholine and GABA only, leaving glutamate and modulatory transmitters unresolved.

VariantExperimentSpec adds an application-variant-experiment-v1 envelope around an unchanged historical reference ExperimentSpec. Its model/sign views expose the resolved configuration to service, preparation and simulator. The envelope digest includes the complete variant definition. RunIdentity retains its existing representation but chooses the additive malecns-application-variant-run-v1 domain for variant envelopes. Explicit variant R0 therefore cannot collide with ordinary R0. Result authoritative content includes the envelope; provenance includes full preparation_variant, variant_digest, preparation_config_digest and actual graph fingerprint. Variant result verification checks provenance bindings and recomputes execution identity. Decoding verifies the exact preset definition, preventing metadata-only or arbitrary-config variants.

No default/null variant field was added to application-experiment-v1. Ordinary canonical bytes, digests, run domain and result identities remain unchanged. The two small test fixtures contain only certified historical spec contracts, not datasets or simulation output. The certified baseline spec remains 5d5e5d95d38b457d0fcc20d7351d3d79e95fc9321b5fb252697763fbdedb9d38; its run remains 4827ec1ebd407566b4254d80f59eaceecc01f9364d903f54a4843683a88920ce. A read-only integrity check of the retained A003R baseline and A006 intervention confirmed the existing pair is still PAIRED, without rerunning either. A synthetic fixture-based regression also preserves both certified spec identities and baseline run identity.

A006 verify_pair first requires identical variant digests, including ordinary-versus-explicit-R0 separation. Cross-variant pairs fail with stable DIFFERENT_PREPARATION_VARIANT. All existing scientific controls remain intact. Same-variant pairs pass for all eight members.

## Parent-owned retention and lifetime

LocalServer owns ParentResultStore under its existing session token. The backend contract creates opaque parent IDs and retains immutable encoded, integrity-checked child results indexed by deterministic execution IDs. Limits: two parents per session, sixteen children per parent, 64,000,000 encoded bytes per parent. Admission beyond capacity fails explicitly; parents and children are never silently evicted. A repeated identical child is idempotent, conflicting content is rejected. Lookup requires the session token, exact parent ID, and a child belonging to that parent. No filesystem paths are accepted. Retrieval returns a freshly decoded verified result, so callers cannot mutate retained evidence.

Cleanup is explicit release or LocalServer.server_close/session shutdown. Shutdown closes admission. Retention is session-local memory, not persistent recovery or archive storage. A future sweep must reserve execution ownership and call this retention seam; it must also retain any additional graph/playback material needed by the eventual UI. No sweep orchestration, reuse, cancellation API, durable checkpoint, or matrix route is claimed here.

Recent Runs HISTORY_LIMIT remains eight. The synthetic regression executes eight variants times baseline/intervention, retains all sixteen distinct results under one parent, then creates twenty-four ordinary Recent Runs entries through RunManager's actual admission/eviction method. All sixteen identities and authoritative results remain retrievable; global history remains eight. Cross-session, cross-parent and path-like lookups are rejected. Capacity, byte bounds, snapshot isolation, release, and shutdown are tested.

## Synthetic integration and CUDA scope

All R0-V7 members execute through VariantExperimentSpec -> resolved PreparationConfig -> ProductionEngine.prepare -> prepare_network -> simulate_lif -> verified ExperimentResult. Fixtures contain four synthetic neurons and two anatomical edges, with one glutamatergic source to distinguish policies. The identity adapter supplies synthetic population identities; preparation, stimulus generation, simulation and result validation use production code.

R0 completes with reference weight/signing. V5 completes with 0.200 mV anatomical weight, effective edge weights +1/-1 mV for five anatomical synapses, and observed executed direct input 50 mV. V7 completes with ConservativeSignPolicy and one retained edge versus reference's two, proving actual sign resolution changes rather than metadata. All eight members also pass same-variant baseline/intervention pairing and JSON result round trips.

CUDA preparation uses the same resolved weighted/signed projection and existing upload_graph. Simulation dispatch receives identical LIFParameters and explicit stimulus semantics; optional CUDA imports remain lazy. A synthetic dispatch test verifies V5 parameters, 50 mV input and uploaded-graph forwarding. Unavailable CUDA rejects with GPU_UNAVAILABLE and an identity-verified partial result. No GPU numerical execution or CPU/GPU parity certification is claimed in this task.

## Scientific firewall and remaining A007 work

A007 remains A7-CONTRACT-GAP for its unfinished robustness execution/view. This prerequisite resolves configurable preparation, variant execution identity, pairing and result retention only. Next recommended task: Application Task A007B ? bounded parent-owned robustness orchestration and evidence API, using this preset, exact same-variant pairing, whole-parent active-run ownership, cooperative cancellation, retained graph/playback evidence and synthetic-only certification before the A007 UI. Do not start it automatically.

Task016/Task017 code and historical artifacts are unchanged. Task017 remains NOT_ROBUST. Real MaleCNS runs 0; Task017 units 0; Task017Q 0; raw-data downloads 0; checkpoint export/import/restore 0/0/0; archive writes 0; B:\MaleCNS-Archive unchanged. No biological conclusion, robustness scoring, historical thresholds, tag, release or version bump.

## Frozen identity values

Preset digest: `34de3189f0630c159fabe140892362ec65228487984224ef880702eb3fd8f139`. Reference config digest: `a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9`.

| Member | Variant SHA-256 |
| --- | --- |
| R0 | `b6f3dea4f530732853e10a89f49cd0794a4662906c53679c775ce19e2ad73d71` |
| V1 | `902c494bb8be20d394c418ce30936a51af8c0a3112257631836174085950ceb4` |
| V2 | `49adf2bb6eed972c5adb356788a52088a1c0db79850d35212ee084ae6959ed02` |
| V3 | `43e8b8eea783504c4981bf118cfce782a95c0d26b1627696ac32a016d93b1f2a` |
| V4 | `b18cb4d9aad647d5a1eece54b35b7bbd010dd9cbd4ee9469f68faf9420af5ff9` |
| V5 | `efc8220ba209e7a6e92d129ae1e3f82678befcb376462b2c450747a2cb86cc61` |
| V6 | `aa6f36f7d54bae073c1cc0dada04485835baaf345e826c2e10cfb014ac384766` |
| V7 | `d67d26b5ae9788e29ee2fa38dd2bfd73a40c2eea038c52b5f8b0a2c08b3623cc` |


## Certification and automated validation

Verdict: **A007A-VARIANT-CONTRACT-CERTIFIED**. Classification: Application backend prerequisite infrastructure; synthetic execution certification. A007 robustness UI remains uncertified and unfinished.

- Targeted A007A: 52 passed, 7.32 seconds.
- Targeted A002-A006 regressions: 59 passed, 16.02 seconds.
- Full `uv run pytest`: 371 passed, one existing explicitly opt-in real-data test skipped, 30.79 seconds. One existing CuPy CUDA-path environment warning. Historical test fixtures did not execute historical Task017 units.
- `uv run python -m compileall src scripts tests`: passed.
- `uv run python scripts/check_tracked_integrity.py`: PASS, nine pinned tracked files and internal identities.
- `git diff --check`: passed.
- `uv build`: source distribution and wheel built, version 0.3.0. MANIFEST.in includes the two small historical identity contract fixtures in the source distribution.
- Fresh wheel installed into a separate temporary virtual environment without CuPy: package import and V5 resolution passed. Installed malecns-workbench entry point loaded root and all five existing JS/CSS assets; absent session token returned 403, authenticated empty Recent Runs returned 200, and no robustness route exists (404).
- Normal `uv run malecns-workbench` startup passed the same bounded smoke without executing simulation.
- Fresh-wheel A007A/A006/A006R tests: 72 passed, 4.52 seconds, against the installed package without CuPy. This includes true synthetic preparation/execution and existing comparison/browser-state regressions.
- Known retained historical baseline/intervention results were read and integrity-checked; baseline spec/run identities and A006 PAIRED eligibility remain exact. No real simulation was run.
- Final scope: fourteen files comprising three application documents, seven source modules, one test module, two contract fixtures and MANIFEST.in. No static assets, historical Task016/Task017 files, scientific artifacts, datasets, dependencies, version, tags, releases or workflow files changed.
- Package version 0.3.0; v0.3.0 peeled target a1a6651163840a982799b1fa82c1904e67f84660; active tracked GitHub Actions workflows zero; stash empty.

The initial smoke harness incorrectly requested assets beneath /static; the established server serves them at root paths. Correcting the harness verified all packaged assets without changing production routes. Initial synthetic fixture tests also found a missing test-only hashlib import, corrected before all final validation.

Publication is authorized only for this certified fourteen-file scope, using `feat: add configurable robustness variant contract`, without tag/release/version bump. Final commit and local/origin/live identity are reported after publication.
