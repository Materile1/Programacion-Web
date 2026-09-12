from types import SimpleNamespace

from app.models import InterviewQuestion, InterviewSession
from app.routers.interview import answer
from app.schemas import InterviewAnswerRequest
from app.services import content_curator


class InterviewDb:
    def __init__(self, session, question):
        self.session = session
        self.question = question
        self.scalar_calls = 0
        self.saved = None

    def scalar(self, query):
        self.scalar_calls += 1
        return self.session if self.scalar_calls == 1 else None

    def get(self, model, identifier):
        return self.question if identifier == self.question.id else None

    def add(self, value):
        self.saved = value

    def commit(self):
        pass


def test_conceptual_interview_answer_is_scored():
    session = InterviewSession(id=10, user_id=3)
    question = InterviewQuestion(id=4, kind="conceptual", prompt="", expected_points='["atomicidad", "rollback"]')
    result = answer(10, InterviewAnswerRequest(question_id=4, answer="Explico atomicidad y rollback"), InterviewDb(session, question), SimpleNamespace(id=3))
    assert result.score == 100


def test_malformed_curated_json_is_discarded(monkeypatch):
    monkeypatch.setattr(content_curator, "fetch_news", lambda limit: [SimpleNamespace(title="WebAssembly")])
    monkeypatch.setattr(content_curator, "get_settings", lambda: SimpleNamespace(openai_api_key="configured", gemini_api_key=None))
    monkeypatch.setattr(content_curator, "_ask_openai", lambda key, prompt: "not-json")
    content, topics, detail = content_curator.curate_review(object())
    assert content is None
    assert topics == ["WebAssembly"]
    assert "validación" in detail
