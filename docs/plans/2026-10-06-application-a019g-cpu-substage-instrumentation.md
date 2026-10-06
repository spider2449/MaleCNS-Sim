# Application Task A019G ? CPU substage instrumentation

Authorization: ?? A019G. Synthetic-only observation; no optimization.
Starting local HEAD, origin/master and live master: `112eff15935041b982561b999acd8ba01b599cf6`.
Root derived with git rev-parse. Initial worktree/staging clean, stash empty,
version 0.3.0, tracked workflows 0. Preserve A019F-B; findings refine rather
than contradict its multiple-cost-center result.

## Guard and semantics

All Python collection, imports, runs, baseline replay and compileall use
MALECNS_A019C_R2_FIREWALL=1 and PYTHONPATH=scripts/a019c_firewall.
Bootstrap activation verified before Python implementation work. Static reads
were code/task evidence only. Guard rejected a baseline helper's attempted git
subprocess before execution; baseline source was then exported by PowerShell git
and replayed inside the guarded interpreter. No bypass or source access occurred.
Accounting is fail-closed guarded accounting, not independent native byte telemetry.
No payload readers, downloads, native direct reads or real execution were used.

OFF remains the default and never reads the timer. Original floating-point
expressions, validation, event order and state mutation order remain unchanged.
Only observational branches and private timing arguments were added. Scheduling's
original comprehension is assigned then returned to permit a closing observation;
its iteration and NumPy construction are unchanged. The active/GPU paths are untouched.
Exact OFF/ON replay compares all dataclass fields, dtype/shape/bytes, membrane,
synaptic, refractory, pending weights/counts, outputs/event order and timestep,
over two 20-ms chunks with trace. All six matrix cases PASS. Independent OFF replay
against both exact starting-SHA modules also PASS for six cases x two chunks.

## Static source boundaries

All boundaries identify literal executable statements in the named module/function.
Named children are exclusive, nested only inside their inclusive A019F parent.
The parent clock is separate from the single child clock. Children never overlap.
Allocation and native NumPy work belong to the operation that executes them;
no allocation/copy is separately counted again.

| Module/function | Child | Exact first through last boundary | Relationship |
|---|---|---|---|
| lif::simulate_lif | mask | allowed = (step > refractory_until) through OR mask | exclusive child of linear_update; allocates mask |
| lif::linear_state_update | coefficients | dt = _finite through g_coefficient branch | exclusive; scalar validation, two np.exp, np.isclose, coefficient arithmetic |
| lif::linear_state_update | membrane | v_next = entire unchanged expression | exclusive; np.asarray views, vector arithmetic and temporaries/allocation |
| lif::linear_state_update | synaptic_decay | g_next = np.asarray(g_mV) * exp_s | exclusive; vector decay and new array |
| lif::simulate_lif | writeback | v[allowed] = updated_v through g[allowed] = updated_g | exclusive scatter/writeback |
| lif::simulate_lif + linear_state_update | residual, not separately timed | np.any(allowed), v[allowed]/g[allowed] argument gathers/copies, function entry, ndim/return, hooks/loop control | parent minus children; no forced attribution |
| stimulus::schedule_events | lookup | position = int(np.searchsorted(...)) through ID validity branch | exclusive child of event_schedule; Python/native boundary per schedule |
| stimulus::schedule_events | grid_validation | step = _grid_steps(...) through endpoint validity branch | exclusive per-event child; _number, rounding, np.isclose; no model delay calculation here |
| stimulus::schedule_events | append | batches.setdefault(step, []).append((position, 1.0)) | exclusive; ordered tuple/list construction and grouping |
| stimulus::schedule_events | packing | original return dict comprehension, now result assignment | exclusive; sorted(batches.items()), two list comprehensions and np.asarray allocations per bin |
| stimulus::schedule_events | residual, not separately timed | batches initialization, iteration, hooks, return plumbing | parent minus children |

Threshold/spike reset, pending-ring insertion, CSR edge iteration and refractory
state mutation remain in other A019F parent stages, outside these two functions.
There is no source/destination edge lookup, pending-ring insertion, or vector
filtering in schedule_events. No invented edge stage or algorithm restructuring.
linear_state_update itself has no Python neuron loop or refractory/threshold work.
The unchanged membrane expression cannot distinguish each temporary independently.

## Controlled workload and protocol

Reuse A019F immutable in-memory CSR construction, seed 1906, degree 8, 0.275-mV
edges, standard model parameters/dt=0.1 ms and existing 30-mV synthetic input.
Times 0,5,10,15,19.9 ms. No parameter tuning or scientific intervention.
G fixes the exact effective scheduled input count at 60, not merely intended input.
Propagation/pending counts are recorded separately and are not claimed fixed.
E uses byte-identical graph/runtime identity with input counts 5,200,2045.
No optional D matrix: edge sensitivity cannot be separated from neuron sensitivity
in G, and an extra density family is not needed for this residual-limited outcome.
Each measured call follows an identical fresh OFF 20-ms precursor; measured
20-ms chunk ends at 40 ms. Three OFF/ON warmup pairs and ten measured pairs per
case, alternating mode order. Graph/state allocation and precursor are outside
wall timing. Every measured OFF and ON call is in the JSON evidence.

| Case | N | Edges | Edges/N | Scheduled input events | Pending before/after | Queued/delivered | OFF/ON median ms | Overhead ms / % / class |
|---|---:|---:|---:|---:|---|---|---|---|
| G1-12 | 128 | 1024 | 8 | 60 | 96/96 | 384/384 | 10.415/11.882 | 1.467 / 14.09% / OHD-B |
| G2-12 | 4096 | 32768 | 8 | 60 | 96/96 | 384/384 | 16.915/18.507 | 1.592 / 9.41% / OHD-B |
| G3-12 | 32768 | 262144 | 8 | 60 | 96/96 | 384/384 | 77.115/78.836 | 1.721 / 2.23% / OHD-A |
| E0-1 | 4096 | 32768 | 8 | 5 | 8/8 | 32/32 | 15.748/17.069 | 1.321 / 8.39% / OHD-B |
| E1-40 | 4096 | 32768 | 8 | 200 | 320/320 | 1280/1280 | 20.348/22.006 | 1.658 / 8.15% / OHD-B |
| E2-409 | 4096 | 32768 | 8 | 2045 | 3272/3272 | 13088/13088 | 61.163/64.441 | 3.278 / 5.36% / OHD-B |

## Substage measurements

Min/median/mean/max nanoseconds and parent/full shares for every child/residual
are in the JSON, alongside all raw calls. Ranking uses medians; shares are ratios
of summed child durations to summed parent/full durations. No hook subtraction.
Below each entry gives median ms and mean share of parent.

| Case | Parent | Child | Median ms | Parent share | Full share |
|---|---|---|---:|---:|---:|
| G1-12 | linear_update | mask | 0.5061 | 7.12% | 4.29% |
| G1-12 | linear_update | coefficients | 3.6843 | 51.59% | 31.08% |
| G1-12 | linear_update | membrane | 1.1501 | 16.07% | 9.68% |
| G1-12 | linear_update | synaptic_decay | 0.2595 | 3.71% | 2.24% |
| G1-12 | linear_update | writeback | 0.2915 | 4.12% | 2.48% |
| G1-12 | linear_update | residual | 1.2456 | 17.39% | 10.48% |
| G1-12 | event_schedule | lookup | 0.0362 | 3.30% | 0.30% |
| G1-12 | event_schedule | grid_validation | 0.9795 | 89.07% | 8.11% |
| G1-12 | event_schedule | append | 0.0182 | 1.73% | 0.16% |
| G1-12 | event_schedule | packing | 0.0194 | 1.78% | 0.16% |
| G1-12 | event_schedule | residual | 0.0449 | 4.12% | 0.38% |
| G2-12 | linear_update | mask | 0.8598 | 7.24% | 4.64% |
| G2-12 | linear_update | coefficients | 3.8428 | 32.29% | 20.69% |
| G2-12 | linear_update | membrane | 2.4787 | 20.87% | 13.38% |
| G2-12 | linear_update | synaptic_decay | 0.4662 | 3.94% | 2.53% |
| G2-12 | linear_update | writeback | 1.4610 | 12.31% | 7.89% |
| G2-12 | linear_update | residual | 2.7715 | 23.34% | 14.96% |
| G2-12 | event_schedule | lookup | 0.0379 | 3.58% | 0.21% |
| G2-12 | event_schedule | grid_validation | 0.9685 | 88.54% | 5.21% |
| G2-12 | event_schedule | append | 0.0186 | 1.72% | 0.10% |
| G2-12 | event_schedule | packing | 0.0215 | 1.97% | 0.12% |
| G2-12 | event_schedule | residual | 0.0463 | 4.20% | 0.25% |
| G3-12 | linear_update | mask | 3.4679 | 6.53% | 4.40% |
| G3-12 | linear_update | coefficients | 5.0530 | 9.56% | 6.44% |
| G3-12 | linear_update | membrane | 14.0480 | 26.37% | 17.78% |
| G3-12 | linear_update | synaptic_decay | 2.0240 | 3.80% | 2.56% |
| G3-12 | linear_update | writeback | 11.8364 | 22.30% | 15.04% |
| G3-12 | linear_update | residual | 16.6720 | 31.44% | 21.19% |
| G3-12 | event_schedule | lookup | 0.0414 | 3.83% | 0.05% |
| G3-12 | event_schedule | grid_validation | 0.9513 | 88.23% | 1.21% |
| G3-12 | event_schedule | append | 0.0191 | 1.75% | 0.02% |
| G3-12 | event_schedule | packing | 0.0227 | 2.11% | 0.03% |
| G3-12 | event_schedule | residual | 0.0442 | 4.08% | 0.06% |
| E0-1 | linear_update | mask | 0.8744 | 7.37% | 5.10% |
| E0-1 | linear_update | coefficients | 3.8087 | 32.32% | 22.37% |
| E0-1 | linear_update | membrane | 2.4317 | 20.52% | 14.20% |
| E0-1 | linear_update | synaptic_decay | 0.4795 | 4.13% | 2.86% |
| E0-1 | linear_update | writeback | 1.4565 | 12.26% | 8.49% |
| E0-1 | linear_update | residual | 2.7629 | 23.40% | 16.20% |
| E0-1 | event_schedule | lookup | 0.0072 | 5.88% | 0.04% |
| E0-1 | event_schedule | grid_validation | 0.0889 | 73.25% | 0.52% |
| E0-1 | event_schedule | append | 0.0027 | 3.04% | 0.02% |
| E0-1 | event_schedule | packing | 0.0136 | 11.36% | 0.08% |
| E0-1 | event_schedule | residual | 0.0073 | 6.47% | 0.05% |
| E1-40 | linear_update | mask | 0.8639 | 7.25% | 3.95% |
| E1-40 | linear_update | coefficients | 3.9143 | 32.71% | 17.84% |
| E1-40 | linear_update | membrane | 2.4731 | 20.75% | 11.32% |
| E1-40 | linear_update | synaptic_decay | 0.4636 | 3.90% | 2.12% |
| E1-40 | linear_update | writeback | 1.4594 | 12.25% | 6.68% |
| E1-40 | linear_update | residual | 2.7729 | 23.14% | 12.62% |
| E1-40 | event_schedule | lookup | 0.1142 | 3.31% | 0.52% |
| E1-40 | event_schedule | grid_validation | 3.1578 | 89.87% | 14.18% |
| E1-40 | event_schedule | append | 0.0578 | 1.72% | 0.27% |
| E1-40 | event_schedule | packing | 0.0369 | 1.07% | 0.17% |
| E1-40 | event_schedule | residual | 0.1396 | 4.03% | 0.64% |
| E2-409 | linear_update | mask | 0.8821 | 7.44% | 1.37% |
| E2-409 | linear_update | coefficients | 3.8822 | 32.67% | 6.03% |
| E2-409 | linear_update | membrane | 2.4785 | 20.80% | 3.84% |
| E2-409 | linear_update | synaptic_decay | 0.4586 | 3.87% | 0.71% |
| E2-409 | linear_update | writeback | 1.4373 | 12.16% | 2.24% |
| E2-409 | linear_update | residual | 2.7357 | 23.06% | 4.25% |
| E2-409 | event_schedule | lookup | 1.1063 | 3.18% | 1.72% |
| E2-409 | event_schedule | grid_validation | 31.4738 | 90.28% | 48.87% |
| E2-409 | event_schedule | append | 0.6056 | 1.74% | 0.94% |
| E2-409 | event_schedule | packing | 0.2822 | 0.80% | 0.43% |
| E2-409 | event_schedule | residual | 1.3876 | 3.99% | 2.16% |

## Reconciliation, overhead and decision

All 60 measured instrumented calls have nonnegative parent and full residuals;
child sum + residual = parent exactly (0 ns accounting error), and A019F stage
sum + full residual = full total. This accounting identity is not independent
proof that timers carry zero overhead. Every residual distribution is retained.
Rubric preserved from A019F: <=5% OHD-A, >5?15% OHD-B, >15% OHD-C.
Observed overhead 2.23?14.09%; no OHD-C. Larger G is A; others B. Tiny E0
schedule shares are noise-sensitive; no statistically calibrated confidence claim.

Linear mean residual shares 17.4?31.4%; scheduling 4.0?6.5%.
Scheduling grid validation dominates non-tiny event cases (~88?90% parent).
At fixed graph its duration grows with events. It is a concrete plausible target,
but no first optimization is selected because the competing graph-sensitive
linear residual remains unresolved. G membrane and writeback grow strongly;
coefficients are roughly fixed per timestep and dominate only smaller graphs.
At G3 membrane is 26.4%, writeback 22.3%, and residual 31.4% of linear parent.

| Important operation | Qualitative classification | Controlled evidence |
|---|---|---|
| coefficients | roughly fixed/per-call (200 timestep invocations) | similar absolute time across G/E; declining G share |
| membrane | neuron-sensitive | strong G growth, relatively stable fixed-graph E |
| synaptic_decay | neuron-sensitive | G growth, small share |
| mask/writeback | neuron-sensitive | G growth; E changes activity/refractory masks |
| linear residual | mixed/unclear | grows with G; contains gathers plus fixed hooks and reduction |
| schedule lookup | event/schedule-sensitive | E increases number of schedules; G fixed schedules |
| grid_validation | event-sensitive | E count scaling; G approximately stable at 60 events |
| append/packing | event-sensitive with fixed/bin component | five bins fixed, E increases list lengths |
| schedule residual | mixed | loop/hook cost grows with events |

No isolated edge-scaling finding: G neurons and edges co-vary. No elaborate
complexity fit, full-real event mix, cache/allocation attribution, or full-real
A019D stage percentages are established. Synthetic attribution only; any
full-real relevance is inference. No A019F reopening or benchmark-contract change.

**A019G-C ? SUBSTAGE RESIDUAL REMAINS TOO LARGE; FINER LOCAL INSTRUMENTATION REQUIRED.**
One concrete first O1 target proven: **No**. No optimization implemented.
Exactly one recommended next task:
**A019H ? bounded synthetic local instrumentation of linear input gathers,
allowed reduction, and call/return residual; no optimization.**
Retain this matrix and exact replay gate; isolate the unclassified linear work
before comparing an O1 candidate against per-event grid validation.

## Validation and closure

Targeted A019F + A019G tests: 14 passed. Prove OFF clock isolation, exact replay,
schema/reset/reconciliation, deterministic matrix, fixed effective input event
counts, fixed graph identities, runner bounds, required synthetic CLI, catalog
prohibition, fail-closed guard and seven deliberate denied source categories.
Independent baseline replay: six cases x two chunks PASS.
compileall src scripts tests: PASS. git diff --check: PASS.
No broad real-dependent discovery, Arena or GPU test execution.

Counters: full-real preparations=0; real advances=0; A019D reruns=0;
GPU runs=0; Arena runs=0; scientific interventions=0; downloads=0; archive writes=0.
All seven accepted registered-read categories=0. Qualifier: fail-closed guarded
accounting, not independent native byte telemetry. Synthetic evidence writes are
report artifacts, not archive writes.

Authorized closure: commit instrumentation/tests/report and push origin master.
Final SHA equality and clean worktree/staging, empty stash, version 0.3.0 and
workflows 0 verified after push and reported externally to avoid self-hash recursion.
No tag/release/version bump.
