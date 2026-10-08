"""Preserve capsule SID inheritance for private temporary directories on Windows."""
from __future__ import annotations

import os
from pathlib import Path


def install(roots):
    """Adjust only task-owned temporary creation, never existing or source ACLs."""
    if os.name != 'nt' or getattr(os.mkdir, '_a025_temp_compat', False):
        return
    roots = tuple(Path(root).resolve() for root in roots)
    original = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        if mode == 0o700 and dir_fd is None:
            target = Path(os.fsdecode(path)).resolve()
            if any(target.is_relative_to(root) for root in roots):
                # CPython 3.14's private-directory ACL omits the capsule SID.
                # Inherit the dedicated output parent's explicit SID grant.
                mode = 0o755
        return original(path, mode, dir_fd=dir_fd)

    mkdir._a025_temp_compat = True
    os.mkdir = mkdir
