"""
File: test_question_engine.py
Location: /tests/core/assessment/
Purpose: Unit tests for the QuestionEngine (rendering and answer validation).

"""

from app.core.assessment.question_engine import QuestionEngine

class DummyQuestion:
    def __init__(self):
        self.id = "q1"
        self.prompt = "What is 2 + 2?"
        self.type = "MULTIPLE_CHOICE"
        self.choices = ["3", "4", "5"]
        self.metadata = {}
        self.correct_option = "4"

class DummyAnswer:
    def __init__(self, selected_option="4", text_response=None, code=None):
        self.selected_option = selected_option
        self.text_response = text_response
        self.code = code

def test_render_question():
    qe = QuestionEngine()
    q = DummyQuestion()
    output = qe.render(q)
    assert 'prompt' in output
    assert output['type'] == "MULTIPLE_CHOICE"

def test_validate_answer_mcq():
    qe = QuestionEngine()
    q = DummyQuestion()
    a = DummyAnswer(selected_option="4")
    assert qe.validate_answer(q, a) is True
    a2 = DummyAnswer(selected_option="42")
    assert qe.validate_answer(q, a2) is False