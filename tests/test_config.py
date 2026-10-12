import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nixdatifier.adapters import madebycli_command, madebycli_flags
from nixdatifier.config import Target, active_profile, autodetect, load_config
from nixdatifier.process import BackendError, Result

FIXTURE = Path(__file__).parent / "fixtures/madebycli-outputs.json"


class ConfigTests(unittest.TestCase):
    def test_every_real_personal_output_has_correct_cli_flags(self):
        outputs = json.loads(FIXTURE.read_text())["nixosConfigurations"]
        self.assertEqual(len(outputs), 18)
        for attribute in outputs:
            host = attribute.split("-")[0]
            flags = madebycli_flags(attribute, host)
            self.assertEqual(flags[0], "--" + host)
            if attribute.endswith("caelestia"):
                self.assertEqual(flags[1:], ["--hyprland", "--caelestia-shell"])
            elif attribute.endswith("all"):
                self.assertEqual(flags[1:], ["--all", "--noctalia"])
            else:
                suffix = attribute[len(host):].strip("-") or "mango"
                self.assertEqual(flags[1:], [*['--' + d for d in suffix.split('-')], "--noctalia"])

    def test_unknown_personal_profile_is_rejected(self):
        for attr in ("nyx-evil", "aether-niri", "nyx; touch /tmp/injected"):
            with self.assertRaises(BackendError):
                madebycli_flags(attr, "nyx")

    def test_active_profile_prefers_system_over_saved_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            state = home / ".local/state/nixos-config/a/b"
            state.mkdir(parents=True)
            (state / "state.json").write_text(json.dumps({"repository": str(home / "nyx"), "profile": "nyx-niri"}))
            marker = home / "profile"
            marker.write_text("nyx-all\n")
            with patch.dict(os.environ, {"XDG_STATE_HOME": str(home / ".local/state")}):
                self.assertEqual(active_profile("nyx", home, marker), "nyx-all")
                marker.write_text("aether-hyprland")
                self.assertEqual(active_profile("nyx", home, marker), "nyx-niri")

    def test_autodetect_includes_both_hosts_and_separate_user_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / "nyx").mkdir()
            (home / "nyx/flake.nix").write_text("{}")
            with patch("nixdatifier.config.Path.home", return_value=home), patch("nixdatifier.config.socket.gethostname", return_value="nyx"), patch("nixdatifier.config.active_profile", return_value="nyx-niri"):
                targets = autodetect()
            self.assertEqual(targets[0].attribute, "nyx-niri")
            self.assertEqual(len(targets), 19)
            self.assertEqual(targets[-1].kind, "profile")
            self.assertEqual({t.attribute for t in targets[:-1]}, set(json.loads(FIXTURE.read_text())["nixosConfigurations"]))

    def test_multiple_flakes_and_home_manager_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "targets.json"
            values = [dict(id="system", label="System", kind="nixos", flake="/a", attribute="workstation"),
                      dict(id="home", label="Home", kind="home-manager", flake="/b", attribute="me@host"),
                      dict(id="dev", label="Dev", kind="devshell", flake="/c", attribute="default")]
            file.write_text(json.dumps({"schema_version": 1, "targets": values}))
            self.assertEqual([t.flake for t in load_config(str(file))], ["/a", "/b", "/c"])
            file.write_text(json.dumps({"schema_version": 1, "targets": values + values[:1]}))
            with self.assertRaisesRegex(BackendError, "unique"):
                load_config(str(file))

    def test_installable_quotes_attribute_as_nix_string(self):
        target = Target.parse(dict(id="safe", label="Safe", kind="nixos", flake="/tmp/flake", attribute='a.b";$(oops)'))
        self.assertEqual(target.installable(), '/tmp/flake#nixosConfigurations."a.b\\\";$(oops)".config.system.build.toplevel')

    def test_untrusted_types_and_refs_are_rejected(self):
        for change in ({"id": None}, {"flake": "-evil"}, {"flake": "path#output"}, {"label": "a\nb"}):
            value = dict(id="test", label="Test", kind="nixos", flake="/a", attribute="host")
            value.update(change)
            with self.assertRaises(BackendError):
                Target.parse(value)

    def test_personal_adapter_checks_repository_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / "nyx").mkdir()
            (home / "nyx/flake.nix").write_text("{}")
            target = Target("nyx", "Nyx", "nixos", str(home / "nyx"), "nyx", "nyx", "madebycli")
            class Runner:
                def run(self, args):
                    return Result("https://example.com/not-the-config\n", "", 0)
            with patch("nixdatifier.adapters.Path.home", return_value=home), patch("nixdatifier.adapters.socket.gethostname", return_value="nyx"):
                with self.assertRaisesRegex(BackendError, "origin"):
                    madebycli_command(target, "rebuild", "", Runner())
