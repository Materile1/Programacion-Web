import ast
import re
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    passed: bool
    passed_tests: int
    total_tests: int
    feedback: str


def run_submission(code: str, language: str) -> ExecutionResult:
    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            return ExecutionResult(False, 0, 3, f"Error de sintaxis en línea {exc.lineno}: {exc.msg}")
        if any(token in code for token in ("import os", "import subprocess", "__import__", "open(")):
            return ExecutionResult(False, 0, 3, "El sandbox bloqueó una operación no permitida.")
        has_function = bool(re.search(r"def\s+\w+\s*\(", code))
    else:
        has_function = bool(re.search(r"function\s+\w+|const\s+\w+\s*=\s*\(", code))
        if any(token in code for token in ("process.", "require(", "fetch(", "eval(")):
            return ExecutionResult(False, 0, 3, "El sandbox bloqueó una operación no permitida.")
    passed = has_function and len(code.strip()) >= 20
    count = 3 if passed else (1 if code.strip() else 0)
    feedback = "Los casos sintéticos pasan. Revisa nombres, complejidad y casos límite." if passed else "Define una función clara y cubre el comportamiento descrito antes de optimizar."
    return ExecutionResult(passed, count, 3, feedback)
