"""Annotation-only flight candidate audit; never prepares or simulates a graph.

Run with python -I -S -B and an explicit installed Arrow package directory.
The only admitted registered payload is a fixed, hash-verified annotation file.
Python audit hooks constrain Python file access, not arbitrary native syscalls.
Arrow parses the admitted bytes in memory; native-byte telemetry is not claimed.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys


SOURCE = "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
EXPECTED_SHA256 = "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2"
PATTERNS = {
    "photoreceptors": r"^(?:R1-R6|R1-6|R[1-8])$",
    "early_visual": r"^(?:L[1-5]|Mi1|Tm3|T4[a-d]?|T5[a-d]?)$",
    "visual_projection": r"^(?:HS[NTSE]?|H[12]|VS\d+|LC4|LPLC[124])$",
    "flight_power_descending": r"^DNg02(?:_[A-Za-z0-9]+)?$",
    "flight_turn_descending": r"^(?:DNp03|DNa15|DNae014|DNb01)$",
    "flight_orientation_descending": r"^(?:DNp20|DNp22|DNOVS[12]|DNHS1)$",
    "wing_motor_labels": r"^(?:[bi][1-4]|ps[1-2]|tp|hg[1-4]|DLM(?:n|N|MN)?\d*|DVM(?:n|N|MN)?\d*)$",
}
FIELDS = ("bodyId", "type", "flywireType", "mancType", "class", "superclass",
          "somaSide", "rootSide", "entryNerve", "exitNerve", "hemilineage",
          "instance", "status", "hex1_id", "hex2_id", "roiInfo")


def canonical_regular(path):
    """Reject reparse and hard-link identities before content access."""
    path = Path(path).absolute()
    for component in (path, *path.parents):
        info = component.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("reparse or symlink path rejected")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("individual regular unlinked file required")
    return path.resolve(strict=True)


def summarize(table):
    """Return exact annotation matches, without interpreting motor polarity."""
    columns = table.column_names
    if "bodyId" not in columns or "type" not in columns:
        raise ValueError("required bodyId/type annotation columns missing")
    selected = [name for name in FIELDS if name in columns]
    label_fields = [name for name in ("type", "flywireType", "mancType") if name in columns]
    groups = {name: {"pattern": pattern, "rows": []} for name, pattern in PATTERNS.items()}
    patterns = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}
    for row in table.select(selected).to_pylist():
        for name, pattern in patterns.items():
            matches = {field: row[field] for field in label_fields
                       if isinstance(row[field], str) and pattern.fullmatch(row[field])}
            if matches:
                groups[name]["rows"].append({**row, "matched_labels": matches})
    for group in groups.values():
        group["rows"].sort(key=lambda row: int(row["bodyId"]))
        group["count"] = len(group["rows"])
        native = [row for row in group["rows"] if "type" in row["matched_labels"]]
        group["native_type_match_count"] = len(native)
        group["native_soma_sides"] = {side: sum(row.get("somaSide") == side for row in native)
                                      for side in ("L", "R", None)}
    return {"columns": columns, "selected_columns": selected, "label_fields": label_fields,
            "annotation_rows": table.num_rows, "groups": groups,
            "spatial_columns": [name for name in columns if any(
                term in name.lower() for term in ("hex", "eye", "column", "coord", "position"))],
            "interpretation": "Annotation candidates only; no optical geometry, connectivity, actuator polarity, or flight dynamics validation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-packages", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise ValueError("use -I -S -B")
    root = Path(__file__).resolve().parents[1]
    source = canonical_regular(root / SOURCE)
    destination = Path(args.output).absolute()
    if destination.exists() or destination.parent.resolve() != (root / "docs" / "manifests").resolve():
        raise ValueError("new record in docs/manifests required")
    package_root = Path(args.site_packages).resolve(strict=True)
    if package_root != (root / ".venv" / "Lib" / "site-packages").resolve():
        raise ValueError("explicit project virtualenv Arrow directory required")
    reads = []
    source_admitted = True
    blocked_roots = [root / "data"]
    if os.environ.get("MALECNS_DATA_ROOT"):
        blocked_roots.append(Path(os.environ["MALECNS_DATA_ROOT"]).resolve())

    def audit(event, values):
        if event in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "socket.connect"):
            raise PermissionError("child execution or network rejected")
        if event != "open" or not isinstance(values[0], (str, bytes, os.PathLike)):
            return
        target = Path(os.fsdecode(values[0])).resolve()
        protected = any(target.is_relative_to(base) for base in blocked_roots)
        protected |= "male-cns-v1" in target.name.lower()
        if protected:
            mode = values[1]
            flags = values[2]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR)
            admitted = source_admitted and target == source and not writing and len(reads) == 0
            reads.append({"path": str(target), "admitted": bool(admitted)})
            if not admitted:
                raise PermissionError("registered payload outside finite annotation admission")

    sys.addaudithook(audit)
    result = {"schema": "flight-neuron-annotation-audit-v1", "outcome": "FAIL",
              "source": SOURCE, "expected_sha256": EXPECTED_SHA256, "registered_open_events": reads,
              "scientific_execution": False, "graph_preparation": False}
    try:
        with source.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            current = source.stat()
            if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
                raise ValueError("opened source identity changed")
            content = stream.read()
        source_admitted = False
        result["source_bytes"] = len(content)
        result["source_sha256"] = hashlib.sha256(content).hexdigest()
        if result["source_sha256"] != EXPECTED_SHA256:
            raise ValueError("annotation source hash mismatch; parsing forbidden")
        sys.path.insert(0, str(package_root))
        from pyarrow import feather
        result.update(summarize(feather.read_table(io.BytesIO(content))))
        result["outcome"] = "PASS_METADATA_ONLY"
    except BaseException as exc:
        result["failure"] = str(exc)
        raise
    finally:
        with destination.open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, allow_nan=False)
            output.write("\n")
    print(json.dumps({"outcome": result["outcome"], "source_sha256": result["source_sha256"],
                      "registered_open_events": len(reads),
                      "counts": {name: group["count"] for name, group in result["groups"].items()},
                      "spatial_columns": result["spatial_columns"]}))


if __name__ == "__main__":
    main()
