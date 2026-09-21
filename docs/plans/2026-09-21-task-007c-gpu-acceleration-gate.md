# Task 007c - Prepared Graph Cache and RTX 3060 CUDA Acceleration Gate

Status: complete

## Scope

This task evaluates prepared-network reuse and an optional CUDA backend for the
validated Task 005 LIF dynamics. The NumPy CPU implementation remains the
scientific reference. Task 008 is not run or restored from its paused stash.

## Checkpoint

- Branch: `master`
- Starting HEAD: `3336162c902a40a7bfd86624ef8d08bb4f064015`
- Baseline: `123 passed`
- Preserved stash: `task008-paused-before-gpu-gate`

## Environment

The checkpoint baseline was `123 passed` on Python 3.14.0. The host has an
NVIDIA GeForce RTX 3060 with 12,288 MiB VRAM, driver 581.15, and
`nvidia-smi` compatibility CUDA 13.0. The installed Toolkit is CUDA 12.4
(`nvcc` 12.4.99) at `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4`.
`CUDA_PATH` points to that installation. CuPy 14.2.0 was installed as the
normal `cupy-cuda12x==14.2.0` optional wheel; both linked CUDA runtime 12.9
and local runtime 12.4 were reported, with NVRTC 12.4. The device compute
capability is 8.6. The CUDA sanity gate allocated float64 arrays and produced
the correct copied result `[2.0, 5.0]`.

## Cache and backend design

`PreparedGraphCache` stores immutable neuron IDs, CSR `indptr`, CSR indices,
and float64 effective signed weights in a compressed NPZ. Its identity includes
the MaleCNS release, curated graph fingerprint, Task 004 sign-policy
fingerprint, unresolved-edge policy, `min_synapses`, synaptic weight, LIF
parameter identity, and cache schema version. A stored content fingerprint and
an expected-identity comparison make stale or mismatched loads fail closed.
Membrane state, conductance, refractory state, delay buffers, RNG state, and
trial results are never cached.

The optional CUDA module keeps the CPU reference unchanged. It uploads the
CSR graph once, using int32 indices because the measured graph bounds are
safe, and processes only outgoing CSR rows for active presynaptic spikes. A
float64 dense delay ring is maintained independently per trial. GPU kernel
launches are synchronized before measurements and after each benchmarked
simulation.

## Equivalence and performance results

The full local graph contains 166,700 neurons and 6,113,545 effective CSR
edges. Cold raw Feather loading/projection took 262.97 s and reached about
23.7 GB Python working set. Cache serialization took 2.126 s, produced a
23,973,200-byte file, and warm load took 0.402 s. Cache fingerprint:
`f73867d2dd7565d1c1e00395b1d421190dcacededbd42922439606179350bdac`.

Measured CUDA allocation deltas were approximately 74 MiB for graph-only,
48 MiB for graph plus one-trial state/delay buffers, and 1,209 MiB for the
batch-30 state/delay allocation; the corresponding theoretical state sizes
were 94.7 MiB, 40.1 MiB, and 1,202 MiB. All requested batch sizes 1, 4, 8,
16, and 30 fit safely in the 12 GB device. A synchronized runtime sample
observed 2,484 MiB used during the real workload, leaving substantial
headroom. Batch 30 was fastest at 4.13 trials/s.

All synthetic equivalence cases passed with exact canonical spike events and
documented tight float64 state tolerances. The bounded full MaleCNS graph
check passed for CPU versus GPU emitted events, counts, and repeated digest.
The representative Task 007 sugar-population 100 Hz schedule was generated
once on CPU and fed unchanged to both backends. Digests matched for both 100 ms and 1,000 ms:
`8c35f92f5865d047a114b2f4603c994c9aaef23aebf23dae241f841e2e359e2d` and
`aa3c0e97a3b92d5805ffed98e346190c73b03bc49f570432d766e62ba5baaca7`.

| Workload | CPU | GPU | Simulation speedup |
| --- | ---: | ---: | ---: |
| 1 trial, 100 ms | 7.318 s | 1.660 s | 4.41x |
| 1 trial, 1,000 ms | 86.408 s | 15.139 s | 5.71x |
| 30 trials, 100 ms | 221.810 s serial | 7.263 s batch 30 | 30.54x |

Including warm cache load and graph upload, the corresponding end-to-end
speedups were 4.55x, 5.72x, and 30.44x. Float32 was not attempted after the
float64 gate; float64 remains the scientific mode.

## Decision

`GPU_READY`

CuPy runs reliably, synthetic and real-graph equivalence passes, repeated GPU
digests are stable, the measured acceleration is useful, and VRAM remains
safe. CuPy is therefore available only through the optional `gpu` dependency
group; normal CPU installation and tests do not require it. Task 008 may use
the CUDA backend, but Task 008 itself was not run in this task.

## Validation

The dedicated Task 007c suite passed with `14 passed, 1 skipped` when the
optional full-graph test is not selected. The skipped test is the explicit
`MALECNS_TASK007C_REAL=1` gate; that gate was run separately and passed. The
final validation was `uv run python -m compileall src` followed by
`uv run python -m pytest -v`: `137 passed, 1 skipped in 5.70 s`. The explicit
CUDA selection passed with `12 passed, 1 skipped, 2 deselected in 1.45 s`.
`git diff --check` passed. The working tree remains uncommitted and the
`task008-paused-before-gpu-gate` stash remains present.
