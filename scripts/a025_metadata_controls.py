"""Temporary profile-only Windows namespace and directory metadata rights."""
from __future__ import annotations

import ctypes
from ctypes import wintypes as W


class UnicodeString(ctypes.Structure):
    _fields_ = [('length', W.WORD), ('maximum', W.WORD), ('buffer', W.LPWSTR)]


class ObjectAttributes(ctypes.Structure):
    _fields_ = [('length', W.ULONG), ('root', W.HANDLE),
                ('name', ctypes.POINTER(UnicodeString)), ('attributes', W.ULONG),
                ('security', ctypes.c_void_p), ('quality', ctypes.c_void_p)]


class Trustee(ctypes.Structure):
    _fields_ = [('multiple', ctypes.c_void_p), ('operation', ctypes.c_int),
                ('form', ctypes.c_int), ('kind', ctypes.c_int), ('name', ctypes.c_void_p)]


class ExplicitAccess(ctypes.Structure):
    _fields_ = [('permissions', W.DWORD), ('mode', ctypes.c_int),
                ('inheritance', W.DWORD), ('trustee', Trustee)]


class MetadataRights:
    """Grant namespace metadata without filesystem listing, contents, or inherited rights."""

    def __init__(self, sid, directories):
        self.sid, self.records = sid, []
        self.nt = ctypes.WinDLL('ntdll')
        self.adv = ctypes.WinDLL('advapi32', use_last_error=True)
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.nt.NtOpenDirectoryObject.argtypes = [ctypes.POINTER(W.HANDLE), W.DWORD,
                                                 ctypes.POINTER(ObjectAttributes)]
        self.nt.NtOpenSymbolicLinkObject.argtypes = self.nt.NtOpenDirectoryObject.argtypes
        self.nt.NtQuerySecurityObject.argtypes = [W.HANDLE, W.DWORD, ctypes.c_void_p,
                                                 W.DWORD, ctypes.POINTER(W.DWORD)]
        self.nt.NtSetSecurityObject.argtypes = [W.HANDLE, W.DWORD, ctypes.c_void_p]
        self.adv.GetSecurityDescriptorDacl.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.BOOL),
                                                       ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(W.BOOL)]
        self.adv.GetSecurityDescriptorControl.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.WORD), ctypes.POINTER(W.DWORD)]
        self.adv.SetEntriesInAclW.argtypes = [W.ULONG, ctypes.POINTER(ExplicitAccess), ctypes.c_void_p,
                                            ctypes.POINTER(ctypes.c_void_p)]
        self.adv.InitializeSecurityDescriptor.argtypes = [ctypes.c_void_p, W.DWORD]
        self.adv.SetSecurityDescriptorDacl.argtypes = [ctypes.c_void_p, W.BOOL, ctypes.c_void_p, W.BOOL]
        self.adv.SetSecurityDescriptorControl.argtypes = [ctypes.c_void_p, W.WORD, W.WORD]
        self.kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p,
                                          W.DWORD, W.DWORD, W.HANDLE]
        self.kernel.CreateFileW.restype = W.HANDLE
        self.kernel.CloseHandle.argtypes = [W.HANDLE]
        self.kernel.LocalFree.argtypes = [ctypes.c_void_p]
        try:
            self.object('\\GLOBAL??', False, 0x20003)
            for name in ('C:', 'D:', 'MountPointManager', 'NUL'):
                self.object('\\GLOBAL??\\' + name, True, 0x20001)
            self.file('\\\\.\\MountPointManager', 0x120089, False)
            self.file('\\\\.\\NUL', 0x120089, False)
            for directory in directories:
                self.file(str(directory), 0x1000A0, True)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def require(status):
        if status < 0:
            raise OSError('Native metadata control failed: NTSTATUS ' + hex(status & 0xffffffff))

    def security(self, handle):
        size = W.DWORD()
        self.nt.NtQuerySecurityObject(handle, 4, None, 0, ctypes.byref(size))
        assert 0 < size.value < 1024 * 1024
        descriptor = ctypes.create_string_buffer(size.value)
        self.require(self.nt.NtQuerySecurityObject(handle, 4, descriptor, len(descriptor), ctypes.byref(size)))
        return descriptor

    def edit(self, handle, mode, permissions):
        descriptor = self.security(handle)
        present, defaulted, old_acl = W.BOOL(), W.BOOL(), ctypes.c_void_p()
        assert self.adv.GetSecurityDescriptorDacl(descriptor, ctypes.byref(present),
                                                 ctypes.byref(old_acl), ctypes.byref(defaulted))
        assert present.value and old_acl.value
        entry = ExplicitAccess(permissions, mode, 0, Trustee(None, 0, 0, 0, self.sid))
        new_acl = ctypes.c_void_p()
        error = self.adv.SetEntriesInAclW(1, ctypes.byref(entry), old_acl, ctypes.byref(new_acl))
        if error:
            raise ctypes.WinError(error)
        try:
            updated = ctypes.create_string_buffer(64)
            assert self.adv.InitializeSecurityDescriptor(updated, 1)
            assert self.adv.SetSecurityDescriptorDacl(updated, True, new_acl, False)
            control, revision = W.WORD(), W.DWORD()
            assert self.adv.GetSecurityDescriptorControl(descriptor, ctypes.byref(control), ctypes.byref(revision))
            assert self.adv.SetSecurityDescriptorControl(updated, 0x1500, control.value & 0x1500)
            self.require(self.nt.NtSetSecurityObject(handle, 4, updated))
        finally:
            self.kernel.LocalFree(new_acl)

    def retain(self, handle, name, permissions):
        try:
            self.edit(handle, 1, permissions)
        except BaseException:
            self.kernel.CloseHandle(handle)
            raise
        self.records.append((handle, name, permissions))

    def object(self, name, symbolic, permissions):
        buffer = ctypes.create_unicode_buffer(name)
        text = UnicodeString(len(name) * 2, (len(name) + 1) * 2, ctypes.cast(buffer, W.LPWSTR))
        attributes = ObjectAttributes(ctypes.sizeof(ObjectAttributes), None, ctypes.pointer(text), 0x40, None, None)
        handle = W.HANDLE()
        opener = self.nt.NtOpenSymbolicLinkObject if symbolic else self.nt.NtOpenDirectoryObject
        self.require(opener(ctypes.byref(handle), 0x60000 | (1 if symbolic else 3), ctypes.byref(attributes)))
        self.retain(handle, name, permissions)

    def file(self, name, permissions, directory):
        handle = self.kernel.CreateFileW(name, 0x60000, 7, None, 3, 0x02000000 if directory else 0, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        self.retain(handle, name, permissions)

    def close(self):
        errors = []
        while self.records:
            handle, name, permissions = self.records.pop()
            try:
                self.edit(handle, 4, 0)
            except BaseException as error:
                errors.append((name, repr(error)))
            finally:
                self.kernel.CloseHandle(handle)
        if errors:
            raise RuntimeError('Metadata SID cleanup failed: ' + repr(errors))
