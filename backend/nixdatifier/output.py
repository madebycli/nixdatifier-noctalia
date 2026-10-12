"""Drain read-only stdout/stderr concurrently with a deadline and byte limits."""

import os
import selectors
import subprocess
import time


class OutputLimit(Exception):
    pass


def capture(proc, limit, timeout):
    deadline = time.monotonic() + timeout
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    with selectors.DefaultSelector() as selector:
        for name in buffers:
            stream = getattr(proc, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(proc.args, timeout)
            for key, _ in selector.select(remaining):
                chunk = os.read(key.fd, 8192)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                buffer = buffers[key.data]
                if len(buffer) + len(chunk) > limit:
                    raise OutputLimit()
                buffer.extend(chunk)
        proc.wait(timeout=max(0, deadline - time.monotonic()))
    return tuple(buffers[name].decode(errors="replace") for name in ("stdout", "stderr"))
