"""Bounded subprocesses. Dynamic values never pass through a shell."""

import os
import signal
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass


class BackendError(Exception):
    pass


@dataclass
class Result:
    stdout: str
    stderr: str
    code: int


class Runner:
    def __init__(self, timeout=18, limit=2_000_000, log=None):
        self.timeout, self.limit, self.log = timeout, limit, log

    def run(self, argv, *, check=True, timeout=None, cwd=None):
        if not argv or any(not isinstance(x, str) or "\0" in x for x in argv):
            raise BackendError("Invalid process arguments")
        env = dict(os.environ, LC_ALL="C", GIT_TERMINAL_PROMPT="0")
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            try:
                proc = subprocess.Popen(argv, cwd=cwd, env=env,
                                        stdout=subprocess.PIPE if self.log else stdout,
                                        stderr=subprocess.STDOUT if self.log else stderr,
                                        # Read-only probes need isolated process groups.
                                        # Terminal jobs must retain their controlling tty.
                                        start_new_session=self.log is None)
            except OSError as exc:
                raise BackendError(f"Cannot start {argv[0]}: {exc}") from exc
            thread = None
            if self.log:
                def tee():
                    while chunk := os.read(proc.stdout.fileno(), 8192):
                        text = chunk.decode(errors="replace")
                        self.log.write(text)
                        self.log.flush()
                        sys.stdout.write(text)
                        sys.stdout.flush()
                thread = threading.Thread(target=tee, daemon=True)
                thread.start()
            try:
                proc.wait(timeout=timeout or self.timeout)
            except subprocess.TimeoutExpired as exc:
                if self.log:
                    proc.terminate()
                else:
                    os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    if self.log:
                        proc.kill()
                    else:
                        os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                raise BackendError(f"{argv[0]} timed out") from exc
            finally:
                if thread:
                    thread.join(timeout=2)
                    proc.stdout.close()
            def tail(stream):
                stream.seek(0, 2)
                size = stream.tell()
                if size > self.limit:
                    raise BackendError(f"{argv[0]} output exceeded {self.limit} bytes")
                stream.seek(0)
                return stream.read().decode(errors="replace")
            result = Result(tail(stdout), tail(stderr), proc.returncode)
        if check and result.code:
            raise BackendError(result.stderr.strip() or result.stdout.strip()
                               or f"{argv[0]} exited with {result.code}; inspect job log")
        return result
