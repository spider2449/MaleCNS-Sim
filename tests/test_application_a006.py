"""Synthetic paired comparison contract and transport checks."""

from dataclasses import replace
from hashlib import sha256
from types import SimpleNamespace
import http.client
import json
import threading

import pytest

from malecns_sim.application.comparisons import PairingError, build_comparison, build_comparison_playback, verify_pair
from malecns_sim.application.models import (
    DatasetIdentity, ExperimentResult, ExperimentSpec, InterventionSpec, ModelSpec,
    ObservablesSpec, RobustnessRequest, RunIdentity, SeedPolicy, SignPolicySpec,
    SpikeEvent, StimulusSpec, TargetSpec, TrialResult, canonical_bytes,
)
from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.application.server import LocalServer
from malecns_sim.application.workbench import DatasetCatalog


def spec(intervention=False):
    params = LIFParameters()
    return ExperimentSpec(
        "application-experiment-v1", "00000000-0000-0000-0000-000000000002" if not intervention else "00000000-0000-0000-0000-000000000003",
        DatasetIdentity("MaleCNS-v1.0", "b"*64, "c"*64, "d"*64, "e"*64, "a"*64, "f"*64),
        "cpu_reference", SeedPolicy("explicit", (7,)), 100.0, 0.1, 1,
        StimulusSpec("1"*64, (100,), "L", 100.0, 0.0, 100.0, 250.0, "reference-poisson-direct-voltage-v1"),
        TargetSpec(16949, "contralateral"), InterventionSpec("outgoing_silence", (16949,)) if intervention else InterventionSpec("none", ()),
        ModelSpec(params, params.fingerprint), SignPolicySpec("Shiu2024SignPolicy", "MaleCNSV1ConsensusThenPredictedThenCelltype"),
        ObservablesSpec(True, (), False, None), RobustnessRequest("none", (), None),
    )


def record(source, count=0, schedule="2"*64, job="a"*32):
    identity = RunIdentity.create(source, (schedule,), source.dataset.projection_fingerprint, "0.3.0")
    spikes = tuple(SpikeEvent(i+1, 16949) for i in range(count))
    trial = TrialResult(0, source.seed_policy.trial_seeds[0], schedule, "3"*64, count, count*1000/source.duration_ms,
                        tuple(i+1 for i in range(count)), spikes, (), ())
    result = ExperimentResult.create(identity=identity, spec=source, invocation_id="synthetic", started_at="", finished_at="",
        provenance={"dataset": source.to_dict()["dataset"], "graph_fingerprint": "4"*64},
        stimulus_summary={"schedule_fingerprints": (schedule,)}, intervention_summary={"kind": source.intervention.kind}, trials=(trial,))
    return SimpleNamespace(job_id=job, spec=source, state="COMPLETED", result=result)


def pair(base_count=0, intervention_count=0):
    return record(spec(), base_count), record(spec(True), intervention_count, job="b"*32)


def changed_model(source):
    params=replace(source.model.parameters,v_threshold_mV=source.model.parameters.v_threshold_mV+1)
    return replace(source,model=ModelSpec(params,params.fingerprint))


def test_pair_metrics_digest_and_zero_baseline():
    a,b=pair()
    result=build_comparison(a,b)
    assert result == build_comparison(a,b)
    assert result["pairing"]["realized_schedule_equal"]
    assert result["target"]["spike_count"]["absolute_delta"] == 0
    assert result["target"]["spike_count"]["relative_delta"] is None
    assert result["target"]["spike_count"]["warning"] == "ZERO_BASELINE"
    assert result["target"]["firing_rate_hz"]["relative_delta"] is None
    without = dict(result); del without["authoritative_digest"]
    assert result["authoritative_digest"] == sha256(canonical_bytes({"domain":"malecns-comparison-result-v1","payload":without})).hexdigest()
    assert result["baseline"]["prepared_graph_fingerprint"] == result["intervention"]["prepared_graph_fingerprint"]
    assert result["baseline"]["base_graph_fingerprint"] != result["baseline"]["prepared_graph_fingerprint"]


def test_nonzero_deltas_and_deterministic_identity():
    a,b=pair(2,3)
    result=build_comparison(a,b)
    assert result["target"]["spike_count"]["absolute_delta"] == 1
    assert result["target"]["spike_count"]["relative_delta"] == .5
    assert result["target"]["firing_rate_hz"]["absolute_delta"] == 10
    assert result["target"]["firing_rate_hz"]["relative_delta"] == .5
    assert result["comparison_id"] == build_comparison(*pair(0,0))["comparison_id"]


@pytest.mark.parametrize("changed,code", [
    (lambda s: replace(s,dataset=replace(s.dataset,manifest_digest="9"*64)), "DIFFERENT_DATASET"),
    (lambda s: replace(s,stimulus=replace(s.stimulus,side="R"),target=TargetSpec(10331,"contralateral"),intervention=InterventionSpec("outgoing_silence",(10331,))), "DIFFERENT_SIDE"),
    (lambda s: replace(s,stimulus=replace(s.stimulus,frequency_hz=150.0)), "DIFFERENT_STIMULUS"),
    (lambda s: replace(s,stimulus=replace(s.stimulus,start_ms=1.0)), "DIFFERENT_STIMULUS"),
    (lambda s: replace(s,stimulus=replace(s.stimulus,member_ids=(101,))), "DIFFERENT_STIMULUS"),
    (lambda s: replace(s,duration_ms=120.0), "DIFFERENT_DURATION"),
    (lambda s: replace(s,dt_ms=.2), "DIFFERENT_DT"),
    (lambda s: replace(s,seed_policy=SeedPolicy("explicit",(8,))), "DIFFERENT_SEED"),
    (changed_model, "DIFFERENT_MODEL"),
    (lambda s: replace(s,target=TargetSpec(10331,"ipsilateral")), "DIFFERENT_TARGET"),
    (lambda s: replace(s,backend="cuda"), "DIFFERENT_BACKEND"),
    (lambda s: replace(s,observables=ObservablesSpec(True,(16949,),False,None)), "DIFFERENT_OBSERVABLES"),
    (lambda s: replace(s,intervention=InterventionSpec("none",())), "NOT_INTERVENTION_PAIR"),
    (lambda s: replace(s,intervention=InterventionSpec("outgoing_silence",(101,))), "NOT_INTERVENTION_PAIR"),
])
def test_mismatch_rejected(changed,code):
    a,b=pair(); b=record(changed(b.spec),job=b.job_id)
    with pytest.raises(PairingError) as error: verify_pair(a,b)
    assert error.value.code == code


def test_schedule_and_incomplete_rejected():
    a,b=pair(); b=record(b.spec,schedule="5"*64,job=b.job_id)
    with pytest.raises(PairingError,match="DIFFERENT_SCHEDULE"): verify_pair(a,b)
    b.state="RUNNING"
    with pytest.raises(PairingError,match="RESULT_NOT_COMPLETE"): verify_pair(a,b)


def test_union_playback_and_recorded_zero():
    a,b=pair()
    comparison=build_comparison(a,b)
    view_a={"nodes":[{"neuron_id":100,"roles":["stimulus"]},{"neuron_id":16949,"roles":["target"]}],"edges":[]}
    view_b={"nodes":[{"neuron_id":101,"roles":["context"]},{"neuron_id":16949,"roles":["target"]}],"edges":[]}
    payload=build_comparison_playback(a,b,comparison,view_a,view_b)
    assert payload["raster_rows"] == [100,101,16949]
    assert payload["baseline"]["sparse_spikes"] == []
    assert payload["baseline"]["duration_ms"] == payload["intervention"]["duration_ms"]
    assert payload["baseline"]["run_id"] == comparison["baseline"]["run_id"]


def test_comparison_api_session_and_backend_export(tmp_path):
    server=LocalServer(0,DatasetCatalog(tmp_path,engine=None),tmp_path)
    a,b=pair(); server.manager.records[a.job_id]=a; server.manager.records[b.job_id]=b
    view={"nodes":[{"neuron_id":16949,"roles":["target"]}],"edges":[],"rendered_node_count":1,"total_candidate_nodes":1,"truncated":False}
    a.subgraphs={("target",80):view};b.subgraphs={("target",80):view}
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(method,path,body=None,authorized=True):
        connection=http.client.HTTPConnection("127.0.0.1",server.server_port)
        headers={"X-Local-Session":server.token} if authorized else {}
        if body is not None:
            headers.update({"Content-Type":"application/json","Origin":f"http://127.0.0.1:{server.server_port}"})
        connection.request(method,path,body=json.dumps(body) if body is not None else None,headers=headers)
        response=connection.getresponse(); status=response.status; payload=json.loads(response.read());connection.close()
        return status,payload
    try:
        selection={"baseline_job_id":a.job_id,"intervention_job_id":b.job_id}
        assert request("POST","/api/comparisons",authorized=False)[0]==403
        assert request("GET","/api/comparisons/missing",authorized=False)[0]==403
        status,created=request("POST","/api/comparisons",selection)
        assert status==201 and created["pairing"]["status"]=="PAIRED"
        status,candidates=request("GET","/api/comparisons/candidates?baseline_job_id="+a.job_id)
        assert status==200 and candidates["candidates"]==[{"job_id":b.job_id,"run_id":b.result.identity.run_id,"eligible":True,"reason":None}]
        status,export=request("GET","/api/comparisons/"+created["comparison_id"]+"/export")
        assert status==200 and export==created
        status,playback=request("GET","/api/comparisons/"+created["comparison_id"]+"/playback?mode=target&cap=80")
        assert status==200 and playback["baseline"]["run_id"]==a.result.identity.run_id
        assert playback["raster_rows"]==[16949]
    finally:
        server.shutdown();server.server_close();thread.join()
