"""Drive ViZDoom's basic scenario from the registered MaleCNS network, or from a control policy.

``--controller network`` prepares the real network once (about 5 minutes) and runs the
generic closed loop. ``random``, ``noop`` and ``attack`` skip the network and give the
baselines needed to interpret its score. All sensory and motor mappings are engineered.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import statistics
import sys
import threading


def _prepare_runtime(root: Path):
    from malecns_sim.application.service import ProductionEngine
    from malecns_sim.application.workbench import DatasetCatalog
    from malecns_sim.runtime import prepare_runtime

    catalog = DatasetCatalog(root / "data", ProductionEngine())
    if not catalog.available():
        raise RuntimeError("registered MaleCNS v1.0 source files are unavailable")
    print("Preparing the registered MaleCNS CPU network (about 5 minutes)...", flush=True)
    runtime = prepare_runtime(catalog.engine.prepare(catalog.files, "cpu").projection, dt_ms=0.1)
    print(f"Prepared {len(runtime.neuron_ids)} neurons", flush=True)
    return runtime


# Readout populations. "flight" reuses the flight coupling's DNp03/DNg02 IDs. "screened" was chosen by a
# 2026-10-19 screen of the 1,332 descending neurons under LC4 input of different left/right balance
# (130/70, 70/130 and 100/100 Hz, 3 seeds x 300 ms): DNp04 L/R fired almost only for same-side input
# (182 vs 2, and 137 vs 0 spikes), DNg33 L/R fired almost only for balanced input (about 100 vs 0-7 spikes).
# Same annotation file as the flight mapping; the choice is engineered and not a biological claim.
SCREENED = {"move_left": (531898,), "move_right": (11137,), "attack": (13317, 13442)}
READOUT_LABELS = {
    "flight": {"move_left": "DNp03 left", "move_right": "DNp03 right", "attack": "DNg02"},
    "screened": {"move_left": "DNp04 left", "move_right": "DNp04 right", "attack": "DNg33"}}


def _network_loop(args, env, root):
    from malecns_sim.application.closed_loop import (
        ClosedLoop, ClosedLoopParameters, GroupRateDecoder, GroupRateEncoder)
    from malecns_sim.application.flight_populations import native_flight_mapping
    from malecns_sim.application.vizdoom_env import button_command, monster_bearing_rates

    runtime = _prepare_runtime(root)
    mapping = native_flight_mapping()
    mapping.validate(runtime.neuron_ids)
    encoder = GroupRateEncoder(
        {"sensory_left": mapping.sensory_left, "sensory_right": mapping.sensory_right},
        monster_bearing_rates(args.maximum_hz), weight_mV=args.input_weight, maximum_hz=args.maximum_hz)
    readout = ({"move_left": mapping.turn_left, "move_right": mapping.turn_right,
                "attack": mapping.power_left + mapping.power_right}
               if args.readout == "flight" else SCREENED)
    decoder = GroupRateDecoder(readout, button_command(args.move_threshold_hz, args.attack_threshold_hz))
    loop = ClosedLoop(runtime, env, encoder, decoder,
                      expected_projection_fingerprint=runtime.projection_fingerprint,
                      parameters=ClosedLoopParameters(neural_ms_per_step=args.neural_ms, seed=args.seed))
    return loop, {**encoder.groups, **decoder.groups}


# Display order, label, role and colour of each watched population in the live viewer.
_VIEW_GROUPS = (
    ("sensory_left", "LC4 left (input)", "#4cc9f0"), ("sensory_right", "LC4 right (input)", "#4895ef"),
    ("move_left", "{move_left} → MOVE LEFT", "#f4a261"), ("move_right", "{move_right} → MOVE RIGHT", "#e76fb4"),
    ("attack", "{attack} → ATTACK", "#ef476f"))


def _start_view(args, groups):
    """Start the live viewer and return ``(view, publish)``; ``publish(record, episode, env, total)``."""
    from malecns_sim.application.closed_loop_view import LiveView

    meta_groups, row_of, offset = [], {}, 0
    names = READOUT_LABELS[args.readout]
    for key, label, color in _VIEW_GROUPS:
        label = label.format(**names)
        ids = groups[key]
        meta_groups.append({"key": key, "label": label, "color": color, "size": len(ids), "offset": offset})
        row_of.update({neuron: offset + index for index, neuron in enumerate(ids)})
        offset += len(ids)
    group_of = {neuron: key for key, ids in groups.items() for neuron in ids}
    sizes = {key: len(ids) for key, ids in groups.items()}
    color = {key: c for key, _, c in _VIEW_GROUPS}
    circuit = {"nodes": [
        {"id": "bearing", "label": "Monster bearing", "kind": "bearing", "x": 0.08, "y": 0.5, "radius": 38, "color": "#e8a33d"},
        {"id": "sensory_left", "label": "LC4 left", "group": "sensory_left", "x": 0.3, "y": 0.22, "color": color["sensory_left"]},
        {"id": "sensory_right", "label": "LC4 right", "group": "sensory_right", "x": 0.3, "y": 0.78, "color": color["sensory_right"]},
        {"id": "network", "label": "MaleCNS network", "kind": "network", "x": 0.55, "y": 0.5, "radius": 52, "color": "#7f8c99"},
        {"id": "move_left", "label": names["move_left"], "group": "move_left", "x": 0.85, "y": 0.17, "color": color["move_left"]},
        {"id": "move_right", "label": names["move_right"], "group": "move_right", "x": 0.85, "y": 0.5, "color": color["move_right"]},
        {"id": "attack", "label": names["attack"], "group": "attack", "x": 0.85, "y": 0.83, "color": color["attack"]}],
        "edges": [["bearing", "sensory_left"], ["bearing", "sensory_right"], ["sensory_left", "network"],
                  ["sensory_right", "network"], ["network", "move_left"], ["network", "move_right"],
                  ["network", "attack"]]}
    view = LiveView({
        "groups": meta_groups, "circuit": circuit,
        "buttons": [{"label": "MOVE LEFT", "color": color["move_left"]}, {"label": "MOVE RIGHT", "color": color["move_right"]},
                    {"label": "ATTACK", "color": color["attack"]}],
        "notes": ["Engineered mapping: monster bearing sets LC4 input rates; readout populations press buttons. "
                  "The circuit arrows summarise paths through the connectome, not individual synapses."]})

    def publish(record, episode, env, total_reward):
        counts = {key: 0 for key in sizes}
        raster = []
        for neuron, time_ms in record.spikes:
            counts[group_of[neuron]] += 1
            raster.append([row_of[neuron], time_ms])
        view.publish({
            "episode": episode, "step": record.step, "neural_time_ms": record.neural_time_ms,
            "neural_ms": args.neural_ms, "neural_wall_ms": record.neural_wall_ms,
            "monster_x": record.observation["monster_x"], "command": [bool(c) for c in record.command],
            "total_reward": total_reward, "kills": record.info["kills"], "done": record.done,
            "input_events": record.input_events, "network_spikes": record.network_spikes,
            "rates_hz": {key: counts[key] * 1000 / (args.neural_ms * sizes[key]) for key in sizes},
            "raster": raster}, env.frame_png())

    return view, publish


def _baseline_episode(args, env, seed):
    rng = random.Random(seed)
    observation, total, steps, kills, done = env.reset(seed), 0.0, 0, 0, False
    while not done and steps < args.max_steps:
        command = {"noop": (False, False, False), "attack": (False, False, True),
                   "random": tuple(rng.random() < 0.5 for _ in range(3))}[args.controller]
        outcome = env.step(command)
        total, steps, kills, done = total + outcome.reward, steps + 1, outcome.info["kills"], outcome.done
    return {"steps": steps, "reward": total, "kills": kills}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", choices=("network", "random", "noop", "attack"), default="network")
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--max-steps", type=int, default=100, help="decisions per episode")
    parser.add_argument("--neural-ms", type=float, default=10.0, help="neural time spent per decision")
    parser.add_argument("--frame-skip", type=int, default=4, help="game tics per decision")
    parser.add_argument("--input-weight", type=float, default=2.0, help="mV per input impulse")
    parser.add_argument("--maximum-hz", type=float, default=200.0)
    parser.add_argument("--readout", choices=("screened", "flight"), default="screened",
                        help="readout populations: screened DNp04/DNg33, or the flight DNp03/DNg02 (default: screened)")
    parser.add_argument("--move-threshold-hz", type=float, default=0.0,
                        help="move readouts must exceed this rate to press (100 Hz = two spikes in 10 ms)")
    parser.add_argument("--attack-threshold-hz", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--window", action="store_true", help="show the game window")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--view", action="store_true",
                        help="serve a live neural-activity page on loopback and keep it open after the last episode")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from malecns_sim.application.vizdoom_env import ViZDoomBasic

    env = ViZDoomBasic(frame_skip=args.frame_skip, window_visible=args.window)
    if args.view and args.controller != "network":
        parser.error("--view needs --controller network")
    loop, groups = _network_loop(args, env, root) if args.controller == "network" else (None, None)
    view = publish = None
    if args.view:
        view, publish = _start_view(args, groups)
        print(f"Live view: {view.url}", flush=True)
    results = []
    try:
        for episode in range(args.episodes):
            seed = args.seed + episode
            if loop is None:
                summary = _baseline_episode(args, env, seed)
            else:
                loop.reset(seed)
                total = [0.0]

                def on_step(record, episode=episode):
                    total[0] += record.reward
                    if publish is not None:
                        publish(record, episode, env, total[0])

                records = loop.run(args.max_steps, on_step=on_step)
                pressed = [sum(bool(c) for c in (r.command[i] for r in records)) for i in range(3)]
                summary = {"steps": len(records), "reward": sum(r.reward for r in records),
                           "kills": records[-1].info["kills"] if records else 0,
                           "presses": dict(zip(("move_left", "move_right", "attack"), pressed)),
                           "input_events": sum(r.input_events for r in records),
                           "network_spikes": sum(r.network_spikes for r in records),
                           "readout_spikes": {name: sum(r.evidence["spikes"][name] for r in records)
                                              for name in ("move_left", "move_right", "attack")},
                           "neural_wall_ms_per_step": statistics.fmean(r.neural_wall_ms for r in records)
                                                       if records else 0.0,
                           # One row per decision: what the network saw and what it pressed.
                           "trace": [{"monster_x": r.observation["monster_x"], "command": list(r.command),
                                      "readout_spikes": r.evidence["spikes"], "input_events": r.input_events,
                                      "network_spikes": r.network_spikes} for r in records]}
            results.append({"episode": episode, "seed": seed, **summary})
            print(json.dumps({k: v for k, v in results[-1].items() if k != "trace"}), flush=True)
    finally:
        if view is None:
            env.close()
    print(f"mean reward {statistics.fmean(r['reward'] for r in results):.1f} over {len(results)} episodes "
          f"({args.controller})", flush=True)
    if args.json_out:
        args.json_out.write_text(json.dumps({"arguments": {k: str(v) for k, v in vars(args).items()},
                                             "results": results}, indent=1))
    if view is not None:
        print("Episodes finished; the live view stays open. Stop this program to close it.", flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            view.close()
            env.close()


if __name__ == "__main__":
    main()
