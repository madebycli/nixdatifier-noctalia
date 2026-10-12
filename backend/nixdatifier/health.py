"""Cheap host health; expensive store scans are separate explicit queries."""

import os
import shutil
import socket
from pathlib import Path

from .process import BackendError


def health(runner):
    nix = runner.run(["nix", "--version"], check=False)
    failed = runner.run(["systemctl", "--failed", "--no-legend", "--plain", "--no-pager"], check=False)
    current, booted = Path("/run/current-system"), Path("/run/booted-system")
    disks = []
    for path in ("/", "/boot", "/nix/store"):
        if Path(path).exists():
            usage = shutil.disk_usage(path)
            disks.append({"path": path, "total": usage.total, "free": usage.free,
                          "used": usage.used, "fraction": usage.used / usage.total})
    return {"host": socket.gethostname(), "kernel": os.uname().release,
            "nix": nix.stdout.strip(), "nix_error": nix.stderr.strip() if nix.code else "",
            "failed_units": failed.stdout.strip().splitlines(),
            "systemd_error": failed.stderr.strip() if failed.code else "",
            "pending_reboot": current.exists() and booted.exists() and current.resolve() != booted.resolve(),
            "disks": disks, "is_nixos": Path("/etc/NIXOS").exists()}


def store_usage(path, runner):
    store = Path(path).resolve()
    if store.parent != Path("/nix/store"):
        raise BackendError("Select a direct /nix/store path")
    details = runner.run(["nix", "path-info", "--json", "--closure-size", str(store)])
    refs = runner.run(["nix-store", "--query", "--referrers", str(store)])
    roots = runner.run(["nix-store", "--query", "--roots", str(store)])
    return {"path": str(store), "details": details.stdout,
            "referrers": refs.stdout.splitlines(), "roots": roots.stdout.splitlines()}
