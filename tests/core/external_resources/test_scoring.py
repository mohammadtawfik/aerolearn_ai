# File: /tests/core/external_resources/test_scoring.py

from app.core.external_resources.scoring import score_resource

class DummyCourse:
    def __init__(self, title):
        self.title = title

def test_score_resource():
    res = {"title": "Math for Kids", "description": ""}
    course = DummyCourse("Math")
    score = score_resource(res, course)
    assert isinstance(score, float)
    assert 0 <= score <= 1.2