"""
Unit tests for the Progress model in app/models/progress.py.

This file ensures correct instantiation, updating, aggregation, and serialization
of user/module progress tracking records.
"""

import pytest

from app.models.progress import Progress, ProgressStatus

class TestProgressModel:

    def test_progress_creation(self):
        """Test creation of progress tracking for a user/objective."""
        progress = Progress(
            user_id="user1",
            objective_id="lesson42",
        )
        assert progress.user_id == "user1"
        assert progress.objective_id == "lesson42"
        assert progress.total_steps == 1, "Default total_steps should be 1"
        assert progress.completed_steps == 0, "Default completed_steps should be 0"
        assert progress.status == ProgressStatus.NOT_STARTED, "Default status should be NOT_STARTED"
        assert isinstance(progress.extra, dict), "extra should default to dict"

    def test_update_progress_status(self):
        """Test updating progress status calculations."""
        progress = Progress(user_id="u", objective_id="o", total_steps=5)
        # Initially not started
        assert progress.status == ProgressStatus.NOT_STARTED
        # Mark some steps as complete
        progress.update_status(completed_steps=3)
        assert progress.completed_steps == 3
        assert progress.status == ProgressStatus.IN_PROGRESS
        # Complete all steps
        progress.update_status(completed_steps=5)
        assert progress.completed_steps == 5
        assert progress.status == ProgressStatus.COMPLETED
        # Mark as failed by explicit override
        progress.update_status(status=ProgressStatus.FAILED)
        assert progress.status == ProgressStatus.FAILED

    def test_progress_aggregation(self):
        """Test aggregation/summary of multiple progress records."""
        p1 = Progress(user_id="u", objective_id="a", total_steps=2, completed_steps=2, status=ProgressStatus.COMPLETED)
        p2 = Progress(user_id="u", objective_id="b", total_steps=4, completed_steps=1, status=ProgressStatus.IN_PROGRESS)
        p3 = Progress(user_id="u", objective_id="c", total_steps=3, completed_steps=0, status=ProgressStatus.NOT_STARTED)

        agg = Progress.aggregate([p1, p2, p3])

        assert agg.user_id == "u"
        assert agg.objective_id == "aggregate"
        assert agg.total_steps == 9, "Sum of total steps"
        assert agg.completed_steps == 3
        # Not all completed, some in progress, so status=IN_PROGRESS
        assert agg.status == ProgressStatus.IN_PROGRESS

        # All completed
        all_completed = [Progress(user_id="u", objective_id=f"x{i}", total_steps=1, completed_steps=1, status=ProgressStatus.COMPLETED) for i in range(3)]
        agg2 = Progress.aggregate(all_completed)
        assert agg2.status == ProgressStatus.COMPLETED

        # All not started
        all_ns = [Progress(user_id="u", objective_id=f"x{i}", total_steps=2, completed_steps=0, status=ProgressStatus.NOT_STARTED) for i in range(4)]
        agg3 = Progress.aggregate(all_ns)
        assert agg3.status == ProgressStatus.NOT_STARTED

    def test_progress_serialization(self):
        """Test progress serialization/deserialization."""
        p = Progress(user_id="u42", objective_id="mod7", total_steps=4, completed_steps=2, status=ProgressStatus.IN_PROGRESS, extra={"score": 65})
        d = p.serialize()
        assert d == {
            "user_id": "u42",
            "objective_id": "mod7",
            "total_steps": 4,
            "completed_steps": 2,
            "status": "in_progress",
            "extra": {"score": 65}
        }
        # Test deserialization
        p2 = Progress.deserialize(d)
        assert p2.user_id == "u42"
        assert p2.objective_id == "mod7"
        assert p2.total_steps == 4
        assert p2.completed_steps == 2
        assert p2.status == ProgressStatus.IN_PROGRESS
        assert p2.extra == {"score": 65}
        # test roundtrip JSON
        json_str = p.to_json()
        p3 = Progress.from_json(json_str)
        assert p3.user_id == p.user_id
        assert p3.objective_id == p.objective_id
        assert p3.status == p.status
        assert p3.extra == p.extra
        assert p3.completed_steps == p.completed_steps
        assert p3.total_steps == p.total_steps
