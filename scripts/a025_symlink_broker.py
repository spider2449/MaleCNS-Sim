"""Host broker for genuine, bounded synthetic file symlink creation only."""
from __future__ import annotations

import ctypes
from ctypes import wintypes as W
import http.server
import json
import os
from pathlib import Path
import secrets
import stat
import threading
from contextlib import contextmanager


class SyntheticSymlinkBroker:
    """Never read target contents or grant a child Windows privileges."""

    def __init__(self, temporary):
        self.root = Path(temporary).resolve(strict=True)
        self.secret = secrets.token_hex(32)
        self.receipts = []
        broker = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                try:
                    if self.path != '/synthetic-file-link' or self.headers.get('Authorization') != broker.secret:
                        raise PermissionError('Broker authorization rejected')
                    size = int(self.headers.get('Content-Length', '0'))
                    if not 0 < size <= 4096:
                        raise ValueError('Invalid broker request size')
                    body = json.loads(self.rfile.read(size))
                    if set(body) != {'target', 'link'}:
                        raise ValueError('Invalid broker fields')
                    target = broker.checked(body['target'], 'outside.py', True)
                    link = broker.checked(body['link'], 'link.py', False)
                    with broker.metadata_locks([broker.root, target.parent, link.parent, target]):
                        target = broker.checked(body['target'], 'outside.py', True)
                        link = broker.checked(body['link'], 'link.py', False)
                        os.symlink(target, link, target_is_directory=False)
                        metadata = link.lstat()
                        observed = os.readlink(link).removeprefix('\\\\?\\')
                        if not stat.S_ISLNK(metadata.st_mode) or os.path.normcase(observed) != os.path.normcase(str(target)):
                            raise RuntimeError('Native link identity mismatch')
                    broker.receipts.append({'target': str(target), 'link': str(link),
                                            'native_symlink': True, 'content_reads': 0})
                    data = b'{"status":"PASS"}'
                    self.send_response(200)
                except Exception as error:
                    data = json.dumps({'status': 'DENIED', 'error': type(error).__name__}).encode()
                    self.send_response(403)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = False
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    @contextmanager
    def metadata_locks(self, paths):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p,
                                      W.DWORD, W.DWORD, W.HANDLE]
        kernel.CreateFileW.restype = W.HANDLE
        kernel.CloseHandle.argtypes = [W.HANDLE]
        handles = []
        try:
            for path in dict.fromkeys(paths):
                # Metadata only; exclude write/delete sharing during validation/create.
                handle = kernel.CreateFileW(str(path), 0x80, 1, None, 3, 0x02200000, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise ctypes.WinError(ctypes.get_last_error())
                handles.append(handle)
            yield
        finally:
            for handle in reversed(handles):
                kernel.CloseHandle(handle)

    def checked(self, value, filename, existing):
        if not isinstance(value, str) or '\x00' in value:
            raise ValueError('Invalid synthetic path')
        path = Path(value)
        if not path.is_absolute() or path.name != filename or '..' in path.parts:
            raise PermissionError('Not an admitted synthetic file')
        relative = path.relative_to(self.root)
        if len(relative.parts) != 2 or not relative.parts[0].startswith('tmp'):
            raise PermissionError('Not an immediate temporary fixture')
        for parent in (self.root, path.parent):
            metadata = parent.lstat()
            if not stat.S_ISDIR(metadata.st_mode) or metadata.st_file_attributes & 0x400:
                raise PermissionError('Reparse parent rejected')
        if existing:
            metadata = path.lstat()
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_file_attributes & 0x400 or metadata.st_nlink != 1:
                raise PermissionError('Nonordinary synthetic target rejected')
        elif os.path.lexists(path):
            raise PermissionError('Existing link destination rejected')
        return path

    def environment(self):
        return {'MALECNS_A025_SYMLINK_URL': 'http://127.0.0.1:' + str(self.server.server_port)
                + '/synthetic-file-link', 'MALECNS_A025_SYMLINK_TOKEN': self.secret}

    def close(self):
        self.server.shutdown()
        self.thread.join(timeout=10)
        self.server.server_close()
        if self.thread.is_alive():
            raise RuntimeError('Synthetic broker thread remains active')
