import json

from app.services import code_runner


def test_execute_code_returns_each_case(monkeypatch):
    result = code_runner.execute_code("def solve(data):\n    return data", "python", json.dumps([
        {"input": 1, "output": 1},
        {"input": 2, "output": 2},
    ]))

    assert result["passed"] is True
    assert result["results"] == [
        {"input": 1, "expected": 1, "actual": 1, "passed": True},
        {"input": 2, "expected": 2, "actual": 2, "passed": True},
    ]


def test_execute_code_rejects_invalid_and_dangerous_code():
    invalid = code_runner.execute_code("def solve(:", "python", "[]")
    dangerous = code_runner.execute_code("import os\ndef solve(data):\n    return data", "python", "[]")

    assert invalid["passed"] is False
    assert "válidos" in invalid["feedback"]
    assert dangerous["passed"] is False
    assert "bloqueó" in dangerous["feedback"]


def test_execute_code_reports_failed_case():
    result = code_runner.execute_code("def solve(data):\n    return data + 1", "python", json.dumps([{"input": 1, "output": 3}]))

    assert result["passed"] is False
    assert result["results"][0]["actual"] == 2


def test_execute_code_stops_timeout():
    result = code_runner.execute_code("def solve(data):\n    while True:\n        pass", "python", json.dumps([{"input": 1, "output": 1}]))

    assert result["passed"] is False
    assert "agotado" in result["stderr"]


def test_execute_javascript_returns_each_case():
    result = code_runner.execute_code("function solve(data) { return data * 2; }", "javascript", json.dumps([
        {"input": 2, "output": 4},
        {"input": 3, "output": 6},
    ]))

    assert result["passed"] is True
    assert all(item["passed"] for item in result["results"])


def test_execute_javascript_reports_failure_and_syntax_error():
    failed = code_runner.execute_code("function solve(data) { return data + 1; }", "javascript", json.dumps([{"input": 1, "output": 3}]))
    invalid = code_runner.execute_code("function solve(data) {", "javascript", "[]")

    assert failed["passed"] is False
    assert failed["results"][0]["actual"] == 2
    assert invalid["passed"] is False
    assert invalid["stderr"]


def test_execute_javascript_rejects_dangerous_api():
    result = code_runner.execute_code("const fs = require('fs');\nfunction solve(data) { return data; }", "javascript", "[]")

    assert result["passed"] is False
    assert "bloqueada" in result["stderr"]