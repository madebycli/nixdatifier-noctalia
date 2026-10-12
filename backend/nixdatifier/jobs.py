"""Terminal jobs survive closing the panel and retain private output logs."""

import json
import os
import shlex
import time
import uuid

from .actions import plan
from .process import BackendError, Runner
from .state import atomic_json, invalidate, operation_lock, state_dir


def run_job(target, action, argument, confirmed, runner=None):
    if not confirmed:
        raise BackendError("Action requires explicit confirmation")
    if os.geteuid() == 0:
        raise BackendError("Run jobs as your desktop user; sudo is used only where needed")
    ident = str(uuid.uuid4())
    path = state_dir() / f"job-{ident}.json"
    log = state_dir() / f"job-{ident}.log"
    record = {"id": ident, "target": target.id, "action": action, "argument": argument,
              "status": "running", "started": time.time(), "pid": os.getpid(), "log": str(log)}
    with operation_lock():
        # Resolve and re-check identity under the operation lock.
        commands = plan(target, action, argument, runner or Runner(timeout=120))
        record["commands"] = commands
        atomic_json(path, record)
        fd = os.open(log, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        error = None
        try:
            with os.fdopen(fd, "w") as output:
                for argv in commands:
                    print("$ " + shlex.join(argv), file=output, flush=True)
                    print("$ " + shlex.join(argv), flush=True)
                    executor = runner or Runner(timeout=10800, log=output)
                    # Interactive stdin remains the terminal; output is retained.
                    executor.run(argv, timeout=10800)
            record["status"] = "success"
        except (BackendError, OSError) as exc:
            error = str(exc)
            record.update(status="failed", error=error)
        finally:
            record["finished"] = time.time()
            atomic_json(path, record)
            invalidate()
            prune()
        if error:
            raise BackendError(error)
    return record


def prune():
    paths = sorted(state_dir().glob("job-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[100:]:
        try:
            data = json.loads(path.read_text())
            if data.get("status") != "running":
                path.with_suffix(".log").unlink(missing_ok=True)
                path.unlink(missing_ok=True)
        except (OSError, ValueError):
            pass


def history():
    rows = []
    for path in state_dir().glob("job-*.json"):
        try:
            data = json.loads(path.read_text())
            if data.get("status") == "running":
                try:
                    os.kill(data["pid"], 0)
                except (OSError, KeyError):
                    data["status"] = "interrupted"
            rows.append(data)
        except (ValueError, OSError):
            pass
    return sorted(rows, key=lambda row: row["started"], reverse=True)[:100]


def read_log(ident):
    try:
        ident = str(uuid.UUID(ident))
    except ValueError as exc:
        raise BackendError("Invalid job id") from exc
    path = state_dir() / f"job-{ident}.log"
    try:
        with path.open("rb") as stream:
            stream.seek(max(0, path.stat().st_size - 32000))
            return stream.read().decode(errors="replace")
    except OSError as exc:
        raise BackendError("No log for this job") from exc
