# Assessment Delivery Workflow – AeroLearn AI

## Overview

This document describes the assessment session management, question rendering, answer validation, and timed control logic integrated in AeroLearn AI as of Day 17.

## Workflow Steps

1. **Session Creation**
   - Initiated by a student/user selecting an assessment/quiz.
   - An `AssessmentSession` is created by `AssessmentSessionManager`, associating user, quiz, and state.

2. **Question Rendering**
   - Questions delivered in order or adaptive sequence via `get_questions()`.
   - Each question complies with the content type (MCQ, text, code, essay, etc.).
   - UI or API service consumes question objects for rendering.

3. **Answer Collection**
   - User answers are submitted to the session (`submit_answer()`).
   - The system validates answer format (type, completeness).
   - Intermediate save/state is supported for in-progress sessions.

4. **Timed Controls**
   - Each assessment session may have a time limit.
   - `tick()` method or UI timer controls session completion upon expiry.
   - Late/timeout finalization transitions state for scoring.

5. **Session Finalization**
   - Submission or timeout marks session as completed (state update).
   - Answers are locked; no further modification allowed.

6. **Integration**
   - Session management logic integrates with grading engine, feedback system, and UI progress tracking.
   - Event bus used for session lifecycle and notification.

## Key Components

- `AssessmentSessionManager` (`app.core.assessment.session_manager`)
- `AssessmentSession` (`app.models.assessment`)
- Question/Quiz/Content models (`app.models.content`)
- UI widgets, API endpoints (varies)

## References

- Integration test: `/tests/integration/test_assessment_engine_day17.py`
- See class docstrings and comments in source for further details.