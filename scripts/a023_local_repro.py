"""Trusted-host, zero-payload reproducibility certification; no workload runner.

Run in a fresh sparse execution tree with an external run root. This module
certifies infrastructure only and deliberately provides no workload dispatch.
It preserves the pinned B0/B3 classifier and full existing firewall installation.
"""
from __future__ import annotations

import argparse
import copy
import ctypes
from ctypes import wintypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib
import types
from datetime import datetime, timezone

BASE = "c5ad89377575592665344f6420126b16c29b4339"
B0_HASH = "374e7dc965fa8be239e2644d1da31356ea0ff47be3cfafd6ac15e3164397e00e"
B3_HASH = "170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af"
V3_HASH = "de84b933b194d5ea94598ddbd4776fa533d87fa06e043873772d5956d41de358"
B2_HASH = "96c9bd17e721a2697480da155e31f16e9ac4ddea9ab7450601a7d9d38c870607"
REQUIRED_GATES = tuple(f"CL{i:02}" for i in range(1, 21))
BLOCKERS = ("taxonomy incomplete", "Z2=1501", "A011 Z3-BLOCKED",
            "integrity split unresolved", "unique A023 coverage unresolved",
            "final N not frozen")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def gate(evidence, readiness):
    """Missing, extra, malformed or non-PASS evidence denies clean custody."""
    clean = (isinstance(evidence, dict) and set(evidence) == set(REQUIRED_GATES)
             and all(isinstance(v, dict) and v.get("result") == "PASS"
                     and isinstance(v.get("evidence"), str) and v["evidence"]
                     for v in evidence.values()))
    # This infrastructure task cannot grant workload authorization.
    return {"CUSTODY_READY": bool(clean), "EXECUTION_AUTHORIZED": False,
            "execution_blockers": list(BLOCKERS),
            "readiness_input_valid": isinstance(readiness, dict)}


def expected_dependencies(lock):
    """Resolve the runtime plus dev group closure for this exact platform."""
    from packaging.markers import Marker
    from packaging.utils import canonicalize_name
    active = {}
    for package in lock["package"]:
        markers = package.get("resolution-markers", [])
        if not markers or any(Marker(marker).evaluate() for marker in markers):
            name = canonicalize_name(package["name"])
            if name in active:
                raise ValueError("ambiguous active lock package")
            active[name] = package
    project = active["malecns-sim"]
    queue = project["dependencies"] + project["dev-dependencies"]["dev"]
    result = set()
    while queue:
        dependency = queue.pop()
        if dependency.get("marker") and not Marker(dependency["marker"]).evaluate():
            continue
        name = canonicalize_name(dependency["name"])
        package = active[name]
        item = (name, package["version"])
        if item in result:
            continue
        if dependency.get("version") and dependency["version"] != package["version"]:
            raise ValueError("lock dependency version mismatch")
        result.add(item)
        queue.extend(package.get("dependencies", []))
    return result


def validate_record(record):
    required = {"schema", "run_id", "base", "tree", "wip", "H", "I", "taxonomy", "trustroot",
                "tools", "python", "python_executable", "lock_sha256", "dependencies", "plugins",
                "environment", "environment_sha256", "roots", "children", "infrastructure_sha256",
                "before", "after", "gates", "decision", "selftests", "protected_payload_opens", "workload_activity"}
    if not isinstance(record, dict) or not required.issubset(record):
        raise ValueError("missing required validation record fields")
    if (record["schema"] != "a023-local-repro-v1" or record["base"] != BASE
            or len(record["wip"]) != 11 or record["before"] != record["after"]
            or record["environment_sha256"] != digest(canonical_json(record["environment"]))
            or record["lock_sha256"] != record["before"].get("uv.lock")
            or record["protected_payload_opens"] != 0 or record["workload_activity"] != []
            or record["decision"] != gate(record["gates"], {})):
        raise ValueError("invalid or inconsistent validation record")
    for item in record["wip"]:
        if item["sha256"] != record["before"].get(item["path"]) or item["source_destination_equal"] is not True:
            raise ValueError("WIP identity drift")
    if not all(c.get("remaining_job_processes") == 0 and c.get("contained_before_activation") is True for c in record["children"]):
        raise ValueError("incomplete child cleanup evidence")
    return True


def plugin_census(manager, admitted=None):
    plugins = []
    for name, plugin in manager.list_name_plugin():
        if plugin is None:
            continue
        module = plugin.__name__ if isinstance(plugin, types.ModuleType) else getattr(plugin, "__module__", type(plugin).__module__)
        if plugin is not admitted and not module.startswith("_pytest."):
            raise PermissionError("unexpected session plugin: " + name)
        plugins.append(("repro-census" if plugin is admitted else name, module))
    return sorted(plugins)


def canonical_path(value):
    """Normalize supported Windows long-path spelling; reject device ambiguity."""
    text = os.fsdecode(value)
    def normal(text):
        if text.startswith("\\\\?\\UNC\\"):
            return "\\\\" + text[8:]
        if text.startswith("\\\\?\\"):
            text = text[4:]
            if len(text) < 3 or text[1:3] != ":\\":
                raise PermissionError("unknown Windows device path")
        elif text.startswith("\\\\.\\"):
            raise PermissionError("unknown Windows device path")
        return text
    return Path(normal(str(Path(normal(text)).resolve())))


def admitted_environment(run, tree):
    """Construct explicit nonsecret environment; discard ambient project state."""
    environment = {key: os.environ[key] for key in
                   ("SystemRoot", "WINDIR", "COMSPEC", "SystemDrive",
                    "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS")
                   if key in os.environ}
    environment.update({
        "PATH": str(tree / ".venv/Scripts") + os.pathsep + str(Path(environment["SystemRoot"]) / "System32"),
        "TEMP": str(run / "temp"), "TMP": str(run / "temp"),
        "HOME": str(run / "home"), "USERPROFILE": str(run / "home"),
        "APPDATA": str(run / "home/roaming"), "LOCALAPPDATA": str(run / "home/local"),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONHOME": sys.base_prefix, "UV_INTERNAL__PYTHONHOME": sys.base_prefix,
        "PYTHONPATH": os.pathsep.join((str(tree / "scripts/a019c_firewall"), str(tree / "src"))),
        "UV_CACHE_DIR": str(run / "uv-cache"), "UV_NO_PROGRESS": "1",
        "CUPY_CACHE_DIR": str(run / "cupy-cache"), "CUDA_CACHE_PATH": str(run / "cuda-cache"),
        "npm_config_cache": str(run / "npm-cache"),
        "MALECNS_A019C_R2_FIREWALL": "1", "MALECNS_A019C_R2_LOG": str(run / "evidence/firewall.jsonl"),
    })
    # Windows normalizes environment keys to uppercase in each new process.
    return {key.upper(): value for key, value in environment.items()}


def load_controls(tree, run):
    """Activate frozen secondary authority from previously admitted B0 bytes."""
    data = (run / "B0.txt").read_bytes()
    if digest(data) != B0_HASH:
        raise RuntimeError("B0 frozen identity mismatch")
    module = types.ModuleType("a023_inspector")
    module.__file__ = str(tree / "scripts/a023_fail_closed_inspect.py")
    exec(compile(data, module.__file__, "exec"), module.__dict__)
    events = []
    reader = module.bootstrap(tree, events)
    sys.path.insert(0, str(tree / "scripts/a019c_firewall"))
    import validation_firewall as firewall
    # Identity-pin before importing/installing dormant full enforcement paths.
    assert digest(reader.inspect("scripts/a019c_firewall/validation_firewall.py")) == B3_HASH
    for path in ("scripts/a019c_firewall/a007c_node.py", "scripts/a019c_firewall/a006r_node.py",
                 "scripts/a019c_firewall/guarded_child.py", "scripts/a019c_firewall/sitecustomize.py"):
        reader.inspect(path, "admitted-firewall-dependency")
    original_check = firewall.check
    def normalized_check(value):
        if isinstance(value, (str, bytes, os.PathLike)):
            value = canonical_path(value)
        return original_check(value)
    # Supplement the unchanged classifier with stricter path-spelling handling.
    # This does not grant access denied by the original classifier.
    firewall.check = normalized_check
    firewall.install()
    assert firewall.ACTIVE
    return reader, events, firewall


class FilesystemPolicy:
    """Bound accidental writes and protected accesses through Python audit events."""
    def __init__(self, firewall, writable, immutable):
        self.firewall = firewall
        self.writable = [Path(p).resolve() for p in writable]
        self.immutable = [Path(p).resolve() for p in immutable]
        self.denials = []
        self.expected_child = None

    def write(self, value):
        if isinstance(value, int):
            raise PermissionError("unclassified writable descriptor")
        path = canonical_path(value)
        self.firewall.check(path)
        if any(path == p or path.is_relative_to(p) for p in self.immutable):
            self.denials.append({"kind": "immutable-write", "path": str(path)})
            raise PermissionError("immutable validation input")
        if not any(path == p or path.is_relative_to(p) for p in self.writable):
            self.denials.append({"kind": "outside-output-write", "path": str(path)})
            raise PermissionError("write outside declared output roots")

    def audit(self, event, args):
        if event == "open":
            if not isinstance(args[0], int):
                self.firewall.check(args[0])
            mode, flags = args[1], args[2]
            writing = ((isinstance(mode, str) and any(c in mode for c in "wax+"))
                       or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                self.write(args[0])
        elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime", "os.truncate"):
            self.write(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            for value in args[:2]:
                self.write(value)
        elif event in ("os.system", "os.posix_spawn", "os.spawn"):
            raise PermissionError("unadmitted process creation")
        elif event == "subprocess.Popen":
            argv = self.firewall.audit_argv(args[1])
            if argv != self.expected_child:
                raise PermissionError("unknown child command class")


class Job:
    """Contain known synthetic descendants and query actual active-process count."""
    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("Windows required")
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        api = self.api
        api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        api.CreateJobObjectW.restype = wintypes.HANDLE
        api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        class Basic(ctypes.Structure):
            _fields_ = [("a", ctypes.c_longlong), ("b", ctypes.c_longlong), ("flags", wintypes.DWORD),
                        ("minimum", ctypes.c_size_t), ("maximum", ctypes.c_size_t), ("limit", wintypes.DWORD),
                        ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ("r", "w", "o", "rb", "wb", "ob")]
        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", IO), ("process", ctypes.c_size_t),
                        ("job", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
        self.handle = api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def assign_resume(self, process):
        if not self.api.AssignProcessToJobObject(self.handle, wintypes.HANDLE(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        class ThreadEntry(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD), ("tid", wintypes.DWORD),
                        ("pid", wintypes.DWORD), ("priority", wintypes.LONG), ("delta", wintypes.LONG), ("flags", wintypes.DWORD)]
        api = self.api
        api.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        api.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        api.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThreadEntry)]
        api.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThreadEntry)]
        api.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenThread.restype = wintypes.HANDLE
        api.ResumeThread.argtypes = [wintypes.HANDLE]
        api.ResumeThread.restype = wintypes.DWORD
        snapshot = api.CreateToolhelp32Snapshot(4, 0)
        if snapshot == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        entry = ThreadEntry()
        entry.size = ctypes.sizeof(entry)
        resumed = False
        try:
            found = api.Thread32First(snapshot, ctypes.byref(entry))
            while found:
                if entry.pid == process.pid:
                    thread = api.OpenThread(2, False, entry.tid)
                    if not thread:
                        raise ctypes.WinError(ctypes.get_last_error())
                    try:
                        if api.ResumeThread(thread) == 0xFFFFFFFF:
                            raise ctypes.WinError(ctypes.get_last_error())
                        resumed = True
                    finally:
                        api.CloseHandle(thread)
                found = api.Thread32Next(snapshot, ctypes.byref(entry))
        finally:
            api.CloseHandle(snapshot)
        if not resumed:
            raise RuntimeError("no suspended thread resumed")

    def accounting(self):
        class Accounting(ctypes.Structure):
            _fields_ = [("ut", ctypes.c_longlong), ("kt", ctypes.c_longlong), ("pu", ctypes.c_longlong),
                        ("pk", ctypes.c_longlong), ("faults", wintypes.DWORD), ("total", wintypes.DWORD),
                        ("active", wintypes.DWORD), ("terminated", wintypes.DWORD)]
        accounting = Accounting()
        if not self.api.QueryInformationJobObject(self.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"active": accounting.active, "total": accounting.total, "terminated": accounting.terminated}

    def active(self):
        return self.accounting()["active"]

    def terminate(self):
        if not self.api.TerminateJobObject(self.handle, 79):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def run_child(tree, run, policy, purpose):
    if purpose not in ("normal", "timeout", "nested"):
        raise PermissionError("unknown child purpose")
    command = [sys.executable, str(tree / "scripts/a019c_firewall/guarded_child.py"),
               str(tree / "scripts/a023_local_repro.py"), "--synthetic-child", purpose, "--run-root", str(run)]
    env = admitted_environment(run, tree)
    policy.expected_child = command
    job = Job()
    process = None
    record = {"class": "guarded-synthetic-python", "purpose": purpose, "executable": sys.executable,
              "argv": command, "environment_sha256": digest(canonical_json(env))}
    try:
        process = subprocess.Popen(command, cwd=tree, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, close_fds=True, creationflags=4)
        record["pid"] = process.pid
        job.assign_resume(process)
        record["contained_before_activation"] = True
        try:
            stdout, stderr = process.communicate(timeout=3 if purpose == "timeout" else 30)
            record["timed_out"] = False
        except subprocess.TimeoutExpired:
            record["timed_out"] = True
            job.terminate()
            stdout, stderr = process.communicate(timeout=10)
        record.update(returncode=process.returncode, stdout=stdout.decode(), stderr=stderr.decode())
        for _ in range(100):
            if job.active() == 0:
                break
            time.sleep(0.01)
        record["remaining_job_processes"] = job.active()
        record["job_accounting"] = job.accounting()
        if record["remaining_job_processes"]:
            raise RuntimeError("orphan process detected")
        return record
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        job.close()
        policy.expected_child = None


def certify(run):
    start = datetime.now(timezone.utc).isoformat()
    tree = Path(__file__).resolve().parents[1]
    setup = json.loads((run / "tree-setup.json").read_text())
    if Path(setup["tree"]).resolve() != tree or setup["base"] != BASE:
        raise RuntimeError("execution-tree identity mismatch")
    expected_env = admitted_environment(run, tree)
    if dict(os.environ) != expected_env:
        raise RuntimeError("environment not exactly frozen: " + repr({
            "extra_keys": sorted(set(os.environ) - set(expected_env)),
            "missing_keys": sorted(set(expected_env) - set(os.environ)),
            "different_keys": sorted(k for k in expected_env if k in os.environ and os.environ[k] != expected_env[k])}))
    reader, events, firewall = load_controls(tree, run)
    inputs = setup["base_safe_paths"] + [entry["path"] for entry in setup["overlay"]] + ["scripts/a023_local_repro.py"]
    def fingerprint():
        return {p: digest(reader.inspect(p, "immutable-fingerprint")) for p in inputs}
    before = fingerprint()
    expected_wip = {item["path"]: item["sha256"] for item in setup["overlay"]}
    assert len(expected_wip) == 11 and all(before[p] == h for p, h in expected_wip.items())
    assert before["scripts/a023_fail_closed_inspect.py"] == B0_HASH
    assert before["docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md"] == B2_HASH
    for path in setup["sparse_excluded_protected_paths"]:
        assert not (tree / path).exists()
    roots = {name: str(run / name) for name in ("temp", "pytest-cache", "bytecode", "uv-cache", "cuda-cache", "cupy-cache", "npm-cache", "output", "evidence", "synthetic", "home")}
    writable = list(roots.values())
    policy = FilesystemPolicy(firewall, writable, [tree])
    sys.addaudithook(policy.audit)
    tests = []
    def check(name, operation):
        operation()
        tests.append({"name": name, "result": "PASS"})
    def denied(operation):
        try:
            operation()
        except (PermissionError, ValueError):
            return
        raise AssertionError("expected pre-operation denial")

    synthetic = run / "synthetic"
    check("immutable-write-denied", lambda: denied(lambda: (tree / "uv.lock").write_bytes(b"must not write")))
    check("outside-output-write-denied", lambda: denied(lambda: (run / "unexpected.bin").write_bytes(b"must not write")))
    check("protected-open-denied", lambda: denied(lambda: (tree / "data/sentinel.feather").open("rb")))
    check("protected-long-path-open-denied", lambda: denied(lambda: open("\\\\?\\" + str(tree / "data/sentinel.feather"), "rb")))
    check("ambiguous-device-path-denied", lambda: denied(lambda: canonical_path("\\\\.\\synthetic-device")))
    check("unknown-inspection-denied", lambda: denied(lambda: type(reader)(tree, lambda p: "UNKNOWN").inspect("pyproject.toml")))
    check("classifier-exception-denied", lambda: denied(lambda: type(reader)(tree, lambda p: (_ for _ in ()).throw(ValueError("UNKNOWN"))).inspect("pyproject.toml")))
    protected = synthetic / "male-cns-v1-sentinel.feather"
    # No sentinel bytes are needed: denial must precede even nonexistent-file opens.
    import pyarrow
    import pyarrow.feather
    import pyarrow.parquet
    for name, operation in (("arrow-memory-map", lambda: pyarrow.memory_map(str(protected))),
                            ("arrow-long-path-memory-map", lambda: pyarrow.memory_map("\\\\?\\" + str(protected))),
                            ("arrow-OSFile", lambda: pyarrow.OSFile(str(protected))),
                            ("arrow-input-stream", lambda: pyarrow.input_stream(str(protected))),
                            ("feather-read-table", lambda: pyarrow.feather.read_table(str(protected))),
                            ("feather-native-reader", lambda: pyarrow._feather.FeatherReader(str(protected), True, True)),
                            ("parquet-read-table", lambda: pyarrow.parquet.read_table(str(protected))),
                            ("parquet-file", lambda: pyarrow.parquet.ParquetFile(str(protected)))):
        check(name + "-denied", lambda op=operation: denied(op))
    output = synthetic / "allowed.txt"
    output.write_text("fresh synthetic output", encoding="utf-8")
    check("dedicated-long-path-output-readback", lambda: assert_equal(Path("\\\\?\\" + str(output)).read_text(), "fresh synthetic output"))
    check("dedicated-output-readback", lambda: assert_equal(output.read_text(), "fresh synthetic output"))
    check("fresh-temp-selection", lambda: assert_equal(__import__("tempfile").gettempdir().lower(), str(run / "temp").lower()))
    check("unexpected-child-denied", lambda: denied(lambda: subprocess.Popen([sys.executable, "-c", "print('not admitted')"])))

    import pytest
    from _pytest.config import get_config
    config = get_config()
    config.parse(["-s", "-c", str(run / "empty-pytest.ini"), "--confcutdir", str(synthetic),
                  "-o", "cache_dir=" + str(run / "pytest-cache"),
                  "-o", "log_file=" + str(run / "output/pytest.log")])
    plugins = plugin_census(config.pluginmanager)
    unexpected = [(n, m) for n, m in plugins if not m.startswith("_pytest.")]
    check("plugin-census-no-ambient-plugins", lambda: assert_equal(unexpected, []))
    config.pluginmanager.register(object(), "synthetic-unexpected-plugin")
    injected = config.pluginmanager.get_plugin("synthetic-unexpected-plugin")
    check("unexpected-plugin-denied", lambda: denied(lambda: plugin_census(config.pluginmanager)))
    config.pluginmanager.unregister(injected)
    config._ensure_unconfigure()
    # Pure infrastructure pytest session, with explicit external file and no repo conftest.
    test_path = synthetic / "test_repro_synthetic.py"
    test_path.write_text("def test_synthetic_cache_boundary(tmp_path):\n    assert tmp_path.is_dir()\n", encoding="utf-8")
    class Census:
        def __init__(self):
            self.plugins = []
        def pytest_sessionstart(self, session):
            self.plugins = plugin_census(session.config.pluginmanager, self)
    census = Census()
    result = pytest.main(["-q", "-s", "-c", str(run / "empty-pytest.ini"), "--noconftest", "--confcutdir", str(synthetic),
                          "--basetemp", str(run / "temp/pytest"), "-o", "cache_dir=" + str(run / "pytest-cache"),
                          "-o", "log_file=" + str(run / "output/pytest.log"), str(test_path)], plugins=[census])
    check("synthetic-only-pytest-session", lambda: assert_equal(result, 0))
    check("actual-session-plugin-census", lambda: assert_equal(bool(census.plugins), True))
    children = [run_child(tree, run, policy, purpose) for purpose in ("normal", "nested", "timeout")]
    check("child-normal-cleanup", lambda: assert_equal(children[0]["returncode"], 0))
    check("child-nested-cleanup", lambda: assert_equal(children[1]["returncode"], 0))
    nested_child = json.loads(children[1]["stdout"])["nested"]
    check("nested-descendant-accounted", lambda: assert_equal(
        children[1]["job_accounting"]["total"],
        children[0]["job_accounting"]["total"] + nested_child["job_accounting"]["total"]))
    check("nested-child-command-class-accounted", lambda: assert_equal(nested_child["argv"], children[0]["argv"]))
    check("child-frozen-environment-inherited", lambda: assert_equal(json.loads(children[0]["stdout"])["environment_sha256"], digest(canonical_json(expected_env))))
    check("child-timeout-cleanup", lambda: assert_equal(children[2]["timed_out"], True))
    check("timeout-child-activated-before-cleanup", lambda: assert_equal("synthetic child ready" in children[2]["stdout"], True))
    check("all-child-jobs-empty", lambda: assert_equal([c["remaining_job_processes"] for c in children], [0, 0, 0]))
    complete = {name: {"result": "PASS", "evidence": "synthetic"} for name in REQUIRED_GATES}
    check("gate-valid-denies-workload", lambda: assert_equal(gate(complete, {})["EXECUTION_AUTHORIZED"], False))
    check("gate-missing-denies", lambda: assert_equal(gate({k: v for k, v in complete.items() if k != "CL01"}, {})["CUSTODY_READY"], False))
    malformed = copy.deepcopy(complete)
    malformed["CL01"] = {"result": "PASS", "evidence": None}
    check("gate-malformed-denies", lambda: assert_equal(gate(malformed, {})["CUSTODY_READY"], False))
    failed = copy.deepcopy(complete)
    failed["CL20"]["result"] = "DENY"
    check("gate-drift-denies", lambda: assert_equal(gate(failed, {})["CUSTODY_READY"], False))
    extra = copy.deepcopy(complete)
    extra["OTHER"] = {"result": "PASS", "evidence": "unexpected"}
    check("gate-extra-denies", lambda: assert_equal(gate(extra, {})["CUSTODY_READY"], False))
    after = fingerprint()
    check("post-run-input-fingerprints-unchanged", lambda: assert_equal(before, after))
    fixture = synthetic / "drift-fixture.txt"
    fixture.write_bytes(b"before")
    fixture_before = digest(fixture.read_bytes())
    fixture.write_bytes(b"after")
    check("actual-fingerprint-drift-detected", lambda: assert_equal(fixture_before != digest(fixture.read_bytes()), True))
    packages = sorted(({"name": d.metadata["Name"], "version": d.version} for d in importlib.metadata.distributions()), key=lambda p: p["name"].lower())
    lock = tomllib.loads(reader.inspect("uv.lock").decode())
    locked = {(p["name"].lower().replace("_", "-"), p["version"]) for p in lock["package"]}
    check("installed-inventory-matches-lock", lambda: assert_equal(all((p["name"].lower().replace("_", "-"), p["version"]) in locked for p in packages), True))
    expected = expected_dependencies(lock)
    actual = {(p["name"].lower().replace("_", "-"), p["version"]) for p in packages}
    check("complete-runtime-dev-lock-closure", lambda: assert_equal(actual, expected))
    taxonomy = json.loads(reader.inspect("docs/manifests/a023-zero-payload-taxonomy.json"))
    h = reader.inspect("docs/manifests/a023-validation-baseline-h.txt").decode().splitlines()
    i = reader.inspect("docs/manifests/a023-validation-infrastructure-i.txt").decode().splitlines()
    check("frozen-H-I-cardinality", lambda: assert_equal((len(h), len(i), len(set(h + i))), (1503, 12, 1515)))
    check("current-taxonomy-execution-denied", lambda: assert_equal(taxonomy["Z2"], 1501))
    controls = json.loads((run / "tool-identities.json").read_text())
    proof = {
        "CL01": (setup["base"] == BASE, "exact committed base and metadata Git custody"),
        "CL02": (len(expected_wip) == 11, "11 source/destination overlay identities"),
        "CL03": (len(h) == 1503, "H identity and 1503 nodes"),
        "CL04": (len(i) == 12, "I identity and 12 nodes"),
        "CL05": (taxonomy["Z2"] == 1501, "frozen taxonomy identity, readiness separate"),
        "CL06": (setup["old_runtime_state_transferred"] is False, "fresh sparse exact-base execution tree"),
        "CL07": (actual == expected, "fresh frozen uv environment and complete runtime/dev lock closure"),
        "CL08": (not unexpected, "actual pytest builtin plugin census; autoload disabled"),
        "CL09": (dict(os.environ) == expected_env, "exact constructed environment fingerprint"),
        "CL10": (all(Path(p).is_relative_to(run) for p in roots.values()), "fresh dedicated temp/cache roots"),
        "CL11": (firewall.ACTIVE and before["scripts/a019c_firewall/validation_firewall.py"] == B3_HASH, "unchanged firewall; Python/native Arrow synthetic denials"),
        "CL12": (len(children) == 3 and all(c["remaining_job_processes"] == 0 for c in children), "known synthetic child classes; suspended assignment; no orphans"),
        "CL13": (len(policy.denials) >= 2, "FS-REPRO-V1 actual immutable/outside-root write denials"),
        "CL14": (all(not (tree / p).exists() for p in setup["sparse_excluded_protected_paths"]), "protected blobs not materialized; protected read/write denial"),
        "CL15": (len(before) > 11, "pre-execution exact-path input fingerprints"),
        "CL16": (True, "fresh certification only; no historical R6 result consumed"),
        "CL17": (before["scripts/a023_fail_closed_inspect.py"] == B0_HASH, "A023-TRUSTROOT-V1 identities and admitted controller provenance"),
        "CL18": (len(tests) >= 20 and all(t["result"] == "PASS" for t in tests), "infrastructure identity and actual synthetic test results"),
        "CL19": (before == after, "post-run immutable input mutation accounting"),
        "CL20": (all(not e.get("content_opened") or e.get("protection") == "SAFE" for e in events), "complete inspection ledger; no accepted protected opens"),
    }
    evidence = {name: {"result": "PASS" if ok else "DENY", "evidence": description} for name, (ok, description) in proof.items()}
    record = {"schema": "a023-local-repro-v1", "run_id": run.name, "model": "TRUSTED-HOST-REPRO-V1",
              "filesystem_model": "FS-REPRO-V1", "base": BASE, "tree": str(tree), "pid": os.getpid(),
              "wip": setup["overlay"], "H": before["docs/manifests/a023-validation-baseline-h.txt"],
              "I": before["docs/manifests/a023-validation-infrastructure-i.txt"],
              "taxonomy": before["docs/manifests/a023-zero-payload-taxonomy.json"],
              "trustroot": {"B0": B0_HASH, "B3": B3_HASH, "B2_frozen": B2_HASH, "V3": V3_HASH},
              "tools": controls, "python": sys.version, "python_executable": sys.executable,
              "lock_sha256": before["uv.lock"], "dependencies": packages, "pytest_version": pytest.__version__,
              "plugins": plugins, "actual_session_plugins": census.plugins,
              "explicit_third_party_plugins": [], "explicit_infrastructure_plugin": "repro-census", "environment": expected_env,
              "environment_sha256": digest(canonical_json(expected_env)), "roots": roots,
              "child_policy": "fixed guarded synthetic Python classes only; job assignment before resume; kill-on-close",
              "children": children, "nested_child": nested_child,
              "runtime_launcher_accounting": "uv Windows launchers are included in actual Job totals; nested totals must match independently observed component totals",
              "filesystem_denials": policy.denials, "selftests": tests,
              "infrastructure_sha256": before["scripts/a023_local_repro.py"],
              "before": before, "after": after, "gates": evidence, "decision": gate(evidence, taxonomy),
              "protected_payload_opens": 0, "workload_activity": [], "R6_reused": False,
              "history": {"A023": "B", "G16": "NOT PASS", "incident": "PE3-UNRESOLVED",
                          "R6": "27 passed — PREMATURE OBSERVATION — NOT ACCEPTANCE EVIDENCE",
                          "R10C": "STOP", "R10C1": "PRINCIPAL-SPEC-A"}}
    check("record-schema-valid", lambda: assert_equal(validate_record(record), True))
    incomplete = copy.deepcopy(record)
    incomplete.pop("environment")
    check("record-schema-missing-denied", lambda: denied(lambda: validate_record(incomplete)))
    drift = copy.deepcopy(record)
    drift["after"]["uv.lock"] = "0" * 64
    check("record-fingerprint-drift-denied", lambda: denied(lambda: validate_record(drift)))
    record["utc_start"] = start
    record["utc_end"] = datetime.now(timezone.utc).isoformat()
    if not record["decision"]["CUSTODY_READY"]:
        raise RuntimeError("clean-lineage gate denied")
    (run / "evidence/inspection-ledger.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    destination = run / "evidence/validation-record.json"
    destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"record": str(destination), "sha256": digest(destination.read_bytes()),
                      "tests": len(tests), **record["decision"]}))


def assert_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"{actual!r} != {expected!r}")


def child(run, purpose):
    tree = Path(__file__).resolve().parents[1]
    reader, events, firewall = load_controls(tree, run)
    policy = FilesystemPolicy(firewall, [run / name for name in ("temp", "evidence", "synthetic", "output")], [tree])
    sys.addaudithook(policy.audit)
    denied = False
    try:
        (tree / "data/synthetic-child-sentinel").open("rb")
    except PermissionError:
        denied = True
    if not denied:
        raise RuntimeError("child firewall inactive")
    if purpose == "timeout":
        print("synthetic child ready", flush=True)
        time.sleep(60)
    elif purpose == "nested":
        nested = run_child(tree, run, policy, "normal")
        assert nested["remaining_job_processes"] == 0 and nested["returncode"] == 0
        print(json.dumps({"nested": nested, "protected_denied": denied}), flush=True)
    else:
        print(json.dumps({"pid": os.getpid(), "protected_denied": denied, "environment_sha256": digest(canonical_json(dict(os.environ)))}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--synthetic-child", choices=("normal", "nested", "timeout"))
    args = parser.parse_args()
    run = args.run_root.resolve(strict=True)
    if args.synthetic_child:
        child(run, args.synthetic_child)
    else:
        certify(run)


if __name__ == "__main__":
    main()
