"""Read-only lock inspection and bounded upstream comparisons."""

import concurrent.futures
import json
from pathlib import Path

from .process import BackendError


def resolve_node(lock, edge, seen=None):
    seen = set() if seen is None else seen
    if isinstance(edge, str):
        if edge not in lock["nodes"]:
            raise BackendError("Unknown flake lock node")
        return edge
    if not isinstance(edge, list) or not edge:
        raise BackendError("Malformed follows path")
    node = lock["root"]
    marker = tuple(edge)
    if marker in seen:
        raise BackendError("Cyclic flake follows path")
    seen.add(marker)
    for name in edge:
        next_edge = lock["nodes"][node].get("inputs", {}).get(name)
        node = resolve_node(lock, next_edge, seen.copy())
    return node


def read_lock(target):
    path = target.local_path() / "flake.lock"
    try:
        lock = json.loads(path.read_text())
        root = lock["nodes"][lock["root"]]
        rows = []
        for name, edge in root.get("inputs", {}).items():
            node = lock["nodes"][resolve_node(lock, edge)]
            rows.append({"name": name, "locked": node.get("locked", {}),
                         "original": node.get("original", {}), "follows": isinstance(edge, list)})
        return rows
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BackendError(f"Cannot parse flake.lock: {exc}") from exc


def remote(original):
    kind, ref = original.get("type"), original.get("ref", "HEAD")
    if original.get("rev"):
        return None  # Explicit revision pins are deliberate, never 'outdated'.
    if kind == "github":
        url = f"https://github.com/{original['owner']}/{original['repo']}.git"
    elif kind == "gitlab":
        url = f"https://gitlab.com/{original['owner']}/{original['repo']}.git"
    elif kind == "sourcehut":
        url = f"https://git.sr.ht/{original['owner']}/{original['repo']}"
    elif kind == "git":
        url = original.get("url", "").removeprefix("git+")
        if not url.startswith(("https://", "ssh://", "git@")):
            return None
    else:
        return None
    return url, ref


def updates(target, runner, offline=False):
    rows = read_lock(target)

    def probe(row):
        row = dict(row)
        row["revision"] = row["locked"].get("rev", row["locked"].get("narHash", ""))
        destination = remote(row["original"])
        if row["follows"] or not destination:
            row["status"] = "follows" if row["follows"] else "pinned"
        elif offline:
            row["status"] = "offline"
        else:
            url, ref = destination
            refs = ["HEAD"] if ref == "HEAD" else [f"refs/heads/{ref}", f"refs/tags/{ref}^{{}}", f"refs/tags/{ref}", ref]
            try:
                out = runner.run(["git", "-c", "protocol.version=2", "ls-remote", "--", url, *refs], timeout=8).stdout
                advertised = [line.split()[0] for line in out.splitlines() if line.split()]
                if not advertised:
                    raise BackendError("Requested upstream ref was not found")
                # Prefer a peeled annotated tag to its tag-object hash.
                peeled = next((line.split()[0] for line in out.splitlines() if line.endswith("^{}")), None)
                row["upstream"] = peeled or advertised[0]
                row["status"] = "update" if row["upstream"] != row["revision"] else "unchanged"
            except BackendError as exc:
                row.update(status="unreachable", error=str(exc))
        return row

    # Noctalia's short subprocess API is not a background update worker.
    # Large target sets are still safe: callers can run this CLI in a terminal.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        result = list(pool.map(probe, rows))
    return {"rows": result, "updates": sum(row["status"] == "update" for row in result),
            "partial": any(row["status"] in {"unreachable", "offline"} for row in result)}


def discover(flake, runner):
    if "#" in flake or flake.startswith("-") or "\0" in flake:
        raise BackendError("Pass a flake reference without #output")
    expression = "f: { nixos = builtins.attrNames (f.nixosConfigurations or {}); home = builtins.attrNames (f.homeConfigurations or {}); shells = builtins.mapAttrs (_: v: builtins.attrNames v) (f.devShells or {}); }"
    result = runner.run(["nix", "eval", "--json", "--no-write-lock-file", flake + "#", "--apply", expression])
    return json.loads(result.stdout)
