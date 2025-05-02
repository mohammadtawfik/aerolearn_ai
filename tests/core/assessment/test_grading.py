"""
File: test_grading.py
Location: /tests/core/assessment/
Purpose: Unit tests for the GradingEngine: MCQ, text, code, partial credit.

"""

from app.core.assessment.grading import GradingEngine

class DummyQuestion:
    def __init__(self, qtype, correct_option=None, correct_answer=None):
        self.type = qtype
        self.correct_option = correct_option
        self.correct_answer = correct_answer

class DummyAnswer:
    def __init__(self, selected_option=None, text_response=None, code=None, response_flags=None):
        self.selected_option = selected_option
        self.text_response = text_response
        self.code = code
        self.response_flags = response_flags

def test_grade_mcq():
    ge = GradingEngine()
    q = DummyQuestion("MULTIPLE_CHOICE", correct_option="a")
    a = DummyAnswer(selected_option="a")
    assert ge.grade(q, a) == 1.0
    a2 = DummyAnswer(selected_option="b")
    assert ge.grade(q, a2) == 0.0

def test_grade_text():
    ge = GradingEngine()
    q = DummyQuestion("TEXT", correct_answer="Four")
    a = DummyAnswer(text_response="four")
    assert ge.grade(q, a) == 1.0
    a2 = DummyAnswer(text_response="five")
    assert ge.grade(q, a2) == 0.0

def test_grade_code():
    ge = GradingEngine()
    q = DummyQuestion("CODE")
    a = DummyAnswer(code="print('Hello')")
    # By default returns 1.0 (simulate full credit)
    assert ge.grade(q, a) == 1.0

def test_grade_partial_credit():
    ge = GradingEngine()
    q = DummyQuestion("ESSAY")
    a = DummyAnswer(response_flags=["criterion1", "criterion2"])
    rubric = {"criterion1": 2, "criterion2": 3, "criterion3": 5}
    score = ge.grade_partial_credit(q, a, rubric)
    assert 0 < score < 1