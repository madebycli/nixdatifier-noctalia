"""Multiple explicit targets, including madebycli's host/profile routing."""

import json
import os
import re
import socket
from dataclasses import asdict, dataclass
from pathlib import Path

from .process import BackendError
from .personal import HOSTS, current_layout, installed_config

KINDS = {"nixos", "home-manager", "devshell", "profile"}



@dataclass(frozen=True)
class Target:
    id: str
    label: str
    kind: str
    flake: str = ""
    attribute: str = ""
    host: str = ""
    adapter: str = "generic"
    profile: str = ""

    @classmethod
    def parse(cls, value):
        try:
            target = cls(**value)
        except (TypeError, KeyError) as exc:
            raise BackendError("Invalid target fields") from exc
        if not isinstance(target.id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", target.id):
            raise BackendError("Target id must be a short, unique identifier")
        for item in asdict(target).values():
            if not isinstance(item, str) or any(c in item for c in "\0\n\r"):
                raise BackendError("Target fields must be single-line strings")
        if target.kind not in KINDS or target.adapter not in {"generic", "madebycli"}:
            raise BackendError("Unsupported target kind or adapter")
        if target.kind != "profile" and (not target.flake or not target.attribute):
            raise BackendError("Flake targets need a flake and an exact output attribute")
        if "#" in target.flake or target.flake.startswith("-"):
            raise BackendError("Store flake and output attribute separately")
        return target

    def local_path(self):
        path = Path(os.path.expanduser(self.flake))
        if not path.is_absolute():
            raise BackendError("This action requires an absolute local flake directory")
        path = path.resolve()
        if not (path / "flake.nix").is_file():
            raise BackendError(f"No flake.nix in {path}")
        return path

    def installable(self):
        flake = os.path.expanduser(self.flake)
        key = json.dumps(self.attribute, ensure_ascii=False)
        if self.kind == "nixos":
            return f"{flake}#nixosConfigurations.{key}.config.system.build.toplevel"
        if self.kind == "home-manager":
            return f"{flake}#homeConfigurations.{key}.activationPackage"
        if self.kind == "devshell":
            return f"{flake}#devShells.{json.dumps(os.uname().machine.replace('amd64', 'x86_64') + '-linux')}.{key}"
        raise BackendError("A user profile is not a flake build target")


def autodetect():
    host = socket.gethostname().split(".")[0]
    home = Path.home()
    targets = []
    configured = installed_config()
    repo, selected = configured or (home / "nix-config", host)
    if selected != host:
        raise BackendError("Installed nx/nixctl HOST differs from this machine")
    if host in HOSTS and current_layout(repo, host):
        for machine in (host, *[h for h in HOSTS if h != host]):
            if current_layout(repo, machine):
                targets.append(Target(machine, machine, "nixos", str(repo), machine, machine, "madebycli"))
    else:
        for repo in (Path("/etc/nixos"), home / "nixos-config", home / ".config/nixos"):
            if (repo / "flake.nix").exists():
                targets.append(Target("system", "System", "nixos", str(repo), host, host))
                break
    profile = Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")) / "nix/profiles/profile"
    if not profile.is_symlink():
        profile = home / ".nix-profile"
    targets.append(Target("user-profile", "User packages", "profile", profile=str(profile)))
    return targets


def load_config(path=None):
    path = Path(os.path.expanduser(path)) if path else Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "nixdatifier-noctalia/targets.json"
    if not path.exists():
        return autodetect()
    try:
        data = json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        raise BackendError(f"Cannot read targets config: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("targets"), list):
        raise BackendError("Expected schema_version 1 and a targets array")
    targets = [Target.parse(item) for item in data["targets"]]
    if len({t.id for t in targets}) != len(targets) or not targets:
        raise BackendError("Target ids must be unique; configure at least one target")
    return targets


def select_target(targets, ident):
    return next((t for t in targets if t.id == ident), None) or _missing(ident)


def _missing(ident):
    raise BackendError(f"Unknown target: {ident}")
