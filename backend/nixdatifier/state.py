"""Atomic, private state, caching and cross-process operation ownership."""

import fcntl
import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from .process import BackendError


def state_dir():
    path = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "nixdatifier-noctalia"
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    return path


def atomic_json(path, value):
    fd, temp = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


@contextmanager
def operation_lock(key="system"):
    name = hashlib.sha256(key.encode()).hexdigest()
    with (state_dir() / f"operation-{name}.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BackendError("Another Nixdatifier operation is running") from exc
        yield


def cached(key, ttl, load, force=False):
    name = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()
    path = state_dir() / f"cache-{name}.json"
    with (state_dir() / f"cache-{name}.lock").open("a") as lock:
        # Readers must return before Noctalia's subprocess deadline.
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BackendError("This query is already running; retry shortly") from exc
        if not force and path.exists() and time.time() - path.stat().st_mtime < ttl:
            try:
                return json.loads(path.read_text())
            except (ValueError, OSError):
                pass
        value = load()
        # A partial network result must remain retryable.
        if not isinstance(value, dict) or not value.get("partial"):
            atomic_json(path, value)
        return value


def invalidate():
    for path in state_dir().glob("cache-*.json"):
        path.unlink(missing_ok=True)
