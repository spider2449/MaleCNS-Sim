# Application A018UJ - Bounded Identity-Evidence Adjudication

## Authorization and disposition

Authorized by `授權 A018UJ`: identity contract adjudication, evidence review,
certification-only repair, synthetic tests and documentation. Repository root
derived with `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD, origin/master and live GitHub master all equal
`d6fdb16e078bfca524214b9d1855ece3f8e9a7d7`; worktree clean, stash empty,
package 0.3.0, active tracked workflows zero. A018UI is A18UI-D / RC4.

**Verdict: A18UJ-A; R-A. Existing A018UR evidence satisfies the corrected gate.**
Superseding status: **A018UR-IDENTITY-ADJUDICATED-CERTIFIED**. This means the
original preparation completed under caps, the original identity rejection
was an invalid cross-layer comparison, frozen evidence satisfies the corrected
fingerprint contract, and no new real run occurred. It does not mean the
original harness returned PASS. Its historical
**A018UR-GRAPH-IDENTITY-MISMATCH** report remains unchanged.

The exact clean generating-run SHA of Task008 remains unestablished.
`f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e` is the committed code/artifact
snapshot, not a newly established execution SHA. Introducing comparison commit:
`4e2e10c3aa1cbef9e9e80b54981e20aefe1ef62e`.

## Q1: Formal identity-layer registry

All serializers below are existing contracts. The registry version
`preparation-identity-v1` labels the new certification record and terminology;
it is not inserted into scientific hashes or existing historical artifacts.
Exact byte contracts are also documented in the immutable A018UI report.

| Layer and canonical name | Exact producer/serializer and covered components | Excluded components | Historical/current fields | Kind and gate eligibility |
| --- | --- | --- | --- | --- |
| L1 dataset_provenance_identity | DatasetIdentity and DatasetCatalog.identity, application/models.py canonical_bytes; registered file SHA256, manifest digest, mapping fingerprint, release; gate checks manifest/mapping plus supervisor source-file verification | signs, effective weights, runtime, performance | dataset fields, manifest_digest, mapping_fingerprint, source sha256; unchanged underlying fields | provenance; mandatory G1 |
| L2 unsigned_graph_digest | graph/fingerprint.py::graph_fingerprint: length-prefixed neuron-ID C bytes, then dtype/C bytes for anatomical CSR indptr, indices, data | signs/evidence, effective weights, original raw pair order, runtime/config | unsigned_graph_fingerprint; workbench PROJECTION_FINGERPRINT/projection_fingerprint and harness unsigned_digest alias; new unsigned_graph_digest | scientific anatomical representation; mandatory G3 |
| L3 effective_projection_fingerprint | dynamics/lif.py::EffectiveSignedProjection.from_signed_connectome: effective-signed-projection-v1 domain, length-prefixed sign/resolution IDs, str(weight), signed fingerprint, then dtype/C bytes of IDs, source/target positions, effective weights, outgoing indptr | dt, delays, state, outer graph name, full config, performance | Task008 full_prepared.effective_projection_fingerprint; projection.fingerprint; application graph_fingerprint alias; new effective_projection_fingerprint | scientific effective representation; mandatory G4 |
| L4 prepared_network_digest | analysis/task008.py::prepare_network and _digest: prepared-network-v1 domain/NUL/sorted compact JSON of graph, unsigned, signed, effective; optional parameters only on explicit-parameter branch | direct arrays, counts, dataset files, full config, backend, cache, timings, runtime/state | Task008 full_prepared.fingerprint; PreparedNetwork.fingerprint; wrong-layer harness prepared_digest deprecated; new prepared_network_digest | operational envelope binding scientific fingerprints; mandatory G5 |
| L5 preparation_config_identity | application/preparation.py::PreparationConfig.digest, application-preparation-config-v1 domain/NUL/canonical_bytes(config): full LIF parameters, sign/resolution IDs, direct-input factor/rule | dataset, graph arrays, runtime state, merge/batch operational settings | preparation_config_digest, config_digest, REFERENCE_CONFIG.digest; new preparation_config_identity | scientific configuration plus adapter rules; mandatory G2 |
| L6 runtime / experiment identity | PreparedRuntime.identity tuple (effective fingerprint, LIFParameters.fingerprint, dt_ms); PreparedTask008.fingerprint uses task008-experiment-v1/_digest; application ExperimentSpec.digest and RunIdentity.create use canonical_bytes/_digest and application-run-v1 (variant-run-v1 when applicable) | invocation/timing/resource metadata; runtime tuple excludes mutable state | identity, spec_digest, run_id, fingerprint; existing fields unchanged | scientific execution definition plus operational package/backend binding; required for future execution, outside preparation G1-G6 |

Nested signed-policy identity is not another name for L2 or L3:
graph/signed.py::signed_graph_fingerprint length-prefixes domain, unsigned
digest, policy IDs, dtype/bytes of IDs, endpoints, anatomical counts, signs,
retained mask, and sorted compact JSON evidence records. It excludes rationale
text and derived signed_counts. L3 and L4 bind this identity. L2 has no explicit
domain marker; existing dtype/native byte-order behavior is unchanged.
L3 does not hash array shapes explicitly; its constrained producer supplies
the representation. These limitations are retained, not silently repaired.

L6 application RunIdentity binds spec digest, dataset, package/engine version,
model, sign policy, seeds, backend, realized schedules, graph fingerprint and
result schema. PreparedTask008 experiment identity binds primary/mirror condition definitions
and left/right population dataclasses; graph/sign identity is separate. No L6 value is required or invented for
the preparation-only adjudication.

## Q2: Terminology and future certification

Canonical names are distinct: unsigned_graph_digest,
effective_projection_fingerprint, prepared_network_digest,
preparation_config_identity. `prepared_digest` is rejected in new executable
gate inputs, not heuristically migrated. Historical JSON remains immutable:
interpret each old field by its actual producer. In particular ed1cf is never
reassigned to L4. A013/A018R/A018UR now read explicit scalar identities and
compare only the same canonical fields through preparation_identity_contract.
Expected L3/L4 constants are separately named EXPECTED_EFFECTIVE_PROJECTION_FINGERPRINT
and EXPECTED_PREPARED_NETWORK_DIGEST. New output uses explicit layer names.
A018UI's historical wrong-gate regression reads the frozen original harness
from Git rather than requiring repaired current code to retain the defect.

| Gate | Mandatory protection | A018UR result / strength |
| --- | --- | --- |
| G1 | registered dataset release, source-file hashes, manifest and mapping; source verification remains in supervisor before preparation | PASS, E4 recorded source/provenance checks |
| G2 | exact reference preparation config; default call, no override; binds parameters and adapter rules excluded by L4 | PASS, E4 observed config; historical default config reconstruction E3 |
| G3 | unsigned anatomical identity | PASS, E4 directly observed |
| G4 | effective signed projection identity | PASS, E3 bound through observed L4 and reconstructed historical tuple |
| G5 | prepared envelope identity, including graph name and nested signed identity | PASS, E4 observed; historical expectation independently E3 and also E4 |
| G6 | 166700 neurons and 24904953 effective edges; guards scope/counts not explicit outer fields | PASS, E4 observed and historical |

G4 is deliberately useful redundant evidence, not a claim of independence:
L4 binds L3 plus graph name, unsigned and signed identity. Direct L3 observation
in future runs makes layer attribution auditable without relying on envelope
binding. G3 is similarly useful layer diagnostics. G2, G1 and explicit counts
cover information not fully present in the outer envelope. There is no
seventh standalone signed gate because the nested signed identity is bound by
both L3 and L4. No scientific coverage is weakened.

## Q3: Independent historical reconstruction and component evidence

The compact tracked record is
`2026-10-05-application-a018uj-identity-contract.json`. Values were extracted
directly from `git show f22e7c7:data/derived/task008-results.json`. Independent tests extract that blob
again, construct the payload from named fields, and execute the historical
_digest function as well as current _digest and the independent helper.
No prose-only oracle or full-real edge source is used.

| Component / layer | Historical value and source | Current/A018UR value and comparison | Grade |
| --- | --- | --- | --- |
| unsigned / L2 | fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4; Task008 full_prepared.unsigned_graph_fingerprint | same directly observed; MATCH | E4 |
| effective / L3 | ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f; Task008 full_prepared.effective_projection_fingerprint | not separately printed by old harness; same bound component tuple reconstructs observed L4; MATCH under fingerprint contract | historical E4, A018UR E3 |
| signed-policy nested identity | 861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25; Task008 full_prepared.signed_policy_fingerprint | bound by identical envelope; sign/resolution labels directly recorded; MATCH | historical E4, A018UR E3 |
| config / L5 | a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9; historical default LIF/sign/resolution settings reconstructed via REFERENCE_CONFIG | same recorded digest and no-override path; MATCH | expected E3, observed E4 |
| LIF parameter identity | 037ed13cf919f0ef9ddfdb8f1876e7f1e4712a5c6deb1adbba0fc64e230b0d27; historical defaults and frozen application fixture | same frozen A018UR report; L5 binds these parameters | E3/E4 |
| dataset manifest / L1 | e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631; pre-A018UR application fixture/workbench | registered manifest matches in frozen A018UR report | E4 |
| mapping / L1 | 832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269; pre-A018UR fixture/workbench | registered mapping matches in frozen A018UR report | E4 |
| source file hashes / L1 | tracked male-cns-v1.0 provenance; exact three hashes in new contract record | supervisor rechecked all three; recorded MATCH | E4 |
| graph name / L4 | full; Task008 full_prepared.graph_name | default full path; identical envelope | E3/E4 |
| serializer marker / L4 | malecns-sim-task008-prepared-network-v1; historical task008.py | same prefix, NUL, sorted compact JSON; MATCH | E3 |
| optional preparation parameter field / L4 | absent; historical payload/code | absent on ProductionEngine.prepare(config=None); MATCH | E3 |
| prepared envelope / L4 | d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495; Task008 full_prepared.fingerprint | same recorded A018UR scalar; MATCH | expected E3 plus historical E4; observed E4 |
| individual full-real arrays | not retained as complete individual component bytes/hashes | unavailable; no regeneration | E0, not a mandatory fingerprint gate |

E0 unavailable; E1 inferred without deterministic binding; E2 recorded but
not independently reproducible; E3 deterministically reconstructed from frozen
evidence; E4 directly recorded exact identity. A018UR scalar/report evidence is
E4 per this task's definition, not a claim that all its source bytes can be
independently replayed. Lowest mandatory grade is E3; no mandatory E0/E1/E2.

Exact default envelope inputs:

```json
{"effective":"ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f","graph":"full","signed":"861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25","unsigned":"fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4"}
```

SHA256(domain UTF8 + NUL + json.dumps(payload, sort_keys=True,
separators=(',', ':'), default=str).encode()) gives
**d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495**.
This is the **derived historical prepared-network expectation**, separately
corroborated by the historical recorded envelope. It never replaces ed1cf.
Field order is deterministic; insertion-order reversal is tested. Python JSON
defaults and optional-parameter behavior remain unchanged.

## Evidence-chain validity and byte availability

The graph/unsigned/signed/effective tuple and default serializer were frozen
in Task008 before A018UR; Task010 separately preserves the component constants
and distinguishes cache effective identity from prepared identity. The later
application config definition, reference fixture, manifest/mapping and source
hash registrations also predate A018UR. Frozen A018UR's report records the
same dataset/config/sign policy, exact envelope, unsigned identity and counts.
No ignored local result JSON is used to create new authoritative evidence.

This is forward hashing, not hash inversion. Reconstructing the historical
tuple yields the directly recorded A018UR envelope. Given the inspected
producer and normal SHA256 collision/second-preimage assumptions, a different
component tuple cannot plausibly yield that recorded value. Thus the existing
L4 observation binds L3 and the signed identity at E3 without a new real run.
That inference is cryptographic evidence binding, not an independently
observed L3 scalar. Future harnesses capture it directly. If the producer were
untrusted, the report forged, or a collision demonstrated, R-A would fail;
none is established by this bounded source/history audit.

All required outer inputs are recorded; no unrecorded array bytes enter the
outer serializer. Inner identities originally depended on arrays, but the
contract uses frozen fingerprints as canonical evidence, not historical
byte-level replay. Task010's cache verification and Task008/011 identities
establish this intended practice. Requiring now-missing raw arrays would be
a different certification contract. A018UJ does not claim such replay.

Different scientific/execution states can share the same tuple when varying
excluded information (runtime parameters/state, source representation outside
the hashed canonical projection, rationale text). G1/G2/G6 cover relevant
preparation exclusions; runtime identity belongs to A019. Existing unsigned
float64 CSR hashing does not certify every original integer representation.
No stronger claim of raw-file/array bijection is made. Nested hash collisions
remain the standard cryptographic limitation. No missing mandatory component
or scientific-content discrepancy is established; signs, weights, neuron IDs,
topology, thresholds and simulation parameters are unchanged.

## Q4: Acceptance, resource evidence and next gate

Choose exactly **R-A**, not R-B/R-C. A018UR's completed preparation resource
evidence is accepted: 101.3569613 s, private peak 5478465536 bytes, working-set
peak 4465192960 bytes, below 600 s / 8 GiB, no fallback, exact counts,
finite weights, cleanup and zero advances. Peaks remain sampled operational
observations, not instantaneous maximum guarantees. No performance rerun.

The original mismatch is invalidated by this new wrong-layer adjudication;
existing execution evidence is accepted under the corrected identity contract.
All G1-G6 pass with E3/E4 evidence. No real retry is necessary or recommended.
No A018UK task is created. **A019 recommended: Yes**, eligible because A18UJ-A,
accepted resource evidence, corrected gate satisfied, no established scientific
discrepancy and no missing mandatory component. Exactly one next task:
**A019 - Full-Real Stateful Advance Benchmark Resume**, requiring separate
authorization. A019 is not executed in A018UJ.

## Scope, validation and firewall

Changes are limited to the new identity record/helper/report/tests and
certification comparison logic in A013/A018R/A018UR with their synthetic
regressions. No src scientific preparation or production-default code changes.
Historical Task008 JSON, Task008 digest, A018UR report and A018UI fixture are
unchanged. The schema labels evidence only; package remains 0.3.0.

Tests cover distinct L2/L3/L4 names, wrong-layer and legacy rejection,
effective-as-envelope rejection, deterministic historical/current serializer
reconstruction, ordering, preserved historical values/provenance, every gate
mismatch and correct tuple, read-only arrays, unchanged src/defaults and no
preparation/execution entry point in the adjudication helper. Synthetic
harness regressions retain real-source-free fixtures and forbidden advance
guards. Ordinary regression tests may run synthetic simulations; the following
zero counters concern A018UJ scientific/real execution, not those test fixtures.

Full-real preparations=0; full-real advances=0; PreparedRuntime.advance=0;
simulate_lif=0; simulate_cuda=0; real Arena=0; real scientific experiments=0;
raw downloads=0; Task017 new units=0; Task017Q=0; archive writes=0.
Historical Task016 unchanged; Task017 unchanged / NOT_ROBUST; B archive
unchanged; no biological interpretation. No tag, release or version mutation.
Validation results and final closure are appended after checks complete.

Independent config check: AST-extracted LIFParameters defaults from the Task008
snapshot were passed to current LIFParameters/PreparationConfig; all parameter
values and sign/resolution IDs matched the pre-A018UR reference fixture at
b967dbd. The reconstructed config digest equals a14d75e6 exactly. PASS.

## Completed validation and closure

Final full `uv run pytest -q`: **1222 passed, 14 skipped**, 183.03 s;
one existing Feather V1 deprecation warning. CUDA/unenabled-real skips expected;
no real gate enabled. Includes all 975 application tests: A018UJ 13, A018UI 11,
A018UR 8, A018R 8, A018U 80, A018T 283, A018S 95, A018 97, A017 79,
A016 68, A015 59, A014 12, A013 17, A011 8; Task011 stateful 9 also pass.
Dedicated A018UJ: 13 passed; corrected A013+A018UJ focused selection: 30 passed.
An initial full collection exposed a sibling import-path error; its repair then
exposed A013's top-level expression-call structural regression. Both were fixed
without relaxing the test, followed by the clean full rerun reported above.

Compileall src/scripts/tests PASS. Tracked integrity PASS (9 frozen files and
internal identities). `git diff --check` PASS. `uv build` PASS, 0.3.0 wheel/sdist.
Final inspected scope: ten intended files; no src/data/artifact/version changes.
Commit/push authorized after these checks. Exact commit identities are reported
in the final response to avoid self-referential commit metadata. No tag/release.
