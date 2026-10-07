import numpy as np
import pytest

from malecns_sim.dynamics.lif import PreparedRuntime, simulate_lif
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule
from test_task005 import _projection


def stimulus(start, duration):
    times = (0, 6.9, 9.9, 19.9, 23.9, 49.9, 97.9, 99.9)
    return ExplicitStimulus((SpikeSchedule(1, tuple(round(t-start, 8) for t in times if start <= t < start+duration)),), weight_mV=30, refractory_free_neuron_ids=(1,))


@pytest.mark.parametrize("chunks", [(10,)*10, (7,13,4,26,50)])
def test_exact_continuity(chunks):
    projection = _projection(((1,2,100), (2,3,100), (3,1,20)))
    runtime = PreparedRuntime(projection)
    whole = runtime.initial_state()
    reference = simulate_lif(projection, duration_ms=100, stimulus=stimulus(0,100), trace_neuron_ids=(1,2,3))
    result = runtime.advance(whole, duration_ms=100, stimulus=stimulus(0,100), trace_neuron_ids=(1,2,3))
    state = runtime.initial_state()
    ids, steps, vs, gs = [], [], [], []
    start = 0
    for duration in chunks:
        chunk = runtime.advance(state, duration_ms=duration, stimulus=stimulus(start,duration), trace_neuron_ids=(1,2,3))
        ids.append(chunk.spike_neuron_ids)
        steps.append(chunk.spike_timesteps)
        vs.append(chunk.trace_v_mV[:,1:])
        gs.append(chunk.trace_g_mV[:,1:])
        start += duration
    np.testing.assert_array_equal(reference.spike_timesteps, result.spike_timesteps)
    np.testing.assert_array_equal(reference.trace_v_mV, result.trace_v_mV)
    np.testing.assert_array_equal(np.concatenate(ids), result.spike_neuron_ids)
    np.testing.assert_array_equal(np.concatenate(steps), result.spike_timesteps)
    np.testing.assert_array_equal(np.concatenate(vs, axis=1), result.trace_v_mV[:,1:])
    np.testing.assert_array_equal(np.concatenate(gs, axis=1), result.trace_g_mV[:,1:])
    for name in ('v_mV','g_mV','refractory_until','pending','pending_event_counts'):
        np.testing.assert_array_equal(getattr(state,name), getattr(whole,name))
    assert state.timestep == whole.timestep == 1000
    assert whole.pending_event_counts.any()
    assert (whole.refractory_until >= 1000).any()


def test_initial_state_and_identity():
    runtime = PreparedRuntime(_projection())
    a, b = runtime.initial_state(), runtime.initial_state()
    np.testing.assert_array_equal(a.v_mV,b.v_mV)
    a.v_mV[0] = 0
    assert b.v_mV[0] == -52
    with pytest.raises(TypeError):
        runtime.advance(b,duration_ms=1,stimulus=object())


from malecns_sim.application.arena import ArenaSession, ArenaState, encode, decode


def command(s, name, **values):
    return s.command({"command":name,"generation":s.generation,"revision":s.revision,**values})


def test_clocks_controls_reset_replay():
    s = ArenaSession()
    initial = s.state.v_mV.copy()
    initial_arena = s.arena
    command(s,"pause")
    command(s,"tick")
    assert s.state.timestep == 0
    command(s,"step")
    assert s.state.timestep == 200 and s.arena.simulation_ms == 20
    command(s,"run")
    command(s,"tick")
    command(s,"pause")
    command(s,"tick")
    assert s.state.timestep == 400
    command(s,"reset")
    np.testing.assert_array_equal(s.state.v_mV,initial)
    assert s.arena == initial_arena and not s.state.pending.any()
    def script():
        command(s,"stimulus",x=.3,y=.1)
        command(s,"intervention",neuron_id=3,silenced=True)
        for _ in range(8): command(s,"step")
        command(s,"intervention",neuron_id=3,silenced=False)
        command(s,"step")
        return list(s.events), s.arena, s.state.v_mV.copy()
    first = script()
    command(s,"reset")
    second = script()
    assert first[:2] == second[:2]
    np.testing.assert_array_equal(first[2],second[2])
    assert first[0][0]["kind"] == "reset"
    assert first[0][1]["kind"] == "stimulus_moved"
    assert first[0][2]["kind"] == "readout_mask"


def test_encoder_decoder_bounds_and_invalid_contracts():
    for x in (0,.5,1):
        for y in (0,.5,1):
            a=ArenaState(stimulus_x=x,stimulus_y=y)
            values,events=encode(a)
            assert values == encode(a)[0] and events == encode(a)[1]
            assert 0 <= values['left'] <= 1 and 0 <= values['right'] <= 1
            assert all(0 <= c <= 24 for c in values['impulses_per_pulse'])
    for counts in ({3:0,4:0},{3:999,4:-3},{3:1,4:4}):
        action=decode(counts)
        assert action==decode(counts)
        assert 0 <= action['forward_units_per_s'] <= .25
        assert -3 <= action['turn_rad_per_s'] <= 3
    for kw in ({'sensory':'invalid'},{'motor':'invalid'},{'readouts':(10331,16949)}):
        with pytest.raises(ValueError): ArenaSession(**kw)
    s=ArenaSession()
    for values in ({'x':float('nan'),'y':0},{'x':2,'y':0}):
        with pytest.raises(ValueError): command(s,'stimulus',**values)
    with pytest.raises(ValueError): command(s,'intervention',neuron_id=99,silenced=True)
    with pytest.raises(ValueError): s.command({'command':'step','generation':0,'revision':0})
    with pytest.raises(ValueError): command(s,'step',v_mV=[0])


def test_synthetic_visible_response_and_intervention():
    left,right=ArenaSession(),ArenaSession()
    command(left,'stimulus',x=.5,y=0)
    command(right,'stimulus',x=.5,y=1)
    for _ in range(20):
        command(left,'step'); command(right,'step')
    assert left.latest['sensory']['left'] > left.latest['sensory']['right']
    assert left.latest['readout_counts'][3] > left.latest['readout_counts'][4]
    assert left.latest['action']['turn_rad_per_s'] < 0
    assert right.latest['action']['turn_rad_per_s'] > 0
    assert left.arena.y < .5 < right.arena.y
    command(left,'intervention',neuron_id=3,silenced=True)
    command(left,'step')
    assert left.latest['action']['left_drive'] == 0


def test_render_speed_cannot_change_backend():
    a,b=ArenaSession(),ArenaSession()
    for _ in range(10): command(a,'step')
    command(b,'run')
    for _ in range(10): command(b,'tick')
    command(b,'pause')
    assert a.arena == b.arena
    np.testing.assert_array_equal(a.state.v_mV,b.state.v_mV)
    assert a.identity == b.identity
    assert a.spec['dt_ms']==.1 and a.spec['control_interval_ms']==20


def test_http_ui_assets_and_commands(tmp_path):
    import json, subprocess, threading
    from pathlib import Path
    from urllib.request import Request,urlopen
    from urllib.error import HTTPError
    from malecns_sim.application.server import LocalServer
    server=LocalServer(0,result_root=tmp_path)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    def get(path,protected=True):
        return urlopen(Request(base+path,headers={"X-Local-Session":server.token} if protected else {}))
    try:
        for asset in ('/arena','/arena.js','/arena.css','/','/app.js','/api/status'):
            with get(asset) as r: assert r.status==200
        with pytest.raises(HTTPError) as e: get('/api/arena',False)
        assert e.value.code==403
        with get('/api/arena') as r: fixture=json.load(r)
        body=json.dumps({'command':'step','generation':fixture['generation'],'revision':fixture['revision']}).encode()
        headers={'Content-Type':'application/json','X-Local-Session':server.token,'Origin':base}
        with urlopen(Request(base+'/api/arena',data=body,headers=headers)) as r: advanced=json.load(r)
        assert advanced['arena']['simulation_ms']==20
        with pytest.raises(HTTPError): urlopen(Request(base+'/api/arena',data=body,headers=headers))
        with get('/api/arena/events') as r: assert json.load(r)['events'][-1]['kind']=='control_step'
        path=tmp_path/'arena.json';path.write_text(json.dumps(advanced))
        root=Path(__file__).resolve().parents[1]
        import os
        if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
            from a011_node import command, environment
            result = subprocess.run(command(path), env=environment(), cwd=str(root),
                                    capture_output=True, text=True, timeout=30, close_fds=True)
            assert 'A011 guard ACTIVE; payload and descendant probes BLOCKED' in result.stdout
        else:
            result=subprocess.run(['node',str(root/'tests/js/application_a011.cjs'),str(path),str(root/'src/malecns_sim/application/static')],capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        print(result.stdout)
    finally:
        server.shutdown();server.server_close();thread.join()
