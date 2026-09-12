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