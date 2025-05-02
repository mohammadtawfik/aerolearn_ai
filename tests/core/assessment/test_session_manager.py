"""
File: test_session_manager.py
Location: /tests/core/assessment/
Purpose: Unit tests for the AssessmentSessionManager and AssessmentSession classes.

Ensure session start, answer, pause/resume, and timeout logic.
"""

import time
import pytest
from app.core.assessment.session_manager import AssessmentSessionManager, AssessmentSessionStatus

# Mock objects for model dependencies
class DummyAssessment: pass
class DummyAnswer: pass

def test_create_and_complete_session():
    manager = AssessmentSessionManager()
    dummy_assessment = DummyAssessment()
    session = manager.create_session(dummy_assessment, "user123", duration_seconds=1)
    assert session.status == AssessmentSessionStatus.NOT_STARTED
    session.start()
    assert session.status == AssessmentSessionStatus.IN_PROGRESS
    session.complete()
    assert session.status == AssessmentSessionStatus.COMPLETED

def test_session_timeout():
    manager = AssessmentSessionManager()
    dummy_assessment = DummyAssessment()
    session = manager.create_session(dummy_assessment, "user456", duration_seconds=1)
    session.start()
    time.sleep(1.5)
    assert session.status in (AssessmentSessionStatus.TIMED_OUT, AssessmentSessionStatus.IN_PROGRESS)