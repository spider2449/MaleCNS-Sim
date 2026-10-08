"""Guarded CPU artifact validation; historical suite evidence is never reused."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import threading
import types
import urllib.error
import urllib.request
import uuid
import zipfile

BASE = "80f57f97eb0429d6d9845766a78e0bc41cd524ca"
REPO = Path("D:/spider/working/MaleCNS-Sim")
DOCS = ("docs/runtime/USER_GUIDE.md", "docs/runtime/RELEASE_GATE.md",
        "docs/releases/0.4.0-preparation.md")
CORE = ("pyproject.toml", "uv.lock", "MANIFEST.in", "README.md", "LICENSE")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def archive_member_allowed(member):
    """Distinguish the package's data-loader code from protected dataset roots."""
    parts = Path(member).parts
    if not parts or Path(member).is_absolute() or ".." in parts:
        return False
    relative = parts[1:] if parts[0].startswith("malecns_sim-") else parts
    return (not relative or (relative[0] != "data"
            and not any(part in ("artifacts", "references", ".venv", "__pycache__") for part in relative)
            and "male-cns-v1" not in member.lower()))


def guard(root, installed=False):
    """Deny protected roots before content opens and unapproved Python children."""
    denied = [REPO / "data", REPO / "artifacts", root / "data", root / "artifacts"]
    if installed:
        denied.append(REPO)
    state = {"denied": 0, "accepted_protected": 0, "expected_child": None}

    def audit(event, args):
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            name = path.as_posix().lower()
            if (any(path.is_relative_to(item.resolve()) for item in denied)
                    or "male-cns-v1" in name or "male-cns/v1.0" in name):
                state["denied"] += 1
                raise PermissionError("A025 protected content denied")
        if event == "subprocess.Popen":
            expected = state["expected_child"]
            command = args[1]
            if isinstance(command, str):
                matches = expected is not None and command == subprocess.list2cmdline(expected)
            else:
                matches = expected is not None and list(command) == expected
            if not matches:
                raise PermissionError("A025 unapproved child denied")
    sys.addaudithook(audit)
    return state


def controls(root, state):
    """Exercise denials without creating or opening any protected file."""
    for target in (REPO / "data/absent", REPO / "artifacts/absent",
                   root / "male-cns-v1/absent"):
        try:
            target.read_bytes()
        except PermissionError:
            pass
        else:
            raise RuntimeError("protected control was admitted")
    try:
        subprocess.run([sys.executable, "-c", "raise SystemExit(99)"], check=True)
    except PermissionError:
        pass
    else:
        raise RuntimeError("child control was admitted")
    require(state["denied"] == 3, "denial accounting mismatch")
    for member in ("malecns_sim/data/__init__.py", "malecns_sim-0.3.0", "malecns_sim-0.3.0/src/malecns_sim/data/io.py"):
        require(archive_member_allowed(member), "ordinary archive fixture rejected")
    for member in ("data/raw/input.feather", "malecns_sim-0.3.0/data/provenance/a.json",
                   "docs/references/research.md", "../secret", "artifacts/result.json"):
        require(not archive_member_allowed(member), "excluded archive fixture admitted")


def smoke(run):
    """Import only the installed wheel after protection activation."""
    state = guard(run, installed=True)
    controls(run, state)
    sys.path.insert(0, str(run / "control/scripts/a019c_firewall"))
    import validation_firewall as firewall
    firewall.DENIED_ROOTS.extend([REPO, REPO / "artifacts", run / "artifacts"])
    firewall.install()
    require(firewall.ACTIVE, "firewall inactive")
    import importlib.metadata as metadata
    import malecns_sim
    import malecns_sim.runtime as runtime_module
    require(Path(malecns_sim.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),
            "project import is not installed artifact")
    require(importlib.util.find_spec("cupy") is None, "CuPy present in CPU environment")
    require(set(runtime_module.__all__) == {"prepare_runtime", "PreparedRuntime", "SimulationState", "AdvanceResult"},
            "public runtime exports changed")
    text = (run / "package/docs/runtime/USER_GUIDE.md").read_text(encoding="utf-8")
    examples = re.findall(r"```python\s*\n(.*?)```", text, re.S)
    require(len(examples) == 4, "guide example topology changed")
    namespace = {}
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(examples[0], "installed-guide-first", "exec"), namespace)
        exec(compile(examples[2], "installed-guide-poisson", "exec"), namespace)
    from malecns_sim import simulate_lif, ExplicitStimulus
    runtime = namespace["runtime"]
    full = namespace["full"]
    reference = simulate_lif(namespace["projection"], duration_ms=4.0, stimulus=full)
    whole = runtime.advance(runtime.initial_state(), duration_ms=4.0, stimulus=full)
    # The second guide example has already advanced its chunked state.
    chunk_state = namespace["state"]
    require(chunk_state.timestep == 40, "guide chunk horizon mismatch")
    chunked = runtime.initial_state()
    records = []
    for start, stop in ((0, 20), (20, 40)):
        from malecns_sim import SpikeSchedule
        local = ExplicitStimulus(tuple(SpikeSchedule(schedule.neuron_id, tuple(
            (step - start) * runtime.dt_ms for time in schedule.spike_times_ms
            for step in (int(round(time / runtime.dt_ms)),) if start <= step < stop
        )) for schedule in full.schedules), weight_mV=full.weight_mV,
            refractory_free_neuron_ids=full.refractory_free_neuron_ids)
        records.append(runtime.advance(chunked, duration_ms=2.0, stimulus=local))
    require(whole.spike_neuron_ids == sum((item.spike_neuron_ids for item in records), ()),
            "chunked spike identity differs from whole horizon")
    require(whole.spike_timesteps == sum((item.spike_timesteps for item in records), ()),
            "chunked spike times differ from whole horizon")
    # Dense reference counts are an independent legacy-engine oracle.
    from collections import Counter
    counts = Counter(whole.spike_neuron_ids)
    require(all(counts[neuron] == int(reference.spike_counts[index])
                for index, neuron in enumerate(runtime.neuron_ids)), "legacy engine count mismatch")
    require(whole.spike_neuron_ids == tuple(map(int, reference.spike_neuron_ids))
            and whole.spike_timesteps == tuple(map(int, reference.spike_timesteps)),
            "legacy engine event oracle mismatch")
    entries = metadata.entry_points(group="console_scripts")
    help_results = {}
    for name in ("malecns-sim", "malecns-workbench"):
        entry = next(item for item in entries if item.name == name)
        previous = sys.argv
        sys.argv = [name, "--help"]
        try:
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                try:
                    entry.load()()
                except SystemExit as exc:
                    require(exc.code == 0, "CLI help failed")
            require("usage:" in captured.getvalue(), "CLI help missing")
            help_results[name] = entry.value
        finally:
            sys.argv = previous
    from malecns_sim.application.server import LocalServer
    server = LocalServer(0, result_root=run / "workbench-results")
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    assets = {}
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url + "/api/status", timeout=10) as response:
            require(json.load(response)["status"] == "READY", "workbench not ready")
        try:
            opener.open(url + "/api/runs", timeout=10)
        except urllib.error.HTTPError as exc:
            require(exc.code == 403, "unauthenticated runs did not reject")
        else:
            raise RuntimeError("unauthenticated runs accepted")
        request = urllib.request.Request(url + "/api/runs", headers={"X-Local-Session": server.token})
        with opener.open(request, timeout=10) as response:
            require(response.status == 200, "authenticated runs did not succeed")
            json.load(response)
        for route in ("/", "/app.js", "/style.css", "/arena", "/arena.js", "/arena.css"):
            with opener.open(url + route, timeout=10) as response:
                data = response.read()
                require(bool(data), "empty static asset")
                assets[route] = hashlib.sha256(data).hexdigest()
    finally:
        server.shutdown()
        thread.join(timeout=10)
        server.server_close()
        require(not thread.is_alive(), "server thread survived shutdown")
    result = {"status": "PASS", "python": sys.version, "origin": malecns_sim.__file__,
              "dependencies": sorted((item.metadata["Name"], item.version) for item in metadata.distributions()),
              "guide_output": output.getvalue(), "guide_examples": 2, "independent_oracle": "legacy dense spike counts",
              "cli": help_results, "assets": assets, "guard": state, "server_cleanup": "PASS"}
    (run / "smoke.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def main():
    run = Path("C:/TEMP") / ("malecns-a025-" + uuid.uuid4().hex)
    run.mkdir()
    state = guard(run)
    controls(run, state)
    job_module = types.ModuleType("a025_job")
    exec(compile((REPO / "scripts/a023_local_repro.py").read_bytes(), "reviewed-job-control", "exec"), job_module.__dict__)
    commands = []
    environment = {key: value for key, value in os.environ.items()
                   if key.upper() in ("SYSTEMROOT", "WINDIR", "COMSPEC", "SYSTEMDRIVE", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS")}
    for directory in ("temp", "home", "uv-cache", "logs", "evidence"):
        (run / directory).mkdir()
    environment.update(TEMP=str(run / "temp"), TMP=str(run / "temp"), HOME=str(run / "home"),
                       USERPROFILE=str(run / "home"), UV_CACHE_DIR=str(run / "uv-cache"),
                       PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + str(Path(environment["SYSTEMROOT"]) / "System32")

    def command(argv, cwd, capture=False):
        argv = list(map(str, argv))
        state["expected_child"] = argv
        job = job_module.Job()
        log = run / "logs" / f"{len(commands):02}.txt"
        try:
            with log.open("w", encoding="utf-8") as stream:
                process = subprocess.Popen(argv, cwd=cwd, env=environment, stdout=stream,
                                           stderr=subprocess.STDOUT, creationflags=4, close_fds=True)
                try:
                    job.assign_resume(process)
                    code = process.wait(timeout=600)
                    accounting = job.accounting()
                    require(accounting["active"] == 0, "active child descendants")
                except BaseException:
                    process.kill()
                    process.wait()
                    job.terminate()
                    raise
            commands.append({"argv": argv, "cwd": str(cwd), "exit": code, "job": accounting, "log": str(log)})
            (run / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
            require(code == 0, "command failed: " + str(log))
            return log.read_text(encoding="utf-8") if capture else None
        finally:
            state["expected_child"] = None
            job.close()

    git, uv = shutil.which("git"), shutil.which("uv")
    require(git and uv, "required tools missing")
    require(command([git, "rev-parse", "HEAD"], REPO, True).strip() == BASE, "source identity changed")
    inventory = command([git, "ls-files", "src"], REPO, True).splitlines()
    inputs = sorted(set(inventory) | set(CORE) | set(DOCS))
    require(all(not (REPO / path).is_symlink() for path in inputs), "symlink input denied")
    before = {path: sha(REPO / path) for path in inputs}
    package = run / "package"
    package.mkdir()
    for path in inputs:
        destination = package / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((REPO / path).read_bytes())
        require(sha(destination) == before[path], "transfer mismatch")
    control_paths = ["scripts/a025_artifact_validation.py", "scripts/a023_local_repro.py"]
    control_paths += ["scripts/a019c_firewall/" + name for name in
                      ("validation_firewall.py", "a007c_node.py", "a006r_node.py", "guarded_child.py", "sitecustomize.py")]
    control_hashes = {}
    for path in control_paths:
        destination = run / "control" / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((REPO / path).read_bytes())
        control_hashes[path] = sha(destination)
    frozen = {"base": BASE, "inputs": before, "controls": control_hashes, "build_backend": "setuptools==80.9.0",
              "historical_suite": "NOT RUN; original H/I/N preserved; no GPU execution admitted",
              "I1": "NOT RUN — REGISTERED-PAYLOAD-REQUIRED", "guides_shipped": list(DOCS)}
    (run / "candidate.json").write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
    print("A025 artifact run: " + str(run), flush=True)
    command([uv, "venv", "--python", sys.executable, run / "build-env", "--no-config"], run)
    build_python = run / "build-env/Scripts/python.exe"
    command([uv, "pip", "install", "--python", build_python, "--no-config", "setuptools==80.9.0"], run)
    command([uv, "build", "--python", build_python, "--no-build-isolation", "--no-config", "--out-dir", run / "dist"], package)
    wheels = list((run / "dist").glob("*.whl"))
    sdists = list((run / "dist").glob("*.tar.gz"))
    require(len(wheels) == len(sdists) == 1, "artifact count mismatch")
    with zipfile.ZipFile(wheels[0]) as archive:
        wheel_members = archive.namelist()
    with tarfile.open(sdists[0]) as archive:
        sdist_members = archive.getnames()
    for member in wheel_members + sdist_members:
        require(archive_member_allowed(member), "excluded archive member: " + member)
    require(all(any(member.endswith("/" + path) for member in sdist_members) for path in DOCS), "sdist guides missing")
    command([uv, "sync", "--python", sys.executable, "--frozen", "--no-dev", "--no-install-project", "--no-config"], package)
    installed_python = package / ".venv/Scripts/python.exe"
    command([uv, "pip", "install", "--python", installed_python, "--no-deps", "--no-config", wheels[0]], run)
    environment["MALECNS_A019C_R2_LOG"] = str(run / "evidence/firewall.jsonl")
    command([installed_python, "-I", "-B", run / "control/scripts/a025_artifact_validation.py", "--smoke", run], run)
    after = {path: sha(REPO / path) for path in inputs}
    require(before == after, "source changed during validation")
    require(all(sha(REPO / path) == expected for path, expected in control_hashes.items()), "control source drift")
    result = {"status": "CPU ARTIFACT PASS; FULL A025 GATE INCOMPLETE", "candidate": frozen,
              "run": str(run), "tools": {str(path): sha(path) for path in (git, uv, sys.executable)},
              "commands": commands, "artifacts": {path.name: sha(path) for path in wheels + sdists},
              "wheel_members": wheel_members, "sdist_members": sdist_members,
              "before_after_equal": True, "guard": state, "smoke": json.loads((run / "smoke.json").read_text())}
    (run / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": str(run), "status": result["status"]}), flush=True)


if __name__ == "__main__":
    raise SystemExit("EXECUTION_DENIED: A025 route certification is incomplete; preserve the contract-violation record")
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke":
        smoke(Path(sys.argv[2]).resolve())
    elif len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        control_root = Path("C:/TEMP")
        control_state = guard(control_root)
        controls(control_root, control_state)
        print("A025 denial controls PASS")
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit("invalid A025 command")
