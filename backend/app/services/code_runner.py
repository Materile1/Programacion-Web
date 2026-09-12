import ast
import json
import os
import subprocess
import sys
from dataclasses import dataclass

try:
    import resource
except ImportError:
    resource = None

@dataclass
class ExecutionResult:
    passed: bool
    passed_tests: int
    total_tests: int
    feedback: str

MAX_OUTPUT_BYTES = 4000
EXECUTION_TIMEOUT_SECONDS = 5
MEMORY_LIMIT_BYTES = 128 * 1024 * 1024
BLOCKED_MODULES = {"os", "subprocess", "socket", "shutil", "ctypes"}
BLOCKED_CALLS = {"eval", "exec", "__import__", "open"}

def _result(stdout: str, stderr: str, passed: bool, feedback: str, results: list[dict] | None = None) -> dict:
    return {"stdout": stdout[-MAX_OUTPUT_BYTES:], "stderr": stderr[-MAX_OUTPUT_BYTES:], "passed": passed, "feedback": feedback, "results": results or []}

def _build_harness(code: str, test_case: dict) -> str:
    return (
        "import json\n"
        + code
        + "\n"
        + "print(json.dumps(solve(" + repr(test_case.get("input")) + "), default=str))\n"
    )


class _UnsafeCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reason = ""

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.split(".", 1)[0] in BLOCKED_MODULES:
                self.reason = f"Importación bloqueada: {alias.name}"
                return
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if (node.module or "").split(".", 1)[0] in BLOCKED_MODULES:
            self.reason = f"Importación bloqueada: {node.module}"
            return
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            self.reason = f"Llamada bloqueada: {node.func.id}"
            return
        if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_CALLS:
            self.reason = f"Llamada bloqueada: {node.func.attr}"
            return
        self.generic_visit(node)


def _validate_code(code: str) -> str | None:
    tree = ast.parse(code)
    visitor = _UnsafeCodeVisitor()
    visitor.visit(tree)
    return visitor.reason or None


def _limit_child_process() -> None:
    if resource is not None:
        resource.setrlimit(resource.RLIMIT_CPU, (EXECUTION_TIMEOUT_SECONDS, EXECUTION_TIMEOUT_SECONDS))
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        try:
            import pwd
            nobody = pwd.getpwnam("nobody")
            os.setgid(nobody.pw_gid)
            os.setuid(nobody.pw_uid)
        except (ImportError, KeyError, PermissionError):
            pass


def _run_case(code: str, test_case: dict) -> tuple[str, str, int]:
    command = [sys.executable, "-I", "-S", "-c", _build_harness(code, test_case)]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        env={"PYTHONIOENCODING": "utf-8"},
        preexec_fn=_limit_child_process if os.name != "nt" else None,
    )
    try:
        stdout, stderr = process.communicate(timeout=EXECUTION_TIMEOUT_SECONDS)
        if process.returncode < 0 and not stderr:
            return "", "Tiempo de ejecución agotado (5 segundos).", 1
        return stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace"), process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return "", "Tiempo de ejecución agotado (5 segundos).", 1

def execute_code(code: str, language: str, test_cases_json: str):
    if language != "python":
        return _result("", "JavaScript requiere un runtime configurado en el worker.", False, "El ejecutor admite Python en este entorno.")
    try:
        ast.parse(code)
        test_cases = json.loads(test_cases_json or "[]")
    except (SyntaxError, json.JSONDecodeError, TypeError) as exc:
        return _result("", str(exc), False, "El código o los casos de prueba no son válidos.")
    if not isinstance(test_cases, list) or any(not isinstance(case, dict) for case in test_cases):
        return _result("", "Formato de casos de prueba inválido.", False, "Los casos de prueba no tienen un formato válido.")
    try:
        blocked_reason = _validate_code(code)
    except SyntaxError as exc:
        return _result("", str(exc), False, "El código o los casos de prueba no son válidos.")
    if blocked_reason:
        return _result("", blocked_reason, False, "El sandbox bloqueó una operación no permitida.")
    stdout_parts = []
    stderr_parts = []
    results = []
    for test_case in test_cases:
        try:
            stdout, stderr, exit_code = _run_case(code, test_case)
        except (OSError, subprocess.SubprocessError) as exc:
            stdout, stderr, exit_code = "", str(exc), 1
        actual_text = stdout.strip()
        try:
            actual = json.loads(actual_text or "null")
        except json.JSONDecodeError:
            actual = None
        expected = test_case.get("output")
        results.append({"input": test_case.get("input"), "expected": expected, "actual": actual, "passed": exit_code == 0 and actual == expected})
        stdout_parts.append(stdout)
        stderr_parts.append(stderr)
    passed_count = sum(result["passed"] for result in results)
    passed = bool(results) and passed_count == len(results)
    feedback = "Todos los casos pasan." if passed else f"Casos superados: {passed_count}/{len(results)}."
    return _result("".join(stdout_parts), "".join(stderr_parts), passed, feedback, results)


def run_submission(code: str, language: str, test_cases_json: str = "[]") -> ExecutionResult:
    executed = execute_code(code, language, test_cases_json)
    results = executed.get("results", [])
    return ExecutionResult(executed["passed"], sum(result["passed"] for result in results), len(results), executed["feedback"])
