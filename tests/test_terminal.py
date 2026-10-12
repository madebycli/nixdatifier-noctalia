import os
import pty
import select
import sys
import tempfile
import time
import unittest
from pathlib import Path


class TerminalTests(unittest.TestCase):
    def test_logged_job_retains_controlling_terminal_for_password_prompts(self):
        # A real pseudo-terminal verifies /dev/tty and foreground input without sudo.
        with tempfile.TemporaryDirectory() as tmp:
            code = """
import sys
from nixdatifier.process import Runner
child = "import os; fd=os.open('/dev/tty',os.O_RDWR); os.write(fd,b'PROMPT:'); answer=os.read(fd,256); assert answer.strip()==b'answer'; print('TTY_OK')"
with open(sys.argv[1], 'w') as log:
    Runner(log=log).run([sys.executable, '-c', child], timeout=5)
"""
            pid, fd = pty.fork()
            if pid == 0:
                os.execv(sys.executable, [sys.executable, "-c", code, str(Path(tmp) / "job.log")])
            output = b""
            sent = False
            status = None
            try:
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline:
                    readable, _, _ = select.select([fd], [], [], 0.1)
                    if readable:
                        try: chunk = os.read(fd, 8192)
                        except OSError: chunk = b""
                        output += chunk
                        if b"PROMPT:" in output and not sent:
                            os.write(fd, b"answer\n")
                            sent = True
                    child_pid, child_status = os.waitpid(pid, os.WNOHANG)
                    if child_pid:
                        status = child_status
                        break
                self.assertIsNotNone(status, output.decode(errors="replace"))
                self.assertEqual(os.waitstatus_to_exitcode(status), 0, output.decode(errors="replace"))
                self.assertIn(b"TTY_OK", output)
                self.assertIn("TTY_OK", (Path(tmp) / "job.log").read_text())
            finally:
                os.close(fd)
                if status is None:
                    os.kill(pid, 9)
                    os.waitpid(pid, 0)
