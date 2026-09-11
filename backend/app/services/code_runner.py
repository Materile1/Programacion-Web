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

def _result(stdout: str, stderr: str, passed: bool, feedback: str) -> dict:
    return {"stdout": stdout[-MAX_OUTPUT_BYTES:], "stderr": stderr[-MAX_OUTPUT_BYTES:], "passed": passed, "feedback": feedback}

def _build_harness(code: str, test_cases: list[dict]) -> str:
    return (
        "import json\n"
        + code
        + "\n"
        + "results = []\n"
        + "for case in "
        + repr(test_cases)
        + ":\n    results.append(solve(case.get('input')))\n"
        + "print(json.dumps(results, default=str))\n"
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
    harness = _build_harness(code, test_cases)
    client = None
    container = None
    remove = True
    try:
        client = docker.from_env()
        container = client.containers.create(
            image=SANDBOX_IMAGE,
            command=["python", "-I", "-S", "-c", harness],
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
        return _result("", "Tiempo de ejecución agotado (5 segundos).", False, "El código superó el límite de tiempo.")
    except ImageNotFound:
        return _result("", f"La imagen {SANDBOX_IMAGE} no está disponible en el daemon Docker.", False, "El sandbox no está disponible.")
    except (ContainerError, APIError) as exc:
        return _result("", str(exc), False, "El sandbox no pudo ejecutar el código.")
    finally:
        if remove and container is not None:
            try:
                container.remove(force=True)
            except (APIError, NotFound):
                pass
        if client is not None:
            client.close()
    expected = [case.get("output") for case in test_cases]
    try:
        actual = json.loads(stdout.strip() or "null")
    except json.JSONDecodeError:
        actual = None
    passed = exit_code == 0 and actual == expected
    return _result(stdout, stderr, passed, "Todos los casos pasan." if passed else f"Casos superados: {sum(a == b for a, b in zip(actual or [], expected))}/{len(expected)}.")


def run_submission(code: str, language: str, test_cases_json: str = "[]") -> ExecutionResult:
    executed = execute_code(code, language, test_cases_json)
    test_cases = json.loads(test_cases_json or "[]")
    return ExecutionResult(executed["passed"], len(test_cases) if executed["passed"] else 0, len(test_cases), executed["feedback"])
