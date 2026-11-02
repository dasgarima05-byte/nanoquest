"""Parent-side helper: run player code in a child process with a timeout."""
import json
import subprocess
import sys
from pathlib import Path

RUNNER = Path(__file__).with_name("sandbox_runner.py")


def _fail(message):
    return {"passed": False, "messages": [], "stdout": "", "error": message, "figure": None}


def run_in_sandbox(level_id, code, timeout=8):
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(RUNNER)],
            input=json.dumps({"level": level_id, "code": code}),
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _fail(f"Your code ran for more than {timeout} seconds. Is there an "
                     "infinite loop? Check your loop conditions.")
    if proc.returncode != 0 or not proc.stdout.strip():
        tail = proc.stderr.strip().splitlines()[-3:]
        return _fail("The simulator crashed: " + " | ".join(tail))
    return json.loads(proc.stdout)
