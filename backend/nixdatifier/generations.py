"""Local generation identity is read from profile symlinks, not UI state."""

import os
import re
import socket
from datetime import datetime, timezone
from pathlib import Path

from .process import BackendError


def profile_path(target):
    if target.kind == "nixos":
        return Path("/nix/var/nix/profiles/system")
    if target.profile:
        return Path(os.path.expanduser(target.profile))
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return state / "nix/profiles/home-manager"


def local_target(target):
    return target.kind != "nixos" or not target.host or target.host == socket.gethostname().split(".")[0]


def list_generations(target, base=None, running=None, booted=None):
    if target.kind == "devshell":
        return {"rows": [], "scope": "development environment"}
    if not local_target(target):
        return {"rows": [], "scope": "other host; only evaluation/build available"}
    base = base or profile_path(target)
    running = running or Path("/run/current-system")
    booted = booted or Path("/run/booted-system")
    rows = []
    for path in base.parent.glob(base.name + "-*-link"):
        match = re.fullmatch(re.escape(base.name) + r"-(\d+)-link", path.name)
        if not match or not path.is_symlink() or not path.exists():
            continue
        closure = path.resolve()
        try:
            stamp = path.lstat().st_mtime
        except OSError:
            continue
        rows.append({"number": int(match[1]), "closure": str(closure),
                     "date": datetime.fromtimestamp(stamp, timezone.utc).isoformat(),
                     "selected": closure == base.resolve(),
                     "running": target.kind == "nixos" and closure == running.resolve(),
                     "booted": target.kind == "nixos" and closure == booted.resolve()})
    rows.sort(key=lambda row: row["number"], reverse=True)
    return {"rows": rows, "scope": "local", "profile": str(base),
            "test_build": target.kind == "nixos" and running.exists()
            and not any(row["running"] for row in rows)}


def generation_path(target, number):
    if not isinstance(number, int) or number <= 0:
        raise BackendError("Generation must be a positive integer")
    row = next((row for row in list_generations(target)["rows"] if row["number"] == number), None)
    if not row:
        raise BackendError("Generation does not exist locally")
    closure = Path(row["closure"])
    if closure.parent != Path("/nix/store"):
        raise BackendError("Generation does not resolve directly into /nix/store")
    return row


def compare(target, before, after, runner):
    a, b = generation_path(target, before), generation_path(target, after)
    result = runner.run(["nix", "store", "diff-closures", a["closure"], b["closure"]])
    return {"before": before, "after": after, "text": result.stdout}
