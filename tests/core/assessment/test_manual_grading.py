"""
File: test_manual_grading.py
Location: /tests/core/assessment/
Purpose: Unit tests for ManualGradingInterface: rubric application, annotation, batch grading.
Fixes assertion to match 'percent' as float (not callable).

"""

from app.core.assessment.manual_grading import ManualGradingInterface

class DummyRubric:
    def __init__(self):
        self.criteria = {
            "criterion1": {"score": 3, "comment": "Well done"},
            "criterion2": {"score": 2, "comment": "Good"}
        }

class DummyAnswer:
    def __init__(self):
        self.annotations = []

class DummySubmission:
    def __init__(self):
        self.id = "s1"
        self.user_id = "u1"
        self.answers = {"q1": DummyAnswer()}
        self.attachments = []
        self.timestamp = "2024-06-18"

def test_apply_rubric():
    mg = ManualGradingInterface()
    answer = DummyAnswer()
    rubric = DummyRubric()
    grade = mg.apply_rubric(answer, rubric)
    assert isinstance(grade.percent, float)
    assert grade.percent == 1.0  # 5/5 in this dummy scenario
    assert grade.max_score == 5

def test_annotate():
    mg = ManualGradingInterface()
    answer = DummyAnswer()
    mg.annotate(answer, "Excellent work")
    assert "Excellent work" in answer.annotations

def test_batch_grade():
    mg = ManualGradingInterface()
    submissions = [DummySubmission()]
    rubric = DummyRubric()
    grades = mg.batch_grade(submissions, rubric)
    assert isinstance(grades, list)
    assert len(grades) > 0
