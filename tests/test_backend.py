import base64
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nixdatifier.cli import dispatch, parser
from nixdatifier.config import Target
from nixdatifier.flakes import remote, resolve_node, updates
from nixdatifier.jobs import run_job
from nixdatifier.process import BackendError, Result, Runner
from nixdatifier.state import cached, operation_lock
from nixdatifier.tools import hash_value


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"XDG_STATE_HOME": str(self.root / "state")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def lock_target(self):
        (self.root / "flake.nix").write_text("{}")
        lock = {"root": "root", "nodes": {"root": {"inputs": {"nixpkgs": "n", "alias": ["nixpkgs"]}},
                "n": {"locked": {"rev": "a" * 40}, "original": {"type": "github", "owner": "NixOS", "repo": "nixpkgs", "ref": "nixos-unstable"}}}}
        (self.root / "flake.lock").write_text(json.dumps(lock))
        return Target("system", "System", "nixos", str(self.root), "host")

    def test_offline_check_never_starts_network_processes(self):
        class Forbidden:
            def run(self, *_args, **_kwargs): raise AssertionError("Network started")
        data = updates(self.lock_target(), Forbidden(), offline=True)
        self.assertEqual([row["status"] for row in data["rows"]], ["offline", "follows"])

    def test_upstream_failure_is_distinct_from_up_to_date(self):
        class Broken:
            def run(self, *_args, **_kwargs): raise BackendError("DNS failed")
        data = updates(self.lock_target(), Broken())
        self.assertTrue(data["partial"])
        self.assertEqual(data["rows"][0]["status"], "unreachable")

    def test_annotated_tag_compares_peeled_commit(self):
        class Tag:
            def run(self, *_args, **_kwargs):
                return Result("b" * 40 + "\trefs/tags/release\n" + "a" * 40 + "\trefs/tags/release^{}\n", "", 0)
        data = updates(self.lock_target(), Tag())
        self.assertEqual(data["rows"][0]["status"], "unchanged")

    def test_explicit_revision_pin_is_not_checked(self):
        self.assertIsNone(remote({"type": "github", "owner": "o", "repo": "r", "rev": "a" * 40}))

    def test_nested_follows_resolves_and_cycles_fail(self):
        lock = {"root": "root", "nodes": {"root": {"inputs": {"child": "c", "cycle": ["cycle"]}},
                "c": {"inputs": {"nested": "n"}}, "n": {}}}
        self.assertEqual(resolve_node(lock, ["child", "nested"]), "n")
        with self.assertRaises(BackendError): resolve_node(lock, ["cycle"])

    def test_mutations_are_serialized(self):
        with operation_lock():
            with self.assertRaisesRegex(BackendError, "running"):
                with operation_lock(): pass

    def test_partial_network_result_is_not_cached(self):
        calls = []
        def load(): calls.append(1); return {"partial": True}
        cached("network", 3600, load)
        cached("network", 3600, load)
        self.assertEqual(len(calls), 2)

    def test_cache_reuses_success_and_invalidates_on_new_key(self):
        calls = []
        def load(): calls.append(1); return {"partial": False}
        cached(["flake", "old-lock"], 3600, load)
        cached(["flake", "old-lock"], 3600, load)
        cached(["flake", "new-lock"], 3600, load)
        self.assertEqual(len(calls), 2)

    def test_missing_program_returns_backend_error(self):
        with self.assertRaises(BackendError): Runner().run(["/nonexistent/nixdatifier-test-program"])

    def test_runner_times_out_instead_of_staying_busy(self):
        with self.assertRaisesRegex(BackendError, "timed out"):
            Runner().run([sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.05)

    def test_runner_does_not_interpret_shell_metacharacters(self):
        value = "';$(touch /tmp/nixdatifier-injection);'"
        result = Runner().run([sys.executable, "-c", "import sys; print(sys.argv[1])", value])
        self.assertEqual(result.stdout.strip(), value)

    def test_large_output_is_reported_not_silently_truncated(self):
        with self.assertRaisesRegex(BackendError, "exceeded"):
            Runner(limit=16).run([sys.executable, "-c", "print('x'*32)"])

    def test_hash_known_vector(self):
        path = self.root / "file"
        path.write_bytes(b"abc")
        result = hash_value("file", str(path), Runner())
        self.assertEqual(result["hex"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(base64.b64decode(result["sri"].split("-", 1)[1]).hex(), result["hex"])

    def test_jobs_require_confirmation_and_nonroot_user(self):
        target = self.lock_target()
        with self.assertRaisesRegex(BackendError, "confirmation"):
            run_job(target, "build", "", False)
        with patch("nixdatifier.jobs.os.geteuid", return_value=0):
            with self.assertRaisesRegex(BackendError, "desktop user"):
                run_job(target, "build", "", True)

    def test_job_build_failure_stops_before_activation(self):
        class Broken:
            calls = []
            def run(self, argv, **_kwargs):
                self.calls.append(argv)
                raise BackendError("Build failed")
        runner = Broken()
        with patch("nixdatifier.jobs.os.geteuid", return_value=1000), patch("nixdatifier.jobs.plan", return_value=[["build"], ["activate"]]):
            with self.assertRaisesRegex(BackendError, "Build failed"):
                run_job(self.lock_target(), "rebuild", "", True, runner)
        self.assertEqual(runner.calls, [["build"]])
        records = list((self.root / "state/nixdatifier-noctalia").glob("job-*.json"))
        self.assertEqual(json.loads(records[0].read_text())["status"], "failed")

    def test_cli_targets_does_not_evaluate_any_flake(self):
        target = self.lock_target()
        config = self.root / "targets.json"
        from dataclasses import asdict
        config.write_text(json.dumps({"schema_version": 1, "targets": [asdict(target)]}))
        args = parser().parse_args(["--config", str(config), "targets"])
        class Forbidden:
            def run(self, *_args, **_kwargs): raise AssertionError("Unexpected evaluation")
        self.assertEqual(dispatch(args, Forbidden())["rows"][0]["id"], "system")
