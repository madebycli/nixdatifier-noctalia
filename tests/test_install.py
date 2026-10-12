import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_registration_is_idempotent_and_preserves_existing_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, NOCTALIA_DATA_HOME=tmp)
            command = ["bash", str(ROOT / "bin/nixdatifier-install-plugin")]
            first = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            destination = Path(tmp) / "plugins/nixdatifier-noctalia"
            self.assertEqual(destination.resolve(), ROOT / "nixdatifier-noctalia")
            second = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0)
            destination.unlink()
            destination.mkdir()
            (destination / "keep").write_text("user copy")
            third = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertNotEqual(third.returncode, 0)
            self.assertEqual((destination / "keep").read_text(), "user copy")

    def test_context_route_and_production_modules_have_consistent_boundaries(self):
        route = (ROOT / ".ai/CONTEXT.md").read_text()
        self.assertIn("project_id: nixdatifier-noctalia", route)
        self.assertIn("entrypoint: projects/nixdatifier-noctalia/INDEX.md", route)
        for name in ("INDEX", "STATUS", "ARCHITECTURE", "SOURCES", "DECISIONS", "TASKS", "RISKS", "TESTS", "GRAPH"):
            self.assertTrue((ROOT / f".ai/{name}.md").exists())
        for folder, suffix in ((ROOT / "backend", "*.py"), (ROOT / "nixdatifier-noctalia", "*.luau")):
            for path in folder.rglob(suffix):
                self.assertLessEqual(len(path.read_text().splitlines()), 250, str(path))
