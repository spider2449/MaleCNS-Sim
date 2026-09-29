"""Verify CuPy allocation, arithmetic, NVRTC compilation, and backend imports."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import cupy as cp

        device_count = int(cp.cuda.runtime.getDeviceCount())
        if device_count < 1:
            raise RuntimeError("no CUDA device is visible")
        device_id = int(cp.cuda.runtime.getDevice())
        properties = cp.cuda.runtime.getDeviceProperties(device_id)
        device_name_value = properties.get("name", b"unknown")
        device_name = (
            device_name_value.decode(errors="replace")
            if isinstance(device_name_value, bytes)
            else str(device_name_value)
        )
        values = cp.asarray([1.25, 2.5, 4.0], dtype=cp.float64)
        computed = cp.square(values) + cp.float64(0.5)
        kernel = cp.RawKernel(
            'extern "C" __global__ void task017_preflight(const double* x, double* y) '
            "{ if (threadIdx.x == 0) y[0] = x[0] * 2.0; }",
            "task017_preflight",
        )
        output = cp.zeros((1,), dtype=cp.float64)
        kernel((1,), (1,), (values, output))
        cp.cuda.Stream.null.synchronize()
        host_values = cp.asnumpy(computed)
        host_kernel = cp.asnumpy(output)
        if host_values.tolist() != [2.0625, 6.75, 16.5] or host_kernel.tolist() != [2.5]:
            raise RuntimeError("GPU arithmetic or compiled-kernel result did not match the expected values")
        from malecns_sim.dynamics.cuda import _schedule_kernel, cuda_available

        if not cuda_available():
            raise RuntimeError("MaleCNS-Sim CUDA backend reports no available device")
        _schedule_kernel(cp).compile()
        cp.cuda.Stream.null.synchronize()
        print(f"CuPy: {cp.__version__}")
        print(f"CUDA device: {device_name} (id={device_id}, count={device_count})")
        print("NVRTC: compiled preflight and MaleCNS-Sim schedule kernels")
        print("GPU_READY")
        return 0
    except Exception as exc:
        print(f"GPU_PREFLIGHT_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
