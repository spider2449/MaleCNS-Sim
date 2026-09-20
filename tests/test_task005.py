import numpy as np
import pytest

from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence,
    NeurotransmitterResolutionPolicy,
)
from malecns_sim.dynamics import (
    EffectiveSignedProjection,
    ExplicitStimulus,
    LIFParameters,
    PoissonStimulus,
    SpikeSchedule,
    linear_state_update,
    simulate_lif,
)
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import ConservativeSignPolicy, Shiu2024SignPolicy


def _signed(edges, labels=None, policy=None):
    labels = labels or {1: "acetylcholine", 2: "gaba", 3: "acetylcholine", 4: "gaba"}
    ids = np.arange(1, max(labels) + 1, dtype=np.int64)
    source = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    target = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    counts = np.asarray([edge[2] for edge in edges], dtype=np.int64)
    connectome = NumericNormalizedConnectome(ids, source, target, counts)
    projection = CuratedNeuronProjection(connectome, len(edges), len(edges), len(edges), 0)
    evidence = [NeurotransmitterEvidence(neuron_id=i, consensus_nt=labels.get(i)) for i in ids]
    return SignedAnatomicalConnectome.from_projection(
        projection,
        evidence,
        NeurotransmitterResolutionPolicy(),
        policy or Shiu2024SignPolicy(),
    )


def _projection(edges=((1, 2, 1), (1, 3, 1), (2, 3, 1))):
    return EffectiveSignedProjection.from_signed_connectome(_signed(edges))


def test_reference_parameters_are_explicit_and_grid_is_exact():
    params = LIFParameters()
    assert (params.v_rest_mV, params.v_reset_mV, params.v_threshold_mV) == (-52.0, -52.0, -45.0)
    assert (params.tau_membrane_ms, params.tau_synapse_ms) == (20.0, 5.0)
    assert (params.refractory_period_ms, params.synaptic_delay_ms) == (2.2, 1.8)
    assert params.synaptic_weight_per_anatomical_synapse_mV == 0.275
    assert params.grid_steps(0.1) == (18, 22)
    with pytest.raises(ValueError, match="not exactly representable"):
        params.grid_steps(0.07)


def test_linear_update_matches_analytical_solution():
    params = LIFParameters()
    dt = 0.1
    v, g = -50.0, 4.0
    actual_v, actual_g = linear_state_update(v, g, parameters=params, dt_ms=dt)
    em = np.exp(-dt / params.tau_membrane_ms)
    es = np.exp(-dt / params.tau_synapse_ms)
    coefficient = (es - em) / (1.0 - params.tau_membrane_ms / params.tau_synapse_ms)
    assert actual_g == pytest.approx(g * es, rel=1e-14, abs=1e-14)
    assert actual_v == pytest.approx(params.v_rest_mV + (v - params.v_rest_mV) * em + g * coefficient, rel=1e-14, abs=1e-14)


def test_resting_neuron_and_synaptic_decay():
    projection = _projection(edges=())
    result = simulate_lif(projection, duration_ms=1.0, trace_neuron_ids=(1,))
    assert result.emitted_spike_count == 0
    assert np.all(result.trace_v_mV == -52.0)
    v, g = linear_state_update(-52.0, 1.0)
    assert v < -52.0 + 0.01
    assert g == pytest.approx(np.exp(-0.1 / 5.0))


def test_positive_and_negative_direct_impulses_have_expected_polarity():
    projection = _projection(edges=())
    positive = simulate_lif(
        projection,
        duration_ms=0.2,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=1.0),
        trace_neuron_ids=(1,),
    )
    negative = simulate_lif(
        projection,
        duration_ms=0.2,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=-1.0),
        trace_neuron_ids=(1,),
    )
    assert positive.trace_v_mV[0, 1] > -52.0
    assert negative.trace_v_mV[0, 1] < -52.0


def test_threshold_reset_and_g_reset():
    projection = _projection(edges=())
    result = simulate_lif(
        projection,
        duration_ms=0.2,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0),
        trace_neuron_ids=(1,),
    )
    assert result.spike_neuron_ids.tolist() == [1]
    assert result.spike_timesteps.tolist() == [1]
    assert result.trace_v_mV[0, 1] == -52.0
    assert result.trace_g_mV[0, 1] == 0.0


def test_refractory_blocks_input_until_strictly_after_2_2_ms():
    projection = _projection(edges=())
    result = simulate_lif(
        projection,
        duration_ms=2.5,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2, 2.3, 2.4)),), weight_mV=10.0),
    )
    assert result.spike_timesteps.tolist() == [1, 25]


def test_incoming_event_during_refractory_is_ignored_and_poisson_targets_can_opt_out():
    projection = _projection(edges=())
    blocked = simulate_lif(
        projection,
        duration_ms=0.4,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2)),), weight_mV=10.0),
    )
    free = simulate_lif(
        projection,
        duration_ms=0.4,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2)),), weight_mV=10.0, refractory_free_neuron_ids=(1,)),
    )
    assert blocked.emitted_spike_count == 1
    assert free.emitted_spike_count == 2


def test_exact_delay_and_signed_sparse_propagation():
    projection = _projection(edges=((1, 2, 1),))
    result = simulate_lif(
        projection,
        duration_ms=2.1,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0),
        trace_neuron_ids=(2,),
    )
    assert result.spike_timesteps.tolist() == [1]
    assert result.trace_g_mV[0, 19] == 0.0
    assert result.trace_g_mV[0, 20] > 0.0
    assert result.queued_synaptic_event_count == 1
    assert result.delivered_synaptic_event_count == 1


def test_self_edge_and_two_neuron_inhibitory_edge_are_supported():
    self_projection = _projection(edges=((1, 1, 1),))
    self_result = simulate_lif(
        self_projection,
        duration_ms=2.1,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0),
    )
    assert self_result.emitted_spike_count == 1
    inhibitory = _projection(edges=((2, 1, 4),))
    result = simulate_lif(
        inhibitory,
        duration_ms=2.1,
        stimulus=ExplicitStimulus((SpikeSchedule(2, (0.0,)),), weight_mV=10.0),
        trace_neuron_ids=(1,),
    )
    assert result.trace_g_mV[0, 20] < 0.0


def test_multiple_and_simultaneous_events_sum_deterministically():
    projection = _projection(edges=())
    stimulus = ExplicitStimulus(
        (SpikeSchedule(1, (0.0, 0.0)), SpikeSchedule(2, (0.0,))), weight_mV=1.0
    )
    first = simulate_lif(projection, duration_ms=0.2, stimulus=stimulus, trace_neuron_ids=(1, 2))
    second = simulate_lif(projection, duration_ms=0.2, stimulus=stimulus, trace_neuron_ids=(1, 2))
    assert first.spike_result_digest == second.spike_result_digest
    assert first.trace_v_mV[0, 1] == pytest.approx(-52.0 + 2.0 * np.exp(-0.1 / 20.0))
    assert first.trace_v_mV[1, 1] == pytest.approx(-52.0 + 1.0 * np.exp(-0.1 / 20.0))


def test_unresolved_edges_are_excluded_and_anatomy_is_unchanged():
    signed = _signed(((1, 2, 5), (3, 4, 7)), labels={1: "acetylcholine", 2: "gaba", 3: "histamine", 4: "gaba"})
    before = signed.connectome.synapse_counts.copy()
    projection = EffectiveSignedProjection.from_signed_connectome(signed)
    assert projection.included_anatomical_weight == 5
    assert projection.excluded_anatomical_weight == 7
    assert projection.excluded_unresolved_edge_count == 1
    assert signed.connectome.synapse_counts.tolist() == before.tolist()


def test_explicit_stimulus_is_sorted_reproducible_and_validates_ids_and_grid():
    projection = _projection(edges=())
    stimulus = ExplicitStimulus((SpikeSchedule(2, (0.2, 0.0, 0.0)),))
    assert stimulus.schedules[0].spike_times_ms == (0.0, 0.0, 0.2)
    assert stimulus.fingerprint == ExplicitStimulus((SpikeSchedule(2, (0.2, 0.0, 0.0)),)).fingerprint
    with pytest.raises(KeyError, match="unknown neuron"):
        simulate_lif(projection, duration_ms=1.0, stimulus=ExplicitStimulus((SpikeSchedule(99, (0.0,)),)))
    with pytest.raises(ValueError, match="not exactly representable"):
        simulate_lif(projection, duration_ms=1.0, dt_ms=0.1, stimulus=ExplicitStimulus((SpikeSchedule(1, (0.05,)),)))


def test_seeded_poisson_is_reproducible_and_uses_reference_scaling():
    poisson = PoissonStimulus((1,), rate_hz=150.0, weight_factor=250.0, seed=42)
    first = poisson.generate(10.0, 0.1, 0.275)
    second = poisson.generate(10.0, 0.1, 0.275)
    assert first.fingerprint == second.fingerprint
    assert first.weight_mV == pytest.approx(68.75)
    assert first.refractory_free_neuron_ids == (1,)
    assert poisson.fingerprint != PoissonStimulus((1,), rate_hz=150.0, seed=43).fingerprint


def test_silencing_disables_outgoing_only():
    projection = _projection(edges=((1, 2, 1),))
    result = simulate_lif(
        projection,
        duration_ms=2.1,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0),
        silenced_neuron_ids=(1,),
        trace_neuron_ids=(2,),
    )
    assert np.all(result.trace_g_mV == 0.0)


def test_fingerprints_and_result_digest_are_deterministic_and_identity_sensitive():
    first_projection = _projection()
    second_projection = _projection()
    first = simulate_lif(first_projection, duration_ms=1.0)
    second = simulate_lif(second_projection, duration_ms=1.0)
    assert first.simulation_fingerprint == second.simulation_fingerprint
    assert first.spike_result_digest == second.spike_result_digest
    conservative = EffectiveSignedProjection.from_signed_connectome(_signed(((1, 2, 1),), policy=ConservativeSignPolicy()))
    assert conservative.signed_policy_fingerprint != first.sign_policy_fingerprint
    assert simulate_lif(conservative, duration_ms=1.0).simulation_fingerprint != first.simulation_fingerprint


def test_effective_weight_preserves_anatomical_count_boundary():
    signed = _signed(((1, 2, 7),))
    projection = EffectiveSignedProjection.from_signed_connectome(signed, synaptic_weight_mV=0.275)
    assert projection.effective_weights_mV.tolist() == [pytest.approx(1.925)]
    assert projection.included_anatomical_weight == 7


def test_effective_inhibitory_weight_uses_presynaptic_sign():
    signed = _signed(((2, 1, 3),))
    projection = EffectiveSignedProjection.from_signed_connectome(signed)
    assert projection.effective_weights_mV.tolist() == [pytest.approx(-0.825)]


def test_two_neuron_chain_keeps_spike_output_compact():
    projection = _projection(edges=((1, 2, 100), (2, 3, 100)))
    result = simulate_lif(
        projection,
        duration_ms=4.0,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0),
    )
    assert result.spike_neuron_ids.tolist() == [1]
    assert result.spike_counts.tolist() == [1, 0, 0, 0]


def test_simulation_reports_identity_metadata():
    result = simulate_lif(_projection(), duration_ms=1.0)
    assert len(result.parameter_fingerprint) == 64
    assert len(result.unsigned_graph_fingerprint) == 64
    assert len(result.sign_policy_fingerprint) == 64
    assert len(result.stimulus_fingerprint) == 64
    assert result.duration_ms == 1.0


def test_parameter_identity_changes_simulation_configuration():
    projection = _projection()
    first = simulate_lif(projection, duration_ms=1.0)
    altered = LIFParameters(synaptic_delay_ms=1.7)
    second = simulate_lif(projection, duration_ms=1.0, parameters=altered)
    assert first.parameter_fingerprint != second.parameter_fingerprint
    assert first.simulation_fingerprint != second.simulation_fingerprint


def test_duration_must_be_on_the_discrete_clock():
    with pytest.raises(ValueError, match="not exactly representable"):
        simulate_lif(_projection(), duration_ms=0.15)


def test_duplicate_schedule_times_are_additive():
    projection = _projection(edges=())
    result = simulate_lif(
        projection,
        duration_ms=0.2,
        stimulus=ExplicitStimulus((SpikeSchedule(1, (0.0, 0.0)),), weight_mV=1.0),
        trace_neuron_ids=(1,),
    )
    assert result.trace_v_mV[0, 1] == pytest.approx(-52.0 + 2.0 * np.exp(-0.1 / 20.0))


def test_poisson_rejects_more_than_one_expected_event_per_step():
    with pytest.raises(ValueError, match="must not exceed one"):
        PoissonStimulus((1,), rate_hz=10001.0).generate(1.0, 0.1, 0.275)


def test_trace_requires_an_explicit_small_subset():
    result = simulate_lif(_projection(), duration_ms=1.0)
    assert result.trace_v_mV is None
    assert result.trace_g_mV is None
