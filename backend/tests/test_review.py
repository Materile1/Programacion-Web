import json

from app.models import ReviewSnippet
from app.routers.review import submit_review
from app.schemas import ReviewSubmitRequest


class FakeDb:
    def __init__(self, snippet):
        self.snippet = snippet

    def get(self, model, identifier):
        return self.snippet if identifier == self.snippet.id else None


def test_review_submission_reports_detected_and_missed_issues():
    snippet = ReviewSnippet(id=1, title="Test", code="", known_issues=json.dumps(["bug de límite", "falta validación"]))

    result = submit_review(1, ReviewSubmitRequest(review="Veo un bug de límite"), FakeDb(snippet), object())

    assert result.detected == ["bug de límite"]
    assert result.missed == ["falta validación"]
    assert result.score == 50