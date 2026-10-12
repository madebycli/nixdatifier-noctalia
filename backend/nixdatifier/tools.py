"""On-demand tooling; secret values and private keys are never read."""

import hashlib
import json
import os
import re
from pathlib import Path

from .process import BackendError


def secrets(target):
    deployed = []
    for path in (Path("/run/secrets"), Path("/run/agenix.d")):
        if path.is_dir():
            try:
                deployed.append({"path": str(path), "names": sorted(p.name for p in path.iterdir())})
            except PermissionError:
                deployed.append({"path": str(path), "error": "Directory is not readable"})
    # Report encrypted source filenames only. Never infer encryption from YAML regexes.
    sources = []
    if target.flake:
        repo = target.local_path()
        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in {".git", ".direnv", "node_modules"}
                       and len(Path(root).relative_to(repo).parts) < 4]
            for name in files:
                path = Path(root) / name
                if name.endswith(".age") or name in {"secrets.yaml", "secrets.yml", "secrets.json"}:
                    sources.append({"path": str(path.relative_to(repo)), "modified": path.stat().st_mtime})
    return {"deployed": deployed, "sources": sources,
            "note": "Metadata only; candidate source names do not prove encryption"}


def hash_value(mode, value, runner):
    if mode == "file":
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise BackendError("Select a regular local file")
        if path.stat().st_size > 100 * 1024 * 1024:
            raise BackendError("Use nix hash file in a terminal for files larger than 100 MiB")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
        import base64
        return {"hex": digest.hexdigest(), "sri": "sha256-" + base64.b64encode(digest.digest()).decode()}
    if mode == "url":
        if not value.startswith("https://"):
            raise BackendError("URL hashing requires HTTPS")
        result = runner.run(["nix", "store", "prefetch-file", "--json", "--", value], timeout=12)
        return json.loads(result.stdout)
    if mode == "path":
        path = Path(value).expanduser().resolve()
        if not path.exists():
            raise BackendError("Path does not exist")
        result = runner.run(["nix", "hash", "path", "--sri", str(path)], timeout=12)
        return {"sri": result.stdout.strip()}
    raise BackendError("Unknown hash mode")


def devenv(folder, runner):
    path = Path(folder).expanduser().resolve()
    if not path.is_dir():
        raise BackendError("Development directory does not exist")
    envrc = path / ".envrc"
    config = ""
    if envrc.is_file():
        with envrc.open(errors="replace") as stream:
            config = stream.read(65536)
    # Inspect syntax, never source/evaluate .envrc.
    directives = sorted(set(re.findall(r"^\s*(use\s+\w+|dotenv|source_env)\b", config, re.MULTILINE)))
    layout = path / ".direnv"
    allowed = False
    data_root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "direnv/allow"
    for permit in data_root.glob("*"):
        if permit.is_file():
            try:
                with permit.open(errors="replace") as stream:
                    allowed = allowed or str(envrc) in stream.read(65536)
            except OSError:
                pass
    return {"path": str(path), "envrc": envrc.is_file(), "allowed": allowed,
            "directives": directives, "cache_exists": layout.exists(),
            "outputs": discover_shells(path, runner) if (path / "flake.nix").exists() else {}}


def discover_shells(path, runner):
    from .flakes import discover
    return discover(str(path), runner).get("shells", {})
