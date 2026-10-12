"""One JSON response envelope for every read-only plugin request."""

import argparse
import hashlib
import json
import sys
from dataclasses import asdict

from . import API_VERSION, VERSION
from .actions import plan
from .config import load_config, select_target
from .flakes import discover, updates
from .generations import compare, list_generations
from .health import health, store_usage
from .jobs import history, read_log, run_job
from .process import BackendError, Runner
from .state import cached
from .tools import devenv, hash_value, secrets


def parser():
    cli = argparse.ArgumentParser(prog="nixdatifier-noctalia")
    cli.add_argument("--version", action="version", version=VERSION)
    cli.add_argument("--config", help="Multi-target JSON configuration")
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("targets")
    discovery = sub.add_parser("discover")
    discovery.add_argument("flake")
    query = sub.add_parser("query")
    query.add_argument("view", choices=["generations", "updates", "health", "secrets", "history", "log", "diff", "store", "hash", "devenv"])
    query.add_argument("--target", default="")
    query.add_argument("--argument", default="")
    query.add_argument("--second", default="")
    query.add_argument("--force", action="store_true")
    query.add_argument("--offline", action="store_true")
    for name in ("plan", "job"):
        action = sub.add_parser(name)
        action.add_argument("action")
        action.add_argument("--target", required=True)
        action.add_argument("--argument", default="")
        if name == "job":
            action.add_argument("--confirm", action="store_true")
    return cli


def query(args, targets, runner):
    if args.view == "history":
        return {"rows": history()}
    if args.view == "log":
        return {"text": read_log(args.argument)}
    if args.view == "health":
        return cached(["health"], 30, lambda: health(runner), args.force)
    target = select_target(targets, args.target or targets[0].id)
    if args.view == "generations":
        return list_generations(target)
    if args.view == "updates":
        fingerprint = hashlib.sha256((target.local_path() / "flake.lock").read_bytes()).hexdigest()
        return cached(["updates", asdict(target), fingerprint, args.offline], 3600,
                      lambda: updates(target, runner, args.offline), args.force)
    if args.view == "secrets":
        return secrets(target)
    if args.view == "diff":
        try:
            return compare(target, int(args.argument), int(args.second), runner)
        except ValueError as exc:
            raise BackendError("Choose two generation numbers") from exc
    if args.view == "store":
        return store_usage(args.argument, runner)
    if args.view == "hash":
        if args.offline and args.second == "url":
            raise BackendError("URL hashing is unavailable in offline mode")
        return hash_value(args.second or "file", args.argument, runner)
    if args.view == "devenv":
        return devenv(args.argument, runner)
    raise BackendError("Unknown query")


def dispatch(args, runner=None):
    runner = runner or Runner()
    targets = load_config(args.config)
    if args.command == "targets":
        return {"rows": [asdict(target) for target in targets]}
    if args.command == "discover":
        return discover(args.flake, runner)
    if args.command == "query":
        return query(args, targets, runner)
    target = select_target(targets, args.target)
    if args.command == "plan":
        return {"commands": plan(target, args.action, args.argument, runner)}
    return run_job(target, args.action, args.argument, args.confirm, runner)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        data = dispatch(args)
        envelope = {"api_version": API_VERSION, "version": VERSION, "ok": True, "data": data}
        code = 0
    except (BackendError, OSError, ValueError, KeyError, TypeError) as exc:
        envelope = {"api_version": API_VERSION, "version": VERSION, "ok": False, "error": str(exc)}
        code = 1
    print(json.dumps(envelope, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
