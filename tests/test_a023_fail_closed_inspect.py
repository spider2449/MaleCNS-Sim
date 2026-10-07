"""Isolated unittest self-tests using synthetic temporary files only."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "scripts/a023_fail_closed_inspect.py"
SPEC = importlib.util.spec_from_file_location("a023_inspect", SOURCE)
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "safe.py").write_bytes(b"import other\n")
        (self.root / "other.py").write_bytes(b"not followed\n")
        (self.root / "protected.bin").write_bytes(b"synthetic only")
        (self.root / "unknown.py").write_bytes(b"unknown")
        (self.root / "directory").mkdir()
        self.reader = INSPECT.Inspector(self.root, self.classify)

    @staticmethod
    def classify(path):
        return {"protected.bin": "PROTECTED", "unknown.py": "UNKNOWN"}.get(
            path.name, "SAFE")

    def assert_before_open(self, path):
        with patch.object(Path, "open", side_effect=AssertionError("opened")) as sentinel:
            with self.assertRaises(INSPECT.Rejected):
                self.reader.inspect(path)
            sentinel.assert_not_called()
        self.assertFalse(self.reader.ledger[-1]["content_opened"])

    def test_exact_safe_content_and_ledger(self):
        self.assertEqual(self.reader.inspect("safe.py"), b"import other\n")
        event = self.reader.ledger[0]
        self.assertEqual(event["bytes"], 13)
        self.assertEqual(event["sha256"], hashlib.sha256(b"import other\n").hexdigest())
        self.assertTrue(event["metadata_checked"])
        self.assertTrue(event["content_opened"])
        self.assertNotIn("content", event)

    def test_wildcards(self):
        for path in ("*.py", "safe?.py", "[s]afe.py", "directory/**/*.py"):
            self.assert_before_open(path)

    def test_directory(self):
        self.assert_before_open("directory")

    def test_traversal(self):
        for path in ("../outside.py", "directory/../safe.py", "directory\\..\\safe.py"):
            self.assert_before_open(path)

    def test_absolute_outside(self):
        self.assert_before_open(str(self.root.parent / "outside.py"))
        self.assert_before_open("C:\\outside.py")

    def test_protected_before_open(self):
        self.assert_before_open("protected.bin")
        self.assertEqual(self.reader.ledger[-1]["protection"], "PROTECTED")

    def test_unknown_before_open(self):
        self.assert_before_open("unknown.py")

    def test_classifier_exception_before_open(self):
        self.reader.classifier = lambda path: (_ for _ in ()).throw(ValueError("UNKNOWN"))
        self.assert_before_open("safe.py")

    def test_explicit_multiple_no_following_exact_ledger(self):
        self.reader.inspect("safe.py")
        self.assertEqual([e["path"] for e in self.reader.ledger], ["safe.py"])
        self.reader.inspect("other.py")
        self.assert_before_open("protected.bin")
        self.assertEqual([e["path"] for e in self.reader.ledger if e["content_opened"]],
                         ["safe.py", "other.py"])
        self.assert_before_open(["safe.py", "other.py"])

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.py"
            target.write_bytes(b"synthetic outside")
            try:
                (self.root / "link.py").symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest("symlinks unavailable: " + str(exc))
            self.assert_before_open("link.py")

    def test_reparse_attribute_before_open(self):
        original = Path.lstat

        def metadata(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path.name == "safe.py":
                class ReparseMetadata:
                    st_mode = result.st_mode
                    st_file_attributes = 0x400
                return ReparseMetadata()
            return result

        with patch.object(Path, "lstat", metadata):
            self.assert_before_open("safe.py")

    def test_hardlink_ambiguity(self):
        try:
            (self.root / "alias.py").hardlink_to(self.root / "safe.py")
        except OSError as exc:
            self.skipTest("hard links unavailable: " + str(exc))
        self.assert_before_open("alias.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
