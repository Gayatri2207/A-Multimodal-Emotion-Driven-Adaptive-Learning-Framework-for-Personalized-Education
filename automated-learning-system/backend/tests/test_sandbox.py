"""Tests for the code execution sandbox."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.sandbox import run_code, evaluate_against_tests


class TestRunCode:
    def test_hello_world(self):
        result = run_code('print("Hello, World!")')
        assert result["exit_code"] == 0
        assert "Hello, World!" in result["stdout"]
        assert not result["timed_out"]

    def test_arithmetic(self):
        result = run_code("print(2 + 3)")
        assert result["stdout"].strip() == "5"

    def test_syntax_error(self):
        result = run_code("def broken(:")
        assert result["exit_code"] != 0
        assert result["stderr"] != "" or result["error"]

    def test_runtime_error(self):
        result = run_code("x = 1 / 0")
        assert result["exit_code"] != 0

    def test_timeout(self):
        result = run_code("while True: pass")
        assert result["timed_out"] is True

    def test_blocked_os_import(self):
        result = run_code("import os; print(os.getcwd())")
        assert result["exit_code"] != 0
        assert "not allowed" in result["stderr"].lower() or result["exit_code"] != 0

    def test_blocked_subprocess(self):
        result = run_code("import subprocess; subprocess.run(['echo', 'hi'])")
        assert result["exit_code"] != 0

    def test_blocked_socket(self):
        result = run_code("import socket; socket.socket()")
        assert result["exit_code"] != 0

    def test_stdin_input(self):
        result = run_code("x = int(input())\nprint(x * 2)", stdin_input="7\n")
        assert result["stdout"].strip() == "14"

    def test_output_capture(self):
        result = run_code("for i in range(5): print(i)")
        lines = result["stdout"].strip().splitlines()
        assert lines == ["0", "1", "2", "3", "4"]

    def test_multiline_code(self):
        code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(10))
"""
        result = run_code(code)
        assert result["stdout"].strip() == "55"


class TestEvaluateAgainstTests:
    def test_all_pass(self):
        code = "a = int(input()); b = int(input()); print(a + b)"
        tests = [
            {"stdin": "1\n2\n", "expected_stdout": "3"},
            {"stdin": "10\n5\n", "expected_stdout": "15"},
        ]
        result = evaluate_against_tests(code, tests)
        assert result["passed"] == 2
        assert result["score"] == 1.0

    def test_partial_pass(self):
        code = "print('wrong')"
        tests = [
            {"stdin": "", "expected_stdout": "wrong"},
            {"stdin": "", "expected_stdout": "right"},
        ]
        result = evaluate_against_tests(code, tests)
        assert result["passed"] == 1
        assert result["failed"] == 1
        assert result["score"] == 0.5

    def test_all_fail(self):
        code = "print('nothing')"
        tests = [{"stdin": "", "expected_stdout": "something"}]
        result = evaluate_against_tests(code, tests)
        assert result["passed"] == 0
        assert result["score"] == 0.0

    def test_empty_tests(self):
        result = evaluate_against_tests("print('hi')", [])
        assert result["total"] == 0
        assert result["score"] == 0.0
