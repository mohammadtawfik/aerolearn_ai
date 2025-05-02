# Feedback Format Specifications – AeroLearn AI

## Overview

Defines structure, delivery, notification, and analytics of assessment feedback (auto/manual) for students.

## Format

- **Recipient(s):** User(s) receiving feedback
- **Assessment Session Reference:** Unique session ID, assessment/quiz title
- **Grade:** Numeric score (fraction, e.g., 0.83, 1.0, etc.)
- **Feedback Message:** String, can be generated (auto) or written (manual)

## Workflow

1. **Creation**
    - Auto-generated from grading flow or input by grader in manual flow.
2. **Delivery**
    - Delivered via `FeedbackService.send_feedback()`
    - Entry made in user's feedback history (UI/APIs)
    - Notifications generated if enabled
3. **Tracking**
    - All feedback persists with session/user
    - Analytics available on delivery, response rates, end effectiveness

## Sample JSON (internal API)

```json
{
  "user_id": 42,
  "session_id": "session_789",
  "assessment_title": "Integration Quiz",
  "grade": 0.83,
  "feedback": "Good explanation, but remember to mention 'mass'."
}
```

## APIs

- `FeedbackService` (`app.core.assessment.feedback`)
- Feedback history: user dashboard, analytics

## References

- `/app/core/assessment/feedback.py`
- Integration test: `/tests/integration/test_assessment_engine_day17.py`