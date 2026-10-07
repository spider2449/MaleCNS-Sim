"""Real suspended-process cleanup control without resuming a profiler workload."""
import ctypes
from ctypes import wintypes as w
from pathlib import Path
import sys
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import profile_application_a019x as profile


def test_assignment_failure_terminates_unassigned_suspended_root(monkeypatch):
    original = ctypes.WinDLL
    kernel = original('kernel32', use_last_error=True)
    captured = {}
    native_create = kernel.CreateProcessW

    def create(*args):
        native_create.argtypes = create.argtypes
        result = native_create(*args)
        if result:
            captured['pid'] = int(args[-1]._obj.pid)
        return result

    def reject(*args):
        ctypes.set_last_error(5)
        return 0

    class Proxy:
        CreateProcessW = staticmethod(create)
        AssignProcessToJobObject = staticmethod(reject)

        def __getattr__(self, name):
            return getattr(kernel, name)

    monkeypatch.setattr(ctypes, 'WinDLL', lambda name, **kwargs: Proxy() if name == 'kernel32'
                        else original(name, **kwargs))
    with tempfile.TemporaryDirectory(prefix='malecns-a019x-') as directory:
        output = profile.output_root(directory)
        with pytest.raises(OSError):
            profile.NativeJob(output, 'control', 'success')
        assert captured.get('pid')
        assert not (output / 'control-success-ready.json').exists()
        kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        kernel.OpenProcess.restype = w.HANDLE
        handle = kernel.OpenProcess(0x100000, False, captured['pid'])
        try:
            assert not handle or kernel.WaitForSingleObject(handle, 0) == 0
        finally:
            if handle:
                kernel.CloseHandle(handle)
