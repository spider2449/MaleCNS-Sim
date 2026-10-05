# Application A018UI - Exact Prepared-Identity Root-Cause Audit

## Authorization, start gate and disposition

Authorized: one bounded identity/root-cause audit. No real preparation retry,
stateful execution, scientific stimulus, GPU execution or production correction.
Root derived by `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD, origin/master and live GitHub master all equaled
`b967dbd92eb9a858d00647591cc8feb50c3f4c79`. Worktree clean; stash empty;
package 0.3.0; tracked active workflows zero. Start gate passed before mutation.

Verdict: **A18UI-D**, **RC4 - HISTORICAL EXPECTED DIGEST IS WRONG-LAYER / MISLABELED**.
The frozen expected value is a valid historical effective-projection identity,
but A018UR compared it to the encompassing prepared-network identity. This is
the first proven exact identity divergence. No production correction is made.

A018UR remains **A018UR-GRAPH-IDENTITY-MISMATCH**, not certified. Its single real
attempt completed in 101.3569613 s, staged merge 26.8814183 s, private peak
5,478,465,536 bytes, working-set peak 4,465,192,960 bytes; 8-GiB cap not hit;
no fallback. Counts 166,700 neurons / 24,904,953 effective edges match;
dataset/provenance, config and unsigned identity match; real advances and
automatic retries zero. These are recorded evidence, not remeasured in A018UI.

Expected frozen value:
`ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`.
Observed A018UR prepared-network value:
`d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`.

## Historical provenance and identity layers

The earliest tracked literal occurrence of ed1cfb is commit
`f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e`, Task 008, in the committed
`data/derived/task008-results.json` historical blob. Its `full_prepared` object
explicitly records `effective_projection_fingerprint=ed1cfb`,
`fingerprint=d773107`, signed policy fingerprint 861f0721... and unsigned
fingerprint fde3d0f5..., with the full graph's counts and cache identity.
This artifact is read via `git show`; no ignored current result is regenerated.
The subsequent Task 010 commit
`fe4048726641a99b3cf9ed33aec406d50700f489` contains executable cross-checks:
`analysis/task010.py::_prepare_verified_cached_network` checks
`cache.projection_fingerprint == ed1cfb`, while separately returning
`PreparedNetwork.fingerprint == d773107`. Task 010's report labels d773107 as
prepared identity. Task 011, committed as
`ae589a9b9726fa2510fff8f32658bc02176f66a3`, explicitly records both: prepared
graph d773107, effective graph ed1cfb. The committed Task 008a preservation
manifest also records d773107 as primary prepared identity.

The generating path was Task 008 `prepare_network`: numeric load, publication
selection, curated projection, Shiu signs, effective projection and persisted
`data/derived/task008/full-prepared-graph.npz`. The Task 008 implementation is
committed at `f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e`. Its report describes
execution completed on 2026-09-21 with changes uncommitted. Consequently the
exact clean Git SHA of the original generating execution is **not established**;
f22e7c7 is both the historical code snapshot and first committed artifact
evidence; it is not falsely asserted to be the clean execution SHA.

Historical config: full graph, min_synapses=0, Shiu2024SignPolicy,
MaleCNSV1ConsensusThenPredictedThenCelltype, synaptic scale 0.275 mV,
default LIF parameters, cached projection. Effective identity is after signs
and effective weights, not a raw graph, export or manifest digest.

Registered source SHA-256 values (`data/provenance/male-cns-v1.0.json`):

| Source | SHA-256 |
| --- | --- |
| annotations | 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2 |
| neurotransmitters | 95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621 |
| weights | e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1 |

No source file was opened to regenerate a real graph. A004 reports a separate
CPU preparation producing ed1cfb; A003R's application result records ed1cfb
because `ApplicationService.execute` uses `projection.fingerprint` for
`provenance.graph_fingerprint`. These are historical repeated observations,
not an independent full-real reproduction in this audit.

| Layer | Exact producer / coverage |
| --- | --- |
| raw source | file SHA-256, distinct from all graph identities |
| unsigned graph | graph/fingerprint.py::graph_fingerprint, neuron IDs and anatomical CSR |
| signed graph | graph/signed.py::signed_graph_fingerprint, unsigned identity, policies, original arrays, evidence/sign records |
| effective projection | dynamics/lif.py::EffectiveSignedProjection.from_signed_connectome; ed1cfb |
| prepared network | analysis/task008.py::prepare_network using _digest; d773107 |
| runtime | PreparedRuntime.identity: effective fingerprint, LIF parameter fingerprint, dt |
| cache | PreparedGraphCache cache fingerprint includes cache contract; historical 8064dbec... is distinct |
| application graph | execute provenance uses effective projection fingerprint |
| configuration | application/preparation.py separate config digest; A018UR a14d75e6... |
| manifest/export | separate provenance/export serialization, neither of the disputed values |

The earliest executable conflation of these frozen values is A013 commit
`4e2e10c3aa1cbef9e9e80b54981e20aefe1ef62e`,
`benchmark_application_a013.py::worker`: PREPARED_ID=ed1cfb then
`prepared.fingerprint == PREPARED_ID`. A018R commit
`f9995c51604f0683b471afda63687665502e858b` repeats this as
`observed.prepared_digest=prepared.fingerprint`; A018UR b967dbd inherits it.
Earlier application prose called ed1cfb a prepared graph fingerprint, but its
actual producer was effective projection. Naming alone did not establish a
prepared-network contract.

## Exact digest contracts

### Prepared network

`analysis/task008.py::prepare_network` constructs a dict with graph name,
unsigned, signed and effective fingerprints. Optional `parameters` is included
only when an explicit parameters argument is supplied. The default production
call supplies no config override, so the optional field is absent.
`_digest(prefix, payload)` computes SHA-256 of:

1. UTF-8 domain `malecns-sim-task008-prepared-network-v1`;
2. one NUL byte;
3. UTF-8 `json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)`.

JSON defaults ensure_ascii=True, allow_nan=True apply. Keys hash in sorted order:
effective, graph, signed, unsigned (parameters between graph and signed if
present). There are no direct numeric arrays, array shapes, CSR bytes, delays,
counts or config digest in this outer serialization. They are bound only by
nested identities where covered. Paths, timings, memory, cache path/fingerprint,
backend and runtime state are excluded.

### Effective projection

`dynamics/lif.py::EffectiveSignedProjection.from_signed_connectome` initializes
SHA-256, adds unprefixed ASCII domain `malecns-sim-effective-signed-projection-v1`,
then in order sign-policy ID, resolution-policy ID, Python `str(weight)` and
signed-graph fingerprint. Each string is UTF-8 with an 8-byte unsigned little
endian byte-length prefix. Default weight string is `0.275`.

Then each array contributes ASCII `str(dtype)` immediately followed by
`tobytes(order='C')`, without a length or shape prefix:

| Order | Array | dtype on audited Windows host | Shape |
| --- | --- | --- | --- |
| 1 | neuron IDs | int64 | N |
| 2 | source positions | int64 | E retained |
| 3 | target positions | int64 | E retained |
| 4 | effective weights | float64 | E retained |
| 5 | outgoing indptr | int64 | N+1 |

Numeric bytes use array dtype byte order (native little endian here), not an
explicit cross-platform endian conversion. C-order logical bytes are requested;
the implementation does not hash stride or contiguity flags. Native int64 and
float64 arrays are produced. No canonical shape serialization is added.
Outgoing targets and weights are exact copies of hashed target/weight arrays.
No incoming signed CSR is constructed or directly hashed. Included/excluded
counts and coverage are not separately serialized. Delays, dt, runtime and
configuration digest are excluded. Signed identity transitively binds original
anatomical counts, topology, evidence, sign and mask arrays.

### Signed and unsigned nested identities

`signed_graph_fingerprint` prefixes **every** field with its 8-byte little
endian length: domain `malecns-sim-signed-connectome-v1`, unsigned ASCII digest,
UTF-8 resolution policy, UTF-8 sign policy, then dtype and C bytes for neuron
IDs, source IDs, target IDs, anatomical counts (int64), signs (int8), retained
mask (bool). Shapes are N, E, E, E, E, E; no shape field. signed_counts int64
are derived but not directly hashed. Evidence records in neuron order serialize
with sorted JSON keys, ensure_ascii=True, compact separators, UTF-8. Record keys
are id, consensus, predicted, celltype, predicted_confidence,
celltype_confidence, ground_truth, superclass, source_field, source_label,
identity, source_confidence, sign. Optional values serialize as null; Python
numeric formatting applies, not rounded floats. Rationale text is excluded.

`graph_fingerprint` length-prefixes numeric neuron-ID C bytes (no ID dtype
marker), then dtype and C bytes for CSR indptr, indices and data. Numeric IDs
are int64; anatomical CSR data is float64; SciPy index dtype is dimension-driven
(int32 for the small fixture and usual real dimensions, not forcibly int64).
Source-row/target-column orientation; sorted indices; duplicate pairs summed by
CSR construction. No domain/schema marker, explicit matrix shape, threshold,
original pair order or raw integer-count representation is included.

Unsigned exact match therefore provisionally excludes neuron-ID bytes and
anatomical CSR topology/data/order at the hashed representation. It does **not**
prove original source/destination array order, integer representation, all large
integer values before float conversion, sign/evidence, retained mask, effective
bytes, outgoing permutation, delays or metadata. No unsupported exclusion is
made from unsigned equality.

## Exact reconstruction and first mismatch

The following small historical payload, passed to historical and current
`_digest`, produces the recorded A018UR d773107 exactly:

```json
{"effective":"ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f","graph":"full","signed":"861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25","unsigned":"fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4"}
```

Historical signed/unsigned identities are explicitly retained in the Task 008
artifact and separately frozen in Task 010 code.
This is a forward reconstruction, not inversion of a SHA-256 digest; it does
not prove current unrecorded real-array bytes equal historical bytes. It proves
the reported mismatch is exactly compatible with the historical prepared
envelope, and that ed1cfb was never that envelope's digest.

First exact mismatch stage: certification identity selection/comparison.
Component/key: `observed.prepared_digest` versus `expected.prepared_digest`.
Historical intended layer/value: effective projection / ed1cfb.
Current selected layer/value: prepared network / d773107.
First differing array/sign/weight index: **not established / not applicable to
the proven mismatch**. Do not attribute downstream scientific differences.

## Component fingerprints and bounded historical oracle

`scripts/audit_application_a018ui.py` provides audit-only SHA-256 fingerprints
of exact bytes, recording dtype, shape and length separately. It does not replace
any production identity. `2026-10-05-application-a018ui-components.json` contains
the complete historical/current table for a deterministic 10-neuron, 80-edge
mixed fixture. All 24 component rows match. Fingerprints include neuron IDs,
edge IDs/order, anatomical counts, signs, signed counts, retained and threshold
masks, effective weights, outgoing permutation, prepared source/target order,
outgoing CSR arrays, anatomical/incoming CSR arrays, policy/config, canonical
metadata and delay/grid. Threshold mask is evaluated on the already-curated
fixture; it does not reconstruct an unavailable prethreshold real graph.

Tests extract historical source by `git show`, execute only the historical
EffectiveSignedProjection class, `_digest` and small-fixture `prepare_network`
using patched in-memory numeric data. No checkout, history rewrite or real
source access. Historical sign, resolution and unsigned digest modules are
identical to current source, checked exactly with line-ending normalization.
Historical preparation and current preparation match exactly on the recorded
fixture. Additional mixed/random/all-excitatory fixtures compare both policies.

| Component | Historical/current fixture | Full-real evidence |
| --- | --- | --- |
| unsigned grouped graph | MATCH | unsigned CSR digest MATCH; original grouped order not independently measured |
| neuron order | MATCH | provisionally MATCH from unsigned digest |
| edge source/destination order | MATCH | unavailable as individual component hashes |
| anatomical integer counts | MATCH | aggregate CSR float64 coverage only; exact integer component unavailable |
| sign array / signed counts | MATCH | individual bytes unavailable |
| effective weights | MATCH | individual bytes unavailable |
| threshold / retained masks | MATCH | individual bytes unavailable |
| prepared ordering / permutation | MATCH | individual bytes unavailable |
| anatomical/incoming CSR | MATCH | unsigned anatomical digest MATCH; incoming not a production owner |
| outgoing indptr / indices / data | MATCH | individual bytes unavailable |
| delay/grid / policies / metadata | MATCH | policies/config MATCH recorded; serialization component unavailable |
| effective vs prepared layer comparison | DIFFERENT by contract | MISMATCH proven, same historical distinction |

No full-real component digest table is invented. Existing tracked reports retain
aggregate identities rather than full real arrays or component hashes. Further
real-array proof is unnecessary to diagnose this comparison error and is not
authorized by A018UI.

## Sign, byte, ordering and source-history audit

Signs: evidence indexed by stringified integer neuron ID; missing evidence gets
an empty NeurotransmitterEvidence. Resolution uses consensus, predicted, then
celltype, selecting the first present nonempty label; explicit unclear does not
fall through. Normalization strips/lowercases and maps gamma-aminobutyric acid
to gaba; unsupported labels unresolved. Shiu maps acetylcholine/dopamine/
octopamine/serotonin to +1, gaba/glutamate to -1. Conservative assigns only
acetylcholine +1 and gaba -1. Lookup uses **source**, never destination. Unresolved
is int8 sentinel 2; mask excludes it. An assigned zero sign would be retained
and contribute zero weights; these two policies do not assign zero. No sign
rule drift exists in historical/current source.

Weights: anatomical int64 counts are selected by sign mask, cast to float64
first, multiplied by int8 sign, then float scale 0.275. No reassociation to
`signed_counts * scale`, no postmultiplication integer cast. IEEE negative zero
is possible for zero magnitude times a negative sign; exact bytes are hashed,
not normalized. Scale must be finite/nonnegative; numeric count input and these
operations introduce no NaNs under the valid fixture contract. No rounding,
NaN canonicalization, endian normalization or stride hashing occurs. Fixture
tests assert exact weight bytes including sensitivity to negative zero.

Ordering: positions derived by searchsorted over sorted IDs, mask alignment
preserved, then `np.lexsort((target, source))`: source primary, target secondary,
stable within equal keys. Weights follow the same permutation. indptr int64
counts each source then cumsum; outgoing arrays copy the prepared target/weight
sequence. Anatomical CSR sorts indices and sums duplicates. Incoming test CSR
is the transpose of anatomical CSR; no incoming production signed CSR exists.
No mathematical sparse-equivalence substitution is used.

| Historical/current identity-sensitive change | Class | Evidence |
| --- | --- | --- |
| sign / resolution / unsigned serializer / curated projection / CSR | I0 | unchanged relevant source |
| effective construction and serializer | I0 | unchanged class; exact historical/current fixtures |
| optional parameters and sign_policy arguments, A007A 637a2236374da27c67489b1c56292a55b7159384 | I1 | explicit parameters adds outer metadata; explicit policy changes signs; default path unchanged |
| optimized integer aggregation route A015-A018T | I1 | grouping/merging can affect arrays; bounded exact regressions test this; default production not promoted |
| A013 comparison of effective expected ID to outer prepared ID | I2 | exact frozen-envelope reconstruction and source comparison |
| A018R / A018UR repeated wrong-layer comparison | I2 | exact observed/expected field producers |

Digest schema/serialization implementations have not changed for the default
historical path. The optional explicit-parameters branch is a new identity
extension, not the cause here: ProductionEngine.prepare(config=None) uses no
override. Unrelated dynamics/stateful additions are excluded from causal review.

## Hypothesis decisions and validity limits

| Hypothesis | Status |
| --- | --- |
| H1 current optimized preparation identity-wrong | not established; mismatch does not demonstrate this |
| H2 historical expected digest different layer | PROVEN |
| H3 older canonicalization caused mismatch | excluded for audited default contracts/source |
| H4 digest implementation drift with exact content | excluded as cause of this mismatch |
| H5 genuine sign/effective/scientific byte difference | not established on real arrays; fixtures match |
| H6 ordering drift with mathematical graph unchanged | not established on real arrays; fixtures match |
| H7 metadata-only serialization drift | excluded as cause; serializers unchanged, layers differ |

Exactly one classification: RC4 / A18UI-D. Full-real scientific content
difference, mathematical topology difference, ordering-only or metadata-only
difference are not proven. Wrong-layer evidence is proven. Historical ed1cfb is
correctly labeled as effective graph in Task 011 and cache code; mislabeled as
the expected prepared-network identity by the retry/benchmark comparison.
Historical ed1cfb has reported repeat preparations, but no current independent
real-array reproduction or exact clean generating execution SHA is claimed.
Historical prepared d773107 is reproducible from committed component identities.

**scientific content match != identity certification**. Fixture equality and
aggregate reconstruction do not certify full-real individual components or waive
the A018UR gate. No A019 recommendation, real retry or expected-value substitution.

## Exactly one next bounded task

Recommend **A018UJ - identity-evidence adjudication**: resolve the explicit
effective-projection versus prepared-network expected-identity contract using
the preserved historical records and this exact reconstruction; define which
typed identity each gate must compare, retaining both frozen values. Document
the evidence required for certification separately. No scientific change, real
preparation, automatic retry, A019 execution or production-default promotion is
included. This is a proposal, not authority to implement a correction now.

## Firewall, changes and validation

Only this plan, component JSON, audit helper and A018UI tests are added.
Production code, scientific semantics, expected digest, production default,
Task016, Task017 and B archive unchanged. Task017 remains NOT_ROBUST.
Full-real preparations/advances, real Arena runs/experiments, raw downloads,
Task017 new units, Task017Q and archive writes: all zero. Audit helper/tests call
no PreparedRuntime.advance, simulate_lif or simulate_cuda. Required regression
tests may execute their existing synthetic simulations; these are not new real
scientific executions. No biological interpretation. No tag/release/version bump.

Targeted A018UI: 11 passed. Remaining validation and Git closure recorded below
after completion; no full-real preparation is part of any validation command.

Validation iteration note: the first full run passed 1208 tests with 14 skips
before the final historical-preparation test was added. During a subsequent
full run, an audit-local metadata bug was corrected: runtime parameters must
not enter prepared-network metadata when preparation used no explicit override.
That already-running process retained the old imported helper and failed the
updated committed-record check (1208 passed, 1 failed, 14 skipped). A fresh
process reruns the final consistent files. The correction affects only audit
diagnostics; no production serialization or expected digest changed.

Final validation: `uv run pytest` collected 1223 tests and completed with
**1209 passed, 14 skipped, 1 warning in 185.69 s**. Skips are the existing CUDA
availability/opt-in real-data gates; no real preparation gate was enabled.
The warning is the existing A016 Feather V1 deprecation fixture.

| Required regression group | Final full-suite result |
| --- | --- |
| targeted A018UI | 11 passed |
| A018UR | 8 passed |
| A018U | 80 passed |
| A018T | 283 passed |
| A018S | 95 passed |
| A018 | 97 passed; A018R additionally 8 passed |
| A017 | 79 passed |
| A016 | 68 passed |
| A015 | 59 passed |
| A014 | 12 passed |
| A013 | 17 passed |
| stateful/A011 | A011 8 passed; Task005 24 passed |
| application regressions | all 962 application tests passed |
| full pytest | 1209 passed, 14 skipped |
| compileall src scripts tests | passed |
| tracked integrity | PASS, 9 tracked files and internal identities |
| diff check | passed, including staged additions |
| uv build | passed, 0.3.0 wheel and source distribution |

Precommit scope: exactly four audit-only additions, no unrelated tracked or
unstaged change, stash empty, tracked workflows zero. Commit/push are authorized
after the valid audit and successful validation. Exact final commit and remote
identity are returned in the task's final report; no self-referential SHA is
embedded in this committed plan.
