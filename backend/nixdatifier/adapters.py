"""Personal integration without replacing its existing safety policies."""

import socket
from pathlib import Path

from .personal import HOSTS, current_layout, installed_config
from .process import BackendError

MODES = {"all", "base", "desktop", "apps"}
REMOTES = {"https://github.com/madebycli/nix-config.git", "git@github.com:madebycli/nix-config.git"}


def madebycli_command(target, action, argument, runner):
    host = socket.gethostname().split(".")[0]
    if target.kind != "nixos" or target.host != host or host not in HOSTS or target.attribute != host:
        raise BackendError("Personal commands require the exact local nyx/aether output")
    repo = target.local_path()
    configured = installed_config()
    expected_repo, expected_host = configured or ((Path.home() / "nix-config").resolve(), host)
    if repo != expected_repo or expected_host != host or not current_layout(repo, host):
        raise BackendError("Target must match the installed nx/nixctl repository and host")
    origin = runner.run(["git", "-C", str(repo), "remote", "get-url", "origin"]).stdout.strip()
    if origin not in REMOTES:
        raise BackendError("Unexpected origin for personal config")
    if action == "rebuild":
        return ["nx", "switch"]
    if action in {"refresh", "preview-updates"}:
        if argument not in MODES:
            raise BackendError("Unknown update category")
        if action == "preview-updates":
            return ["nx", "check"]  # nx check intentionally checks every root input.
        return ["nx", "update", *([] if argument == "all" else [argument])]
    if action == "clean":
        try:
            count = int(argument)
        except ValueError as exc:
            raise BackendError("Keep between 1 and 20 backups") from exc
        if not 1 <= count <= 20:
            raise BackendError("Keep between 1 and 20 backups")
        return ["nx", "clean", str(count)]
    if action == "refresh-input":
        if not argument or argument.startswith("-") or not all(c.isalnum() or c in "_.-" for c in argument):
            raise BackendError("Choose an exact root input name")
        return ["nx", "update", argument]
    commands = {"optimize": ["nx", "optimise"], "rollback": ["nx", "rollback"],
                "pull": ["nx", "pull"], "settings": ["nix-settings"],
                "sync": ["dots", "sync"], "dot-status": ["dots", "status"],
                "dot-pull": ["dots", "pull"], "dot-push": ["dots", "push"]}
    if action in commands:
        return commands[action]
    raise BackendError("This action is not provided by the personal adapter")
