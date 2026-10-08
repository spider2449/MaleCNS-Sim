"""Prepare the registered MaleCNS network and serve the coupled flight view.

This launcher performs one explicit CPU preparation before opening the local
server. It does not create a synthetic fallback or prepare a graph in HTTP.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0..65535")

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from malecns_sim.application.flight import FlightSession
    from malecns_sim.application.flight_body import FlybodyBody
    from malecns_sim.application.flight_populations import native_flight_mapping
    from malecns_sim.application.server import LocalServer
    from malecns_sim.application.service import ProductionEngine
    from malecns_sim.application.workbench import DatasetCatalog
    from malecns_sim.runtime import prepare_runtime

    # Resolve the registered dataset from the checkout, independent of cwd.
    catalog = DatasetCatalog(root / "data", ProductionEngine())
    if not catalog.available():
        raise RuntimeError("registered MaleCNS v1.0 source files are unavailable")
    for path, expected in zip(
            (catalog.files.annotation, catalog.files.neurotransmitter, catalog.files.weights),
            (catalog.identity.annotation_sha256, catalog.identity.neurotransmitter_sha256,
             catalog.identity.weights_sha256)):
        if _digest(path) != expected:
            raise RuntimeError(f"registered source digest mismatch: {path.name}")

    print("Preparing the registered MaleCNS CPU network; the server is not open yet.", flush=True)
    prepared = catalog.engine.prepare(catalog.files, "cpu")
    runtime = prepare_runtime(prepared.projection, dt_ms=0.1)
    mapping = native_flight_mapping()
    mapping.validate(runtime.neuron_ids)
    print(f"Prepared {len(runtime.neuron_ids)} neurons; projection {runtime.projection_fingerprint}", flush=True)

    body = FlybodyBody(pattern_kind="engineered-oscillator")
    session = FlightSession(runtime, mapping, body,
                            expected_projection_fingerprint=runtime.projection_fingerprint)
    server = LocalServer(args.port, catalog=catalog, flight_session=session)
    url = f"http://127.0.0.1:{server.server_port}/flight#token={server.token}"
    print(f"MaleCNS real flight coupling\nOpen {url}", flush=True)
    if args.open:
        import webbrowser
        webbrowser.open(url, new=2)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMaleCNS real flight coupling stopped.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
