"""Explicit isolated synthetic review launcher; never uses production dataset files."""
from __future__ import annotations
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import time
from urllib.request import Request, urlopen
import numpy as np
from malecns_sim.analysis.task008 import derive_task008_populations, prepare_network
from malecns_sim.application.models import (ExperimentSpec, DatasetIdentity, SeedPolicy, StimulusSpec, TargetSpec, InterventionSpec, ModelSpec, SignPolicySpec, ObservablesSpec, RobustnessRequest)
from malecns_sim.application.service import DatasetFiles, ProductionEngine
from malecns_sim.application.server import LocalServer
from malecns_sim.application.workbench import DatasetCatalog
from malecns_sim.application.preparation import PRESET_ID
from malecns_sim.application.robustness import VARIANTS
from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.homology import MaleCNSCandidate, population_fingerprint
def _candidate(body_id, side):
    return MaleCNSCandidate(body_id=str(body_id), type="LB3a", flywire_type="LB3", side=side, root_side=side, soma_side=None, superclass="cb_sensory", cell_class="gustatory", entry_nerve="MxLbN", consensus_nt="acetylcholine", resolved_nt="acetylcholine", task004_sign=1)

def _spec(*, population=None, graph="a" * 64, sign="Shiu2024SignPolicy", resolution="MaleCNSV1ConsensusThenPredictedThenCelltype"):
    population = population or derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False).sugar_left
    params = LIFParameters()
    return ExperimentSpec(
        "application-experiment-v1", "00000000-0000-0000-0000-000000000002",
        DatasetIdentity("MaleCNS-v1.0", "b" * 64, "c" * 64, "d" * 64, "e" * 64, graph, "f" * 64),
        "cpu_reference", SeedPolicy("explicit", (7,)), 5.0, 0.1, 1,
        StimulusSpec(population_fingerprint(population), tuple(int(i) for i in population.candidate_body_ids), "L", 100.0, 0.0, 5.0, 250.0, "reference-poisson-direct-voltage-v1"),
        TargetSpec(16949, "contralateral"), InterventionSpec("none", ()),
        ModelSpec(params, params.fingerprint), SignPolicySpec(sign, resolution),
        ObservablesSpec(True, (16949,), False, None), RobustnessRequest("none", (), None),
    )

def make_fixture(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather
    from malecns_sim.analysis.task007 import MALE_CNS_ANNOTATION_COLUMNS, NT_COLUMNS

    annotation = tmp_path / "annotation.feather"
    neurotransmitter = tmp_path / "nt.feather"
    weights = tmp_path / "weights.feather"
    ids = [100, 200, 10331, 16949]
    rows = []
    for body, side, flywire in ((100, "L", "LB3"), (200, "R", "LB3"), (10331, "L", "CB0701"), (16949, "R", "CB0701")):
        row = {key: None for key in MALE_CNS_ANNOTATION_COLUMNS}
        row.update(bodyId=body, flywireType=flywire, type="LB3a" if flywire == "LB3" else "MN9", rootSide=side, somaSide=side, superclass="cb_sensory" if flywire == "LB3" else "motor", **{"class": "gustatory" if flywire == "LB3" else "motor"}, entryNerve="MxLbN")
        rows.append(row)
    feather.write_feather(pa.Table.from_pylist(rows), annotation)
    nt_rows = [{**{key: None for key in NT_COLUMNS}, "body": body, "consensus_nt": "glutamate" if body == 200 else "acetylcholine"} for body in ids]
    feather.write_feather(pa.Table.from_pylist(nt_rows), neurotransmitter)
    feather.write_feather(pa.table({"body_pre": [100, 200], "body_post": [16949, 10331], "weight": [5, 5]}), weights)
    prepared = prepare_network(annotation, neurotransmitter, weights)
    population = derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False).sugar_left
    spec = _spec(population=population, graph=prepared.projection.unsigned_graph_fingerprint, sign=prepared.projection.sign_policy_id, resolution=prepared.projection.resolution_policy_id)
    spec = replace(spec, dataset=replace(spec.dataset, annotation_sha256=hashlib.sha256(annotation.read_bytes()).hexdigest(), neurotransmitter_sha256=hashlib.sha256(neurotransmitter.read_bytes()).hexdigest(), weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest()))
    files = DatasetFiles(annotation, neurotransmitter, weights, spec.dataset.manifest_digest, spec.dataset.mapping_fingerprint)

    class SyntheticAdapter(ProductionEngine):
        def identities(self, files):
            return derive_task008_populations((_candidate(100, "L"), _candidate(200, "R")), enforce_task007_right=False)

        def simulate(self, prepared, spec, stimulus):
            self.executed_input_amplitude = stimulus.weight_mV
            self.executed_parameters = spec.model.parameters
            return super().simulate(prepared, spec, stimulus)
    return spec, files, SyntheticAdapter()
class ReviewCatalog(DatasetCatalog):
    def __init__(self, root):
        self.review_spec, self.review_files, engine = make_fixture(root)
        super().__init__(root, engine)
        original = engine.simulate
        def simulate(prepared, child, stimulus):
            result = original(prepared, child, stimulus)
            variant = child.variant.variant_id
            if child.seed_policy.trial_seeds == (8,) and variant == "V4":
                raise RuntimeError("SYNTHETIC REVIEW bounded V4 failure")
            baseline = child.intervention.kind == "none"
            counts_by_variant = {"R0": (0, 1), "V1": (1, 3), "V2": (3, 1), "V3": (2, 2), "V4": (1, 2), "V5": (3, 2), "V6": (1, 1), "V7": (2, 1)}
            count = counts_by_variant[variant][0 if baseline else 1]
            keep = result.spike_neuron_ids != child.target.neuron_id
            ids = np.concatenate((result.spike_neuron_ids[keep], np.full(count,child.target.neuron_id,dtype=np.int64)))
            steps = np.concatenate((result.spike_timesteps[keep],np.arange(1,count+1,dtype=np.int64)))
            order = np.lexsort((ids,steps)); ids,steps=ids[order],steps[order]
            counts=np.asarray([np.count_nonzero(ids==i) for i in prepared.projection.neuron_ids],dtype=np.int64)
            spike_digest=hashlib.sha256(b"malecns-sim-spike-result-v1"+ids.tobytes()+steps.tobytes()+counts.tobytes()).hexdigest()
            return replace(result,spike_neuron_ids=ids,spike_timesteps=steps,spike_counts=counts,spike_result_digest=spike_digest,emitted_spike_count=len(ids),active_neuron_count=int(np.count_nonzero(counts)))
        engine.simulate=simulate
    @property
    def files(self): return self.review_files
    @property
    def identity(self): return self.review_spec.dataset
    def metadata(self):
        return {**super().metadata(), "display_name":"SYNTHETIC REVIEW DATA - No MaleCNS scientific result", "manifest_digest":self.identity.manifest_digest,"synthetic_review":True}
    def spec(self, selection):
        spec=super().spec(selection)
        return replace(spec,duration_ms=5.0,stimulus=replace(spec.stimulus,end_ms=5.0),observables=self.review_spec.observables)

def start_review(port=0, partial=True):
    temporary=tempfile.TemporaryDirectory(prefix="malecns-a007c-synthetic-")
    root=Path(temporary.name)
    server=LocalServer(port,ReviewCatalog(root),root/"results")
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base="http://127.0.0.1:"+str(server.server_port)
    selection={"dataset_key":"male-cns-v1","side":"L","frequency_hz":100.0,"mode":"none","backend":"cpu_reference","seed":7}
    def create(variants, seed):
        request=Request(base+"/api/robustness",data=json.dumps({"selection":{**selection,"seed":seed},"preset_id":PRESET_ID,"variant_ids":list(variants),"reuse_policy":"EXACT_REUSE_OR_EXECUTE","aggregate_rule":"NO_AGGREGATE_RULE"}).encode(),headers={"X-Local-Session":server.token,"Content-Type":"application/json","Origin":base},method="POST")
        with urlopen(request) as response: identity=json.load(response)["robustness_id"]
        deadline=time.monotonic()+30
        while server.robustness.get(identity)["result"]["overall_state"] not in ("COMPLETE","PARTIAL","FAILED","CANCELLED"):
            if time.monotonic()>deadline: raise RuntimeError("Synthetic review creation timed out")
            time.sleep(.02)
        return identity
    source=create(("R0",),7)
    complete=create(VARIANTS,7)
    request=Request(base+"/api/robustness/"+source+"/release",data=b"{}",headers={"X-Local-Session":server.token,"Content-Type":"application/json","Origin":base},method="POST")
    with urlopen(request) as response: json.load(response)
    if partial: create(VARIANTS,8)
    return server, temporary, complete

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--port",type=int,default=0);args=parser.parse_args()
    server,temporary,identity=start_review(args.port)
    print("SYNTHETIC REVIEW DATA - No MaleCNS scientific result",flush=True)
    print("http://127.0.0.1:"+str(server.server_port)+"/#token="+server.token,flush=True)
    print("Complete eight-variant review parent: "+identity,flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown();server.server_close();temporary.cleanup()
if __name__ == "__main__": main()
