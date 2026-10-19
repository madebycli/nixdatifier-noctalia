import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nixdatifier.adapters import madebycli_command
from nixdatifier.config import Target, autodetect, load_config
from nixdatifier.process import BackendError, Result

FIXTURE = Path(__file__).parent / "fixtures/madebycli-outputs.json"


class ConfigTests(unittest.TestCase):
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
        for change in ({"id": None}, {"kind": []}, {"adapter": {}}, {"flake": "-evil"}, {"flake": "path#output"}, {"label": "a\nb"}):
            value = dict(id="test", label="Test", kind="nixos", flake="/a", attribute="host")
            value.update(change)
            with self.assertRaises(BackendError):
                Target.parse(value)

    def test_invalid_config_roots_return_actionable_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "targets.json"
            for value in ([], None, "config", 42):
                file.write_text(json.dumps(value))
                with self.assertRaisesRegex(BackendError, "schema_version"):
                    load_config(str(file))
