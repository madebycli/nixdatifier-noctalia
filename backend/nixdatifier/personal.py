"""Read the installed nx/nixctl configuration without executing shell code."""

import os
import shlex
from pathlib import Path

from .process import BackendError

HOSTS = ("nyx", "aether")


def installed_config():
    nx, ctl = os.environ.get("NX_CONF"), os.environ.get("NIXCTL_CONF")
    if nx and ctl and Path(nx).resolve() != Path(ctl).resolve():
        raise BackendError("NX_CONF and NIXCTL_CONF must identify the same configuration")
    path = Path(nx or ctl or "/etc/nixctl.conf")
    if not path.exists() and not (nx or ctl):
        return None
    try:
        values = {}
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, sep, raw = line.partition("=")
            if key.strip() not in {"REPO", "HOST"}:
                continue
            parts = shlex.split(raw, comments=True)
            if not sep or len(parts) != 1 or key.strip() in values:
                raise ValueError("ambiguous assignment")
            values[key.strip()] = parts[0]
        repo = Path(values["REPO"])
        host = values["HOST"]
        if not repo.is_absolute() or host not in HOSTS:
            raise ValueError("expected an absolute REPO and HOST nyx/aether")
        return repo.resolve(), host
    except (OSError, ValueError, KeyError) as exc:
        raise BackendError(f"Cannot read nx/nixctl configuration {path}: {exc}") from exc


def current_layout(repo, host):
    return (repo / "flake.nix").is_file() and (repo / "hosts" / host / "features.nix").is_file()
