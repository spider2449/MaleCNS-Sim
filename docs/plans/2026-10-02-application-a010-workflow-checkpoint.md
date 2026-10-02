# Application A010 — workflow checkpoint and next-capability decision

Date: 2026-10-02. Audit only; no product behavior change.

## Start gate and method

Root dynamically derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`. Local HEAD, origin/master and live GitHub
master all equalled `20043dd3b0ceae55dfdba89ebe98a4e7811c0c0e`.
Worktree clean; stash empty; package 0.3.0; active tracked workflows 0.
`v0.3.0^{}` equalled `a1a6651163840a982799b1fa82c1904e67f84660`.

Current closure records establish A3-VERTICAL-SLICE-CERTIFIED,
A4-INTERACTIVE-VIEWPORT-CERTIFIED, A5-AUTHORITATIVE-PLAYBACK-CERTIFIED,
A6-COMPARISON-CERTIFIED, A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED,
A007A-VARIANT-CONTRACT-CERTIFIED, A007B-ORCHESTRATION-CERTIFIED,
A7-ROBUSTNESS-VIEW-CERTIFIED and A8-DOCUMENTATION-REPRODUCIBILITY-CERTIFIED.
Historical pending statements are superseded only by their recorded closures.

Normal engineering audit: production source, regression tests, application
guides and task records. A010 started a production LocalServer on an automatic
loopback port, read `/api/status` (READY) and `/` (production setup HTML),
confirmed zero run records, and shut it down. No Run/Validate/sweep POST was
issued by this smoke inspection. Synthetic regression execution is not
scientific execution. No new browser walkthrough or visual certification is
claimed; friction findings below are source-observed affordances and documented
operating limits, not measured new-user behavior. No A009 clean room, blind
packet, independent operator context or delegated audit was used.

## Evidence index

Paths below are relative to the repository root.

- E1: `src/malecns_sim/application/workbench.py`, DatasetCatalog options/spec:
  pinned local resources and exactly six selection fields; fixed family.
- E2: `application/models.py`, `service.py`, `serialization.py`: strict specs,
  deterministic identities, actual schedule binding, provenance, execution
  phases, backend dispatch, cooperative cancellation and verified results.
- E3: `application/server.py`, RunManager/LocalServer/Handler: history limit 8,
  atomic export before completion, temporary result root, in-memory registries,
  protected route allowlist and no import route.
- E4: `application/static/index.html`, `app.js`, `run-status.js`: production
  controls, invalidation after edits, preview, history, phase/elapsed/previous
  result labels, authenticated download and token storage.
- E5: `application/playback.py`, `subgraph.py`, `comparisons.py` and corresponding
  static JS: verified sparse events, bounded schematic context, controlled
  pairing, synchronized views and backend numeric deltas.
- E6: `application/preparation.py`, `robustness.py`, `retention.py`,
  `static/robustness.js`: explicit R0–V7 definitions, serial orchestration,
  exact reuse, retained parent evidence, export and explicit release.
- E7: `docs/application/USER_GUIDE.md`, `REPRODUCIBILITY.md`, `ARCHITECTURE.md`:
  operating instructions, wheel certification and scientific boundaries.
- E8: `docs/plans/2026-10-01-application-a003-local-visual-workbench.md` and
  `2026-10-01-application-a006-baseline-intervention-comparison.md`: historical
  real CPU integration evidence and timings, including accepted zero baseline.
- E9: A004/A005/A006S/A007A/A007B/A007C/A008 plan closure records and
  `tests/test_application_a002.py` through A008, A006R and
  `tests/test_workbench_session.py`: current certified boundaries/regressions.

## Capability matrix

Status describes software availability, not biological validity.

| Capability | Status | Certified task | Backend authority | UI surface | Known limitation | User consequence |
|---|---|---|---|---|---|---|
| Local startup | Supported | A003/A006S/A008 | LocalServer session/Host/Origin | Printed URL, status | Per-process token; local data separate | Open current complete URL |
| Definition | Supported, bounded | A003 | DatasetCatalog → ExperimentSpec | Setup | MN9/sugar family only | Cannot author arbitrary investigation |
| Validation | Supported | A002/A003 | Strict spec/catalog validation | Validate/preview | Prepared membership/provenance also checked at execution | Validation is not a completed preparation |
| CPU execution | Supported, real integration certified | A003/A006 | Existing prepare_network/simulate_lif | Run | Full graph preparation, one ordinary active run | Potentially costly wait |
| Optional CUDA | Dispatch supported; scientific readiness limited | A002/A007A | Lazy CUDA adapter | Backend picker | No real Application GPU/parity certification | Prefer CPU for certified path |
| Real status | Supported | A003/A006R/A006S | Lifecycle events | Sticky phase/elapsed/timeline | No preparation percentage/ETA | Wait using actual phase |
| Cancellation | Partial surface | A002/A007B/A007C | Cooperative boundaries | Cancel sweep | Ordinary Run has no cancel route/button; opaque call may finish | Cannot immediately interrupt ordinary run |
| Recent Runs | Supported, session only | A003/A006R | RunManager records | Inspector buttons | Last eight admissions, oldest evicted | Export before eviction/exit |
| Connectivity | Supported, schematic | A004 | Prepared projection/subgraph | Filter, 80/160 cap, inspector | 1,200 edges; no anatomical coordinates | Context is incomplete, not a pathway |
| Playback | Supported | A005 | Recorded result events | Raster/cursor/neuron activity | No traces requested by production setup | Sparse spikes inspectable, voltage unavailable |
| Comparison | Supported, controlled | A006 | Pair verification/backend deltas | Pair selectors/paired intervention | Corresponding MN9 only; retained jobs required | Arbitrary runs rejected |
| Robustness variants | Infrastructure supported | A007A | Immutable preparation envelopes | Fixed sweep preset | R0–V7 only | No arbitrary model exploration |
| Robustness orchestration | Synthetic-certified infrastructure | A007B | Serial parent manager/exact reuse | Explicit start/cancel | Up to 16 children; real sweeps 0 | Separate scientific authorization needed |
| Robustness evidence UI | Synthetic-certified | A007C | Backend rows/comparisons | Matrix/chart/shared comparison | NO_AGGREGATE_RULE; bounded snapshots | No default robustness verdict |
| Export | Supported | A002/A006/A007B/C | Verified backend contracts | Three download surfaces | Evidence, not reopenable project state | Preserve files outside session |
| Installed wheel | Supported | A008 | Packaged entry point/assets | Same production shell | Data not bundled; GPU optional | Configure registered local data root |
| Documentation | Supported | A008 | Contract-grounded docs | User guide/reproducibility | Earlier task records retain historical wording | Use current guide/closure precedence |

## Production workflow transitions

| Transition | Classification | Concrete evidence and consequence |
|---|---|---|
| Start → Define | CLEAR | E1/E3/E4/E7: automatic port, current token, dataset availability and five visible choices; missing data explicitly blocks definition |
| Define → Validate | CLEAR | E1/E4: Validate sends exact bounded selection; edits clear validation and disable Run; preview displays returned spec/digest |
| Validate → Run | CLEAR | E3/E4: validated selection enables explicit Run; server revalidates same deterministic spec; busy admission rejects overlap |
| Run → Inspect | CLEAR | E2–E4: phases/events/errors; terminal completion follows export verification; result/history expose identities |
| Inspect → Playback | CLEAR | E4/E5: completed selected result loads identity-bound sparse playback and bounded graph; unavailable traces explicit |
| Run → Compare | CLEAR | E3/E5: select completed baseline, Run paired intervention, select pair, Compare; exact backend eligibility required |
| Compare → Robustness | FUNCTIONAL_BUT_AWKWARD | E4/E6: separate panel above comparison; validate baseline in setup and explicitly start a preset, rather than promote the displayed comparison; ordinary reference runs are not automatically explicit-variant R0 evidence |
| Robustness → Export | CLEAR | E6: explicit parent export, partial evidence/errors preserved; release is separate and unavailable while active |

The intended eleven-step flow is coherent within one retained CPU session and
the certified family. Robustness extends that flow as certified infrastructure,
not as a historically executed real Application sweep. Cross-day project work
and general authoring are outside this coherence claim.

## First-experiment technical readiness

This is readiness for a separately specified, authorized CPU experiment within
the supported family, not authorization or biological readiness.

| Check | Classification | Evidence / limit |
|---|---|---|
| Experiment identity | READY | E1/E2: deterministic selection/spec, separate invocation metadata |
| Dataset provenance | READY_WITH_LIMITATION | E1/E2: pinned hashes/identities; files must already exist; catalog presence alone is not provenance verification |
| Reference preparation | READY | E2/E8: existing engine/reference config, historical real CPU completion |
| Target/stimulus resolution | READY_WITH_LIMITATION | E1: frozen sugar members and contralateral MN9 only; prepared membership checked |
| Deterministic seeds | READY | E1/E2: explicit one-trial seed, realized schedule fingerprint; seed equality alone insufficient for pairing |
| Backend selection | READY_WITH_LIMITATION | CPU certified; CUDA dispatch only |
| Result integrity | READY | E2/E3: manifest/authoritative verification and export readback before completion |
| Playback retention | READY_WITH_LIMITATION | E3/E5: recorded spikes while run retained; no UI-selected traces |
| Comparison eligibility | READY_WITH_LIMITATION | E5/E8: exact controlled pair; zero baseline relative metric null |
| Robustness contract | READY_WITH_LIMITATION | E6/E9: synthetic-certified R0–V7, serial, no aggregate verdict; real execution untested |
| Export | READY | E2/E5/E6: authoritative downloadable evidence |
| Failure visibility | READY | E2/E4/E6: typed errors/phases and failed/partial rows; ordinary failed run has no normal completed-result download |
| Recovery/retry | READY_WITH_LIMITATION | E3/E4: terminal failure frees ordinary admission; explicit fresh retry, no automatic resume/checkpoint or crash recovery |
| Duration/preparation cost | READY_WITH_LIMITATION | Fixed 100 ms simulated duration; elapsed/phase visible; no future ETA or preflight resource estimate |
| Storage/retention | READY_WITH_LIMITATION | Eight runs, bounded parents, temporary files, explicit external export; no reopen UI |

No software blocker was established for an explicitly bounded CPU session that
exports evidence before exit. Scientific question, justified intervention,
registered data verification at execution, agreed cost/retention and separate
execution authorization remain prerequisites. CUDA experiments, general
authoring and cross-session UI review are not covered by this conclusion.

## Operational cost structure

No new execution or runtime prediction. E8 records A003R loading 5.588 s,
preparation 284.976 s, trial 7.560 s, finalization 0.118 s, total 290.682 s;
export 97,367 bytes. Historical A006 baseline/intervention totals were
304.605/299.416 s. These are certification observations on their historical
environment, not benchmarks or future ETAs. The failed A003 observed process
peak working set 24,694,001,664 bytes; successful-run peak was not measured.

| Operation | Real run count / cost structure |
|---|---|
| One baseline | One run: validate, load, prepare full network, simulate, finalize/export; no warm-cache promise |
| One intervention | One further controlled run with inherited pair settings; preparation/execution remain real work |
| One A006 comparison | Zero additional simulations after eligible results exist; verify pair, construct metrics/playback/views/export. Historical construction 34.1 ms is not a future ETA |
| Optional R0–V7 | Up to sixteen child runs, serial baseline/intervention pairs; exact verified reuse can reduce new executions. Explicit variant R0 has distinct identity from ordinary reference R0; ordinary baseline cannot be assumed reusable |

No multiplication of historical timings into a sweep ETA. Synthetic sixteen-child
timings in A007B measure fixtures only. Exporting a file does not free in-memory
retention; parent release is explicit. Researcher must preserve downloads.

## Friction audit

Likelihood is an affordance-based assessment, not a measured user frequency.

| Observed friction | Evidence | Likelihood | Consequence | Blocks real use? |
|---|---|---|---|---|
| Executed details hidden in collapsed preview | E4 details element; E1 fixed mapping | Each pre-run review | Must expand to inspect exact IDs/spec | No, labels expose family and validation is explicit |
| History buttons show state and short job ID only | E4 loadRunHistory | Several retained runs | Open each to distinguish side/frequency/seed | No for bounded pair; real discoverability gap |
| Preparation may dominate with no progress granularity | E2/E4/E8 | Every cold full preparation | Long wait, uncertain remaining cost | No, real phase/elapsed visible; no invented ETA warranted |
| Robustness not a direct next action on comparison | E4/E6 separate baseline validation/start | Each sweep setup | Re-select/validate correct baseline; scrolling | No; explicit costly start is useful |
| Narrow matrix scroll and deep page | E4 CSS matrix min-width 1050; sections stacked | Narrow windows | Horizontal/vertical navigation effort | No demonstrated blocker; prior A007C responsive acceptance stands |
| Identity/event density | E4 wrapped IDs and timeline | Every inspection | Audit information demands attention | No evidence requiring redesign |
| Lost retained inspection on shutdown/eviction | E3/E6/E7 | Every restart or ninth admission | Cannot later use playback/comparison UI on old evidence | Yes for cross-session workflow, no for export-first session |
| Ordinary run cancellation absent | E3 POST allowlist/E4 | Long unwanted ordinary run | Wait or stop process; no cooperative cancel UI | No for planned bounded run; real control gap |
| Retry after FAILED is a new run | E3/E4 | On failure | Preparation repeated; partial ordinary evidence lacks download surface | No established retry blocker; no resume guarantee |

CPU/CUDA unavailable labeling, previous-result labeling, protected downloads and
paired-intervention action already address common ambiguity. There is no new
evidence that setup overload, export discoverability or current/previous result
confusion demands a correction before real CPU use.

## Persistence and export reopenability

| Boundary | Exactly what survives |
|---|---|
| Same-tab page refresh | Token in sessionStorage (when available), server records/exports/parents. DOM selection, validated setup, cursor and active watch are recreated, not saved. History can reselect retained jobs; sweeps can be reselected. Storage failure leaves token in URL for refresh |
| New server/application process | New token/instance and empty RunManager/comparison/parent registries. No discovery/loading of previous result root |
| Recent Runs eviction | Oldest record removed on admission beyond eight: UI result/playback/subgraph/pair endpoints lose ordinary job access. Previously written JSON may remain in temporary root; no promised discovery or cleanup/lifetime policy. Parent-owned children remain independent |
| Robustness parent release | Terminal parent evidence/children/graphs deleted from owned store and sweep removed; exports already downloaded survive as external files. No automatic restore |
| Process exit | Memory registries disappear. Normal temporary result files are not explicitly deleted by server_close, but residual files are not a durable registry or supported recovery mechanism. Downloaded files remain wherever researcher saved them |

Parents: at most two, sixteen children each, 64,000,000 byte-accounted bytes per
parent; full capacity rejects new admission rather than evicting children.
Parent lifetime is explicit release or session shutdown, independent of Recent
Runs. Comparisons have an in-memory registry; ordinary comparison inspection
still requires retained referenced jobs. No durable comparison history.

Can a researcher shut down today and reopen yesterday's evidence in the
Application UI? **No.** Backend ExperimentResult decoding/integrity checking
exists for trusted code, but is not a production import workflow. The exports
also do not promise standalone reconstruction of every schematic display.

| Export | Authoritative evidence? | Importable/reopenable Application state? | Later UI inspection without retained session? |
|---|---|---|---|
| ExperimentResult | Yes, strict result and provenance/integrity | No production import; Python read_result is not a project reopen feature | No |
| Comparison | Yes, backend pair identities/metrics/digest | No; comparison export alone is not both full retained runs/views | No |
| Robustness | Yes, spec/result/definitions/role provenance/metrics/failures/integrity envelope | No; parent export is not a complete restorable parent store | No |

Classification: **major usability gap for longitudinal research and a future
capability**, acceptable disclosed current limitation for an export-first bounded
session. It is not automatically a prerequisite before every first experiment.
If cross-session UI investigation becomes a requirement, reopenability must be
scoped before that workflow is promised. No checkpoint mechanism is implied.

## Authoring scope and scientific-workflow gaps

Production UI is **purpose-built for the certified MN9/sugar family**, not general
application experiment authoring (E1/E4). Side L sugar → MN9_R/16949, side R
sugar → MN9_L/10331; frequencies 10/25/50/100/150/200 Hz. Duration 100 ms,
dt 0.1 ms, one trial, input interval 0–100 ms and direct-input factor 250 fixed.
CPU reference or available CUDA; editable explicit integer seed 0–4294967295,
default 1555062870. Intervention none or corresponding-MN9 outgoing silence.
Reference model/sign/preparation fixed for ordinary runs; robustness exposes
the fixed eight-variant preset, exact reuse and NO_AGGREGATE_RULE. Sparse spikes
requested, no selected voltage/delivery traces, one authoritative target.

| Candidate dimension | Classification | Evidence / scientific consequence |
|---|---|---|
| Easier body-ID targeting | REAL GAP WITH EVIDENCE for broader authoring | E1 has no target field; search only finds displayed neurons, not execution targets |
| Arbitrary intervention/editor | REAL GAP WITH EVIDENCE for broader authoring | E1 corresponding target only; A006 pair contract also restricts intervention. Would require explicit contract review |
| Saved reusable presets | NICE_TO_HAVE | No save/load control; six fixed choices easily re-entered; no demonstrated repeated-authoring burden |
| Experiment duplication | CURRENTLY_SUPPORTED in limited form | Paired intervention derives baseline choices; general saved duplicate/editor absent, NICE_TO_HAVE |
| Richer target metrics | NOT_JUSTIFIED | Spike count/rate already authoritative; no requested additional metric/question |
| Multi-target observation | REAL GAP WITH EVIDENCE for multi-target questions | One TargetSpec metric; sparse spikes permit neuron inspection but are not multi-target metric authoring |
| Trace selection | REAL GAP WITH EVIDENCE | Backend supports bounded opt-in traces; E1 requests none; UI cannot select before execution |
| Population summaries | CURRENTLY_SUPPORTED in limited form | Derived displayed-neuron bins; general authoritative population metrics NOT_JUSTIFIED without a definition |
| Result notes/annotations | NICE_TO_HAVE | No model/control; external export notes possible, no observed annotation requirement |
| Comparison history | REAL GAP WITH EVIDENCE for longitudinal work | In-memory registry and retained-job dependence; no durable UI history |
| Restart persistence/import/reopen | REAL GAP WITH EVIDENCE | E3/E6/E7 exact loss boundaries above |
| Batch definitions | NOT_JUSTIFIED | Only fixed robustness serial orchestration; no defined batch investigation |
| Parameter exploration beyond preset | OUT_OF_SCOPE for current contract | Strict certified definitions; arbitrary overrides rejected; new science contract required |

Absence alone does not establish priority. These gaps become scientific limits
when an investigation actually needs arbitrary targeting, traces, multiple
metrics or cross-session inspection; no such question was authorized in A010.

## CUDA and robustness readiness

CUDA configuration dispatch: supported. Optional import safety: supported and
tested without CuPy. UI selection: supported, disabled/labeled unavailable from
backend options; server/service explicitly reject unavailable GPU with
GPU_UNAVAILABLE. Real Application GPU execution certified: **No**.
CPU/CUDA numerical equivalence certified: **No**. CUDA is READY_WITH_LIMITATION
for configuration infrastructure and NOT_READY as a certified real scientific
Application execution path. No real GPU test was performed here.

Robustness infrastructure: A007A/B/C certified through synthetic variants,
orchestration, retention, pair/schedule identities, failure/cancel/release/export
and manually accepted synthetic UI. Historical real Application robustness
sweeps/runs: **0**. This does not erase earlier real CPU A003/A006 integration
runs. Biological robustness interpretation: not certified. Historical Task017
remains **NOT_ROBUST** under its separate frozen experiment; the Application
default remains **NO_AGGREGATE_RULE**, aggregate_result null.

First real sweep justification: **INFRASTRUCTURE_READY_BUT_NOT_JUSTIFIED**.
No current scientific question, informative controlled contrast, variant
hypothesis or interpretation policy is specified. A validated baseline does
not supply those. A future justified baseline/intervention question should
precede deciding whether sixteen serial children add meaningful evidence.

## Bounded candidate comparison and decision

At most four product candidates, derived from observed gaps:

| Capability | Problem/evidence | Dependencies | Scientific risk | Scope | Required before first bounded CPU experiment? | Scientific contract change? |
|---|---|---|---|---|---|---|
| Integrity-checked single-result reopen | Cross-session inspection loss, E3/E7/E8 | Strict reader, owned registry, retained view availability policy; comparison/parent reopen separately scoped | Misbinding imported evidence or recreating unavailable context | Medium | No, unless cross-session UI required | No change to result meaning; new import/retention contract |
| Ordinary-run cooperative cancel | No ordinary cancel route/control, E3/E4 | Owned cancellation signal, actual service boundaries, partial export policy | Misrepresenting interrupted/late-completed evidence | Small/medium | No | Lifecycle surface change, no engine science change |
| Descriptive Recent Runs selection | State/job fragment lacks experiment summary, E4 | Backend spec summaries, identity-safe selection | Low; display only | Small | No | No |
| Bounded trace authoring | UI requests no traces despite backend support, E1/E2 | Trace body membership validation, cost limits, pairing compatibility | Observation selection/resource cost; must not alter metrics | Medium | No without trace question | Observable selection contract extension |

Each can unblock a specific observed workflow, be bounded, preserve backend
authority and avoid duplicating the engine. None presently beats stopping new
Application implementation: first-result scientific requirements have not been
specified, and present CPU use can complete/export within one session. Durable
all-object projects or arbitrary intervention editors would expand architecture
and pairing science without a current question. Cosmetic refinements have no
new blocking acceptance evidence. A real experiment would be more informative
than speculative features only once a question and envelope are justified.
No numerical ranking is used.

**Exactly one decision: A10-E — APPLICATION STABILIZATION CHECKPOINT; NO NEW
CAPABILITY JUSTIFIED.** This is an engineering checkpoint, not a release.

- A10-A is invalid now: no scientifically justified question has been supplied;
  repeating the zero-baseline plumbing pair is not automatically a new investigation.
- A10-B/C/D are not required first for the supported export-first CPU session;
  gaps are real but priority depends on the actual investigation workflow.
- A10-F understates existing certified coherent functionality; retaining it
  while stopping feature expansion is justified.

Exact next direction: **stop Application capability development temporarily;
request a separately scoped scientific question and intended observation/session
workflow before selecting a new implementation or execution task.** No next
product task is selected or implemented. No experiment authorization envelope
is proposed because its scientific question is missing. Future authorization
must explicitly bound baseline/intervention, target/stimulus, CPU backend,
seed/duration/observables, maximum run count, reuse/robustness, stop conditions,
cost/retention and interpretation limits. This audit grants no execution.

## A009 disposition and scientific firewall

A009/A009R/A009S: **NOT CERTIFIED**. The attempted independent-new-user
methodology was abandoned because operator isolation/manual orchestration
complexity became disproportionate and introduced its own error risk.
This is not a repository/product failure. A009 is not continued or revived;
this audit is the only new disposition record.

A010 real MaleCNS simulations 0; real Application scientific child runs 0;
Task017 units 0; Task017Q 0; raw-data downloads 0; checkpoint
export/import/restore 0/0/0; archive writes 0; BANC 0.
Historical Task016 unchanged; historical Task017 unchanged / NOT_ROBUST;
`B:\MaleCNS-Archive` unchanged (no archive operation performed). No new
biological claim, causal interpretation, robustness verdict or scientific score.
No product source, dataset, historical artifact, tag, release or version change.

## A010 validation and publication

- Relevant A002–A008/A006R/session regressions: 141 passed, 48.39 s.
- Production startup/read-only HTTP smoke: PASS; READY, production HTML,
  zero run records and zero simulation requests. An initial shell-quoting
  SyntaxError occurred before execution; corrected stdin script passed.
- Full pytest: 384 passed, 14 skipped, 54.13 s. Eleven skips require an
  available CuPy/CUDA device, two other CUDA tests are unavailable, and the
  opt-in bounded full-graph test remains gated. No real-data gate enabled.
- compileall: PASS for src/scripts/tests.
- Tracked integrity: PASS, nine frozen files and internal identities.
- Build: PASS, 0.3.0 source distribution and wheel. No new installed-wheel
  certification claimed; A008 supplies that existing evidence.
- Final diff check: PASS. Scope: only this new audit record; stash empty.
  Publication identity is reported in the final response because a commit
  cannot embed its own final SHA without changing that SHA.

Authorized commit scope: this audit file only. Push origin master after passing
validation; verify identical local/origin/live SHA, clean worktree, empty stash
and zero tracked workflows. No tag/release/version bump.
