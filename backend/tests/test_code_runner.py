import json

from app.services import code_runner


class FakeContainer:
    def __init__(self, output):
        self.output = output

    def start(self):
        pass

    def wait(self, timeout):
        return {"StatusCode": 0}

    def logs(self, stdout, stderr):
        return self.output.encode() if stdout else b""

    def remove(self, force):
        pass


class FakeContainers:
    def __init__(self):
        self.outputs = iter(["1", "99"])

    def create(self, **kwargs):
        return FakeContainer(next(self.outputs))


class FakeClient:
    def __init__(self):
        self.containers = FakeContainers()

    def close(self):
        pass


def test_execute_code_returns_each_case(monkeypatch):
    monkeypatch.setattr(code_runner.docker, "from_env", lambda: FakeClient())

    result = code_runner.execute_code("def solve(data):\n    return data", "python", json.dumps([
        {"input": 1, "output": 1},
        {"input": 2, "output": 2},
    ]))

    assert result["passed"] is False
    assert result["results"] == [
        {"input": 1, "expected": 1, "actual": 1, "passed": True},
        {"input": 2, "expected": 2, "actual": 99, "passed": False},
    ]