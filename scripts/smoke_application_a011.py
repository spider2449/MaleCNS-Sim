"""Install the built wheel in an isolated temporary environment and smoke it."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="a011-wheel-") as temporary:
    target = Path(temporary)
    subprocess.run([sys.executable, "-m", "venv", str(target / "venv")], check=True)
    python = target / "venv/Scripts/python.exe"
    subprocess.run(["uv", "pip", "install", "--python", str(python),
                    str(root / "dist/malecns_sim-0.3.0-py3-none-any.whl")], check=True)
    script = """from pathlib import Path
from importlib.metadata import version
import malecns_sim.application.arena as arena
from malecns_sim.application.server import LocalServer
s=arena.ArenaSession();s.step();assert s.arena.simulation_ms==20
assert version('malecns-sim')=='0.3.0'
assert 'site-packages' in str(Path(arena.__file__))
static=Path(arena.__file__).parent/'static'
for name in ('arena.html','arena.js','arena.css','index.html','app.js'): assert (static/name).is_file()
server=LocalServer(0);server.server_close()
print('Fresh wheel PASS: installed runtime, server and arena/static assets')
"""
    clean = os.environ.copy()
    clean.pop("PYTHONPATH", None)
    subprocess.run([str(python), "-c", script], cwd=target, env=clean, check=True)
