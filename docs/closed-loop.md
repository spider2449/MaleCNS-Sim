# Generic closed loop and ViZDoom

`malecns_sim.application.closed_loop` couples the prepared LIF runtime to any environment:
observation -> `SensoryEncoder` (direct spike schedules) -> `runtime.advance(neural_ms_per_step)`
-> `MotorDecoder` (spike counts -> command) -> `Environment.step`. There is no plasticity, and
every sensory and motor mapping is engineered. None of it is a biological claim.

## ViZDoom `basic.cfg`

Environment: `application/vizdoom_env.py` (`ViZDoomBasic`). Buttons are MOVE_LEFT, MOVE_RIGHT and
ATTACK. The monster's horizontal bearing (label buffer) sets the LC4 left/right input rates.

```
D:\spider\vizdoom-env\Scripts\python.exe scripts\run_vizdoom.py --controller network --episodes 3 --view
```

The environment needs `pip install vizdoom` in an isolated Python 3.12 environment outside the
checkout, with the project installed editable. `--controller random|noop|attack` skip the network
and give baselines. `--view` serves a loopback, token-protected live page (circuit graph, raster,
rates, game frame). The first run prepares the real network (about 5 minutes, about 20 GB peak RAM).

Readouts: `screened` (default) uses DNp04 left/right for movement and DNg33 for attack, chosen by
a screen of the descending neurons under biased LC4 input. `flight` reuses the flight DNp03/DNg02 IDs
and almost never attacks. `--move-threshold-hz 100` requires two spikes in a 10 ms window.

## Results (held-out seeds 100-129, 30 episodes each, 75 decisions max)

| Policy | Mean reward | Median | Episodes with a kill |
|---|---|---|---|
| Network, frame-skip 2, move threshold 100 Hz | -86.0 | 16 | 18 / 30 |
| Network, frame-skip 4, threshold 0 | -159.9 | -300 | 12 / 30 |
| Random, frame-skip 2 | -65.0 | 38 | 23 / 30 |
| Random, frame-skip 4 | -86.4 | 14 | 23 / 30 |
| Attack only | -127.0 | 95 | 17 / 30 |

The tuned configuration beats the untuned one (paired mean +73.9, Wilcoxon p = 0.004) but is
statistically indistinguishable from random pressing (Mann-Whitney p = 0.48, 95% bootstrap CI of the
mean difference -112 to +74). The scenario rewards random play, so the score does not show that
the network aims. Treat this as a working interface, not as a competent player.
