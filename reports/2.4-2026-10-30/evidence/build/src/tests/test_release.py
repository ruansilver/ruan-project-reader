"""Release rules and rollback, entirely in temporary engineering directories."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("build_release", Path(__file__).resolve().parents[1] / "build_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "design/versions").mkdir(parents=True)
        self.source = self.root / "src/ruan-project-reader"
        self.source.mkdir(parents=True)

    def design(self, version, status="approved"):
        path = self.root / "design/versions" / f"{version}.md"
        path.write_text(f'---\nversion: "{version}"\nstatus: {status}\n---\n\n# Design\n', encoding="utf-8")
        return path

    def source_version(self, version):
        (self.source / "SKILL.md").write_text(f'---\nname: ruan-project-reader\ndescription: Test release\nmetadata:\n  version: "{version}"\n---\n\n# Test\n', encoding="utf-8")

    def test_numeric_semver_approved_only(self):
        self.design("1.9.0")
        self.design("1.10.0")
        self.design("2.2.0", "draft")
        self.assertEqual(release.select_target(self.root)[0], "1.10.0")

    def test_no_approved(self):
        self.design("2.2.0", "draft")
        with self.assertRaises(ValueError):
            release.select_target(self.root)

    def test_filename_conflict(self):
        self.design("2.2.0").rename(self.root / "design/versions/2.3.0.md")
        with self.assertRaises(ValueError):
            release.select_target(self.root)

    def test_duplicate_metadata_rejected(self):
        path = self.design("2.2.0")
        path.write_text('---\nversion: "2.2.0"\nversion: "2.1.0"\nstatus: approved\n---\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            release.select_target(self.root)

    def test_build_hash_and_idempotence(self):
        self.design("2.2.0")
        self.source_version("2.2.0")
        (self.source / ".gitkeep").touch()
        (self.source / "__pycache__").mkdir()
        (self.source / "__pycache__/x.pyc").write_bytes(b"cache")
        data, changed = release.publish(self.root)
        self.assertTrue(changed)
        self.assertFalse((self.root / "install/ruan-project-reader/.gitkeep").exists())
        self.assertFalse((self.root / "install/ruan-project-reader/__pycache__").exists())
        self.assertEqual(release.verify_release(self.root), data)
        self.assertFalse(release.publish(self.root)[1])

    def test_normalized_text_hash_binary_unchanged(self):
        p = self.source / "文本.md"
        p.write_bytes(b"first\nsecond\n")
        initial = release.artifact_hash(self.source)
        p.write_bytes(b"first\r\nsecond\r\n")
        self.assertEqual(initial, release.artifact_hash(self.source))
        self.assertEqual(release.normalized(b"\xff\r\n"), b"\xff\r\n")

    def test_modified_artifact_stops_before_writes(self):
        self.design("1.0.0")
        self.source_version("1.0.0")
        release.publish(self.root)
        installed = self.root / "install/ruan-project-reader/SKILL.md"
        installed.write_text("user edit", encoding="utf-8")
        self.design("2.2.0")
        self.source_version("2.2.0")
        with self.assertRaises(ValueError):
            release.publish(self.root)
        self.assertEqual(installed.read_text(), "user edit")

    def test_failed_validation_preserves_release(self):
        self.design("1.0.0")
        self.source_version("1.0.0")
        old, _ = release.publish(self.root)
        self.design("2.2.0")
        with self.assertRaises(ValueError):
            release.publish(self.root)
        self.assertEqual(release.verify_release(self.root), old)

    def test_failed_replacement_rolls_back(self):
        self.design("1.0.0")
        self.source_version("1.0.0")
        old, _ = release.publish(self.root)
        self.design("2.2.0")
        self.source_version("2.2.0")
        original = release.os.replace
        calls = []

        def fail_once(src, dst):
            calls.append((src, dst))
            if len(calls) == 2:
                raise OSError("injected replace failure")
            return original(src, dst)

        with patch.object(release.os, "replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                release.publish(self.root)
        self.assertEqual(release.verify_release(self.root), old)

    def test_manifest_derived_exact_fields(self):
        self.design("2.2.0")
        self.source_version("2.2.0")
        data, _ = release.publish(self.root)
        self.assertEqual(set(data), {"version", "design_document", "skill_name", "design_sha256", "artifact_sha256"})
        self.assertEqual(json.loads((self.root / "install/.release.json").read_text()), data)


if __name__ == "__main__":
    unittest.main()
