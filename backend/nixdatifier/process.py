"""Bounded subprocesses. Dynamic values never pass through a shell."""

import codecs
import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass

from .output import OutputLimit, capture


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
        try:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT if self.log else subprocess.PIPE,
                                    # Interactive jobs must retain their controlling tty.
                                    start_new_session=self.log is None)
        except OSError as exc:
            raise BackendError(f"Cannot start {argv[0]}: {exc}") from exc
        thread = None
        if self.log:
            def tee():
                decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
                while chunk := os.read(proc.stdout.fileno(), 8192):
                    self._write(decoder.decode(chunk))
                self._write(decoder.decode(b"", final=True))
            thread = threading.Thread(target=tee, daemon=True)
            thread.start()
        try:
            if self.log:
                proc.wait(timeout=timeout or self.timeout)
                out, err = "", ""
            else:
                out, err = capture(proc, self.limit, timeout or self.timeout)
            result = Result(out, err, proc.returncode)
        except (subprocess.TimeoutExpired, OutputLimit) as exc:
            self._stop(proc)
            reason = "timed out" if isinstance(exc, subprocess.TimeoutExpired) else f"output exceeded {self.limit} bytes"
            raise BackendError(f"{argv[0]} {reason}") from exc
        except BaseException:
            self._stop(proc)
            raise
        finally:
            if thread:
                thread.join(timeout=2)
            proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
        if check and result.code:
            raise BackendError(result.stderr.strip() or result.stdout.strip()
                               or f"{argv[0]} exited with {result.code}; inspect job log")
        return result

    def _write(self, text):
        self.log.write(text)
        self.log.flush()
        sys.stdout.write(text)
        sys.stdout.flush()

    def _stop(self, proc):
        def send(sig):
            try:
                if self.log:
                    proc.send_signal(sig)
                else:
                    os.killpg(proc.pid, sig)
            except ProcessLookupError:
                pass
        send(signal.SIGTERM)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            send(signal.SIGKILL)
            proc.wait()
        # The group can still contain descendants after its leader exited.
        if not self.log:
            send(signal.SIGKILL)
