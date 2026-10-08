"""Resolve real NT handles using a frozen drive map inside the Windows capsule."""
from __future__ import annotations

import ctypes
from ctypes import wintypes as W
import json
import ntpath
import os


def install(mapping_path):
    """Preserve native existence/link checks without querying the Mount Manager."""
    if os.name != 'nt' or getattr(ntpath._getfinalpathname, '_a025_nt_resolver', False):
        return
    import nt
    with open(mapping_path, encoding='utf-8') as stream:
        mapping = json.load(stream)
    assert set(mapping) == {'C:', 'D:'}
    assert len(set(mapping.values())) == len(mapping)
    assert all(value.startswith('\\Device\\HarddiskVolume') for value in mapping.values())
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p,
                                  W.DWORD, W.DWORD, W.HANDLE]
    kernel.CreateFileW.restype = W.HANDLE
    kernel.GetFinalPathNameByHandleW.argtypes = [W.HANDLE, W.LPWSTR, W.DWORD, W.DWORD]
    kernel.GetFinalPathNameByHandleW.restype = W.DWORD
    kernel.CloseHandle.argtypes = [W.HANDLE]

    def final_path(path):
        original = os.fspath(path)
        text = os.fsdecode(original)
        handle = kernel.CreateFileW(text, 0, 0, None, 3, 0x02000000, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            length = kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 2)
            if not length:
                raise ctypes.WinError(ctypes.get_last_error())
            if length >= len(buffer):
                raise ctypes.WinError(206)
            resolved = buffer.value
            for drive, device in mapping.items():
                if (resolved.casefold() == device.casefold()
                        or resolved.casefold().startswith(device.casefold() + '\\')):
                    result = '\\\\?\\' + drive + resolved[len(device):]
                    return os.fsencode(result) if isinstance(original, bytes) else result
            raise PermissionError('Native volume is outside the frozen drive map')
        finally:
            kernel.CloseHandle(handle)

    final_path._a025_nt_resolver = True
    nt._getfinalpathname = final_path
    ntpath._getfinalpathname = final_path
