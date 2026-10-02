"""Bounded synthetic closed-loop demonstrator; all action semantics engineered."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import threading
from time import perf_counter

import numpy as np

from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import NeurotransmitterEvidence, NeurotransmitterResolutionPolicy
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import Shiu2024SignPolicy
from malecns_sim.dynamics.lif import EffectiveSignedProjection, PreparedRuntime
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule


def synthetic_projection():
    ids = np.array([1, 2, 3, 4], dtype=np.int64)
    graph = NumericNormalizedConnectome(ids, np.array([1,2]), np.array([3,4]), np.array([100,100]))
    curated = CuratedNeuronProjection(graph,2,2,2,0)
    signed = SignedAnatomicalConnectome.from_projection(curated,
        [NeurotransmitterEvidence(neuron_id=int(i), consensus_nt="acetylcholine") for i in ids],
        NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy())
    return EffectiveSignedProjection.from_signed_connectome(signed)


@dataclass(frozen=True)
class ArenaState:
    x: float = 0.5
    y: float = 0.5
    heading: float = 0.0
    stimulus_x: float = 0.8
    stimulus_y: float = 0.25
    simulation_ms: float = 0.0


def encode(state):
    dx, dy = state.stimulus_x-state.x, state.stimulus_y-state.y
    bearing = math.atan2(math.sin(math.atan2(dy,dx)-state.heading), math.cos(math.atan2(dy,dx)-state.heading))
    intensity = max(0.0, 1.0-math.hypot(dx,dy)/math.sqrt(2))
    left = intensity*(1-math.sin(bearing))/2
    right = intensity*(1+math.sin(bearing))/2
    # Fixed grid pulses: amplitudes encode sensory channels without stochastic state.
    # Duplicate direct impulses give separate bounded channel amplitudes under existing semantics.
    counts = [int(round(24*left)),int(round(24*right))]
    events = ExplicitStimulus(tuple(SpikeSchedule(i+1,tuple(t for t in (0.,5.,10.,15.) for _ in range(counts[i]))) for i in range(2)), weight_mV=1)
    return {"bearing_rad":bearing,"intensity":intensity,"left":left,"right":right,"impulses_per_pulse":counts,"pulse_times_ms":[0,5,10,15],"weight_mV":1}, events


def decode(counts, silenced=()):
    drives = [min(1.0,max(0.0,float(counts[i])/4)) if i not in silenced else 0.0 for i in (3,4)]
    return {"left_drive":drives[0],"right_drive":drives[1],"turn_rad_per_s":3*(drives[1]-drives[0]),"forward_units_per_s":0.25*(drives[0]+drives[1])/2}


def environment_step(state, action):
    heading = math.atan2(math.sin(state.heading+action["turn_rad_per_s"]*.02),math.cos(state.heading+action["turn_rad_per_s"]*.02))
    distance = action["forward_units_per_s"]*.02
    return ArenaState(min(1,max(0,state.x+math.cos(heading)*distance)),min(1,max(0,state.y+math.sin(heading)*distance)),heading,state.stimulus_x,state.stimulus_y,state.simulation_ms+20)


class ArenaSession:
    """Serialized command owner; rendering never supplies neural values."""
    def __init__(self, sensory="arena-sensory-v1", motor="arena-motor-v1", readouts=(3,4)):
        if sensory != "arena-sensory-v1" or motor != "arena-motor-v1" or readouts != (3,4):
            raise ValueError("unsupported adapter or readout")
        self.runtime = PreparedRuntime(synthetic_projection())
        self.spec = {"schema":"application-closed-loop-v1","network":self.runtime.projection.fingerprint,
            "network_kind":"synthetic-four-neuron-v1","environment":"arena-environment-v1","sensory":sensory,"motor":motor,
            "dt_ms":.1,"control_interval_ms":20,"seed":0,"readouts":[3,4],"intervention":"readout-mask-v1",
            "mode":"manual","maximum_steps":1500,"initial_arena":asdict(ArenaState()),
            "parameters":self.runtime.parameters.fingerprint,"initial_silenced":[]}
        self.identity = hashlib.sha256(json.dumps(self.spec,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        self.lock = threading.Lock()
        self.generation = 0
        self.revision = 0
        self.reset()

    def reset(self):
        self.state = self.runtime.initial_state()
        self.arena = ArenaState()
        self.running = False
        self.silenced = set()
        self.events = [{"kind":"reset","simulation_ms":0.0}]
        self.trail = [[self.arena.x,self.arena.y]]
        self.latest = None
        self.performance = {}
        self.generation += 1
        self.revision += 1

    def record(self, kind, **values):
        self.events.append({"kind":kind,"simulation_ms":self.arena.simulation_ms,**values})

    def step(self):
        if self.state.timestep >= 300000:
            self.running = False
            raise ValueError("bounded 30-second session exhausted; Reset required")
        before = asdict(self.arena)
        start = perf_counter()
        sensory, stimulus = encode(self.arena)
        encoded = perf_counter()
        result = self.runtime.advance(self.state,duration_ms=20,stimulus=stimulus,trace_neuron_ids=(3,4))
        advanced = perf_counter()
        counts = {int(i):int(c) for i,c in zip(self.runtime.projection.neuron_ids,result.spike_counts)}
        action = decode(counts,self.silenced)
        decoded = perf_counter()
        self.arena = environment_step(self.arena,action)
        finished = perf_counter()
        self.performance = {"encode_ms":(encoded-start)*1000,"neural_ms":(advanced-encoded)*1000,"decode_ms":(decoded-advanced)*1000,"environment_ms":(finished-decoded)*1000}
        self.latest = {"before":before,"sensory":sensory,"readout_counts":counts,"window_ms":20,
            "selected_v_mV":self.state.v_mV[2:].tolist(),"selected_g_mV":self.state.g_mV[2:].tolist(),
            "spikes":{"ids":result.spike_neuron_ids.tolist(),"timesteps":result.spike_timesteps.tolist()},
            "action":action,"after":asdict(self.arena),"silenced":sorted(self.silenced),"warnings":[]}
        self.record("control_step",evidence=self.latest)
        self.trail.append([self.arena.x,self.arena.y])

    def command(self, body):
        with self.lock:
            if set(body)-{"command","generation","revision","x","y","neuron_id","silenced"}:
                raise ValueError("unknown command fields")
            command = body.get("command")
            if command not in ("reset","run","pause","step","tick","stimulus","intervention"):
                raise ValueError("invalid command")
            if body.get("generation") != self.generation or body.get("revision") != self.revision:
                raise ValueError("stale session command")
            if len(self.events) >= 5000 and command != "reset":
                self.running = False
                raise ValueError("bounded event log exhausted; Reset required")
            if command == "reset":
                self.reset()
            elif command in ("run","pause"):
                self.running = command == "run"
                self.record(command)
            elif command in ("step","tick"):
                if command == "step":
                    if self.running:
                        raise ValueError("Pause before manual Step")
                    self.record("manual_step")
                    self.step()
                elif self.running:
                    self.step()
            elif command == "stimulus":
                x,y = body.get("x"),body.get("y")
                if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not 0 <= v <= 1 for v in (x,y)):
                    raise ValueError("stimulus coordinates must be finite in [0,1]")
                self.arena = ArenaState(self.arena.x,self.arena.y,self.arena.heading,float(x),float(y),self.arena.simulation_ms)
                self.record("stimulus_moved",x=x,y=y)
            elif command == "intervention":
                neuron = body.get("neuron_id")
                if type(neuron) is not int or neuron not in (3,4) or type(body.get("silenced")) is not bool:
                    raise ValueError("allowlisted readout and boolean required")
                if body["silenced"]: self.silenced.add(neuron)
                else: self.silenced.discard(neuron)
                self.record("readout_mask",neuron_id=neuron,silenced=body["silenced"])
            self.revision += 1
            return self.snapshot()

    def snapshot(self):
        sensory,_ = encode(self.arena)
        return {"session_identity":self.identity,"spec":self.spec,"generation":self.generation,"revision":self.revision,
            "running":self.running,"arena":asdict(self.arena),"sensory_preview":sensory,"latest":self.latest,
            "silenced":sorted(self.silenced),"trail":self.trail[-300:],"history":[e["evidence"] for e in self.events if e["kind"]=="control_step"][-60:],
            "event_count":len(self.events),"performance":self.performance}
