"""Request a genuine host-created symlink for the isolated synthetic fixture."""
from __future__ import annotations
import json
import os


def install():
    if os.name != 'nt' or not os.environ.get('MALECNS_A025_SYMLINK_URL'):
        return
    original = os.symlink

    def symlink(src, dst, target_is_directory=False, *, dir_fd=None):
        try:
            return original(src, dst, target_is_directory, dir_fd=dir_fd)
        except OSError as error:
            if error.winerror != 1314 or target_is_directory or dir_fd is not None:
                raise
            from pathlib import Path
            if Path(os.fsdecode(src)).name != 'outside.py' or Path(os.fsdecode(dst)).name != 'link.py':
                raise
            import urllib.request
            body = json.dumps({'target': os.fsdecode(src), 'link': os.fsdecode(dst)}).encode()
            request = urllib.request.Request(os.environ['MALECNS_A025_SYMLINK_URL'], data=body,
                headers={'Authorization': os.environ['MALECNS_A025_SYMLINK_TOKEN']}, method='POST')
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=10) as response:
                if json.loads(response.read(1024)) != {'status': 'PASS'}:
                    raise RuntimeError('Synthetic native link broker rejected fixture')

    os.symlink = symlink
