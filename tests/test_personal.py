import json
import os
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nixdatifier.actions import plan
from nixdatifier.adapters import madebycli_command
from nixdatifier.config import Target, autodetect
from nixdatifier.personal import installed_config
from nixdatifier.process import BackendError, Result


class Runner:
    def __init__(self, origin="https://github.com/madebycli/nix-config.git"):
        self.origin = origin
    def run(self, args, **kwargs):
        return Result(self.origin if args[0] == "git" else "nyx", "", 0)


class PersonalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.repo = self.home / "custom checkout ' $(not-a-command)"
        self.repo.mkdir()
        (self.repo / "flake.nix").write_text("{}")
        for host in ("nyx", "aether"):
            path = self.repo / "hosts" / host
            path.mkdir(parents=True)
            (path / "features.nix").write_text('{ my.kernel = "latest"; }')
        (self.repo / "flake.lock").write_text(json.dumps({"root": "root", "nodes": {
            "root": {"inputs": {"noctalia": "noctalia"}}, "noctalia": {"locked": {}, "original": {}}
        }}))
        self.conf = self.home / "nixctl.conf"
        self.conf.write_text(f"REPO={shlex.quote(str(self.repo))}\nHOST=nyx\n")
        self.env = patch.dict(os.environ, {"NX_CONF": str(self.conf), "NIXCTL_CONF": str(self.conf)})
        self.env.start(); self.addCleanup(self.env.stop)
        self.host = patch("socket.gethostname", return_value="nyx")
        self.host.start(); self.addCleanup(self.host.stop)
        self.target = Target("nyx", "Nyx", "nixos", str(self.repo), "nyx", "nyx", "madebycli")

    def test_current_source_fixture_contains_exactly_two_real_hosts(self):
        value = json.loads((Path(__file__).parent / "fixtures/madebycli-outputs.json").read_text())
        self.assertEqual(value["nixosConfigurations"], ["aether", "nyx"])
        with patch("nixdatifier.config.Path.home", return_value=self.home):
            targets = autodetect()
        self.assertEqual([t.attribute for t in targets], ["nyx", "aether", ""])
        self.assertEqual(targets[-1].kind, "profile")
        self.assertTrue(all(t.flake == str(self.repo) for t in targets[:-1]))

    def test_old_profile_marker_and_saved_sync_state_are_not_read(self):
        (self.home / "profile").write_text("nyx-all")
        old = self.home / ".local/state/nixos-config/a"
        old.mkdir(parents=True)
        (old / "state.json").write_text('{"profile":"nyx-niri"}')
        with patch("nixdatifier.config.Path.home", return_value=self.home):
            self.assertEqual(autodetect()[0].attribute, "nyx")

    def test_current_commands_keep_build_confirmation_and_lock_lifecycle_in_nx(self):
        cases = [("rebuild", "", ["nx", "switch"]), ("refresh", "all", ["nx", "update"]),
                 ("refresh", "desktop", ["nx", "update", "desktop"]),
                 ("refresh", "apps", ["nx", "update", "apps"]),
                 ("preview-updates", "base", ["nx", "check"]),
                 ("clean", "5", ["nx", "clean", "5"]),
                 ("optimize", "", ["nx", "optimise"]), ("rollback", "", ["nx", "rollback"]),
                 ("sync", "", ["dots", "sync"]), ("pull", "", ["nx", "pull"]),
                 ("settings", "", ["nix-settings"]), ("dot-pull", "", ["dots", "pull"])]
        for action, argument, expected in cases:
            with self.subTest(action=action, argument=argument):
                commands = plan(self.target, action, argument, Runner())
                self.assertEqual(commands, [expected])
                self.assertFalse(set(expected) & {"--yes", "--commit", "--push"})

    def test_individual_personal_input_update_uses_transactional_nx_flow(self):
        self.assertEqual(plan(self.target, "update-input", "noctalia", Runner()), [["nx", "update", "noctalia"]])
        with self.assertRaises(BackendError):
            plan(self.target, "update-input", "--push", Runner())

    def test_removed_profiles_and_foreign_hosts_cannot_run_personal_mutations(self):
        for host, attribute in [("nyx", "nyx-niri"), ("aether", "aether"), ("nyx", "nyx; injected")]:
            target = Target("bad", "Bad", "nixos", str(self.repo), attribute, host, "madebycli")
            with self.assertRaises(BackendError):
                madebycli_command(target, "refresh", "all", Runner())

    def test_origin_and_configured_path_are_both_required(self):
        with self.assertRaisesRegex(BackendError, "origin"):
            madebycli_command(self.target, "refresh", "all", Runner("https://example.org/wrong"))
        other = self.home / "other"
        other.mkdir(); (other / "flake.nix").write_text("{}")
        target = Target("bad", "Bad", "nixos", str(other), "nyx", "nyx", "madebycli")
        with self.assertRaisesRegex(BackendError, "installed"):
            madebycli_command(target, "refresh", "all", Runner())

    def test_removed_categories_and_unsafe_cleanup_counts_are_rejected(self):
        for mode in ("packages", "kernel", "profiles", "--yes", "all;bad"):
            with self.assertRaises(BackendError):
                madebycli_command(self.target, "refresh", mode, Runner())
        for count in ("0", "21", "1; bad"):
            with self.assertRaises(BackendError):
                madebycli_command(self.target, "clean", count, Runner())

    def test_config_is_parsed_literally_without_sourcing_shell(self):
        repo, host = installed_config()
        self.assertEqual((repo, host), (self.repo, "nyx"))
        self.assertFalse((self.home / "not-a-command").exists())
        for text in ("REPO=relative\nHOST=nyx", "REPO=/a\nHOST=../nyx", "REPO=/a\nREPO=/b\nHOST=nyx"):
            self.conf.write_text(text)
            with self.assertRaises(BackendError): installed_config()

    def test_conflicting_nx_and_nixctl_configurations_are_an_error(self):
        with patch.dict(os.environ, {"NIXCTL_CONF": str(self.home / "different")}):
            with self.assertRaisesRegex(BackendError, "same configuration"):
                installed_config()

    def test_configured_host_must_match_the_actual_machine(self):
        self.conf.write_text(f"REPO={shlex.quote(str(self.repo))}\nHOST=aether\n")
        with self.assertRaisesRegex(BackendError, "differs"):
            autodetect()
