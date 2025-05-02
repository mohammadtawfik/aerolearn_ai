"""
Integration Tests – Assessment Engine (AeroLearn AI Day 17 Integration)

This file must be saved at: /tests/integration/test_assessment_engine_day17.py

Covers:
  - Assessment session management and delivery integration
  - Auto-grading multi-type questions (MCQ, text NLP, code)
  - Manual grading (rubrics, feedback)
  - Feedback notification and analytics

Assumes all core and model implementations are complete.
"""

import pytest

from app.core.assessment.session_manager import AssessmentSessionManager
from app.core.assessment.grading import GradingEngine
from app.core.assessment.manual_grading import ManualGradingService
from app.core.assessment.feedback import FeedbackService
from app.models.assessment import (
    Assessment, AssessmentSession, QuestionType, Answer, Rubric, ManualGradingAssignment
)
from app.models.user import User
from app.models.content import Quiz, Lesson, Module, Topic
from app.models.course import Course
# Add other necessary imports for in-memory/test db setup, event bus, etc.


@pytest.fixture
def test_user():
    return User(id=1, username="student1", email="student1@example.com", role="student")


@pytest.fixture
def test_professor():
    return User(id=2, username="professorx", email="profx@example.com", role="professor")


@pytest.fixture
def quiz_mixed_types():
    # Make a quiz with all question types
    return Quiz(
        title="Integration Quiz",
        questions=[
            # Auto-graded MCQ
            QuestionType.mcq(question="2+2=?", options=["3", "4", "5"], answer="4"),
            # Auto-graded text/NLP
            QuestionType.text(question="State Newton's second law", expected_keywords=["force", "mass", "acceleration"]),
            # Auto-graded code
            QuestionType.code(
                question="Write a function to add two numbers.",
                solution_code="def add(a, b): return a + b",
                test_cases=[{"input": [2, 2], "output": 4}]
            ),
            # Manual-graded essay
            QuestionType.essay(question="Explain the significance of Bernoulli’s principle.", rubric_id=1),
        ]
    )


@pytest.fixture
def assessment_session(test_user, quiz_mixed_types):
    # Create an open session
    return AssessmentSessionManager().start_session(user=test_user, quiz=quiz_mixed_types)


def test_assessment_session_lifecycle(assessment_session):
    # Test session start
    assert assessment_session.is_active
    # Simulate answer/timeout/finalize logic
    for q in assessment_session.quiz.questions:
        if hasattr(q, "answer"):
            assessment_session.submit_answer(q, q.answer or "irrelevant")
        else:
            assessment_session.submit_answer(q, "force = mass * acceleration")
    assessment_session.finalize()
    assert assessment_session.is_completed


def test_question_rendering_and_answer_validation(assessment_session):
    # Render questions via service (simulate UI)
    questions = assessment_session.get_questions()
    assert len(questions) == 4
    # Submit valid and invalid answers, check validation
    valid_mcq = questions[0]
    invalid_mcq = "wrong"
    assert assessment_session.validate_answer(valid_mcq, "4") is True
    assert assessment_session.validate_answer(valid_mcq, invalid_mcq) is False


def test_timed_assessment_controls(monkeypatch, assessment_session):
    # Simulate timer expiry and forced submission
    monkeypatch.setattr(assessment_session, "is_time_expired", lambda: True)
    assessment_session.tick()
    assert assessment_session.is_completed
    assert assessment_session.time_expired


def test_autograding_flow(assessment_session):
    # Submit answers to autograded questions
    answers = [
        Answer(question=assessment_session.quiz.questions[0], response="4"),  # MCQ
        Answer(question=assessment_session.quiz.questions[1], response="Force equals mass times acceleration"),  # Text
        Answer(question=assessment_session.quiz.questions[2], response="def add(a, b): return a + b"),  # Code
    ]
    # Assume answers list matches question order
    for a in answers:
        assessment_session.submit_answer(a.question, a.response)
    assessment_session.finalize()
    scores = GradingEngine.grade_session(assessment_session)
    # Assert full or partial credit as per grading system
    assert scores["total"] >= 2.5  # at least passing
    assert all(qid in scores["breakdown"] for qid in range(3))


def test_partial_credit_and_mixed_types(assessment_session):
    # Miss some answers/submit partials
    assessment_session.submit_answer(
        assessment_session.quiz.questions[0], "3"
    )  # wrong MCQ
    assessment_session.submit_answer(
        assessment_session.quiz.questions[1], "force only"
    )  # missing keywords
    assessment_session.submit_answer(
        assessment_session.quiz.questions[2], "def add(a, b): return a-b"
    )  # wrong code
    assessment_session.finalize()
    scores = GradingEngine.grade_session(assessment_session)
    # Should have partial/zero credit
    assert 0 < scores["total"] < 3
    assert scores["breakdown"][0] == 0  # MCQ fail
    assert scores["breakdown"][1] >= 0.3  # Text partial
    assert scores["breakdown"][2] < 1  # Code fail


def test_manual_grading_assignment_and_feedback(test_user, test_professor, assessment_session):
    # Assume session had an essay/manual question (question 3)
    essay_q = assessment_session.quiz.questions[3]
    assessment_session.submit_answer(essay_q, "It lowers pressure in a flow.")
    assessment_session.finalize()
    # Assign to professor for manual grading
    assignment = ManualGradingAssignment(
        assessor=test_professor, session=assessment_session, rubric_id=1
    )
    ManualGradingService.assign(assignment)
    # Professor grades
    grade, feedback = ManualGradingService.grade(
        assignment, answer="It lowers...", rubric=Rubric.by_id(1)
    )
    assert grade > 0
    assert isinstance(feedback, str) and len(feedback) > 0
    # Feedback delivery
    sent = FeedbackService.send_feedback(
        user=test_user, assessment_session=assessment_session, feedback=feedback, grade=grade
    )
    assert sent is True
    # Feedback is retrievable for analytics tracking
    history = FeedbackService.get_feedback_history(user=test_user)
    assert any(fb["session_id"] == assessment_session.id for fb in history)


def test_feedback_notification_and_analytics(test_user, assessment_session):
    # Simulate feedback given
    feedback = "Well done, remember: F=ma!"
    FeedbackService.send_feedback(
        user=test_user, assessment_session=assessment_session, feedback=feedback, grade=1.0
    )
    # Student interface receives notification (mocked)
    notifications = FeedbackService.get_notifications(user=test_user)
    assert any(feedback in n["message"] for n in notifications)

    # Analytics: confirm feedback is logged for effectiveness stats
    stats = FeedbackService.get_analytics(user=test_user)
    assert stats["delivered"] > 0
    assert "effectiveness" in stats


def test_cross_module_assessment_integration(test_user):
    # Create assessment pulling from several modules
    quiz = Quiz(
        title="Final Exam",
        questions=[
            # From multiple source modules
            QuestionType.mcq(question="Module1: Capital of France?", options=["Paris", "Rome"], answer="Paris"),
            QuestionType.text(question="Module2: Define entropy", expected_keywords=["disorder", "thermodynamics"]),
        ]
    )
    session = AssessmentSessionManager().start_session(user=test_user, quiz=quiz)
    session.submit_answer(quiz.questions[0], "Paris")
    session.submit_answer(quiz.questions[1], "Measure of disorder in thermodynamics")
    session.finalize()
    result = GradingEngine.grade_session(session)
    assert result["total"] == pytest.approx(2.0)


def test_full_pipeline_student_progress_updates(test_user):
    # Simulate entire pipeline: attempt, grade, feedback, progress update
    quiz = Quiz(
        title="Pipeline Test",
        questions=[
            QuestionType.mcq(question="Earth's shape?", options=["Flat", "Sphere"], answer="Sphere")
        ]
    )
    session = AssessmentSessionManager().start_session(user=test_user, quiz=quiz)
    session.submit_answer(quiz.questions[0], "Sphere")
    session.finalize()
    GradingEngine.grade_session(session)
    FeedbackService.send_feedback(user=test_user, assessment_session=session, feedback="Correct!", grade=1.0)
    progress = test_user.get_progress()
    assert progress["assessments_completed"] >= 1
    assert progress["last_grade"] == 1.0
