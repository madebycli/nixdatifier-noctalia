import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nixdatifier.actions import plan
from nixdatifier.config import Target
from nixdatifier.generations import list_generations
from nixdatifier.process import BackendError, Result


class RecordingRunner:
    def __init__(self, output="nyx"):
        self.calls, self.output = [], output

    def run(self, args, **kwargs):
        self.calls.append((args, kwargs))
        return Result(self.output, "", 0)


class ActionsTests(unittest.TestCase):
    def target(self):
        return Target("nyx", "Nyx", "nixos", "/tmp/config", "nyx", "nyx")

    def test_preview_cannot_write_lock_or_activate(self):
        runner = RecordingRunner()
        commands = plan(self.target(), "preview", "", runner)
        self.assertEqual(commands[0][:2], ["nix", "build"])
        self.assertIn("--no-write-lock-file", commands[0])
        self.assertIn("--dry-run", commands[0])
        self.assertEqual(runner.calls, [])

    def test_system_build_precedes_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "flake.nix").write_text("{}")
            target = Target("nyx", "Nyx", "nixos", tmp, "nyx-niri", "nyx")
            runner = RecordingRunner()
            with patch("nixdatifier.actions.socket.gethostname", return_value="nyx"), patch("nixdatifier.generations.socket.gethostname", return_value="nyx"):
                commands = plan(target, "rebuild", "", runner)
            self.assertEqual([argv[2] for argv in commands], ["build", "switch"])
            self.assertTrue(all(argv[-1] == tmp + "#nyx-niri" for argv in commands))

    def test_claimed_host_does_not_override_actual_output_host(self):
        with patch("nixdatifier.actions.socket.gethostname", return_value="nyx"), patch("nixdatifier.generations.socket.gethostname", return_value="nyx"):
            with self.assertRaisesRegex(BackendError, "another host"):
                plan(self.target(), "rebuild", "", RecordingRunner("aether"))

    def test_foreign_host_cannot_activate_local_machine(self):
        target = Target("other", "Other", "nixos", "/a", "aether", "aether")
        with patch("nixdatifier.generations.socket.gethostname", return_value="nyx"):
            with self.assertRaises(BackendError):
                plan(target, "boot", "", RecordingRunner())

    def test_current_booted_and_selected_generations_are_protected(self):
        for protected in ("running", "booted", "selected"):
            row = {"number": 3, "closure": "/nix/store/x-system", "running": False, "booted": False, "selected": False}
            row[protected] = True
            with patch("nixdatifier.actions.generation_path", return_value=row), patch("nixdatifier.actions.local_target", return_value=True):
                with self.assertRaisesRegex(BackendError, "protected"):
                    plan(self.target(), "generation-delete", "3", RecordingRunner())

    def test_delete_is_exact_generation_not_global_cleanup(self):
        row = {"number": 7, "closure": "/nix/store/x-system", "running": False, "booted": False, "selected": False}
        with patch("nixdatifier.actions.generation_path", return_value=row), patch("nixdatifier.actions.local_target", return_value=True):
            commands = plan(self.target(), "generation-delete", "7", RecordingRunner())
        self.assertEqual(commands, [["sudo", "nix-env", "--profile", "/nix/var/nix/profiles/system", "--delete-generations", "7"]])

    def test_generation_number_cannot_be_shell_text(self):
        with patch("nixdatifier.actions.local_target", return_value=True):
            with self.assertRaises(BackendError):
                plan(self.target(), "generation-switch", "3; rm -rf /", RecordingRunner())

    def test_generation_identity_reads_three_different_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in (1, 2, 3):
                (root / str(n)).mkdir()
                (root / f"system-{n}-link").symlink_to(root / str(n))
            base, running, booted = (root / name for name in ("system", "running", "booted"))
            for link, num in ((base, 3), (running, 2), (booted, 1)):
                link.symlink_to(root / str(num))
            with patch("nixdatifier.generations.local_target", return_value=True):
                rows = list_generations(self.target(), base, running, booted)["rows"]
            self.assertEqual([row["number"] for row in rows], [3, 2, 1])
            self.assertTrue(rows[0]["selected"])
            self.assertTrue(rows[1]["running"])
            self.assertTrue(rows[2]["booted"])

    def test_profile_upgrade_does_not_change_system_inputs(self):
        target = Target("packages", "Packages", "profile", profile="/tmp/profile")
        self.assertEqual(plan(target, "profile-upgrade", "", RecordingRunner()),
                         [["nix", "profile", "upgrade", "--profile", "/tmp/profile", "--all"]])

    def test_home_manager_is_a_distinct_activation_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "flake.nix").write_text("{}")
            target = Target("home", "Home", "home-manager", tmp, "user@host")
            commands = plan(target, "home-switch", "", RecordingRunner())
            self.assertEqual([argv[:2] for argv in commands], [["home-manager", "build"], ["home-manager", "switch"]])
