"""Synthetic Windows AppContainer/Job controls without project workloads."""
from __future__ import annotations

import ctypes
from ctypes import wintypes as W
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid


class Startup(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR),
                ('title', W.LPWSTR), ('x', W.DWORD), ('y', W.DWORD), ('width', W.DWORD),
                ('height', W.DWORD), ('chars_x', W.DWORD), ('chars_y', W.DWORD),
                ('fill', W.DWORD), ('flags', W.DWORD), ('show', W.WORD),
                ('reserved_size', W.WORD), ('reserved_bytes', ctypes.c_void_p),
                ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]


class StartupEx(ctypes.Structure):
    _fields_ = [('startup', Startup), ('attributes', ctypes.c_void_p)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]


class Capabilities(ctypes.Structure):
    _fields_ = [('sid', ctypes.c_void_p), ('capabilities', ctypes.c_void_p),
                ('count', W.DWORD), ('reserved', W.DWORD)]


class SidAttributes(ctypes.Structure):
    _fields_ = [('sid', ctypes.c_void_p), ('attributes', W.DWORD)]


class SecurityAttributes(ctypes.Structure):
    _fields_ = [('size', W.DWORD), ('descriptor', ctypes.c_void_p), ('inherit', W.BOOL)]


def private_desktop(sid):
    """Keep restricted workloads away from the host's interactive desktop."""
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.GetProcessWindowStation.restype = W.HANDLE
    user.CreateWindowStationW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.POINTER(SecurityAttributes)]
    user.CreateWindowStationW.restype = W.HANDLE
    user.SetProcessWindowStation.argtypes = [W.HANDLE]
    user.CreateDesktopW.argtypes = [W.LPCWSTR, ctypes.c_void_p, ctypes.c_void_p, W.DWORD,
                                  W.DWORD, ctypes.POINTER(SecurityAttributes)]
    user.CreateDesktopW.restype = W.HANDLE
    user.CloseDesktop.argtypes = [W.HANDLE]
    user.CloseWindowStation.argtypes = [W.HANDLE]
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    adv.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, ctypes.POINTER(W.HANDLE)]
    adv.GetTokenInformation.argtypes = [W.HANDLE, ctypes.c_int, ctypes.c_void_p, W.DWORD, ctypes.POINTER(W.DWORD)]
    adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.LPWSTR)]
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [W.LPCWSTR, W.DWORD,
                                                                       ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
    kernel = api()
    kernel.GetCurrentProcess.restype = W.HANDLE
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    token, size = W.HANDLE(), W.DWORD()
    own_text, app_text, descriptor = W.LPWSTR(), W.LPWSTR(), ctypes.c_void_p()
    station = desktop = None
    original = user.GetProcessWindowStation()
    name = 'MaleCNSA025_' + uuid.uuid4().hex
    try:
        require(adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)))
        adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
        data = ctypes.create_string_buffer(size.value)
        require(adv.GetTokenInformation(token, 1, data, size, ctypes.byref(size)))
        own_sid = ctypes.cast(data, ctypes.POINTER(SidAttributes)).contents.sid
        require(adv.ConvertSidToStringSidW(own_sid, ctypes.byref(own_text)))
        require(adv.ConvertSidToStringSidW(sid, ctypes.byref(app_text)))
        sddl = ('D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;GA;;;' + own_text.value + ')(A;;GA;;;'
                + app_text.value + ')S:(ML;;NW;;;LW)')
        require(adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None))
        security = SecurityAttributes(ctypes.sizeof(SecurityAttributes), descriptor, False)
        station = user.CreateWindowStationW(name, 0, 0xF037F, ctypes.byref(security))
        require(station)
        require(user.SetProcessWindowStation(station))
        desktop = user.CreateDesktopW('Default', None, None, 0, 0xF01FF, ctypes.byref(security))
        require(desktop)
        return user, station, desktop, name + '\\Default'
    except BaseException:
        if desktop:
            user.CloseDesktop(desktop)
        if station:
            user.SetProcessWindowStation(original)
            user.CloseWindowStation(station)
        raise
    finally:
        require(user.SetProcessWindowStation(original))
        if token:
            kernel.CloseHandle(token)
        for pointer in (own_text, app_text, descriptor):
            if pointer:
                kernel.LocalFree(pointer)


def api():
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.InitializeProcThreadAttributeList.argtypes = [ctypes.c_void_p, W.DWORD, W.DWORD, ctypes.POINTER(ctypes.c_size_t)]
    kernel.UpdateProcThreadAttribute.argtypes = [ctypes.c_void_p, W.DWORD, ctypes.c_size_t,
                                                ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
    kernel.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
    kernel.CreateProcessW.argtypes = [W.LPCWSTR, W.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        W.BOOL, W.DWORD, ctypes.c_void_p, W.LPCWSTR, ctypes.POINTER(StartupEx), ctypes.POINTER(ProcessInfo)]
    kernel.WaitForSingleObject.argtypes = [W.HANDLE, W.DWORD]
    kernel.GetExitCodeProcess.argtypes = [W.HANDLE, ctypes.POINTER(W.DWORD)]
    kernel.CloseHandle.argtypes = [W.HANDLE]
    kernel.ResumeThread.argtypes = [W.HANDLE]
    kernel.TerminateProcess.argtypes = [W.HANDLE, W.UINT]
    return kernel


def require(success):
    if not success:
        raise ctypes.WinError(ctypes.get_last_error())


def prepare_tempfile_compat(tools):
    """Seed an explicit startup control only in the staged trusted runtime."""
    tools = Path(tools)
    helper = Path(__file__).with_name('a025_tempfile_compat.py')
    site = tools / 'Lib/site-packages'
    site.mkdir(exist_ok=True)
    shutil.copy2(helper, site / 'a025_tempfile_compat.py')
    shutil.copy2(helper.with_name('a025_path_compat.py'), site / 'a025_path_compat.py')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.QueryDosDeviceW.argtypes = [W.LPCWSTR, W.LPWSTR, W.DWORD]
    mapping = {}
    for drive in ('C:', 'D:'):
        buffer = ctypes.create_unicode_buffer(32768)
        require(kernel.QueryDosDeviceW(drive, buffer, len(buffer)))
        mapping[drive] = buffer.value
    (site / 'a025-volume-map.json').write_text(json.dumps(mapping, sort_keys=True) + '\n')
    (site / 'a025-path-compat.pth').write_text(
        "import a025_path_compat as _a025_path; import os as _a025_path_os; _a025_path.install(_a025_path_os.path.join(_a025_path_os.path.dirname(_a025_path.__file__), 'a025-volume-map.json'))\n",
        encoding='utf-8')
    (site / 'a025-tempfile-compat.pth').write_text(
        "import a025_tempfile_compat as _a025; import os as _a025_os; _a025.install([_a025_os.environ['TEMP'], _a025_os.environ['MALECNS_A025_OUTPUT']])\n",
        encoding='utf-8')


def launch(python, script, output, sid, job, internet=False, timeout_ms=60000, extra_environment=None):
    kernel = api()
    size = ctypes.c_size_t()
    kernel.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
    attributes = ctypes.create_string_buffer(size.value)
    require(kernel.InitializeProcThreadAttributeList(attributes, 1, 0, ctypes.byref(size)))
    security = Capabilities(sid, None, 0, 0)
    internet_sid = ctypes.c_void_p()
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    adv.ConvertStringSidToSidW.argtypes = [W.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
    adv.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, ctypes.POINTER(W.HANDLE)]
    adv.GetTokenInformation.argtypes = [W.HANDLE, ctypes.c_int, ctypes.c_void_p, W.DWORD, ctypes.POINTER(W.DWORD)]
    adv.CreateProcessAsUserW.argtypes = [W.HANDLE, W.LPCWSTR, W.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        W.BOOL, W.DWORD, ctypes.c_void_p, W.LPCWSTR, ctypes.POINTER(StartupEx), ctypes.POINTER(ProcessInfo)]
    adv.CreateRestrictedToken.argtypes = [W.HANDLE, W.DWORD, W.DWORD, ctypes.c_void_p,
        W.DWORD, ctypes.c_void_p, W.DWORD, ctypes.c_void_p, ctypes.POINTER(W.HANDLE)]
    adv.SetTokenInformation.argtypes = [W.HANDLE, ctypes.c_int, ctypes.c_void_p, W.DWORD]
    adv.GetLengthSid.argtypes = [ctypes.c_void_p]
    adv.GetLengthSid.restype = W.DWORD
    kernel.GetCurrentProcess.restype = W.HANDLE
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    if internet:
        require(adv.ConvertStringSidToSidW('S-1-15-3-1', ctypes.byref(internet_sid)))
        internet_capability = SidAttributes(internet_sid, 4)
        security.capabilities = ctypes.cast(ctypes.pointer(internet_capability), ctypes.c_void_p)
        security.count = 1
    process = ProcessInfo()
    startup = StartupEx()
    startup.startup.cb = ctypes.sizeof(startup)
    startup.attributes = ctypes.cast(attributes, ctypes.c_void_p)
    environment = dict(SYSTEMROOT=os.environ['SYSTEMROOT'], WINDIR=os.environ['WINDIR'],
                       TEMP=str(output), TMP=str(output), HOME=str(output), USERPROFILE=os.environ['USERPROFILE'],
                       LOCALAPPDATA=os.environ['LOCALAPPDATA'], APPDATA=os.environ['APPDATA'],
                       SystemDrive=os.environ['SystemDrive'],
                       MALECNS_A025_OUTPUT=str(output),
                       PROCESSOR_ARCHITECTURE=os.environ['PROCESSOR_ARCHITECTURE'],
                       NUMBER_OF_PROCESSORS=os.environ['NUMBER_OF_PROCESSORS'],
                       COMSPEC=os.environ['COMSPEC'],
                       CUPY_CACHE_DIR=str(output / 'cupy-cache'), CUDA_CACHE_PATH=str(output / 'cuda-cache'),
                       PATH=str(python.parent) + os.pathsep + os.environ['SYSTEMROOT'] + '/System32',
                       PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    if extra_environment:
        environment.update(extra_environment)
    block = ctypes.create_unicode_buffer('\0'.join(key + '=' + value for key, value in sorted(environment.items(), key=lambda item: item[0].upper())) + '\0\0')
    command = ctypes.create_unicode_buffer(subprocess.list2cmdline([str(python), '-I', '-S', '-B', str(script), str(output)]))
    created = False
    current_token, linked_token = W.HANDLE(), W.HANDLE()
    administrator_sid, integrity_sid = ctypes.c_void_p(), ctypes.c_void_p()
    desktop_objects = None
    try:
        desktop_objects = private_desktop(sid)
        startup.startup.desktop = desktop_objects[3]
        require(kernel.UpdateProcThreadAttribute(attributes, 0, 0x20009,
            ctypes.byref(security), ctypes.sizeof(security), None, None))
        require(kernel.CreateProcessW(str(python), command, None, None, False,
            0x80000 | 0x400 | 0x4 | 0x08000000, block, str(output), ctypes.byref(startup), ctypes.byref(process)))
        created = True
        carrier = type('SuspendedProcess', (), {'pid': process.pid, '_handle': process.process})()
        job.assign_resume(carrier)
        if kernel.WaitForSingleObject(process.process, timeout_ms) != 0:
            raise RuntimeError('synthetic process timeout')
        code = W.DWORD()
        require(kernel.GetExitCodeProcess(process.process, ctypes.byref(code)))
        deadline = time.monotonic() + 5
        accounting = job.accounting()
        while accounting['active'] and time.monotonic() < deadline:
            time.sleep(0.02)
            accounting = job.accounting()
        return {'pid': process.pid, 'exit': code.value, 'job': accounting}
    finally:
        if created:
            kernel.TerminateProcess(process.process, 79)
            kernel.WaitForSingleObject(process.process, 10000)
            kernel.CloseHandle(process.thread)
            kernel.CloseHandle(process.process)
        kernel.DeleteProcThreadAttributeList(attributes)
        if internet_sid:
            kernel.LocalFree(internet_sid)
        if current_token:
            kernel.CloseHandle(current_token)
        if linked_token:
            kernel.CloseHandle(linked_token)
        if administrator_sid:
            kernel.LocalFree(administrator_sid)
        if integrity_sid:
            kernel.LocalFree(integrity_sid)
        if desktop_objects:
            user, station, desktop, _ = desktop_objects
            require(user.CloseDesktop(desktop))
            require(user.CloseWindowStation(station))


def main():
    route_controls = sys.argv[1:] == ['--route-controls']
    gpu_probe = route_controls or sys.argv[1:] == ['--gpu-probe']
    if sys.argv[1:] and not gpu_probe:
        raise SystemExit('invalid synthetic isolation control mode')
    root = Path('C:/TEMP') / ('malecns-a025-windows-' + uuid.uuid4().hex)
    root.mkdir()
    tools, inputs, output = root / 'tools', root / 'input', root / 'output'
    tools.mkdir()
    inputs.mkdir()
    output.mkdir()
    if route_controls:
        shutil.copy2(shutil.which('uv'), tools / 'uv.exe')
        shutil.copy2('C:/Windows/System32/curl.exe', tools / 'curl.exe')
    runtime = Path(sys._base_executable).parent
    for name in ('python.exe', 'python3.dll', 'python314.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'):
        shutil.copy2(runtime / name, tools / name)
    for name in ('Lib', 'DLLs'):
        shutil.copytree(runtime / name, tools / name,
                        ignore=shutil.ignore_patterns('__pycache__', 'site-packages'))
    prepare_tempfile_compat(tools)
    if gpu_probe:
        packages = Path(__file__).resolve().parents[1] / '.venv/Lib/site-packages'
        for name in ('numpy', 'numpy.libs', 'cupy', 'cupyx', 'cupy_backends', 'cuda', 'nvidia'):
            shutil.copytree(packages / name, tools / 'Lib/site-packages' / name,
                           ignore=shutil.ignore_patterns('__pycache__'))
    (inputs / 'ordinary.txt').write_text('ordinary-control', encoding='utf-8')
    sentinel = root / 'ungranted-sentinel.txt'
    sentinel.write_text('synthetic-secret', encoding='utf-8')
    probe = '''import ctypes, json, pathlib, subprocess, sys, traceback
from ctypes import wintypes as W
out = pathlib.Path(sys.argv[1])
try:
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = W.HANDLE
    adv.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, ctypes.POINTER(W.HANDLE)]
    adv.GetTokenInformation.argtypes = [W.HANDLE, ctypes.c_int, ctypes.c_void_p, W.DWORD, ctypes.POINTER(W.DWORD)]
    token = W.HANDLE()
    assert adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token))
    actual, size = W.DWORD(), W.DWORD()
    assert adv.GetTokenInformation(token, 29, ctypes.byref(actual), ctypes.sizeof(actual), ctypes.byref(size))
    assert actual.value == 1
    elevated = W.DWORD()
    assert adv.GetTokenInformation(token, 20, ctypes.byref(elevated), ctypes.sizeof(elevated), ctypes.byref(size))
    adv.LookupPrivilegeNameW.argtypes = [W.LPCWSTR, ctypes.c_void_p, W.LPWSTR, ctypes.POINTER(W.DWORD)]
    adv.GetTokenInformation(token, 3, None, 0, ctypes.byref(size))
    privileges = ctypes.create_string_buffer(size.value)
    assert adv.GetTokenInformation(token, 3, privileges, size, ctypes.byref(size))
    count = ctypes.cast(privileges, ctypes.POINTER(W.DWORD)).contents.value
    privilege_names = []
    for index in range(count):
        luid = ctypes.byref(privileges, 4 + index * 12)
        name, length = ctypes.create_unicode_buffer(128), W.DWORD(128)
        assert adv.LookupPrivilegeNameW(None, luid, name, ctypes.byref(length))
        privilege_names.append(name.value)
    assert set(privilege_names) <= {'SeChangeNotifyPrivilege', 'SeIncreaseWorkingSetPrivilege'}, privilege_names
    sys.path.insert(0, str(pathlib.Path(sys.executable).parent / 'Lib/site-packages'))
    import a025_path_compat
    a025_path_compat.install(pathlib.Path(a025_path_compat.__file__).with_name('a025-volume-map.json'))
    assert out.resolve(strict=True) == out
    assert pathlib.Path(INPUT).resolve(strict=True) == pathlib.Path(INPUT)
    assert pathlib.Path(INPUT).read_text() == 'ordinary-control'
    try:
        pathlib.Path(INPUT).write_text('forbidden')
    except PermissionError:
        pass
    else:
        raise RuntimeError('read-only input was writable')
    kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
    kernel.CreateFileW.restype = W.HANDLE
    handle = kernel.CreateFileW(SENTINEL, 0x80000000, 7, None, 3, 0, None)
    assert handle == ctypes.c_void_p(-1).value and ctypes.get_last_error() == 5
    native_roots = []
    for denied_root in DENIED_ROOTS:
        handle = kernel.CreateFileW(denied_root, 0x80000000, 7, None, 3, 0x02000000, None)
        assert handle == ctypes.c_void_p(-1).value and ctypes.get_last_error() == 5
        native_roots.append(denied_root)
    metadata_device_denials = []
    for device, access in DEVICE_DENIALS:
        handle = kernel.CreateFileW(device, access, 7, None, 3, 0, None)
        if handle != ctypes.c_void_p(-1).value:
            kernel.CloseHandle(handle)
            raise RuntimeError('Unexpected native device access: ' + device)
        assert ctypes.get_last_error() == 5
        metadata_device_denials.append(device)
    child = subprocess.run([sys.executable, '-I', '-S', '-B', '-c',
        "import ctypes,pathlib; p=pathlib.Path(" + repr(SENTINEL) + ");\\ntry: p.read_bytes()\\nexcept PermissionError: pass\\nelse: raise RuntimeError('child read escaped')"], timeout=20)
    assert child.returncode == 0
    (out / 'positive.txt').write_text('output-control')
    result = {'status': 'PASS', 'appcontainer_token': actual.value, 'native_denial': 'ERROR_ACCESS_DENIED',
              'child_denial': 'PASS', 'readonly_input': 'PASS', 'writable_output': 'PASS',
              'native_root_denials': native_roots, 'metadata_device_denials': metadata_device_denials, 'token_elevation_marker': elevated.value,
              'actual_token_privileges': privilege_names}
    if GPU_PROBE:
        sys.path.insert(0, str(pathlib.Path(sys.executable).parent / 'Lib/site-packages'))
        import cupy
        result['gpu_device_count'] = cupy.cuda.runtime.getDeviceCount()
        result['cupy_version'] = cupy.__version__
        assert result['gpu_device_count'] >= 1
    if ROUTE_CONTROLS:
        version = subprocess.run([str(pathlib.Path(sys.executable).parent / 'uv.exe'), '--version'],
                                  capture_output=True, text=True, timeout=20, check=True)
        result['uv'] = version.stdout.strip()
        query = subprocess.run([str(pathlib.Path(sys.executable).parent / 'uv.exe'), '-vv',
                                'python', 'find', sys.executable, '--no-config'],
                               capture_output=True, text=True, timeout=20)
        result['uv_interpreter_query'] = {'exit': query.returncode, 'stdout': query.stdout, 'stderr': query.stderr}
        import zipfile
        bundled, = (pathlib.Path(sys.executable).parent / 'Lib/ensurepip/_bundled').glob('pip-*.whl')
        pip_tool = out / 'pip-tool'
        with zipfile.ZipFile(bundled) as archive:
            archive.extractall(pip_tool)
        target = out / 'venv-control'
        subprocess.run([sys.executable, '-I', '-m', 'venv', '--without-pip', str(target)], timeout=20, check=True)
        import shutil
        site = target / 'Lib/site-packages'
        for name in ('a025_tempfile_compat.py', 'a025-tempfile-compat.pth',
                     'a025_path_compat.py', 'a025-path-compat.pth', 'a025-volume-map.json'):
            shutil.copy2(pathlib.Path(sys.executable).parent / 'Lib/site-packages' / name, site / name)
        bootstrap = "import sys,runpy; sys.path.insert(0," + repr(str(pip_tool)) + "); runpy.run_module('pip',run_name='__main__')"
        pip_control = subprocess.run([sys.executable, '-I', '-B', '-c', bootstrap,
            '--python', str(target / 'Scripts/python.exe'), '--isolated', '--version'],
            capture_output=True, text=True, timeout=20)
        assert pip_control.returncode == 0, pip_control.stdout + pip_control.stderr
        result['pip_target_environment'] = pip_control.stdout.strip()
        lock = __import__('tomllib').loads(pathlib.Path(LOCK).read_text())
        entry, = (entry for entry in lock['package'] if entry['name'] == 'colorama')
        wheel, = entry['wheels']
        requirements = out / 'installer-control.txt'
        requirements.write_text('colorama==' + entry['version'] + ' --hash=' + wheel['hash'] + '\\n')
        installer = subprocess.run([str(target / 'Scripts/python.exe'), '-I', '-B', '-c', bootstrap,
            '--isolated', '--disable-pip-version-check', 'install', '--no-cache-dir', '--no-deps',
            '--require-hashes', '-r', str(requirements)], capture_output=True, text=True, timeout=60)
        assert installer.returncode == 0, installer.stdout + installer.stderr
        result['pip_hashed_wheel_install'] = 'PASS'
        control_project = out / 'uv-sync-control'
        control_project.mkdir()
        sep=chr(10)
        (control_project/'pyproject.toml').write_text(sep.join([
            '[project]', 'name="a025-control"', 'version="0.0.0"',
            'requires-python=">=3.12"', 'dependencies=["colorama==0.4.6"]', '']))
        (control_project/'uv.lock').write_text(sep.join([
            'version=1', 'revision=3', 'requires-python=">=3.12"', '[[package]]',
            'name="a025-control"', 'version="0.0.0"', 'source={virtual="."}',
            'dependencies=[{name="colorama"}]', '[package.metadata]',
            'requires-dist=[{name="colorama",specifier="==0.4.6"}]', '[[package]]',
            'name="colorama"', 'version='+json.dumps(entry['version']),
            'source={registry='+json.dumps(entry['source']['registry'])+'}',
            'wheels=[{url='+json.dumps(wheel['url'])+',hash='+json.dumps(wheel['hash'])
                +',size='+str(wheel['size'])+'}]', '']))
        import os
        uv_environment=dict(os.environ,VIRTUAL_ENV=str(target),UV_CACHE_DIR=str(out/'uv-sync-cache'))
        uv_sync=subprocess.run([str(pathlib.Path(sys.executable).parent/'uv.exe'), 'sync',
            '--frozen','--offline','--no-build','--no-install-project','--active',
            '--project',str(control_project)],env=uv_environment,capture_output=True,text=True,timeout=45)
        assert uv_sync.returncode==0, uv_sync.stdout+uv_sync.stderr
        result['uv_frozen_sync_control']={'status':'PASS','stdout':uv_sync.stdout,'stderr':uv_sync.stderr}

        backend_output = out / 'backend-control'
        backend_output.mkdir()
        home = out / 'isolated-home'
        (home / 'local').mkdir(parents=True)
        (home / 'roaming').mkdir()
        temporary = out / 'separate-temp'
        temporary.mkdir()
        import os
        original_environment = {key: os.environ[key] for key in
            ('SYSTEMROOT', 'WINDIR', 'COMSPEC', 'SYSTEMDRIVE',
             'PROCESSOR_ARCHITECTURE', 'NUMBER_OF_PROCESSORS') if key in os.environ}
        original_environment.update(TEMP=str(temporary), TMP=str(temporary), HOME=str(home),
            USERPROFILE=str(home), LOCALAPPDATA=str(home / 'local'), APPDATA=str(home / 'roaming'),
            PYTHONHOME=sys.base_prefix, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
            MALECNS_A025_OUTPUT=str(out), PATH=str(target / 'Scripts'))
        private_output_code = ("import tempfile,pathlib; t=tempfile.TemporaryDirectory(dir="
            + repr(str(backend_output)) + "); p=pathlib.Path(t.name)/'ordinary.txt'; "
            "p.write_text('ordinary'); assert p.read_text()=='ordinary'; t.cleanup(); print('PASS')")
        private_output = subprocess.run([str(target / 'Scripts/python.exe'), '-B', '-c', private_output_code],
            env=original_environment, capture_output=True, text=True, timeout=20)
        assert private_output.returncode == 0, private_output.stdout + private_output.stderr
        result['original_environment_private_output'] = private_output.stdout.strip()
        assert private_output.stderr == '', private_output.stderr
        result['stock_python_startup_without_warning'] = 'PASS'
        node_script = out / 'node-metadata-control.js'
        node_script.write_text("console.log('PASS');")
        node_main = subprocess.run(['C:/Program Files/nodejs/node.exe', '--permission',
            '--allow-fs-read=' + str(node_script), str(node_script)],
            capture_output=True, text=True, timeout=20)
        assert node_main.returncode == 0 and node_main.stdout.strip() == 'PASS', node_main.stderr
        result['node_main_module_metadata'] = 'PASS'
        import ctypes.wintypes as wt
        class NativeStartup(ctypes.Structure):
            _fields_ = [('cb', wt.DWORD), ('reserved', wt.LPWSTR), ('desktop', wt.LPWSTR),
                ('title', wt.LPWSTR), ('x', wt.DWORD), ('y', wt.DWORD), ('width', wt.DWORD),
                ('height', wt.DWORD), ('chars_x', wt.DWORD), ('chars_y', wt.DWORD),
                ('fill', wt.DWORD), ('flags', wt.DWORD), ('show', wt.WORD),
                ('reserved_size', wt.WORD), ('reserved_bytes', ctypes.c_void_p),
                ('stdin', wt.HANDLE), ('stdout', wt.HANDLE), ('stderr', wt.HANDLE)]
        class NativeInfo(ctypes.Structure):
            _fields_ = [('process', wt.HANDLE), ('thread', wt.HANDLE), ('pid', wt.DWORD), ('tid', wt.DWORD)]
        kernel.CreateProcessW.argtypes = [wt.LPCWSTR, wt.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
            wt.BOOL, wt.DWORD, ctypes.c_void_p, wt.LPCWSTR, ctypes.POINTER(NativeStartup), ctypes.POINTER(NativeInfo)]
        kernel.TerminateProcess.argtypes = [wt.HANDLE, wt.UINT]
        kernel.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
        class NativeSecurity(ctypes.Structure):
            _fields_=[('size',wt.DWORD),('descriptor',ctypes.c_void_p),('inherit',wt.BOOL)]
        security=NativeSecurity(ctypes.sizeof(NativeSecurity),None,True)
        kernel.CreateFileW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,wt.HANDLE]
        native_log=kernel.CreateFileW(str(out/'nsight-suspended-control.log'),0x40000000,3,ctypes.byref(security),1,0x80,None)
        native_input=kernel.CreateFileW('NUL',0x80000000,3,ctypes.byref(security),3,0x80,None)
        assert all(handle not in (None,ctypes.c_void_p(-1).value) for handle in (native_log,native_input)), ctypes.WinError(ctypes.get_last_error())
        startup=NativeStartup(); startup.cb=ctypes.sizeof(startup); info=NativeInfo()
        startup.flags=0x100; startup.stdin=native_input; startup.stdout=startup.stderr=native_log
        nsight='C:/Program Files/NVIDIA Corporation/Nsight Systems 2025.5.2/target-windows-x64/nsys.exe'
        argv=ctypes.create_unicode_buffer(subprocess.list2cmdline([nsight,'--version']))
        created=kernel.CreateProcessW(nsight,argv,None,None,True,0x4|0x400|0x08000000,
                                      None,str(out),ctypes.byref(startup),ctypes.byref(info))
        assert created, ctypes.WinError(ctypes.get_last_error())
        try:
            assert kernel.TerminateProcess(info.process,79)
            assert kernel.WaitForSingleObject(info.process,10000)==0
        finally:
            kernel.CloseHandle(info.thread); kernel.CloseHandle(info.process)
            kernel.CloseHandle(native_log); kernel.CloseHandle(native_input)
        result['nsight_suspended_native_create_cleanup']={'status':'PASS','pid':info.pid,'resumed':False}

        result['strict_native_path_resolution'] = 'PASS'
        version = subprocess.run(['C:/Program Files/nodejs/node.exe', '--version'],
                                  capture_output=True, text=True, timeout=20, check=True)
        result['node'] = version.stdout.strip()
        curl_control = subprocess.run([str(pathlib.Path(sys.executable).parent / 'curl.exe'), '--version'],
                                      capture_output=True, text=True, timeout=15)
        assert curl_control.returncode == 0
        result['curl'] = curl_control.stdout.splitlines()[0]
        import http.server, threading, urllib.request
        server = http.server.HTTPServer(('127.0.0.1', 0), http.server.BaseHTTPRequestHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                opener.open('http://127.0.0.1:' + str(server.server_port), timeout=5)
            except urllib.error.HTTPError as error:
                assert error.code == 501
            result['loopback'] = 'PASS'
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
            assert not thread.is_alive()
except BaseException:
    result = {'status': 'FAIL', 'exception': traceback.format_exc()}
(out / 'probe.json').write_text(json.dumps(result, indent=2))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
'''.replace('INPUT', repr(str(inputs / 'ordinary.txt'))).replace('SENTINEL', repr(str(sentinel)))
    repository = Path(__file__).resolve().parents[1]
    probe = probe.replace('DENIED_ROOTS', repr([str(repository / name) for name in ('data', 'artifacts')]))
    probe = probe.replace('DEVICE_DENIALS', repr([(r'\\.\C:', 0x80000000), (r'\\.\D:', 0x80000000), (r'\\.\PhysicalDrive0', 0x80000000), (r'\\.\MountPointManager', 0x40000000)]))
    probe = probe.replace('GPU_PROBE', repr(gpu_probe))
    probe = probe.replace('ROUTE_CONTROLS', repr(route_controls))
    if route_controls:
        shutil.copy2(repository / 'uv.lock', inputs / 'uv.lock')
    probe = probe.replace('LOCK', repr(str(inputs / 'uv.lock')))
    script = inputs / 'probe.py'
    script.write_text(probe, encoding='utf-8')
    profile = 'MaleCNSA025.' + uuid.uuid4().hex
    userenv = ctypes.WinDLL('userenv', use_last_error=True)
    userenv.CreateAppContainerProfile.argtypes = [W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, ctypes.c_void_p,
                                                 W.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    userenv.CreateAppContainerProfile.restype = ctypes.c_long
    userenv.DeleteAppContainerProfile.argtypes = [W.LPCWSTR]
    userenv.DeleteAppContainerProfile.restype = ctypes.c_long
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.LPWSTR)]
    adv.FreeSid.argtypes = [ctypes.c_void_p]
    kernel = api()
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    sid, text = ctypes.c_void_p(), W.LPWSTR()
    result = userenv.CreateAppContainerProfile(profile, profile, 'A025 synthetic isolation control', None, 0, ctypes.byref(sid))
    if result != 0:
        raise RuntimeError('profile creation failed: ' + hex(result & 0xffffffff))
    evidence = {'run': str(root), 'profile': profile,
                'claim': 'Windows boundary/GPU compatibility development; no candidate acceptance',
                'gpu_probe': gpu_probe, 'dependency_source': 'existing tool packages; not fresh install evidence',
                'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'metadata_helper_sha256': hashlib.sha256(Path(__file__).with_name('a025_metadata_controls.py').read_bytes()).hexdigest()}
    job = None
    metadata_rights = None
    node_granted = loopback_granted = nsight_granted = False
    nsight = Path('C:/Program Files/NVIDIA Corporation/Nsight Systems 2025.5.2/target-windows-x64/nsys.exe')
    nsight_hash = hashlib.sha256(nsight.read_bytes()).hexdigest() if route_controls else None
    node = Path('C:/Program Files/nodejs/node.exe')
    node_hash = hashlib.sha256(node.read_bytes()).hexdigest() if route_controls else None
    try:
        require(adv.ConvertSidToStringSidW(sid, ctypes.byref(text)))
        evidence['sid'] = text.value
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from a025_metadata_controls import MetadataRights
        metadata_rights = MetadataRights(sid, [Path('C:/'), Path('C:/TEMP'), root])
        evidence['metadata_rights'] = [{'object': name, 'mask': hex(mask)}
                                      for _, name, mask in metadata_rights.records]
        for path, permission in ((tools, '(OI)(CI)RX'), (inputs, '(OI)(CI)RX'), (output, '(OI)(CI)M')):
            subprocess.run(['icacls', str(path), '/grant', '*' + text.value + ':' + permission],
                           check=True, capture_output=True, text=True)
        subprocess.run(['icacls', str(output), '/setintegritylevel', '(OI)(CI)L'],
                       check=True, capture_output=True, text=True)
        if route_controls:
            subprocess.run(['icacls', str(node), '/grant', '*' + text.value + ':RX'],
                           check=True, capture_output=True, text=True)
            node_granted = True
            subprocess.run(['icacls', str(nsight), '/grant', '*' + text.value + ':RX'],
                           check=True, capture_output=True, text=True)
            nsight_granted = True
            evidence['nsight_sha256'] = nsight_hash
            subprocess.run(['CheckNetIsolation.exe', 'LoopbackExempt', '-a', '-n=' + profile],
                           check=True, capture_output=True, text=True)
            loopback_granted = True
        before = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for directory in (tools, inputs) for path in directory.rglob('*') if path.is_file()}
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from a023_local_repro import Job
        job = Job()
        evidence['process'] = launch(tools / 'python.exe', script, output, sid, job, internet=route_controls)
        after = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in before}
        evidence.update(tool_input_hashes=before, immutable=before == after,
                        network='internet-client plus profile-only loopback exemption' if route_controls else 'no network capability')
        if (output / 'probe.json').exists():
            evidence['probe'] = json.loads((output / 'probe.json').read_text())
        evidence['status'] = ('PASS' if evidence['process']['exit'] == 0
                              and evidence['process']['job']['active'] == 0
                              and evidence.get('probe', {}).get('status') == 'PASS'
                              and before == after else 'FAIL')
    finally:
        if job is not None:
            job.close()
            evidence['job_cleanup'] = 'closed; kill-on-close retained'
        if loopback_granted:
            subprocess.run(['CheckNetIsolation.exe', 'LoopbackExempt', '-d', '-n=' + profile],
                           check=True, capture_output=True, text=True)
            evidence['loopback_cleanup'] = 'profile-only exemption removed'
        if node_granted:
            subprocess.run(['icacls', str(node), '/remove:g', '*' + text.value],
                           check=True, capture_output=True, text=True)
            assert hashlib.sha256(node.read_bytes()).hexdigest() == node_hash
            evidence['node_cleanup'] = 'temporary SID grant removed; tool bytes unchanged'
        if metadata_rights is not None:
            metadata_rights.close()
            evidence['metadata_cleanup'] = 'temporary profile SID entries removed'
        if nsight_granted:
            subprocess.run(['icacls', str(nsight), '/remove:g', '*' + text.value],
                           check=True, capture_output=True, text=True)
            assert hashlib.sha256(nsight.read_bytes()).hexdigest() == nsight_hash
            evidence['nsight_cleanup'] = 'temporary SID grant removed; tool bytes unchanged'
        deleted = userenv.DeleteAppContainerProfile(profile)
        evidence['profile_cleanup_hresult'] = deleted
        if deleted != 0:
            evidence['status'] = 'FAIL'
        if text:
            kernel.LocalFree(text)
        adv.FreeSid(sid)
        (root / 'isolation.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': evidence['status'], 'evidence': str(root / 'isolation.json')}))
    if evidence['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
