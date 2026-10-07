"""R3-only exact-path inspection; no subprocesses or reference following.

Run with Python -I -S -B. The fixed guard source is the reviewed bootstrap
exception. Its identity is pinned; its unchanged check() defines protection.
The ledger covers control-source reads as well as requested content reads.
This is an operational inspection route, not an arbitrary-command sandbox.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import stat
import sys
import types

GUARD = "scripts/a019c_firewall/validation_firewall.py"
GUARD_SHA256 = "170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af"


class Rejected(ValueError):
    """A target cannot safely be opened."""


def repository_root():
    """Discover custody by metadata only, without reading the .git marker."""
    for candidate in Path(__file__).absolute().parents:
        if (candidate / ".git").exists():
            return candidate.resolve(strict=True)
    raise Rejected("repository root UNKNOWN")


def exact_target(root, relative):
    """Validate lexical and filesystem metadata before any content access."""
    if not isinstance(relative, str) or not relative:
        raise Rejected("explicit individual relative path required")
    windows = PureWindowsPath(relative)
    parts = relative.replace("\\", "/").split("/")
    if (Path(relative).is_absolute() or windows.drive or windows.root
            or any(c in relative for c in "*?[]:\x00")
            or any(p in ("", ".", "..") for p in parts)):
        raise Rejected("absolute, wildcard, ambiguous or traversal path")
    root = Path(root).resolve(strict=True)
    current = root
    # Reject every reparse point, including junctions, even inside custody.
    for component in [root, *[root.joinpath(*parts[:i])
                              for i in range(1, len(parts) + 1)]]:
        info = component.lstat()
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400):
            raise Rejected("symlink/reparse target")
        current = component
    canonical = current.resolve(strict=True)
    if not canonical.is_relative_to(root):
        raise Rejected("outside repository")
    info = canonical.stat()
    if not stat.S_ISREG(info.st_mode):
        raise Rejected("individual regular file required")
    if info.st_nlink != 1:
        raise Rejected("hard-link protection identity UNKNOWN")
    return canonical, info


class Inspector:
    def __init__(self, root, classifier, ledger=None):
        self.root = Path(root).resolve(strict=True)
        self.classifier = classifier
        self.ledger = [] if ledger is None else ledger

    def inspect(self, relative, role="requested", expected_hash=None):
        event = dict(path=relative, role=role, metadata_checked=False,
                     content_opened=False)
        self.ledger.append(event)
        try:
            target, before = exact_target(self.root, relative)
            event.update(metadata_checked=True, canonical_path=str(target))
            decision = self.classifier(target)
            event["protection"] = decision
            if decision != "SAFE":
                raise Rejected("protection is " + str(decision))
            # Repeat metadata checks after classification; do not claim an OS
            # sandbox against concurrent hostile replacement of the workspace.
            again, checked = exact_target(self.root, relative)
            if again != target or (before.st_dev, before.st_ino) != (
                    checked.st_dev, checked.st_ino):
                raise Rejected("target changed before open")
            with target.open("rb") as stream:
                event["content_opened"] = True
                opened = os.fstat(stream.fileno())
                if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    raise Rejected("opened identity changed")
                content = stream.read()
            digest = hashlib.sha256(content).hexdigest()
            event.update(bytes=len(content), sha256=digest)
            if expected_hash is not None and digest != expected_hash:
                raise Rejected("reviewed control identity changed")
            event["result"] = "ACCEPTED"
            return content
        except Exception as exc:
            event.update(result="REJECTED", reason=str(exc))
            raise Rejected(str(exc)) from exc


def bootstrap(root, ledger):
    """Read only the explicitly reviewed fixed control, then reuse check()."""
    bootstrap_reader = Inspector(
        root, lambda path: "SAFE" if path == root / GUARD else "UNKNOWN", ledger)
    content = bootstrap_reader.inspect(GUARD, "reviewed-guard-bootstrap",
                                       GUARD_SHA256)
    module = types.ModuleType("a023_reviewed_validation_firewall")
    module.__file__ = str(root / GUARD)
    exec(compile(content, module.__file__, "exec"), module.__dict__)
    if module.ROOT != root:
        raise Rejected("guard/root custody mismatch")

    def classify(path):
        try:
            module.check(path)
        except module.SourceAccessDenied:
            return "PROTECTED"
        except Exception:
            return "UNKNOWN"
        return "SAFE"

    if classify(root / GUARD) != "SAFE":
        raise Rejected("bootstrap control not safe under guard")
    return Inspector(root, classify, ledger)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True,
                        help="new external JSON ledger; must not already exist")
    parser.add_argument("--emit", action="store_true",
                        help="emit only explicitly requested accepted content")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    root = repository_root()
    destination = Path(args.ledger).resolve()
    if destination.is_relative_to(root) or destination.exists():
        raise Rejected("ledger must be new and outside repository")
    # Reserve the external ledger before opening repository content.
    events = []
    outcome = "FAIL"
    with destination.open("x", encoding="utf-8") as output:
        try:
            reader = bootstrap(root, events)
            reader.inspect("scripts/a023_fail_closed_inspect.py", "reader-control")
            for relative in args.paths:
                content = reader.inspect(relative)
                if args.emit:
                    print("=== " + relative + " ===", flush=True)
                    sys.stdout.buffer.write(content)
                    sys.stdout.buffer.write(b"\n")
                    sys.stdout.buffer.flush()
            outcome = "PASS"
        finally:
            record = dict(root=str(root), outcome=outcome, events=events,
                          protected_content_opens=sum(
                              e["content_opened"] and e.get("protection") != "SAFE"
                              for e in events))
            json.dump(record, output, indent=2)
            output.write("\n")
    print(json.dumps(dict(outcome=outcome, ledger=str(destination),
                         opened_content_events=sum(e["content_opened"] for e in events))))


if __name__ == "__main__":
    main()
