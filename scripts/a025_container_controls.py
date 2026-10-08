"""Certify a finite Docker mount boundary using synthetic ordinary files only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import uuid

IMAGE = "sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203"


def command(*arguments: str) -> str:
    result = subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "--exec", "/usr/bin/docker", *arguments],
        text=True, capture_output=True, check=True, timeout=60,
    )
    return result.stdout


def main() -> None:
    token = uuid.uuid4().hex
    root = Path("C:/TEMP") / ("malecns-a025-controls-" + token)
    ordinary = root / "ordinary"
    ordinary.mkdir(parents=True)
    (ordinary / "positive.txt").write_text("ordinary-control", encoding="utf-8")
    sentinel = root / "unmounted-sentinel.txt"
    sentinel.write_text("synthetic-unmounted-control", encoding="utf-8")
    linux_root = "/mnt/c/TEMP/" + root.name
    name = "malecns-a025-controls-" + token
    probe = """
import json, os, pathlib, subprocess
assert pathlib.Path('/input/positive.txt').read_text() == 'ordinary-control'
assert os.getuid() == 1000
status = pathlib.Path('/proc/self/status').read_text()
assert 'CapEff:\\t0000000000000000' in status
assert 'NoNewPrivs:\\t1' in status
try:
    pathlib.Path('/input/forbidden-write').write_text('denied')
except OSError:
    pass
else:
    raise RuntimeError('read-only input accepted a write')
denied = [SENTINEL, '/mnt/d/spider/working/MaleCNS-Sim/data',
          '/mnt/d/spider/working/MaleCNS-Sim/artifacts',
          '/var/run/docker.sock', '/run/WSL', '/proc/1/root/mnt/c']
for target in denied:
    result = subprocess.run(['/bin/cat', target], capture_output=True)
    assert result.returncode != 0 and not result.stdout, target
child = subprocess.run(['/usr/local/bin/python', '-I', '-c',
    "import pathlib; assert not pathlib.Path(" + repr(SENTINEL) + ").exists()"], check=True)
assert not pathlib.Path('/mnt/c').exists()
assert not pathlib.Path('/mnt/d').exists()
print(json.dumps({'status': 'PASS', 'native_denials': len(denied),
                  'child_boundary': 'PASS', 'readonly_input': 'PASS',
                  'uid': os.getuid(), 'mountinfo': pathlib.Path('/proc/self/mountinfo').read_text()}))
""".replace("SENTINEL", repr(linux_root + "/unmounted-sentinel.txt"))
    created = False
    evidence = {"image": IMAGE, "run": str(root), "claim": "synthetic mount-boundary controls only"}
    try:
        container = command(
            "create", "--name", name, "--pull=never", "--init", "--read-only",
            "--user", "1000:1000", "--cap-drop=ALL", "--security-opt", "no-new-privileges",
            "--network=none", "--pids-limit=64", "--memory=256m",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
            "--mount", "type=bind,src=" + linux_root + "/ordinary,dst=/input,readonly",
            IMAGE, "/usr/local/bin/python", "-I", "-B", "-c", probe,
        ).strip()
        created = True
        info = json.loads(command("inspect", container))[0]
        host = info["HostConfig"]
        assert host["Privileged"] is False and host["ReadonlyRootfs"] is True
        assert host["NetworkMode"] == "none" and host["PidMode"] == ""
        assert host["CapDrop"] == ["ALL"] and host["Devices"] == []
        assert "no-new-privileges" in host["SecurityOpt"]
        assert info["Config"]["User"] == "1000:1000" and info["Image"] == IMAGE
        mounts = info["Mounts"]
        assert len(mounts) == 1 and mounts[0]["Destination"] == "/input"
        assert mounts[0]["Source"] == linux_root + "/ordinary" and mounts[0]["RW"] is False
        output = command("start", "--attach", container)
        state = json.loads(command("inspect", container))[0]["State"]
        assert state["ExitCode"] == 0 and not state["Running"]
        evidence.update(status="PASS", configuration=host, mounts=mounts,
                        controls=json.loads(output), terminal_state=state)
    finally:
        if created:
            command("rm", name)
            assert not command("ps", "--all", "--quiet", "--filter", "name=^/" + name + "$").strip()
            evidence["cleanup"] = "container removed; no matching container remains"
        (root / "controls.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "evidence": str(root / "controls.json")}))


if __name__ == "__main__":
    main()
