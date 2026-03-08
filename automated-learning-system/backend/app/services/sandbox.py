"""
Safe Python code execution sandbox.

Uses subprocess with a strict timeout and a restricted execution environment.
Standard I/O is captured; dangerous imports are blocked before execution.
"""

import re
import subprocess
import sys
import os
import uuid
import time
from pathlib import Path
from typing import Dict, Any

TIMEOUT_SECONDS = 5
MAX_OUTPUT_CHARS = 4096

# Modules that must never be imported inside submitted code
BLOCKED_IMPORTS = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib",
    "importlib", "ctypes", "multiprocessing", "threading",
    "http", "urllib", "requests", "ftplib", "smtplib",
    "pickle", "shelve", "dbm", "sqlite3",
    "signal", "resource", "gc",
}

_GUARD = f"""import builtins as _b
_BLOCKED = {BLOCKED_IMPORTS!r}
_ri = _b.__import__
def _si(name, *a, **kw):
    if name.split(".")[0] in _BLOCKED:
        raise ImportError(f"Import of '{{name}}' is not allowed in submitted code.")
    return _ri(name, *a, **kw)
_b.__import__ = _si
"""


def _write_temp(code: str) -> Path:
    """Write code to a uniquely named temp file and return its path."""
    tmp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", ".")))
    tmp_path = tmp_dir / f"sandbox_{uuid.uuid4().hex}.py"
    tmp_path.write_text(_GUARD + "\n# --- user code ---\n" + code, encoding="utf-8")
    return tmp_path


def _sanitize_stderr(stderr: str, tmp_path: Path) -> str:
    """
    Return a student-friendly version of a Python traceback.

    - Replaces the temp file's absolute path with '<your_code.py>'
    - Strips the guard code's internal line numbers
    - Preserves the actual error type and message
    """
    if not stderr:
        return ""
    # Replace the exact temp path (Windows and Unix forms)
    pattern = re.escape(str(tmp_path))
    cleaned = re.sub(pattern, "<your_code.py>", stderr)
    # Generic fallback: any path ending in sandbox_<hex>.py
    cleaned = re.sub(r'[A-Za-z]:\\[^"]*sandbox_[0-9a-f]+\.py', "<your_code.py>", cleaned)
    cleaned = re.sub(r'/tmp/sandbox_[0-9a-f]+\.py', "<your_code.py>", cleaned)
    # Remove guard-only lines (lines that reference _si / _ri / _BLOCKED internals)
    lines = cleaned.splitlines()
    visible = [
        ln for ln in lines
        if not any(internal in ln for internal in ("_si(", "_ri(", "_BLOCKED", "_b.__import__", "import builtins"))
    ]
    return "\n".join(visible).strip()


def run_code(code: str, stdin_input: str = "") -> Dict[str, Any]:
    """
    Execute Python code safely and return the result.

    Args:
        code: Python source code submitted by the user
        stdin_input: Optional string to pass as stdin to the process

    Returns:
        dict with keys:
            stdout (str), stderr (str), exit_code (int), timed_out (bool), error (str|None)
    """
    tmp_path = _write_temp(code)
    result: Dict[str, Any] = {
        "stdout": "",
        "stderr": "",
        "clean_stderr": "",
        "exit_code": -1,
        "timed_out": False,
        "error": None,
        "exec_time_ms": 0,
    }
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, str(tmp_path)],
            input=stdin_input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
        )
        result["exec_time_ms"] = round((time.perf_counter() - t0) * 1000)
        result["stdout"] = proc.stdout[:MAX_OUTPUT_CHARS]
        result["stderr"] = proc.stderr[:MAX_OUTPUT_CHARS]
        result["clean_stderr"] = _sanitize_stderr(proc.stderr, tmp_path)[:MAX_OUTPUT_CHARS]
        result["exit_code"] = proc.returncode
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["exec_time_ms"] = TIMEOUT_SECONDS * 1000
        result["error"] = f"Execution timed out after {TIMEOUT_SECONDS}s"
        result["clean_stderr"] = f"Time Limit Exceeded ({TIMEOUT_SECONDS}s)"
    except Exception as e:
        result["error"] = str(e)
        result["clean_stderr"] = str(e)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return result


def evaluate_against_tests(code: str, test_cases: list) -> Dict[str, Any]:
    """
    Run code against a list of test cases.

    Args:
        code: User-submitted Python code
        test_cases: list of dicts with keys 'stdin', 'expected_stdout'

    Returns:
        dict with 'passed', 'failed', 'total', 'details'
    """
    details = []
    passed = 0
    for i, tc in enumerate(test_cases):
        stdin = tc.get("stdin", "")
        expected = tc.get("expected_stdout", "").strip()
        res = run_code(code, stdin_input=stdin)

        actual = res["stdout"].strip()
        ok = (not res["timed_out"]) and (res["exit_code"] == 0) and (actual == expected)

        # Determine a human-readable error type
        if res["timed_out"]:
            error_type = "TLE"
        elif res["exit_code"] != 0:
            # Extract the last line of the traceback as the short error label
            last_line = (res["clean_stderr"] or res["stderr"]).strip().splitlines()
            error_type = last_line[-1] if last_line else "RuntimeError"
        else:
            error_type = None

        if ok:
            passed += 1
        details.append({
            "test_case": i + 1,
            "passed": ok,
            "stdin": stdin,                           # pass input back to frontend
            "stdout": res["stdout"],
            "actual": actual,                     # stripped, always the real program output
            "expected": expected,
            "stderr": res["stderr"],
            "clean_stderr": res.get("clean_stderr", ""),
            "error_type": error_type,
            "timed_out": res["timed_out"],
            "exec_time_ms": res.get("exec_time_ms", 0),
        })
    total = len(test_cases)
    return {
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "score": round(passed / total, 3) if total else 0.0,
        "details": details,
    }

