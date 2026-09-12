import ast
import json
from dataclasses import dataclass

import docker
from docker.errors import APIError, ContainerError, ImageNotFound, NotFound
from requests.exceptions import ReadTimeout

@dataclass
class ExecutionResult:
    passed: bool
    passed_tests: int
    total_tests: int
    feedback: str

SANDBOX_IMAGE = "python:3.12-slim"
MAX_OUTPUT_BYTES = 4000

def _result(stdout: str, stderr: str, passed: bool, feedback: str, results: list[dict] | None = None) -> dict:
    return {"stdout": stdout[-MAX_OUTPUT_BYTES:], "stderr": stderr[-MAX_OUTPUT_BYTES:], "passed": passed, "feedback": feedback, "results": results or []}

def _build_harness(code: str, test_case: dict) -> str:
    return (
        "import json\n"
        + code
        + "\n"
        + "print(json.dumps(solve(" + repr(test_case.get("input")) + "), default=str))\n"
    )

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
    if any(token in code for token in ("import os", "import subprocess", "__import__", "open(", "socket", "shutil", "ctypes")):
        return _result("", "Operación bloqueada por el sandbox.", False, "El sandbox bloqueó una operación no permitida.")
    client = None
    stdout_parts = []
    stderr_parts = []
    results = []
    try:
        client = docker.from_env()
        for test_case in test_cases:
            container = None
            try:
                container = client.containers.create(
                    image=SANDBOX_IMAGE,
                    command=["python", "-I", "-S", "-c", _build_harness(code, test_case)],
                    network_mode="none",
                    mem_limit="128m",
                    nano_cpus=500_000_000,
                    pids_limit=64,
                    user="65534:65534",
                    read_only=True,
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges:true"],
                    environment={"PYTHONIOENCODING": "utf-8"},
                )
                container.start()
                wait_result = container.wait(timeout=5)
                stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
                stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
                exit_code = wait_result.get("StatusCode", 1) if isinstance(wait_result, dict) else 1
            except (ReadTimeout, TimeoutError):
                stdout, stderr, exit_code = "", "Tiempo de ejecución agotado (5 segundos).", 1
            finally:
                if container is not None:
                    try:
                        container.remove(force=True)
                    except (APIError, NotFound):
                        pass
            actual_text = stdout.strip()
            try:
                actual = json.loads(actual_text or "null")
            except json.JSONDecodeError:
                actual = None
            expected = test_case.get("output")
            results.append({"input": test_case.get("input"), "expected": expected, "actual": actual, "passed": exit_code == 0 and actual == expected})
            stdout_parts.append(stdout)
            stderr_parts.append(stderr)
    except ImageNotFound:
        return _result("", f"La imagen {SANDBOX_IMAGE} no está disponible en el daemon Docker.", False, "El sandbox no está disponible.")
    except (ContainerError, APIError) as exc:
        return _result("", str(exc), False, "El sandbox no pudo ejecutar el código.", results)
    finally:
        if client is not None:
            client.close()
    passed_count = sum(result["passed"] for result in results)
    passed = bool(results) and passed_count == len(results)
    feedback = "Todos los casos pasan." if passed else f"Casos superados: {passed_count}/{len(results)}."
    return _result("".join(stdout_parts), "".join(stderr_parts), passed, feedback, results)


def run_submission(code: str, language: str, test_cases_json: str = "[]") -> ExecutionResult:
    executed = execute_code(code, language, test_cases_json)
    results = executed.get("results", [])
    return ExecutionResult(executed["passed"], sum(result["passed"] for result in results), len(results), executed["feedback"])
