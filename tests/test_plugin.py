import ctypes
import ctypes.util
import json
import os
import re
import subprocess
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "nixdatifier-noctalia"


class PluginTests(unittest.TestCase):
    def test_manifest_entries_settings_and_catalog(self):
        manifest = tomllib.loads((PLUGIN / "plugin.toml").read_text())
        catalog = tomllib.loads((ROOT / "catalog.toml").read_text())["plugin"][0]
        for key in ("id", "version", "plugin_api"):
            self.assertEqual(manifest[key], catalog[key])
        self.assertEqual(manifest["plugin_api"], 26)
        for kind in ("widget", "shortcut", "panel", "service"):
            for entry in manifest[kind]: self.assertTrue((PLUGIN / entry["entry"]).is_file())
        declared = {setting["key"] for setting in manifest["setting"]}
        reads = set()
        for path in PLUGIN.rglob("*.luau"):
            reads.update(re.findall(r'getConfig\("([^"]+)"\)', path.read_text()))
        self.assertEqual(reads, declared)

    def test_translations_cover_static_keys_and_dynamic_statuses(self):
        en = json.loads((PLUGIN / "translations/en.json").read_text())
        de = json.loads((PLUGIN / "translations/de.json").read_text())
        self.assertEqual(set(en), set(de))
        for path in PLUGIN.rglob("*.luau"):
            for key in re.findall(r'(?:c\.tr|noctalia\.tr)\("([^"]+)"\)', path.read_text()):
                self.assertIn(key, en)
        for status in ("update", "unchanged", "pinned", "follows", "offline", "unreachable"):
            self.assertIn("status." + status, en)

    def test_ui_contract_with_lua_compatible_runtime(self):
        script = ROOT / "tests/lua_host.lua"
        env = dict(os.environ, NIXDATIFIER_PLUGIN=str(PLUGIN))
        binary = os.environ.get("NIXDATIFIER_LUA")
        if binary:
            result = subprocess.run([binary, str(script)], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return
        library = ctypes.util.find_library("lua5.4")
        self.assertIsNotNone(library, "Install Lua 5.4 or set NIXDATIFIER_LUA; UI tests must not be skipped")
        lua = ctypes.CDLL(library)
        lua.luaL_newstate.restype = ctypes.c_void_p
        lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
        lua.luaL_loadfilex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lua.lua_pcallk.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_longlong, ctypes.c_void_p]
        lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        lua.lua_tolstring.restype = ctypes.c_char_p
        lua.lua_close.argtypes = [ctypes.c_void_p]
        vm = lua.luaL_newstate()
        previous = os.environ.get("NIXDATIFIER_PLUGIN")
        os.environ["NIXDATIFIER_PLUGIN"] = str(PLUGIN)
        try:
            lua.luaL_openlibs(vm)
            code = lua.luaL_loadfilex(vm, str(script).encode(), None)
            if code == 0: code = lua.lua_pcallk(vm, 0, 0, 0, 0, None)
            error = lua.lua_tolstring(vm, -1, None) if code else b""
            self.assertEqual(code, 0, error.decode() if error else "Lua harness failed")
        finally:
            lua.lua_close(vm)
            if previous is None: os.environ.pop("NIXDATIFIER_PLUGIN", None)
            else: os.environ["NIXDATIFIER_PLUGIN"] = previous
