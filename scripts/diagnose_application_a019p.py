"""Guarded, synthetic-only gather feasibility prototypes; no production edits."""
import inspect
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns

import validation_firewall as guard

if not guard.ACTIVE:
    raise RuntimeError("active source firewall required before workload imports")

import numpy as np
from malecns_sim.dynamics import lif
import benchmark_application_a019g as graph

START = "98e1854c10bfb42442bb198e110d5ccce9fb7f68"
MODES = ("compress", "take", "scratch_v")


def gather(mode, v, g, mask, buffers, scratch):
    """Exact ascending selection, with bounded private destination ownership."""
    if mode == "compress":
        k = int(np.count_nonzero(mask))
        a, b = (x[:k] for x in buffers)
        np.compress(mask, v, out=a)
        np.compress(mask, g, out=b)
    else:
        indices = np.flatnonzero(mask)
        k = indices.size
        a = scratch[0][:k] if mode == "scratch_v" else buffers[0][:k]
        np.take(v, indices, out=a, mode="clip")
        if mode == "scratch_v":
            b = g[mask]
        else:
            b = buffers[1][:k]
            np.take(g, indices, out=b, mode="clip")
    return a, b


def prototype(mode, observations, owned=None):
    """Compile an isolated source clone; preserve all downstream statements."""
    text = inspect.getsource(lif.simulate_lif)
    allocation = "    membrane_scratch = (np.empty(n, dtype=np.float64), np.empty(n, dtype=np.float64))"
    expression = "            input_v, input_g = v[allowed], g[allowed]"
    assert text.count(allocation) == text.count(expression) == 1
    if mode != "scratch_v":
        text = text.replace(allocation, allocation + "\n    gather_buffers = (np.empty(n), np.empty(n))")
    else:
        text = text.replace(allocation, allocation + "\n    gather_buffers = ()")
    text = text.replace(expression, "            observe(allowed, step, membrane_scratch, v, g)\n"
                        "            input_v, input_g = gather(mode, v, g, allowed, gather_buffers, membrane_scratch)")
    def observe(mask, step, scratch, v, g):
        assert not np.shares_memory(*scratch)
        assert all(not np.shares_memory(a, b) for a in scratch for b in (v, g))
        observations.append((step, int(np.count_nonzero(mask)), id(scratch[0])))
        if owned is not None and not any(scratch is x for x in owned):
            owned.append(scratch)
    namespace = dict(lif.__dict__, gather=gather, mode=mode, observe=observe)
    exec(compile(text, "<a019p-test-only-source-clone>", "exec"), namespace)
    return namespace["simulate_lif"]


def selection_probes():
    bits = np.array([0, 0x8000000000000000, 0x7ff8000000000001,
                     0x7ff8000000001234, 0xfff8000000000042,
                     0x7ff0000000000001, 0x7ff0000000000000,
                     0xfff0000000000000, 1, 0x3ff0000000000000,
                     0x3ff0000000000000, 0x8000000000000001], dtype=np.uint64)
    v, g = bits.view(np.float64), bits[::-1].copy().view(np.float64)
    n = v.size
    masks = {"empty": np.zeros(n, bool), "one": np.arange(n) == 3,
             "sparse": np.arange(n) % 5 == 0, "mixed": np.arange(n) % 3 != 0,
             "alternating": np.arange(n) % 2 == 0, "full": np.ones(n, bool)}
    rows = []
    for mode in MODES:
        buffers = (np.empty(n), np.empty(n))
        scratch = (np.empty(n), np.empty(n))
        for label, mask in masks.items():
            expected = v[mask], g[mask]
            assert all(x.flags.owndata and x.base is None for x in expected)
            assert all(not np.shares_memory(x, y) for x in expected for y in (v, g))
            actual = gather(mode, v, g, mask, buffers, scratch)
            for x, y in zip(expected, actual):
                graph.base.exact(x, y)
            # Arithmetic may quiet signaling NaNs; compare its exact output bytes.
            with np.errstate(all="ignore"):
                reference = lif.linear_state_update(*expected, _scratch=(np.empty(n), np.empty(n)))
                result = lif.linear_state_update(*actual, _scratch=scratch)
            for x, y in zip(reference, result):
                graph.base.exact(x, y)
            left, right = (v.copy(), g.copy()), (v.copy(), g.copy())
            for state, update in ((left, reference), (right, result)):
                state[0][mask], state[1][mask] = update
            for x, y in zip(left, right):
                graph.base.exact(x, y)
            rows.append(dict(mode=mode, selection=label, k=int(mask.sum()), exact_bytes=True))
    # Both buffers as inputs corrupt g before the final decay reads it.
    scratch = (np.arange(n, dtype=float), np.arange(n, dtype=float) + 1)
    expected = lif.linear_state_update(scratch[0].copy(), scratch[1].copy())
    actual = lif.linear_state_update(*scratch, _scratch=scratch)
    assert expected[1].tobytes() != actual[1].tobytes()
    return dict(rows=rows, both_scratch_reuse="REJECT: original g overwritten before decay")


def replay():
    rows = []
    original = lif.simulate_lif
    for mode in MODES:
        observations = []
        owned = []
        clone = prototype(mode, observations, owned)
        runtime, stimulus, _ = graph.synthetic_case(128, 8, 12)
        left, right, fresh = (runtime.initial_state() for _ in range(3))
        left.refractory_until[::3] = right.refractory_until[::3] = 7
        left.g_mV[::5] = right.g_mV[::5] = .25
        retained = []
        for chunk in range(3):
            expected = runtime.advance(left, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1, 2))
            try:
                lif.simulate_lif = clone
                actual = runtime.advance(right, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1, 2))
            finally:
                lif.simulate_lif = original
            graph.base.exact(expected, actual)
            graph.base.exact(left, right)
            retained.append(actual)
        assert fresh.timestep == 0 and not fresh.pending.any()
        assert all(not np.shares_memory(getattr(a, name), getattr(b, name))
                   for a, b in ((left, right), (right, fresh)) for name in graph.base.STATE_ARRAYS)
        # Retain scratch references for this test so allocator address reuse
        # cannot be mistaken for cross-advance ownership sharing.
        try:
            lif.simulate_lif = clone
            runtime.advance(fresh, duration_ms=1, stimulus=lif.ExplicitStimulus(()))
            empty = runtime.initial_state()
            empty.refractory_until.fill(100)
            before = len(observations)
            runtime.advance(empty, duration_ms=1, stimulus=lif.ExplicitStimulus(()))
            assert len(observations) == before
        finally:
            lif.simulate_lif = original
        assert len(owned) == 4
        assert all(not np.shares_memory(a, b) for i, x in enumerate(owned)
                   for y in owned[i + 1:] for a in x for b in y)
        rows.append(dict(mode=mode, chunks=3, replay="exact all state/result fields and bytes",
                         observed_k=sorted({k for _, k, _ in observations}), cross_state_isolated=True,
                         scratch_owners_disjoint=True, empty_branch_skips=True))
    return rows


def structural():
    rows = []
    original = lif.linear_state_update
    for label, n, degree, count in graph.CASES[:3]:
        runtime, stimulus, _ = graph.synthetic_case(n, degree, count)
        ks = []
        def observed(v, g, **kwargs):
            ks.append(v.size)
            assert v.flags.owndata and g.flags.owndata
            return original(v, g, **kwargs)
        try:
            lif.linear_state_update = observed
            state = runtime.initial_state()
            runtime.advance(state, duration_ms=20, stimulus=stimulus)
        finally:
            lif.linear_state_update = original
        scenarios = []
        for name, k in (("empty", 0), ("sparse", 1), ("mixed", n // 2), ("dense", n - 1), ("full", n)):
            refractory = np.full(n, 1, dtype=np.int64)
            refractory[:k] = -1
            mask = (0 > refractory) | np.zeros(n, bool)
            assert np.count_nonzero(mask) == k
            scenarios.append(dict(selection=name, k=k, density=k/n, each_bytes=8*k,
                                  total_bytes=16*k, result_arrays=2 if k else 0, mask_bytes=n,
                                  empty_branch_skips_gathers=k == 0))
        rows.append(dict(case=label, n=n, observed_k_min=min(ks), observed_k_max=max(ks),
                         observed_k_counts={str(k): ks.count(k) for k in sorted(set(ks))},
                         observed_total_payload_bytes=sum(16*k for k in ks), scenarios=scenarios))
    return rows


def timing(repeats=15, loops=100):
    rows = []
    for n in (4096, 32768):
        v, g = np.arange(n, dtype=float), np.arange(n, dtype=float) * .25
        for density in ("sparse", "mixed", "dense", "full"):
            mask = np.arange(n) % 100 == 0 if density == "sparse" else np.arange(n) % 3 != 0
            if density == "dense":
                mask = np.arange(n) % 100 != 0
            if density == "full":
                mask = np.ones(n, bool)
            buffers, scratch = (np.empty(n), np.empty(n)), (np.empty(n), np.empty(n))
            indices = np.flatnonzero(mask)
            def baseline():
                return v[mask], g[mask]
            operations = {"baseline": baseline, "count": lambda: np.count_nonzero(mask),
                          "indices": lambda: np.flatnonzero(mask),
                          "take_write": lambda: (np.take(v, indices, out=buffers[0][:indices.size], mode="clip"),
                                                  np.take(g, indices, out=buffers[1][:indices.size], mode="clip"))}
            for mode in MODES:
                operations[mode] = lambda mode=mode: gather(mode, v, g, mask, buffers, scratch)
            raw = []
            for repeat in range(repeats + 3):
                pair = {}
                names = list(operations)
                if repeat % 2:
                    names.reverse()
                for name in names:
                    started = perf_counter_ns()
                    for _ in range(loops):
                        operations[name]()
                    pair[name] = (perf_counter_ns() - started) / loops
                if repeat >= 3:
                    raw.append(pair)
            rows.append(dict(n=n, selection=density, k=indices.size, raw_ns=raw,
                             median_ns={name: median(p[name] for p in raw) for name in operations}))
    return dict(repeats=repeats, warmups=3, loops=loops, cases=rows,
                qualifier="Source-local rejection/choice evidence only; no production speedup claim; allocation setup excluded")


def firewall():
    categories = ("mapping", "provenance", "neurotransmitter", "annotation", "connectome", "neuron_metadata", "other")
    for name in categories:
        try:
            open(guard.ROOT / "data" / ("a019p-blocked-" + name), "rb")
        except guard.SourceAccessDenied:
            pass
        else:
            raise AssertionError("registered source guard failed")
    return dict(active=guard.ACTIVE, blocked_probes=7, accepted_registered_reads={
        "REAL_" + name: 0 for name in ("MAPPING", "PROVENANCE", "NEUROTRANSMITTER", "ANNOTATION",
                                      "CONNECTIVITY", "NEURON_METADATA", "OTHER_REGISTERED_DATA")})


def masked_alternative():
    """Reject eager full-array work by an observable masked-out exception."""
    v = np.array([0., np.inf])
    g = np.array([1., -np.inf])
    mask = np.array([True, False])
    with np.errstate(all="raise"):
        lif.linear_state_update(v[mask], g[mask])
        try:
            lif.linear_state_update(v, g)
        except FloatingPointError:
            pass
        else:
            raise AssertionError("expected masked-out invalid arithmetic")
    return dict(eager="REJECT: masked-out infinity causes new FloatingPointError",
                where_ufunc="Not selected: six full-length masked traversals versus six compact K traversals; new arithmetic/writeback contract",
                risk="HIGH", production_prototype=False)


def assessment():
    names = ("measured_relevance", "allocation_reduction", "extra_mask_index_work", "specificity",
             "exact_confidence", "alias_lifetime_confidence", "validation_burden", "implementation_risk",
             "local_cost", "o1_readiness")
    scores = {
        "A_compress": ("HIGH", "LOW", "HIGH", "CONCRETE", "HIGH", "HIGH", "HIGH", "MEDIUM", "UNFAVORABLE", "NOT_READY"),
        "B_shared_indices_take_clip": ("HIGH", "HIGH", "MEDIUM", "CONCRETE", "HIGH", "HIGH", "HIGH", "MEDIUM", "UNFAVORABLE", "NOT_READY"),
        "C_voltage_scratch_only": ("HIGH", "MEDIUM", "MEDIUM", "CONCRETE", "HIGH", "HIGH", "HIGH", "MEDIUM", "UNFAVORABLE", "NOT_READY"),
        "C_both_scratch": ("HIGH", "HIGH", "MEDIUM", "CONCRETE", "LOW", "LOW", "HIGH", "HIGH", "UNCLEAR", "NOT_READY"),
        "D_eager_full_array": ("HIGH", "HIGH", "HIGH", "CONCRETE", "LOW", "MEDIUM", "HIGH", "HIGH", "UNFAVORABLE", "NOT_READY"),
        "D_where_ufunc": ("HIGH", "HIGH", "HIGH", "PARTIAL", "LOW", "MEDIUM", "HIGH", "HIGH", "UNCLEAR", "NOT_READY")}
    return dict(classification="A019P-C", second_o1_target_ready=False,
                next_task="A019Q — evidence-only decision on ending the current CPU O1 line versus beginning GPU equivalence/certification work",
                scorecard={key: dict(zip(names, values)) for key, values in scores.items()},
                mask_expression="(step > refractory_until) | refractory_free_mask", mask_lifetime="M5: M4 dynamics plus per-advance static refractory-free override",
                gather_expressions=["v[allowed]", "g[allowed]"],
                k_today="Not explicitly known; Boolean indexing derives output shape internally. np.any supplies only nonemptiness.",
                k_candidate="A: count_nonzero full pass; B/C: newly allocated flatnonzero np.intp[K], size supplies K",
                memory=dict(persistent_bytes=0, baseline_per_call_float_payload="16*K",
                            A=dict(extra_advance_bytes="16*N", per_call="two internal 8*K index payloads and two buffered 8*K float payloads, sequential"),
                            B=dict(extra_advance_bytes="16*N", per_call="8*K np.intp indices; no new float result payload under checked clip out contract"),
                            C=dict(extra_advance_bytes=0, per_call="8*K indices + 8*K Boolean g result; v uses existing scratch[0]")),
                main_uncertainty="Sparse G3 take locally favorable; no production/full-real speed inference. Not competitive on the current dense G1/G2/G3 target.",
                native_allocation_telemetry=False,
                api_sources=["https://numpy.org/doc/stable/reference/generated/numpy.take.html",
                             "https://numpy.org/doc/stable/reference/generated/numpy.compress.html",
                             "https://raw.githubusercontent.com/numpy/numpy/v2.5.3/numpy/_core/src/multiarray/item_selection.c"])


def run():
    return dict(schema="a019p-input-gather-feasibility-v1", authorization="授權 A019P",
                starting_sha=START, numpy=np.__version__, production_optimization=False,
                firewall=firewall(), selection=selection_probes(), replay=replay(),
                structural=structural(), timing=timing(), full_array=masked_alternative(), assessment=assessment(),
                zero_execution={name: 0 for name in ("full_real_preparations", "real_advances", "reruns_a019d_a019l",
                    "gpu_runs", "arena_runs", "interventions", "downloads", "archive_writes")},
                accounting="fail-closed guarded accounting, not independent native byte telemetry")


if __name__ == "__main__":
    Path("docs/plans/a019p-input-gather-feasibility-evidence.json").write_text(
        json.dumps(run(), indent=2) + "\n", encoding="utf-8")
