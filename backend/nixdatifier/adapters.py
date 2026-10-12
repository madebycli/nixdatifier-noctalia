"""Personal integration without replacing its existing safety policies."""

import socket
from pathlib import Path

from .config import SUFFIXES
from .process import BackendError

MODES = {"all", "base", "packages", "kernel", "desktop", "profiles"}
REMOTES = {"https://github.com/madebycli/nix-config.git", "git@github.com:madebycli/nix-config.git"}


def madebycli_flags(attribute, host):
    if host not in {"nyx", "aether"} or attribute not in {host + s for s in SUFFIXES}:
        raise BackendError("Unknown madebycli host/profile")
    suffix = attribute[len(host):].lstrip("-")
    if suffix == "hyprland-caelestia":
        return ["--" + host, "--hyprland", "--caelestia-shell"]
    if suffix == "all":
        return ["--" + host, "--all", "--noctalia"]
    desktops = suffix.split("-") if suffix else ["mango"]
    return ["--" + host, *["--" + d for d in desktops], "--noctalia"]


def madebycli_command(target, action, argument, runner):
    host = socket.gethostname().split(".")[0]
    if target.host != host or host not in {"nyx", "aether"}:
        raise BackendError("Personal commands only run on their own host")
    repo = target.local_path()
    if repo != (Path.home() / host).resolve():
        raise BackendError("Personal scripts require the matching ~/nyx or ~/aether checkout")
    origin = runner.run(["git", "-C", str(repo), "remote", "get-url", "origin"]).stdout.strip()
    if origin not in REMOTES:
        raise BackendError("Unexpected origin for personal config")
    if action == "rebuild":
        return ["config-update", *madebycli_flags(target.attribute, host)]
    if action in {"refresh", "preview-updates"}:
        if argument not in MODES:
            raise BackendError("Unknown update category")
        return ["nix-refresh" if action == "refresh" else "nix-updates", argument]
    if action == "clean":
        try:
            count = int(argument)
        except ValueError as exc:
            raise BackendError("Keep between 1 and 20 backups") from exc
        if not 1 <= count <= 20:
            raise BackendError("Keep between 1 and 20 backups")
        return ["nix-clean", str(count)]
    commands = {"optimize": "nix-optimize", "rollback": "nix-rollback",
                "sync": "config-sync", "save-config": "save-config",
                "script-update": "script-update"}
    if action in commands:
        return [commands[action]]
    raise BackendError("This action is not provided by the personal adapter")
