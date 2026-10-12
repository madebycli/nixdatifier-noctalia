"""Reviewed action plans; interactive execution stays in a terminal."""

import json
import socket
from pathlib import Path

from .adapters import madebycli_command
from .config import active_profile
from .generations import generation_path, local_target, profile_path
from .process import BackendError


def local_system(target, runner):
    if target.kind != "nixos" or not local_target(target):
        raise BackendError("System actions are restricted to the local NixOS host")
    # Verify actual output identity instead of trusting a target's host label.
    key = json.dumps(target.attribute)
    actual = runner.run(["nix", "eval", "--raw", "--no-write-lock-file",
                         f"{target.flake}#nixosConfigurations.{key}.config.networking.hostName"]).stdout.strip()
    if actual != socket.gethostname().split(".")[0]:
        raise BackendError("Selected NixOS output belongs to another host")


def plan(target, action, argument, runner):
    if action == "build":
        return [["nix", "build", "--no-write-lock-file", "--no-link", target.installable()]]
    if action == "preview":
        return [["nix", "build", "--dry-run", "--no-write-lock-file", "--no-link", target.installable()]]
    if action == "update-input":
        if not argument or argument.startswith("-") or "/" in argument:
            raise BackendError("Choose an exact root input name")
        from .flakes import read_lock
        if argument not in {r["name"] for r in read_lock(target)}:
            raise BackendError("Input is not present in this flake")
        return [["nix", "flake", "update", argument, "--flake", str(target.local_path())]]
    if action == "profile-upgrade" and target.kind == "profile":
        return [["nix", "profile", "upgrade", "--profile", str(profile_path(target)), "--all"]]
    if target.adapter == "madebycli" and action in {
        "rebuild", "refresh", "preview-updates", "clean", "optimize", "rollback", "sync", "save-config", "script-update"
    }:
        if action == "rebuild":
            local_system(target, runner)
        # Category commands resolve the installed active profile themselves.
        if action in {"refresh", "preview-updates"} and target.attribute != active_profile():
            raise BackendError("Category updates apply to the active profile; select it first")
        return [madebycli_command(target, action, argument, runner)]
    if action in {"rebuild", "boot"}:
        local_system(target, runner)
        flake = f"{target.local_path()}#{target.attribute}"
        return [["sudo", "nixos-rebuild", "build", "--flake", flake],
                ["sudo", "nixos-rebuild", "switch" if action == "rebuild" else "boot", "--flake", flake]]
    if action in {"generation-switch", "generation-boot", "generation-delete"}:
        if target.kind != "nixos" or not local_target(target):
            raise BackendError("Generation actions are local NixOS actions")
        try:
            number = int(argument)
        except ValueError as exc:
            raise BackendError("Choose a generation number") from exc
        row = generation_path(target, number)
        base = str(profile_path(target))
        if action == "generation-delete":
            if row["selected"] or row["running"] or row["booted"]:
                raise BackendError("Running, booted and next-boot generations are protected")
            return [["sudo", "nix-env", "--profile", base, "--delete-generations", str(number)]]
        return [["sudo", "nix-env", "--profile", base, "--switch-generation", str(number)],
                ["sudo", row["closure"] + "/bin/switch-to-configuration",
                 "switch" if action == "generation-switch" else "boot"]]
    if action == "gc":
        return [["nix", "store", "gc"]]
    if action == "optimize":
        return [["nix", "store", "optimise"]]
    if action == "direnv-allow":
        folder = Path(argument).expanduser().resolve()
        if not (folder / ".envrc").is_file():
            raise BackendError("Choose a directory containing .envrc")
        return [["direnv", "allow", str(folder)]]
    if action == "home-switch" and target.kind == "home-manager":
        return [["home-manager", "build", "--flake", f"{target.local_path()}#{target.attribute}"],
                ["home-manager", "switch", "--flake", f"{target.local_path()}#{target.attribute}"]]
    raise BackendError("Unsupported action for this target")
