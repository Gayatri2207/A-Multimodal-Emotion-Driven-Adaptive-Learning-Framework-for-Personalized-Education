"""
Coding service — public API used by routes.

Delegates actual code execution to sandbox.py so all evaluation logic
lives in one place.
"""

from app.services.sandbox import run_code, evaluate_against_tests


def evaluate_code(code: str, stdin_input: str = "") -> dict:
    """
    Execute a single code snippet and return the result.

    Returns a dict with keys:
        stdout, stderr, clean_stderr, exit_code, timed_out,
        error, exec_time_ms, score, feedback
    """
    result = run_code(code, stdin_input=stdin_input)

    # Derive a simple 0–100 score and human feedback from execution outcome
    if result["timed_out"]:
        score = 0
        feedback = "Time Limit Exceeded — your solution ran too long."
    elif result["exit_code"] != 0:
        score = 0
        feedback = result.get("clean_stderr") or result.get("stderr") or "Runtime error."
    else:
        # Output produced successfully
        output = result.get("stdout", "").strip()
        score = 100 if output else 50
        feedback = "Code executed successfully." if output else "No output produced."

    result["score"] = score
    result["feedback"] = feedback
    return result


def evaluate_submission(code: str, test_cases: list) -> dict:
    """
    Run code against a list of test cases and return aggregated results.

    Each test_case dict must have 'stdin' and 'expected_stdout' keys.

    Returns a dict with keys:
        passed, failed, total, score (0.0–1.0), details
    """
    return evaluate_against_tests(code, test_cases)

