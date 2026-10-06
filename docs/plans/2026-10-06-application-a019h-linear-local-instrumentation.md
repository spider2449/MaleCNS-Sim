# A019H bounded synthetic linear-local instrumentation

Authorization: user explicitly authorized A019H, including terminal commit/push.
Starting local HEAD, origin/master and live GitHub master:
`cabe0d750ee9cc830a9fd8be889f69acb940af92`.
Worktree/staging/stash empty; version 0.3.0; tracked workflows zero.

Synthetic-only. No optimization, real-source execution, GPU, benchmark-contract
change, model change, tag, release or version bump is authorized.
Preserve A019G-C and its 17.4-31.4% unresolved linear residual.

Plan: map source; extend existing exclusive timers; prove exact OFF/ON and
starting-SHA compatibility; reuse G1/G2/G3 at 60 input events plus E0/E2;
run three paired warmups and ten measured pairs; reconcile every ON call;
assess overhead and attribution; record one classification and one next task;
run targeted guarded tests, compileall and diff check; commit and push.

All Python execution uses the existing fail-closed sitecustomize firewall,
activated before imports and test collection. Accounting is fail-closed guarded
accounting, not independent native byte telemetry.

## Source-local map

Spans below refer to the final source in `src/malecns_sim/dynamics/lif.py`.

| Function / span | Operation and shape | Boundary / allocation / indexing / reduction | Timing |
|---|---|---|---|
| simulate_lif / lif.py:581-589 | parent entry, mask timer setup and np.any(allowed); allowed bool[N] -> bool scalar | Python -> NumPy reduction; scalar only; mask temporaries already in mask; indexed=False; reduction=True | allowed_reduction; entry/hooks remain residual |
| simulate_lif / lif.py:592-599 | v[allowed], g[allowed], call keyword binding and tuple unpack; two float64[N] -> two float64[K], K=count_nonzero(allowed) | Python -> NumPy advanced indexing -> Python call; two existing gathered arrays; no additional array copy; indexed=True; reduction=False | input_gather; call entry/unpack/cleanup remain residual |
| linear_state_update / lif.py:141-143 | function entry and first substart; two float64[K] arguments | Python; call frame; indexed=False; reduction=False | residual; no clean exclusive interval without nested hooks |
| linear_state_update / lif.py:154-169 | between timers, np.ndim(v_mV), branch and tuple return; ndim scalar; tuple of two float64[K] arrays | Python -> NumPy shape inspection -> Python; return tuple; scalar path float conversion; ndarray path no semantic copy; indexed=False; reduction=False | return_shape_check; tuple return and hook bookkeeping remain residual |
| simulate_lif / lif.py:599-606 | gather reference release, writeback timer hooks, parent close; two gathered float64[K] released; v/g float64[N] | Python refcount/NumPy indexed writeback; no new semantic array; indexed scatter already in writeback; indexed=True; reduction=False | writeback unchanged; cleanup/hooks remain residual |
| PreparedRuntime.advance / lif.py:438-457 | runtime checks, simulate_lif arguments and result return; state N; pending ring_size x N | Python; call frames/result reference; indexed=False; reduction=False | outside linear parent; existing full advance residual |
| simulate_lif_active / lif.py:787-794 | active_positions, refractory gathers, allowed_positions, linear arguments/writeback; active int64[A], allowed bool[A], arguments float64[K] | Python -> NumPy indexing; fromiter and gathered arrays; indexed=True; reduction=False | alternate immediate caller; not used by PreparedRuntime.advance or this matrix; unchanged |

The existing membrane expression retains its original NumPy arithmetic and temporary arrays; synaptic decay retains its multiplication allocation. They are already timed, so no duplicate allocation stage is added. No separate allowed-array gather exists in the measured dense caller. Boolean gathers retain their left-to-right order and release their added local references immediately after the call. Timing insertion preserves every array operation and FP order. No semantic array copies are added. Tuple materialization and wrapper entry cannot be isolated cleanly with the existing non-nested timer without additional hook overhead, so they remain residual.

## Results

Classification: **A019H-B — LINEAR RESIDUAL LOCALIZED; MULTIPLE LINEAR O1 TARGETS REMAIN PLAUSIBLE.**

Raw pairs and all min/median/mean/max distributions are in `a019h-linear-local-evidence.json`. Each measured advance has 200 timesteps at dt=0.1 ms; state is advanced once before measurement to exercise continuation. Three paired warmups and ten alternating OFF/ON measured pairs per case. Exact equality covers every state and result dataclass field, including array bytes/dtypes/shapes, refractory/pending/delayed state, event order, outputs and simulated time. Starting-SHA OFF compatibility: five cases, two chunks each, PASS. Instrumentation is OFF by default and disabled timers never read the clock.

| Case | N / edges / scheduled input events | Linear parent mean ms | Previous sum % | Newly explained % | Remaining % | Overhead % / class |
|---|---|---|---|---|---|---|
| G1-12 | 128 / 1024 / 60 | 7.30841 | 79.155 | 11.960 | 8.885 | 14.942 / OHD-B |
| G2-12 | 4096 / 32768 / 60 | 12.54726 | 74.661 | 18.881 | 6.458 | 9.497 / OHD-B |
| G3-12 | 32768 / 262144 / 60 | 53.14364 | 68.142 | 29.927 | 1.930 | 3.643 / OHD-A |
| E0-1 | 4096 / 32768 / 5 | 12.25981 | 74.733 | 19.043 | 6.224 | 8.818 / OHD-B |
| E2-409 | 4096 / 32768 / 2045 | 12.11502 | 74.848 | 18.731 | 6.420 | 6.274 / OHD-B |

| Case | New substage | Min ms | Median ms | Mean ms | Max ms | Parent share |
|---|---|---|---|---|---|---|
| G1-12 | allowed_reduction | 0.43010 | 0.44955 | 0.44857 | 0.47130 | 6.138% |
| G1-12 | input_gather | 0.29840 | 0.30970 | 0.30756 | 0.31420 | 4.208% |
| G1-12 | return_shape_check | 0.11430 | 0.11740 | 0.11795 | 0.12350 | 1.614% |
| G2-12 | allowed_reduction | 0.47160 | 0.48610 | 0.51470 | 0.78330 | 4.102% |
| G2-12 | input_gather | 1.61300 | 1.66430 | 1.71596 | 2.20030 | 13.676% |
| G2-12 | return_shape_check | 0.12560 | 0.12735 | 0.13841 | 0.21730 | 1.103% |
| G3-12 | allowed_reduction | 0.58540 | 0.59765 | 0.60275 | 0.63900 | 1.134% |
| G3-12 | input_gather | 14.86110 | 15.05720 | 15.05199 | 15.18210 | 28.323% |
| G3-12 | return_shape_check | 0.23450 | 0.25000 | 0.24967 | 0.26110 | 0.470% |
| E0-1 | allowed_reduction | 0.47480 | 0.48690 | 0.48917 | 0.50860 | 3.990% |
| E0-1 | input_gather | 1.68180 | 1.71470 | 1.71724 | 1.76600 | 14.007% |
| E0-1 | return_shape_check | 0.12360 | 0.12860 | 0.12823 | 0.13410 | 1.046% |
| E2-409 | allowed_reduction | 0.47660 | 0.49290 | 0.49152 | 0.51310 | 4.057% |
| E2-409 | input_gather | 1.60350 | 1.63340 | 1.64866 | 1.74220 | 13.608% |
| E2-409 | return_shape_check | 0.12260 | 0.12870 | 0.12912 | 0.14640 | 1.066% |

All 50 measured ON advance calls reconcile exactly: previous named sum + newly explained sum + local residual = linear parent, with zero integer-nanosecond accounting error. Full stage sum + full residual also reconciles. Replay and schema/reset reconciliation are additionally checked by the targeted tests. This accounting identity is not independent proof of zero timer cost. Residual is computed explicitly, never hidden in an other stage.

A019G residual 17.4-31.4%; A019H weighted-mean case residual range **1.930390917897231-8.884695850397008%**. New residual distributions remain in evidence. Most of the large-graph unresolved work is localized. Overhead rubric: <=5% OHD-A; >5-15% OHD-B; >15% OHD-C. Observed 3.643-14.942%; no OHD-C. Small G1 is close to the caution boundary. No timing retry or matrix expansion.

## Scaling and target gate

At fixed 60 scheduled events, input-gather means are 0.30756 / 1.71596 / 15.05199 ms for G1/G2/G3: neuron-sensitive, supported by the actual Boolean-index source over N-length state arrays. G neurons and edges co-vary, so this matrix does not independently identify edge sensitivity; these operations do not read edges. Allowed reduction is mixed: 0.44857 / 0.51470 / 0.60275 ms, mostly per-call overhead with a possible array-size contribution. Return-shape check is unclear: 0.11795 / 0.13841 / 0.24967 ms; nominal shape query has no N-sized arithmetic and its larger-case increase cannot be assigned to array traversal.

E0/E2 share the same 4096/32768 graph with 5/2045 scheduled events. Gather mean changes 1.71724 -> 1.64866 ms (-3.99%); reduction 0.48917 -> 0.49152 ms (+0.48%); return check 0.12823 -> 0.12912 ms (+0.69%). No material positive activity sensitivity is established. Allowed masks vary with refractory activity; synthetic negative/no-sensitivity evidence is limited to these cases.

Existing membrane, writeback, mask and synaptic decay remain neuron-sensitive; coefficients are fixed/per-call source work, with timing/cache variation across cases. Do not infer exponents or full-real percentages.

Input gathers pass direct measurement, concrete source, stable G attribution, meaningful large-graph share (28.323% linear, 19.104% synthetic advance at G3), source-consistent neuron scaling, plausible exact-semantics preservation, and acceptable overhead gates. Remaining G3 residual is 1.930%, so residual uncertainty no longer dominates the choice. However, membrane (25.603%) and indexed writeback (22.294%) are similarly substantial graph-sensitive alternatives; these timings do not prove which exact contract-preserving transformation is both feasible and preferable. No single first O1 target is proven. The result is B, not a forced target choice. No schedule instrumentation was reopened; A019G scheduling evidence is preserved, but no workload-independent scheduling superiority is established.

Exactly one next task: **A019I — bounded synthetic allocation/lifetime and contract-preserving feasibility diagnostic of linear input gathers versus membrane evaluation and indexed writeback; no optimization**. Do not start it automatically.

## Validation, limitations and closure

Targeted A019F/G/H suite: 18 passed. Includes OFF defaults, exact ON/OFF, starting-SHA replay, schema/reset/accounting, deterministic matrix, G events invariant, synthetic CLI bounds, catalog prohibition and all seven denied registered categories. For reproducible baseline certification, export `git show cabe0d750ee9cc830a9fd8be889f69acb940af92:src/malecns_sim/dynamics/lif.py` to an external temporary Python module and set `A019H_BASELINE_MODULE` to it. The baseline was loaded only under the active guard. compileall src scripts tests PASS; git diff --check PASS. No broad real-dependent test discovery.

Counters: full-real preparations=0; real advances=0; A019D reruns=0; GPU runs=0; Arena runs=0; interventions=0; downloads=0; archive writes=0. All seven accepted registered-source read categories=0. Deliberate firewall denial tests are blocked before content reads. Qualifier: **fail-closed guarded accounting, not independent native byte telemetry**. Synthetic evidence writes are report artifacts.

Limitations: timer entry/accounting and reference cleanup remain residual; no calibrated confidence intervals, independent native allocation telemetry, edge-only scaling or full-real inference. No optimization, semantics change, benchmark-contract change, tag, release or version bump. Authorized terminal closure commits these five task files and pushes origin master. Exact final local/origin/live identity and clean worktree/staging/stash are verified after push and reported externally to avoid self-hash recursion. Version remains 0.3.0; tracked workflows remain zero.
