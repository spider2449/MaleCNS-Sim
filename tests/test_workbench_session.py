"""Browser session recovery regressions without scientific engine execution."""

import shutil
import subprocess
from pathlib import Path


def test_browser_session_recovery():
    node = shutil.which("node")
    assert node, "Node is required for browser session regressions"
    app = Path(__file__).parents[1] / "src/malecns_sim/application/static/app.js"
    script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8').split('const $ =')[0];
function load(blocked, hash, stored) {
  let removed = false, reloads = 0;
  const listeners = {};
  const location = {hash, pathname:'/', search:'', reload(){reloads++;}};
  const storage = {
    getItem(){if(blocked) throw Error('blocked'); return stored;},
    setItem(key, value){if(blocked) throw Error('blocked'); stored = value;}
  };
  const context = vm.createContext({URLSearchParams, location, sessionStorage:storage,
    window:{history:{replaceState(){removed=true;location.hash='';}},
      addEventListener(name, handler){listeners[name]=handler;}}});
  vm.runInContext(source, context);
  return {context, location, listeners, removed, reloads:()=>reloads};
}
let page = load(false, '#token=fresh', 'stale');
assert.equal(vm.runInContext('token', page.context), 'fresh');
assert.equal(page.removed, true);
page.location.hash = '#token=replacement';
page.listeners.hashchange();
assert.equal(page.reloads(), 1);
page.location.hash = '#other';page.listeners.hashchange();
assert.equal(page.reloads(), 1);
page = load(true, '#token=fresh', 'stale');
assert.equal(vm.runInContext('token', page.context), 'fresh');
assert.equal(page.removed, false);
assert.equal(page.location.hash, '#token=fresh');
page = load(false, '', 'fresh');
assert.equal(vm.runInContext('token', page.context), 'fresh');
"""
    import os
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        from session_node import command
        from a007c_node import environment
        result = subprocess.run(command(), env=environment(), cwd=str(app.parents[4]),
                                capture_output=True, text=True, timeout=30, close_fds=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'Browser session guard ACTIVE; payload and descendants BLOCKED' in result.stdout
    else:
        subprocess.run([node, "-e", script, str(app)], check=True)



def test_instances_and_exclusive_fixed_port(tmp_path):
    import threading
    import socket
    import pytest
    from malecns_sim.application.server import LocalServer
    from malecns_sim.application.workbench import DatasetCatalog
    from test_application_a003 import _request

    servers = [LocalServer(0, DatasetCatalog(tmp_path, None), tmp_path) for _ in range(2)]
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in servers]
    for thread in threads:
        thread.start()
    try:
        first, second = servers
        assert first.server_port != second.server_port
        assert first.token != second.token
        assert first.server_instance_id != second.server_instance_id
        for server in servers:
            port = server.server_port
            assert port > 0 and server.server_address[0] == "127.0.0.1"
            status, payload = _request(port, "GET", "/api/status")
            assert status == 200
            assert payload["server_instance_id"] == server.server_instance_id
            assert server.token not in str(payload) and "token" not in payload
            assert _request(port, "GET", "/api/runs", token=server.token)[0] == 200
            for route in ("/api/runs", "/api/runs/nope/result", "/api/comparisons/candidates"):
                assert _request(port, "GET", route)[0] == 403
            assert _request(port, "GET", "/api/runs", token="wrong")[0] == 403
            assert _request(port, "GET", "/api/runs", token=server.token, origin="http://evil.example")[0] == 403
            assert _request(port, "GET", "/api/status", host="evil.example")[0] == 403
            with pytest.raises(OSError):
                LocalServer(port, DatasetCatalog(tmp_path, None), tmp_path)
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                assert server.socket.getsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE) == 1
        code, payload = _request(second.server_port, "GET", "/api/runs", token=first.token)
        assert code == 403 and payload["error"]["session_reason"] == "rejected"
        assert payload["error"]["server_instance_id"] == second.server_instance_id
        assert _request(first.server_port, "GET", "/api/runs", token=first.token)[0] == 200
    finally:
        for server, thread in zip(servers, threads):
            server.shutdown()
            server.server_close()
            thread.join()


def test_default_launcher_prints_bound_owner(capsys, monkeypatch, tmp_path):
    import sys
    from urllib.parse import urlsplit, parse_qs
    from malecns_sim.application import server as module
    from malecns_sim.application.workbench import DatasetCatalog
    from test_application_a003 import _request
    import threading

    original = module.LocalServer
    real_serve = original.serve_forever
    captured = []
    def create(port):
        assert port == 0
        server = original(port, DatasetCatalog(tmp_path, None), tmp_path)
        captured.append(server)
        return server
    monkeypatch.setattr(module, "LocalServer", create)
    monkeypatch.setattr(sys, "argv", ["malecns-workbench"])
    def serve(server):
        output = capsys.readouterr().out
        assert output.startswith("MaleCNS workbench\nServer instance: " + server.server_instance_id)
        url = urlsplit(output.split("Open ")[1].strip())
        assert url.port == server.server_port > 0
        token = parse_qs(url.fragment)["token"][0]
        thread = threading.Thread(target=lambda: real_serve(server), daemon=True)
        thread.start()
        try:
            assert _request(url.port, "GET", "/api/runs", token=token)[0] == 200
        finally:
            server.shutdown()
            thread.join()
    monkeypatch.setattr(original, "serve_forever", serve)
    try:
        module.main()
    finally:
        for server in captured:
            server.server_close()



def test_launcher_keyboard_interrupt_closes_without_traceback(capsys, monkeypatch):
    import sys
    from unittest.mock import Mock
    from malecns_sim.application import server as module

    server = Mock(server_port=12345, token="test-token", server_instance_id="test-instance")
    server.serve_forever.side_effect = KeyboardInterrupt
    monkeypatch.setattr(module, "LocalServer", lambda port: server)
    monkeypatch.setattr(sys, "argv", ["malecns-workbench"])

    assert module.main() is None
    server.serve_forever.assert_called_once_with()
    server.server_close.assert_called_once_with()
    captured = capsys.readouterr()
    assert captured.out.endswith("\nMaleCNS workbench stopped.\n")
    assert captured.err == ""
