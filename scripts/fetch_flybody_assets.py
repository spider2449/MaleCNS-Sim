"""Download the published flybody flight policy and measured wing pattern.

Source: https://doi.org/10.25378/janelia.25309105 (figshare, version 4).
Archives are checked against figshare MD5s; the extracted policy directory and
wing pattern are checked against the SHA-256 identities pinned in
``malecns_sim.application.flight_body``. Nothing else is extracted.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.request
import zipfile

ARCHIVES = {
    "trained-fly-policies.zip": ("https://ndownloader.figshare.com/files/44815195",
                                 "12934d5a1c60631a710bc2b6d297d3ce", "flight/"),
    "datasets_flight-imitation.zip": ("https://ndownloader.figshare.com/files/51196859",
                                      "bb35ce27e07c4ffbd3d56ff6dec90905", "wing_pattern_fmech.npy"),
}


def _download(url: str, destination: Path, expected_md5: str) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "MaleCNS-Sim asset fetch"})
    digest = hashlib.md5()
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as handle:
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            digest.update(chunk)
            handle.write(chunk)
    if digest.hexdigest() != expected_md5:
        raise RuntimeError(f"{destination.name}: MD5 {digest.hexdigest()} differs from figshare {expected_md5}")


def _extract(archive: Path, member_prefix: str, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        members = [name for name in bundle.namelist() if name == member_prefix or name.startswith(member_prefix)]
        if not members:
            raise RuntimeError(f"{archive.name} lacks {member_prefix}")
        for name in members:
            target = (destination / name).resolve()
            if destination.resolve() not in target.parents:
                raise RuntimeError(f"unsafe archive path {name}")
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(name) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=root / "data" / "flybody")
    args = parser.parse_args()
    sys.path.insert(0, str(root / "src"))
    from malecns_sim.application.flight_body import (FLIGHT_POLICY_SHA256, WING_PATTERN_FMECH_SHA256,
                                                     directory_sha256)

    dest = args.dest.resolve()
    if (dest / "flight").exists() or (dest / "wing_pattern_fmech.npy").exists():
        raise SystemExit(f"{dest} already contains flybody assets; remove them to fetch again")
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        for name, (url, md5, member) in ARCHIVES.items():
            archive = Path(scratch) / name
            print(f"Downloading {name}...", flush=True)
            _download(url, archive, md5)
            _extract(archive, member, dest)
    policy_sha = directory_sha256(dest / "flight")
    pattern_sha = hashlib.sha256((dest / "wing_pattern_fmech.npy").read_bytes()).hexdigest()
    if policy_sha != FLIGHT_POLICY_SHA256 or pattern_sha != WING_PATTERN_FMECH_SHA256:
        raise SystemExit("extracted assets differ from the pinned identities; do not use them")
    print(f"Flight policy: {dest / 'flight'}\nWing pattern: {dest / 'wing_pattern_fmech.npy'}\nIdentities verified.")


if __name__ == "__main__":
    main()
