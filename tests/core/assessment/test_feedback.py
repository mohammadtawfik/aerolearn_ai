"""
File: test_feedback.py
Location: /tests/core/assessment/
Purpose: Unit tests for FeedbackEngine: feedback delivery, notification, response tracking, analytics.

"""

from app.core.assessment.feedback import FeedbackEngine

class DummySubmission:
    def __init__(self):
        self.id = "subm1"
        self.user_id = "user1"

class DummyFeedback:
    def __init__(self, submission_id, user_id, feedback_text, personalized=True):
        self.submission_id = submission_id
        self.user_id = user_id
        self.feedback_text = feedback_text
        self.personalized = personalized

def test_deliver_feedback(monkeypatch):
    fe = FeedbackEngine()
    submission = DummySubmission()
    # Patch _notify to a silent/non-printing version
    monkeypatch.setattr(fe, '_notify', lambda user_id, feedback: None)
    feedback = fe.deliver_feedback(submission, "Well done", personalized=True)
    assert feedback.feedback_text == "Well done"
    assert feedback.personalized is True

def test_feedback_response_tracking_and_analytics():
    fe = FeedbackEngine()
    s = DummySubmission()
    feedback_obj = fe.deliver_feedback(s, "Nice work")
    fe.track_response(s.id, responded=True)
    effectiveness = fe.feedback_effectiveness(s.user_id)
    assert effectiveness == 1.0