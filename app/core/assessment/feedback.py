"""
File: feedback.py
Location: /app/core/assessment/
Purpose: Feedback delivery to students, notifications, analytics. Fulfills the feedback-related tasks in the Day 17 Plan.
- Adds FeedbackService as a system-level API expected by test and integration code.

All new assessment engine logic is placed under app/core/assessment/ per project conventions.
"""

from typing import Dict, List, Optional, Callable, Any
from app.models.assessment import Submission, Feedback  # Both should be present in assessment.py

class FeedbackEngine:
    def __init__(self):
        self.delivered_feedback: Dict[str, Feedback] = {}
        self.feedback_responses: Dict[str, bool] = {}

    def deliver_feedback(self, submission: Submission, feedback_text: str, personalized: bool = True) -> Feedback:
        student_id = submission.user_id
        feedback = Feedback(
            submission_id=submission.id,
            user_id=student_id,
            feedback_text=feedback_text,
            personalized=personalized
        )
        self.delivered_feedback[submission.id] = feedback
        self._notify(student_id, feedback)
        return feedback

    def _notify(self, user_id: str, feedback: Feedback):
        # Placeholder. Would interface with notification_center or similar system.
        print(f"Notification sent to user {user_id}: {feedback.feedback_text}")

    def track_response(self, submission_id: str, responded: bool):
        self.feedback_responses[submission_id] = responded

    def feedback_effectiveness(self, user_id: str) -> float:
        """
        Calculate feedback effectiveness as the ratio of responded/total feedback for user.
        """
        user_feedback = [fid for fid, fb in self.delivered_feedback.items() if fb.user_id == user_id]
        if not user_feedback:
            return 0.0
        responded = [fid for fid in user_feedback if self.feedback_responses.get(fid)]
        return len(responded) / len(user_feedback)
        
    # Additional helper methods for history, notifications, and analytics
    def feedback_history(self, user_id: str) -> List[Feedback]:
        """Return all feedback items for a specific user."""
        return [fb for fb in self.delivered_feedback.values() if fb.user_id == user_id]

    def notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Return notification-formatted feedback for a user."""
        return [
            {"message": fb.feedback_text, "submission_id": fb.submission_id, "created_at": getattr(fb, "created_at", None)}
            for fb in self.delivered_feedback.values()
            if fb.user_id == user_id
        ]

    def analytics(self, user_id: str) -> Dict[str, Any]:
        """Return analytics data for a user's feedback."""
        delivered = len([fb for fb in self.delivered_feedback.values() if fb.user_id == user_id])
        effectiveness = self.feedback_effectiveness(user_id)
        return {
            "delivered": delivered,
            "effectiveness": effectiveness
        }

class FeedbackService:
    """
    Service façade for feedback delivery, notification, and analytics,
    coordinating internal FeedbackEngine and providing a stable API for integration and tests.
    """

    _engine = FeedbackEngine()

    @classmethod
    def send_feedback(cls, user: Any, assessment_session: Any, feedback: str, grade: float = None) -> bool:
        """
        Delivers feedback for a user's submission/session. Returns True if sent.
        """
        # Assume session has an attached submission, or create one.
        submission = getattr(assessment_session, "submission", None)
        if submission is None:
            # Simulate: compose a submission from session data.
            submission = Submission(
                id=f"session-{getattr(assessment_session, 'id', 'UNKNOWN')}",
                user_id=getattr(user, "id", user) if hasattr(user, "id") else user,
                assessment_id=getattr(assessment_session, "id", "UNKNOWN"),
                answers={},  # Fill as appropriate
            )
        fb_obj = cls._engine.deliver_feedback(submission, feedback_text=feedback, personalized=True)
        # Additional steps: Store grade, log the event, etc. could be added here
        return fb_obj is not None

    @classmethod
    def get_feedback_history(cls, user: Any) -> List[Dict[str, Any]]:
        """
        Return feedback items delivered to the user,
        each with a session_id key if possible (for test compatibility).
        """
        user_id = getattr(user, "id", user)
        history = []
        for fb in cls._engine.feedback_history(user_id=user_id):
            d = vars(fb).copy()
            # Add session_id for integration test compatibility
            # Try to extract from submission_id, fallback to UNKNOWN
            session_id = None
            if hasattr(fb, 'submission_id') and isinstance(fb.submission_id, str):
                if fb.submission_id.startswith("session-"):
                    session_id = fb.submission_id[8:]
                else:
                    session_id = fb.submission_id
            d['session_id'] = session_id if session_id else d.get('session_id', None)
            history.append(d)
        return history

    @classmethod
    def get_notifications(cls, user: Any) -> List[Dict[str, Any]]:
        """
        Return recent feedback-related notifications for a user.
        """
        user_id = getattr(user, "id", user)
        return cls._engine.notifications(user_id=user_id)

    @classmethod
    def get_analytics(cls, user: Any) -> Dict[str, Any]:
        """
        Return analytics on feedback for a user.
        """
        user_id = getattr(user, "id", user)
        return cls._engine.analytics(user_id=user_id)
