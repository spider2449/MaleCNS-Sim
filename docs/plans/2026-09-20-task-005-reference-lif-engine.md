# Task 005 - Reference Leaky Integrate-and-Fire Engine

Status: implementation and validation complete, changes intentionally left
uncommitted for review.

## 1. Task goal

Task 005 adds a deterministic CPU reference dynamics layer for the validated
MaleCNS curated graph. The boundary is:

```text
curated MaleCNS graph
-> Task 004 signed anatomical connectivity
-> explicit LIF parameters
-> sparse delayed spike dynamics
-> reproducible compact spike output
```

It does not implement a feeding experiment, sensory coupling, motor control,
or biological parameter fitting.

## 2. Primary scientific references

- Shiu et al., “A Drosophila computational brain model reveals sensorimotor
  processing,” Nature 634, 210-219 (2024),
  [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9).
- The official [philshiu/Drosophila_brain_model repository](https://github.com/philshiu/Drosophila_brain_model).
- The inspected [reference `model.py`](https://raw.githubusercontent.com/philshiu/Drosophila_brain_model/main/model.py).
- The inspected [official `environment_full.yml`](https://raw.githubusercontent.com/philshiu/Drosophila_brain_model/main/environment_full.yml).
- Brian’s [refractoriness documentation](https://brian2.readthedocs.io/en/stable/user/refractoriness.html)
  and [input-stimulus documentation](https://brian2.readthedocs.io/en/stable/user/input.html).

## 3. Exact Shiu equations

The companion source defines the two linear state variables as:

```text
dv/dt = (v_rest - v + g) / tau_membrane       (unless refractory)
dg/dt = -g / tau_synapse                     (unless refractory)
```

Presynaptic events execute `g_post += w_pre_post`. The source calls this an
alpha synapse, but it contains one decaying `g` state; Task 005 preserves that
published behavior and does not introduce a two-state textbook alpha filter.

The threshold expression is strict `v > v_threshold`. Reset sets `v` to the
reset voltage and clears `g`; the source reset string also contains `w = 0`,
but the reference neuron equations do not define a neuron-level `w` state.

## 4. Exact reference parameters

`LIFParameters` is an immutable object with these values, in mV and ms:

| Parameter | Value |
| --- | ---: |
| `v_rest` | -52.0 mV |
| `v_reset` | -52.0 mV |
| `v_threshold` | -45.0 mV |
| `tau_membrane` | 20.0 ms |
| `tau_synapse` | 5.0 ms |
| `refractory_period` | 2.2 ms |
| `synaptic_delay` | 1.8 ms |
| `synaptic_weight_per_anatomical_synapse` | 0.275 mV |

The exported `REFERENCE_LIF_PARAMETERS` instance is the default, and its
fingerprint is included in every simulation configuration.

## 5. Original code behavior

The companion source constructs `NeuronGroup(..., method='linear',
threshold='v > v_th', reset=..., refractory='rfc')`, initializes `v` to
`v_0`, `g` to zero, and `rfc` to `t_rfc`. `Synapses` uses
`on_pre='g += w'` with one uniform delay and assigns
`connectivity * w_syn` to `w`.

`PoissonInput` targets `v` directly, uses `N=1`, weights each event by
`w_syn * f_poi`, and sets the refractory period of stimulated targets to zero.
The reference defaults are `r_poi=150 Hz`, `r_poi2=0 Hz`, and `f_poi=250`.

The source’s `silence` function sets the weights selected by a source-neuron
index to zero. That code disables outgoing connections. The repository README
describes silencing as setting connections “to and from” zero, but the
executable `model.py` behavior is the narrower outgoing-only operation and is
the behavior implemented here.

## 6. dt provenance

The original `model.py` does not assign `defaultclock.dt`; it relies on
Brian2’s default clock. The historical companion environment is Python 3.10
with Brian2 2.5.1. MaleCNS-Sim explicitly uses `dt=0.1 ms` for reproducibility.
This is an engineering reproducibility choice and is not claimed to be an
explicit `dt=0.1 ms` statement in the Nature Methods.

## 7. State-update mathematics

For one interval of length `h`, the exact linear update is:

```text
E_m = exp(-h / tau_membrane)
E_s = exp(-h / tau_synapse)
g_next = E_s * g

v_next = v_rest + E_m * (v - v_rest) + C * g
C = (E_s - E_m) / (1 - tau_membrane / tau_synapse)
```

When the two time constants are equal, the continuous-limit coefficient
`C = (h / tau_membrane) * E_m` is used. `linear_state_update` is vectorized
over NumPy float64 arrays and is regression-tested against these expressions.
It is not forward Euler.

## 8. Scheduling semantics

The discrete boundary order is explicitly implemented as follows for boundary
`t=k*dt`:

1. apply direct deterministic/Poisson input writes;
2. apply delayed `g` writes due at this boundary;
3. analytically update `v` and `g` over `[t, t+dt]` for allowed neurons;
4. evaluate the strict threshold at the updated state;
5. emit spikes at `t+dt`, reset `v` and `g`, and set refractory state;
6. enqueue outgoing events for `t+dt+delay`.

The reference 1.8 ms delay is exactly 18 steps at 0.1 ms. The reference 2.2
ms refractory interval is exactly 22 steps; Brian’s timestep-safe comparison
keeps a neuron refractory while `t-lastspike <= 2.2 ms`, so a normal neuron
first becomes eligible strictly after the 22-step boundary.

Future parameter combinations that are not exactly representable on the
selected clock fail with a clear `ValueError`; no implicit rounding policy is
used.

## 9. Refractory semantics

Both `v` and `g` are clamped because both reference differential equations are
marked `unless refractory`. Incoming writes to these state variables are
ignored while the neuron is refractory, matching Brian’s documented behavior
for read-only refractory variables. Threshold tests are also blocked.

Reference-style direct Poisson targets are explicitly assigned a zero
refractory period in the generated stimulus, so their input and threshold
processing remain enabled. This exemption is narrow and represented in the
stimulus object; it is not a universal engine default.

## 10. Delayed-event model

The engine builds deterministic outgoing CSR-like row ranges from active
resolved presynaptic edges. Each emitted spike visits only its outgoing row,
adds signed effective weights to a dense NumPy delay ring, and records an event
count. The ring has `delay_steps + 1` slots and does not allocate a dense
neuron-by-neuron connectivity matrix. Multiple writes to one target use
`np.add.at` and therefore sum deterministically.

## 11. Signed-edge projection

`EffectiveSignedProjection.from_signed_connectome` consumes the immutable
Task 004 object and includes only `signed_edge_mask == True` edges. For each
included edge:

```text
effective_weight_mV = synapse_count
                       * presynaptic_sign
                       * synaptic_weight_per_anatomical_synapse_mV
```

Anatomical counts remain available separately. The projection records included
and excluded anatomical weight, excluded unresolved edge count, unsigned graph
fingerprint, resolution-policy identity, signed-policy fingerprint, and its
own effective-edge fingerprint. Unresolved edges are not invented as zero
weights and are not propagated.

The projection stores the scalar used to construct its effective weights, and
the simulator rejects a mismatch between that scalar and the supplied LIF
parameter. This prevents a custom simulation from silently using an anatomical
weight different from the parameter identity it reports.

## 12. Explicit stimulus model

`SpikeSchedule(neuron_id, spike_times_ms)` is the primary deterministic input
interface. IDs must exist in the projection and times must be non-negative,
strictly on the selected timestep grid, and before the simulation endpoint.
Schedules are sorted by neuron and time. Duplicate times are retained as
independent impulses and therefore add their direct voltage weight.

The explicit stimulus is a direct-voltage input, matching the target-variable
behavior of the reference `PoissonInput`; it is not silently converted into a
new anatomical edge.

## 13. Poisson model

`PoissonStimulus` uses an explicit NumPy `default_rng(seed)` and one Bernoulli
draw per target per timestep, with probability `rate_hz * dt / 1000`. It uses
the reference rates and scaling as explicit options: 150 Hz, 0 Hz for the
second class, and `weight_factor=250`, producing `0.275 * 250 = 68.75 mV`
for the default input weight.

The generated schedule is reproducible for the same configuration and seed.
It does not claim to reproduce Brian2’s random-number stream, and no Poisson
stream is used in equivalence tests.

## 14. Silencing semantics

`simulate_lif(..., silenced_neuron_ids=...)` suppresses outgoing rows from
those neurons only. Incoming edges remain intact and a silenced neuron can
still receive input and emit its own spike; this follows the inspected
`model.py` assignment behavior rather than the broader README wording.

## 15. Brian2 micro-oracle results

The historical source/environment provenance was inspected directly. A
Python-3.12 optional probe using the current `uv` environment attempted to
resolve Brian2, but the install/import command did not complete after several
minutes and was terminated. No Brian2 version was successfully imported in
this environment, and Brian2 was not added to production or test dependencies.

Accordingly, there is no claimed Brian2 trace result in this task. Scheduling
and refractory behavior were derived from the executable `model.py` plus the
Brian documentation cited above, then locked with analytical and deterministic
synthetic tests. This is an explicit oracle-unavailable disposition, not a
claim of Brian2 equivalence.

## 16. Equivalence results

Analytical equivalence is covered for the exact coupled update, including
synaptic decay and the membrane response. Deterministic regression coverage
also verifies threshold/reset, delayed writes, refractory writes, and signed
event accumulation. A live Brian2 equivalence suite was not run because no
compatible Brian2 import was obtained under the current Python 3.12
environment.

## 17. Synthetic test matrix

`tests/test_task005.py` contains 24 fast offline tests covering:

- rest, exact state update, exponential `g`, positive/negative input, and
  threshold/reset;
- refractory blocking, refractory-free targets, incoming refractory writes,
  exact delay, self-edges, excitatory/inhibitory weights, and chains;
- multiple and simultaneous deterministic events, duplicate-time semantics,
  unresolved-edge exclusion, and unchanged anatomy;
- explicit schedule validation, invalid IDs/grid times, seeded Poisson
  reproducibility/scaling, and invalid high-rate input;
- compact result metadata, parameter/projection identity sensitivity,
  deterministic simulation fingerprints and spike-result digests, and the
  explicit small-subset trace boundary.

## 18. Real MaleCNS smoke test

The local official v1.0 Feather files were loaded and projected onto the
166,700 publication-curated neuron IDs. Both the full curated graph and the
`min_synapses=5` projection used `Shiu2024SignPolicy` and the explicit
consensus-first resolution policy. A single curated source (`10001`) received
one deterministic 10 mV direct pulse at 0 ms for 3 ms. This is a bounded
engineering stimulus and is not a biological interpretation.

## 19. Performance measurements

The first fresh-process pass measured:

| Substrate | Effective edges | Included anatomical weight | Unresolved edges | Projection time | Simulation time |
| --- | ---: | ---: | ---: | ---: | ---: |
| full curated | 24,904,953 | 121,444,188 | 677,985 | 30.24 s | 0.13 s |
| `>=5` | 6,113,545 | 88,022,553 | 128,573 | 9.91 s | 0.12 s |

The full raw load plus curation completed in 247.61 s in that process. The
Windows process working set observed during large-table loading was about
20-24 GB; this is dominated by raw ingestion/aggregation and not a claim that
the short dynamics loop requires that amount after setup. The first pass
reported one spike, one active neuron, and respectively 313 and 64 queued and
delivered resolved synaptic events.

## 20. Deterministic fingerprints and second pass

The second fresh-process real-data pass prepared the same 166,700-neuron,
25,582,938-edge curated substrate in 258.10 s and ran each smoke configuration
twice. Both runs had equal configuration fingerprints and equal spike digests:

| Substrate | Simulation fingerprint | Spike-result digest | Runs |
| --- | --- | --- | --- |
| full curated | `85b58f0473f1e8c1a3f65a0ce3e6d3ef5c971d323de00f406d250e73b42d1b62` | `7403850e33d601f0db00a731690cde3242cece62d2f6bac20c4841b19de176ed` | 2 equal |
| `>=5` | `db859a6758fdc152b08a3ff91e3a63f018877f5efb43b7c45234529df39e65d9` | `7403850e33d601f0db00a731690cde3242cece62d2f6bac20c4841b19de176ed` | 2 equal |

The equal spike digest is expected here because the one stimulated source
spiked once and no downstream target crossed threshold during 3 ms; the graph
and threshold still change the configuration and event-count metadata.

## 21. Known deviations from the original FlyWire/Shiu model

- MaleCNS v1.0 is not the exact FlyWire v630 network used by Shiu et al.
- MaleCNS simulation edges are curated neuron-level projections and exclude
  unresolved Task 004 signs instead of silently assigning them.
- MaleCNS-Sim explicitly fixes `dt=0.1 ms`; the original code relies on Brian’s
  default clock.
- The deterministic direct stimulus and seeded NumPy Poisson generator are
  reproducibility interfaces, not Brian2 input/RNG stream reproduction.
- The reference engine is an independent NumPy implementation rather than a
  Brian2 runtime dependency.
- Silencing follows executable companion-code outgoing-only behavior even
  though the companion README uses broader “to and from” wording.

## 22. Scientific limitations and explicit nonclaims

MaleCNS-Sim uses MaleCNS v1.0, not the exact FlyWire v630 network. Task 004
signs are modelling policies, not complete receptor-level functional truth.
The 0.275 mV anatomical-synapse multiplier is a Shiu model parameter, not a
measured universal synaptic efficacy. Neurons are single-compartment point
models; morphology is ignored. Receptor identity, co-transmission, gap
junctions, neuropeptide/modulatory dynamics, and plasticity are not modelled.
Poisson input is an experimental modelling device. Successful numerical
reproduction of this reference engine does not imply biological equivalence,
sensorimotor prediction, or feeding behavior.

## Files changed

- `src/malecns_sim/dynamics/__init__.py`
- `src/malecns_sim/dynamics/lif.py`
- `src/malecns_sim/dynamics/stimulus.py`
- `tests/test_task005.py`
- `README.md`
- this plan

## Validation record

At the Task 005 start, `master` was clean at `394ba20` and the Task 004 suite
reported 50 passed. The Task 005 synthetic suite reported 24 passed. Final
compile, full-suite, hygiene, and status commands are recorded in the handoff
report after they run.

## Recommended next task

Task 006 - Reproduce a Known Sensorimotor Experiment.
