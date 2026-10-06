"""Frozen EQ-B certification using common, bounded synthetic fixtures."""

from dataclasses import asdict, fields, replace
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from malecns_sim.dynamics.lif import PreparedRuntime, REFERENCE_LIF_PARAMETERS
from malecns_sim.dynamics.cuda import GPUPreparedRuntime
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule
from test_application_a019s import CASES, FIELDS, events, projection, snapshot

TOL = 2e-13
RECORDS = []


def cpu_snapshot(state):
    return {name: getattr(state, name).copy() for name in FIELDS}


def compare_array(reference, subject):
    assert reference.shape == subject.shape
    assert reference.dtype == subject.dtype
    exact = reference.tobytes() == subject.tobytes()
    if reference.dtype.kind == "f":
        finite = bool(np.all(np.isfinite(reference)) and np.all(np.isfinite(subject)))
        error = np.abs(subject - reference)
        nonzero = reference != 0
        relative = error[nonzero] / np.abs(reference[nonzero])
        record = dict(elements=reference.size, byte_exact=exact, finite=finite,
                      shape=list(reference.shape), dtype=str(reference.dtype),
                      max_abs=float(error.max(initial=0)),
                      max_relative=float(relative.max(initial=0)),
                      relative_elements=int(nonzero.sum()),
                      pass_eq_b=finite and bool(np.all(np.isclose(
                          subject, reference, rtol=TOL, atol=TOL, equal_nan=False))))
        assert record["pass_eq_b"], record
        return record
    mismatches = int(np.count_nonzero(reference != subject))
    assert mismatches == 0
    return dict(elements=reference.size, byte_exact=exact, mismatches=mismatches,
                shape=list(reference.shape), dtype=str(reference.dtype))


def compare_state(cpu, gpu):
    assert cpu.timestep == gpu.timestep
    left, right = cpu_snapshot(cpu), snapshot(gpu)
    return dict(timestep=cpu.timestep, ring_cursor=cpu.timestep % cpu.pending.shape[0],
                pending_nonempty=bool(np.any(left["pending_event_counts"])),
                pending_counts=left["pending_event_counts"].tolist(),
                refractory_deadlines=left["refractory_until"].tolist(),
                exact_discrete_mismatches=0,
                fields={name: compare_array(left[name], right[name]) for name in FIELDS})


def compare_result(cpu, gpu):
    record = {}
    for field in fields(cpu):
        left, right = getattr(cpu, field.name), getattr(gpu, field.name)
        if isinstance(left, np.ndarray):
            record[field.name] = compare_array(left, right)
        else:
            assert left == right, (field.name, left, right)
            record[field.name] = left
    return record


def trajectory(case):
    name, edges, entries, weight, free, chunks, parameters = case
    p = projection(edges)
    parameters = parameters or REFERENCE_LIF_PARAMETERS
    cpu, gpu = PreparedRuntime(p, parameters), GPUPreparedRuntime(p, parameters)
    a, b = cpu.initial_state(), gpu.initial_state()
    fixture = dict(name=name, edges=edges, entries=entries, weight=weight,
                   refractory_free=free, chunks=chunks, dt_ms=0.1,
                   parameters=asdict(parameters), initial="rest/zero/-1/zero/zero",
                   projection_digest=p.fingerprint)
    fixture["digest"] = hashlib.sha256(json.dumps(fixture, sort_keys=True).encode()).hexdigest()
    boundaries, repeats, offset = [], [], 0
    try:
        initial = compare_state(a, b)
        for chunk in chunks:
            stimulus = events(entries, weight, free, offset, offset + chunk)
            args = dict(duration_ms=chunk * 0.1, stimulus=stimulus,
                        trace_neuron_ids=(1, 2, 3, 4))
            left, right = cpu.advance(a, **args), gpu.advance(b, **args)
            boundary = compare_state(a, b)
            boundary.update(start_step=offset, end_step=offset + chunk,
                            stimulus_digest=stimulus.fingerprint,
                            output=compare_result(left, right))
            before = snapshot(b)
            # Materialized readback and repeated snapshot must not mutate state.
            _ = right.spike_times_ms, right.trace_v_mV.tobytes(), right.spike_result_digest
            after = snapshot(b)
            assert all(before[f].tobytes() == after[f].tobytes() for f in FIELDS)
            repeats.append((after, right))
            boundaries.append(boundary)
            offset += chunk
        if name in ("S3-delayed", "S4-pending"):
            first = boundaries[0]
            assert first["output"]["delivered_synaptic_event_count"] == 0
            assert repeats[0][0]["pending_event_counts"][0, 1] == 1
            assert repeats[0][0]["pending"][0, 1] == 0.275
            if name == "S3-delayed":
                assert boundaries[1]["output"]["delivered_synaptic_event_count"] == 1
                assert boundaries[1]["output"]["trace_g_mV"]["pass_eq_b"]
        if name == "S5-refractory":
            assert repeats[0][0]["refractory_until"][0] == 23
            assert np.concatenate([r.spike_timesteps for _, r in repeats]).tolist() == [1, 25]
        if name == "S9-output-S12-duplicates":
            assert repeats[0][0]["pending_event_counts"][0, 2] == 3
            assert repeats[0][0]["pending"][0, 2] == 0
        if name == "zero-delay":
            assert repeats[0][0]["pending_event_counts"][0, 1] == 1
            assert boundaries[1]["output"]["delivered_synaptic_event_count"] == 1
        return dict(fixture=fixture, initial=initial, boundaries=boundaries, result="PASS"), repeats
    finally:
        b.close()
        gpu.close()


@pytest.mark.parametrize("case", CASES, ids=[case[0] for case in CASES])
def test_common_trajectory(case):
    record, first = trajectory(case)
    if case[0] in ("S3-delayed", "S5-refractory", "S7-repeated"):
        second_record, second = trajectory(case)
        for (left, result_left), (right, result_right) in zip(first, second):
            assert all(left[f].tobytes() == right[f].tobytes() for f in FIELDS)
            for field in fields(result_left):
                a, b = getattr(result_left, field.name), getattr(result_right, field.name)
                assert a.tobytes() == b.tobytes() if isinstance(a, np.ndarray) else a == b
        record["determinism"] = "two fresh GPU runs: all state/output bytes exact"
    RECORDS.append(record)


def test_C6_C8_C10():
    p = projection(((0, 1, 0.275),))
    cpu, gpu = PreparedRuntime(p), GPUPreparedRuntime(p)
    a, b = cpu.initial_state(), cpu.initial_state()
    x, y = gpu.initial_state(), gpu.initial_state()
    pristine_cpu, pristine_gpu = cpu_snapshot(b), snapshot(y)
    record = dict(name="C6-C8-C10", boundaries=[],
                  fixture=dict(edges=((0, 1, 0.275),), projection_digest=p.fingerprint,
                               dt_ms=0.1, parameters=asdict(REFERENCE_LIF_PARAMETERS),
                               initial="rest/zero/-1/zero/zero", chunks=(10, 5, 20),
                               A_events=((1, 0),), B_events=((2, 0),), weight=10.))
    try:
        for field in FIELDS:
            assert not np.shares_memory(getattr(a, field), getattr(b, field))
            assert getattr(x, field).data.ptr != getattr(y, field).data.ptr
        args = dict(duration_ms=1.0, stimulus=events(((1, 0),)), trace_neuron_ids=(1, 2))
        compare_result(cpu.advance(a, **args), gpu.advance(x, **args))
        record["boundaries"].append(compare_state(a, x))
        assert all(pristine_cpu[f].tobytes() == cpu_snapshot(b)[f].tobytes() for f in FIELDS)
        assert all(pristine_gpu[f].tobytes() == snapshot(y)[f].tobytes() for f in FIELDS)
        args["stimulus"] = events(((2, 0),))
        compare_result(cpu.advance(b, **args), gpu.advance(y, **args))
        record["boundaries"].append(compare_state(b, y))
        # Independent same-runtime states reproduce both differing trajectories.
        for stimulus, expected_cpu, expected_gpu in (
                (events(((1, 0),)), a, x), (events(((2, 0),)), b, y)):
            c, z = cpu.initial_state(), gpu.initial_state()
            args["stimulus"] = stimulus
            compare_result(cpu.advance(c, **args), gpu.advance(z, **args))
            assert all(cpu_snapshot(c)[f].tobytes() == cpu_snapshot(expected_cpu)[f].tobytes() for f in FIELDS)
            assert all(snapshot(z)[f].tobytes() == snapshot(expected_gpu)[f].tobytes() for f in FIELDS)
            z.close()
        del a
        x.close()
        x.close()
        for steps in (5, 20):
            args.update(duration_ms=steps * 0.1, stimulus=events())
            compare_result(cpu.advance(b, **args), gpu.advance(y, **args))
            record["boundaries"].append(compare_state(b, y))
        record.update(result="PASS", isolation="PASS", release_continue="PASS")
        RECORDS.append(record)
    finally:
        x.close()
        y.close()
        gpu.close()


ADMISSIONS = [
    ("zero", lambda: events()), ("one", lambda: events(((1, 0),))),
    ("duplicate-timestamps-ids", lambda: events(((2, 0), (1, 0), (1, 0)))),
    ("duplicate-within-schedule", lambda: ExplicitStimulus((SpikeSchedule(1, (0., 0.)),))),
    ("last-grid", lambda: events(((1, 9),))),
    ("endpoint", lambda: events(((1, 10),))),
    ("just-before", lambda: ExplicitStimulus((SpikeSchedule(1, (np.nextafter(1., 0.),)),))),
    ("negative", lambda: ExplicitStimulus((SpikeSchedule(1, (-0.1,)),))),
    ("outside", lambda: events(((1, 11),))),
    ("unknown-id", lambda: events(((99, 0),))),
    ("off-grid", lambda: ExplicitStimulus((SpikeSchedule(1, (0.05,)),))),
    ("nan", lambda: ExplicitStimulus((SpikeSchedule(1, (float('nan'),)),))),
    ("inf", lambda: ExplicitStimulus((SpikeSchedule(1, (float('inf'),)),))),
    ("malformed-schedule", lambda: ExplicitStimulus(([],))),
    ("boolean-id", lambda: ExplicitStimulus((SpikeSchedule(True, (0.,)),))),
    ("malformed-times-shape", lambda: ExplicitStimulus((SpikeSchedule(1, ((0., 0.),)),))),
    ("wrong-public-type", lambda: []),
    ("zero-duration", lambda: events()),
    ("off-grid-duration", lambda: events()),
]


@pytest.mark.parametrize("name,factory", ADMISSIONS, ids=[c[0] for c in ADMISSIONS])
def test_admission(name, factory):
    cpu, gpu = PreparedRuntime(projection()), GPUPreparedRuntime(projection())
    a, b = cpu.initial_state(), gpu.initial_state()
    before_cpu, before_gpu = cpu_snapshot(a), snapshot(b)
    outcomes, results = [], []
    try:
        for runtime, state in ((cpu, a), (gpu, b)):
            try:
                stimulus = factory()
                duration = {"zero-duration": 0., "off-grid-duration": 0.15}.get(name, 1.)
                result = runtime.advance(state, duration_ms=duration, stimulus=stimulus,
                                         trace_neuron_ids=(1, 2, 3, 4))
                outcomes.append("accept")
                results.append(result)
            except (ValueError, TypeError, KeyError) as exc:
                outcomes.append(type(exc).__name__)
        assert outcomes[0] == outcomes[1]
        record = dict(name="admission-" + name, outcome=outcomes[0], result="PASS")
        if outcomes[0] == "accept":
            record["output"] = compare_result(*results)
            record["state"] = compare_state(a, b)
        else:
            assert a.timestep == b.timestep == 0
            assert b.status == "ready"
            assert all(before_cpu[f].tobytes() == cpu_snapshot(a)[f].tobytes() for f in FIELDS)
            assert all(before_gpu[f].tobytes() == snapshot(b)[f].tobytes() for f in FIELDS)
            record["rejection_no_mutation"] = True
        RECORDS.append(record)
    finally:
        b.close()
        gpu.close()


def test_ring_maximum_slot_and_wrap():
    parameters = replace(REFERENCE_LIF_PARAMETERS, synaptic_delay_ms=0.3)
    case = ("ring-wrap-multiplicity", ((0, 2, 0.275), (0, 2, -0.1), (1, 2, 0.2)),
            ((1, 2), (2, 2), (1, 6), (2, 6)), 10., (1, 2), (3, 1, 3, 1, 4), parameters)
    record, snapshots = trajectory(case)
    assert snapshots[0][0]["pending_event_counts"][2, 2] == 3
    assert record["boundaries"][0]["output"]["delivered_synaptic_event_count"] == 0
    assert record["boundaries"][2]["output"]["delivered_synaptic_event_count"] == 3
    assert record["boundaries"][4]["output"]["delivered_synaptic_event_count"] == 3
    RECORDS.append(record)


@pytest.fixture(scope="session", autouse=True)
def write_evidence():
    yield
    target = os.environ.get("MALECNS_A019T_RECORDS")
    if target:
        Path(target).write_text(json.dumps(RECORDS, indent=2, allow_nan=False) + "\n", encoding="utf-8")
