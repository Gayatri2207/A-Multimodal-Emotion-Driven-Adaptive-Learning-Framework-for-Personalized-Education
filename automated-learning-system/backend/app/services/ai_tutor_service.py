"""
AI Coding Tutor Service
=======================
Analyses student-submitted Python code against a problem description and
returns structured, educational feedback.

Architecture
------------
1. **Rule-based engine** (always available):
   - Python AST parsing for syntax errors and structural issues
   - Loop-nesting analysis for Big-O estimation
   - Common anti-pattern detection (bare ``except``, mutable defaults, etc.)
   - Problem-description keyword matching for algorithm hints
   - Code-quality scoring (naming, function length, comments)

2. **LLM engine** (optional, activated by env vars):
   - ``OPENAI_API_KEY`` → uses OpenAI ``gpt-3.5-turbo``
   - ``OLLAMA_URL``     → uses local Ollama (default model ``llama3``)
   Falls back silently to the rule-based engine if unavailable.

3. **Emotion-aware verbosity**:
   - ``emotion_score < 0.35`` (frustrated) → detailed, step-by-step guidance
   - ``emotion_score > 0.70`` (bored/confident) → terse, challenge-focused hints
   - Otherwise → balanced feedback
"""

from __future__ import annotations

import ast
import os
import re
import textwrap
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TutorFeedback:
    """Structured feedback returned to the caller."""
    summary: str = ""
    mistakes: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    algorithm_insight: str = ""
    hints: list[str] = field(default_factory=list)
    time_complexity: str = "Unknown"
    space_complexity: str = "Unknown"
    readability_score: int = 0   # 0-100
    efficiency_score: int = 0    # 0-100
    emotion_note: str = ""
    raw_text: str = ""           # full LLM response when available


# ---------------------------------------------------------------------------
# Helper: AST-based code analysis
# ---------------------------------------------------------------------------

def _parse_code(code: str) -> tuple[Optional[ast.Module], Optional[str]]:
    """Return (tree, None) on success or (None, error_message) on SyntaxError."""
    try:
        return ast.parse(code), None
    except SyntaxError as exc:
        return None, f"SyntaxError on line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        return None, str(exc)


def _count_max_loop_depth(tree: ast.Module) -> int:
    """Return the maximum nesting depth of for/while loops in the AST."""
    max_depth = [0]

    class LoopVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0

        def _visit_loop(self, node):
            self.depth += 1
            max_depth[0] = max(max_depth[0], self.depth)
            self.generic_visit(node)
            self.depth -= 1

        visit_For = _visit_loop
        visit_While = _visit_loop

    LoopVisitor().visit(tree)
    return max_depth[0]


def _estimate_complexity(tree: ast.Module) -> tuple[str, str]:
    """Return (time_complexity, space_complexity) strings."""
    depth = _count_max_loop_depth(tree)
    # Check for recursion
    has_recursion = False
    funcs: list[str] = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for func_node in ast.walk(tree):
        if isinstance(func_node, ast.FunctionDef):
            for call in ast.walk(func_node):
                if isinstance(call, ast.Call):
                    func_name = getattr(call.func, "id", "") or getattr(call.func, "attr", "")
                    if func_name in funcs:
                        has_recursion = True

    if has_recursion:
        time_c = "O(n) to O(2ⁿ) — recursion detected (analyse recurrence relation)"
        space_c = "O(n) — recursion stack"
    elif depth == 0:
        time_c = "O(1) — no loops detected"
        space_c = "O(1)"
    elif depth == 1:
        time_c = "O(n) — single loop"
        space_c = "O(1) unless extra data structures are used"
    elif depth == 2:
        time_c = "O(n²) — nested loops"
        space_c = "O(1) to O(n)"
    else:
        time_c = f"O(n^{depth}) — {depth}-deep nested loops (consider optimising)"
        space_c = "O(n) or higher"

    return time_c, space_c


def _detect_issues(tree: ast.Module, code: str) -> list[str]:
    """Return a list of detected code issues."""
    issues: list[str] = []
    lines = code.splitlines()

    for node in ast.walk(tree):
        # Bare except
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append("Bare `except:` clause — catch specific exceptions to avoid masking bugs.")

        # Mutable default argument
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(
                        f"Mutable default argument in `{node.name}()` — use `None` and initialise inside the function."
                    )

        # Missing return in a non-trivial function
        if isinstance(node, ast.FunctionDef):
            body_stmts = node.body
            has_return = any(isinstance(s, ast.Return) for s in ast.walk(node))
            has_yield  = any(isinstance(s, ast.Yield)  for s in ast.walk(node))
            if not has_return and not has_yield and len(body_stmts) > 1:
                # Exclude __init__ and functions that only print
                non_trivial = [s for s in ast.walk(node) if isinstance(s, (ast.Assign, ast.If, ast.For, ast.While))]
                if non_trivial:
                    issues.append(f"`{node.name}()` has no `return` statement — is the result being returned correctly?")

        # Single-letter variable names (excluding loop counters i/j/k/n/m)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if len(node.id) == 1 and node.id not in ("i", "j", "k", "n", "m", "x", "y", "z", "_"):
                issues.append(f"Variable `{node.id}` is a single character — use a descriptive name.")

    # Extremely long lines
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            issues.append(f"Line {i} is {len(line)} characters — consider breaking it up for readability.")

    return issues[:6]  # cap to avoid overwhelming the student


def _detect_improvements(tree: ast.Module, code: str) -> list[str]:
    """Return actionable improvement suggestions."""
    improvements: list[str] = []

    # List comprehension opportunities
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            # Simple pattern: for x in y: result.append(...)
            if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
                call = node.body[0].value
                if isinstance(call, ast.Call) and getattr(call.func, "attr", "") == "append":
                    improvements.append("Consider replacing the for+append loop with a list comprehension for conciseness.")
                    break

    # Dictionary lookup instead of chain of if-elif
    elif_chains = [n for n in ast.walk(tree) if isinstance(n, ast.If) and n.orelse and isinstance(n.orelse[0], ast.If)]
    if len(elif_chains) >= 3:
        improvements.append("Long if-elif chain detected — consider using a dictionary for O(1) lookup instead.")

    # Range(len(...)) anti-pattern
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if getattr(node.func, "id", "") == "range" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Call) and getattr(arg.func, "id", "") == "len":
                    improvements.append("Use `for item in collection` (or `enumerate`) instead of `range(len(...))`.")
                    break

    # Repeated string concatenation in a loop
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                        improvements.append("String concatenation in a loop is O(n²) — use `''.join(parts)` instead.")
                        break

    return improvements[:4]


def _readability_score(code: str, tree: ast.Module) -> int:
    """Heuristic 0-100 readability score."""
    score = 70
    lines = [l for l in code.splitlines() if l.strip()]

    # Docstrings / comments
    has_comment = any(l.strip().startswith("#") for l in lines)
    has_docstring = any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                        for n in ast.walk(tree))
    if has_comment or has_docstring:
        score += 10

    # Long functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and len(node.body) > 30:
            score -= 10
            break

    # Magic numbers
    magic = [n for n in ast.walk(tree) if isinstance(n, ast.Constant)
             and isinstance(n.value, (int, float)) and n.value not in (0, 1, -1, 2)]
    if len(magic) > 3:
        score -= 5

    return max(0, min(100, score))


def _efficiency_score(time_complexity: str) -> int:
    """Simple efficiency score derived from estimated complexity."""
    if "O(1)"   in time_complexity: return 95
    if "O(n)"   in time_complexity and "²" not in time_complexity: return 80
    if "O(n²)"  in time_complexity: return 55
    if "O(n^"   in time_complexity: return 30
    if "O(2ⁿ)"  in time_complexity: return 20
    return 65


# ---------------------------------------------------------------------------
# Helper: problem-description keyword → algorithm hints
# ---------------------------------------------------------------------------

_ALGORITHM_HINTS: list[tuple[list[str], str]] = [
    (["two sum", "pair", "complement"],
     "This looks like a Two-Sum problem — a hash map lets you find the complement in O(1)."),
    (["sorted", "binary search", "search in sorted"],
     "The sorted input is a strong hint to use Binary Search — O(log n) instead of O(n)."),
    (["subarray", "sliding window", "maximum sum subarray", "minimum window"],
     "Sliding-window technique is often optimal for contiguous-subarray problems."),
    (["tree", "binary tree", "bst", "traversal"],
     "Think about which traversal you need: inorder (sorted BST), preorder, postorder, or BFS for level-order."),
    (["graph", "shortest path", "connected components"],
     "Graph problems often need BFS (shortest unweighted path) or DFS (connectivity/cycles)."),
    (["dynamic programming", "dp", "fibonacci", "knapsack", "longest common"],
     "Try to identify overlapping sub-problems — define dp[i] and its recurrence relation."),
    (["stack", "parentheses", "balanced", "next greater"],
     "A stack is ideal for matching/nesting problems — push on open, pop on close."),
    (["linked list", "reverse list", "cycle"],
     "Slow+fast pointer technique is key for linked-list cycle detection and middle-finding."),
    (["anagram", "permutation", "character frequency"],
     "Character-frequency counts (collections.Counter or a 26-slot array) make anagram checks O(n)."),
    (["palindrome"],
     "Two-pointer approach (left+right converging) checks palindromes in O(n) with O(1) space."),
    (["matrix", "2d array", "spiral", "rotate"],
     "For matrix problems, think about in-place transformations layer by layer."),
    (["merge", "interval", "overlapping intervals"],
     "Sort intervals by start time first, then merge greedily in one pass."),
]


def _match_algorithm_hint(problem_text: str) -> str:
    lower = problem_text.lower()
    for keywords, hint in _ALGORITHM_HINTS:
        if any(kw in lower for kw in keywords):
            return hint
    return ""


# ---------------------------------------------------------------------------
# Emotion-aware preamble
# ---------------------------------------------------------------------------

def _emotion_note(emotion_score: float) -> str:
    if emotion_score < 0.35:
        return ("You seem to be finding this challenging — that's completely normal! "
                "Let's break it down step by step. Take your time.")
    if emotion_score > 0.70:
        return ("You're doing great! Here's a quick nudge to push you further — "
                "try to solve it with better time complexity.")
    return ""


# ---------------------------------------------------------------------------
# Rule-based tutor (always available)
# ---------------------------------------------------------------------------

def _rule_based_analysis(
    problem: str,
    code: str,
    emotion_score: float,
) -> TutorFeedback:
    fb = TutorFeedback()
    fb.emotion_note = _emotion_note(emotion_score)

    # ── Syntax / parse ──────────────────────────────────────────────────────
    tree, syntax_error = _parse_code(code)
    if syntax_error:
        fb.summary = "Your code has a syntax error that prevents it from running."
        fb.mistakes.append(syntax_error)
        fb.hints.append("Fix the syntax error first, then re-submit.")
        fb.hints.append("Check for missing colons after `if/for/while/def`, mismatched brackets, or wrong indentation.")
        fb.time_complexity = "N/A"
        fb.space_complexity = "N/A"
        fb.readability_score = 0
        fb.efficiency_score = 0
        return fb

    # ── Complexity ──────────────────────────────────────────────────────────
    fb.time_complexity, fb.space_complexity = _estimate_complexity(tree)

    # ── Structural issues ───────────────────────────────────────────────────
    fb.mistakes = _detect_issues(tree, code)

    # ── Improvement suggestions ─────────────────────────────────────────────
    fb.improvements = _detect_improvements(tree, code)

    # ── Algorithm insight ───────────────────────────────────────────────────
    fb.algorithm_insight = _match_algorithm_hint(problem)

    # ── Hints (emotion-aware verbosity) ─────────────────────────────────────
    if emotion_score < 0.35:
        # Frustrated — give more detailed hints
        if fb.algorithm_insight:
            fb.hints.append(f"Algorithm tip: {fb.algorithm_insight}")
        fb.hints.append("Try tracing through your code with the first example input manually.")
        fb.hints.append("Check your edge cases: empty input, single element, all same values.")
        if "O(n²)" in fb.time_complexity or "O(n^" in fb.time_complexity:
            fb.hints.append("Your current solution may be too slow — look for a way to avoid the nested loops.")
    elif emotion_score > 0.70:
        # Bored/confident — minimal hints, push for optimisation
        if fb.algorithm_insight:
            fb.hints.append(fb.algorithm_insight)
        if "O(n²)" in fb.time_complexity or "O(n^" in fb.time_complexity:
            fb.hints.append("Challenge: can you reduce the time complexity to O(n) or O(n log n)?")
    else:
        # Neutral — balanced
        if fb.algorithm_insight:
            fb.hints.append(fb.algorithm_insight)
        fb.hints.append("Make sure you have handled edge cases (empty input, large values).")

    # ── Scores ──────────────────────────────────────────────────────────────
    fb.readability_score = _readability_score(code, tree)
    fb.efficiency_score  = _efficiency_score(fb.time_complexity)

    # ── Summary ─────────────────────────────────────────────────────────────
    issues_count = len(fb.mistakes)
    if issues_count == 0 and not fb.improvements:
        fb.summary = "Your code looks structurally sound! Focus on correctness and edge cases."
    elif issues_count > 0:
        fb.summary = f"Found {issues_count} issue(s) to address. Review the details below."
    else:
        fb.summary = "Your code runs, but there are style/efficiency improvements worth making."

    return fb


# ---------------------------------------------------------------------------
# Optional LLM engine — OpenAI
# ---------------------------------------------------------------------------

def _openai_analysis(problem: str, code: str, emotion_score: float) -> Optional[str]:
    """Call OpenAI if OPENAI_API_KEY is set. Returns raw text or None."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        import openai  # type: ignore
        verbosity = (
            "Be very detailed and encouraging." if emotion_score < 0.35 else
            "Be brief and focus on optimisation." if emotion_score > 0.70 else
            "Be balanced."
        )
        prompt = _build_llm_prompt(problem, code, verbosity)
        # Support both openai>=1.0 (new client) and older versions
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert coding tutor. Never reveal full solutions."},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=600,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()
        except AttributeError:
            # Fallback for openai<1.0
            openai.api_key = api_key
            response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert coding tutor. Never reveal full solutions."},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=600,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Optional LLM engine — HuggingFace Inference API (free tier)
# ---------------------------------------------------------------------------

def _huggingface_analysis(problem: str, code: str, emotion_score: float) -> Optional[str]:
    """Call HuggingFace Inference API if HF_API_TOKEN is set. Returns raw text or None.

    Set HF_API_TOKEN env var to your HuggingFace token (free at huggingface.co).
    Optionally set HF_MODEL to override the default model.
    """
    hf_token = os.environ.get("HF_API_TOKEN", "")
    if not hf_token:
        return None
    try:
        import requests  # type: ignore
        model = os.environ.get("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
        verbosity = (
            "Be very detailed and encouraging." if emotion_score < 0.35 else
            "Be brief and focus on optimisation." if emotion_score > 0.70 else
            "Be balanced."
        )
        prompt = _build_llm_prompt(problem, code, verbosity)
        # Wrap in Mistral instruction format for instruction-tuned models
        formatted = f"[INST] {prompt} [/INST]"
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers={"Authorization": f"Bearer {hf_token}"},
            json={
                "inputs": formatted,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.4,
                    "return_full_text": False,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # HF returns a list of generated text dicts
        if isinstance(data, list) and data:
            return data[0].get("generated_text", "").strip()
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Optional LLM engine — Ollama (local)
# ---------------------------------------------------------------------------

def _ollama_analysis(problem: str, code: str, emotion_score: float) -> Optional[str]:
    """
    Call Ollama for AI tutor feedback.

    Auto-detects Ollama at http://localhost:11434 if OLLAMA_URL is not set.
    Set OLLAMA_MODEL to override the model (default: llama3, fallback: codellama).

    Install Ollama: https://ollama.ai
    Pull a model:   ollama pull llama3
                    ollama pull codellama
    """
    # Auto-detect: prefer env var, fall back to localhost
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    try:
        import requests  # type: ignore

        # Verify Ollama is actually running (fast check — 0.3 s to avoid blocking on Windows)
        try:
            ping = requests.get(f"{ollama_url}/api/tags", timeout=0.3)
            if ping.status_code != 200:
                return None
            available_models = [m["name"] for m in ping.json().get("models", [])]
        except Exception:
            return None  # Ollama not running

        if not available_models:
            return None

        # Pick best available model: prefer code-specialized models
        preferred = os.environ.get("OLLAMA_MODEL", "")
        code_models = ["deepseek-coder", "codellama", "codegemma", "llama3", "llama2", "mistral"]
        if preferred and preferred in available_models:
            model = preferred
        else:
            model = next((m for m in code_models if any(m in a for a in available_models)),
                         available_models[0])

        verbosity = (
            "Be very detailed and encouraging." if emotion_score < 0.35 else
            "Be brief and focus on optimisation." if emotion_score > 0.70 else
            "Be balanced."
        )
        prompt = _build_llm_prompt(problem, code, verbosity)
        resp = requests.post(
            f"{ollama_url.rstrip('/')}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        return text if len(text) > 20 else None
    except Exception:
        return None


def _build_llm_prompt(problem: str, code: str, verbosity_instruction: str) -> str:
    return textwrap.dedent(f"""
        You are a coding tutor helping a student learn. {verbosity_instruction}
        DO NOT reveal the full solution. Guide, don't solve.

        Problem:
        {problem[:800]}

        Student's code:
        ```python
        {code[:1200]}
        ```

        Provide feedback in this exact format:
        **Mistakes detected:** (list any bugs or errors)
        **How to fix:** (brief targeted guidance)
        **Algorithm insight:** (explain the ideal approach conceptually)
        **Hint:** (one nudge without giving the answer)
        **Time complexity:** (estimate)
    """).strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_code(
    problem: str,
    code: str,
    emotion_score: float = 0.5,
) -> dict:
    """
    Analyse ``code`` against ``problem`` and return structured tutor feedback.

    Parameters
    ----------
    problem : str
        Problem title + description.
    code : str
        Student's Python solution.
    emotion_score : float
        0 = very frustrated, 1 = very engaged/bored.
        Adjusts feedback verbosity.

    Returns
    -------
    dict with keys:
        summary, mistakes, improvements, algorithm_insight,
        hints, time_complexity, space_complexity,
        readability_score, efficiency_score, emotion_note,
        raw_text (LLM output if available), source ("llm" | "rules")
    """
    emotion_score = max(0.0, min(1.0, float(emotion_score)))

    # Try LLM engines first (graceful degradation)
    llm_text = _openai_analysis(problem, code, emotion_score) \
            or _huggingface_analysis(problem, code, emotion_score) \
            or _ollama_analysis(problem, code, emotion_score)

    # Always run rule-based analysis for structured fields
    fb = _rule_based_analysis(problem, code, emotion_score)

    if llm_text:
        fb.raw_text = llm_text
        # Override summary with first line of LLM response for richer display
        first_line = llm_text.split("\n")[0].strip().lstrip("#*").strip()
        if first_line:
            fb.summary = first_line

    result = {
        "summary":           fb.summary,
        "mistakes":          fb.mistakes,
        "improvements":      fb.improvements,
        "algorithm_insight": fb.algorithm_insight,
        "hints":             fb.hints,
        "time_complexity":   fb.time_complexity,
        "space_complexity":  fb.space_complexity,
        "readability_score": fb.readability_score,
        "efficiency_score":  fb.efficiency_score,
        "emotion_note":      fb.emotion_note,
        "raw_text":          fb.raw_text,
        "source":            "llm" if llm_text else "rules",
    }
    return result
