"""
app/models/progress.py
======================

Data models for student progress tracking across modules, lessons, quizzes, with standardized metrics.

Location: app/models/progress.py
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
import json

class ProgressStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Progress:
    """
    Core progress tracking model with status and step tracking.
    Enables analytics and reporting on student progress.
    """
    def __init__(
        self,
        user_id: str,
        objective_id: str,
        total_steps: int = 1,
        completed_steps: int = 0,
        status: Union[ProgressStatus, str] = ProgressStatus.NOT_STARTED,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.objective_id = objective_id
        self.total_steps = total_steps
        self.completed_steps = completed_steps
        if isinstance(status, str):
            self.status = ProgressStatus(status)
        else:
            self.status = status
        self.extra = extra or {}

    def update_status(self, completed_steps: Optional[int] = None, status: Optional[Union[ProgressStatus, str]] = None):
        """Update completed steps and optionally status"""
        if completed_steps is not None:
            self.completed_steps = completed_steps
        if status is not None:
            if isinstance(status, str):
                self.status = ProgressStatus(status)
            else:
                self.status = status
        else:
            # Auto-calculate status if not explicitly given
            if self.completed_steps >= self.total_steps:
                self.status = ProgressStatus.COMPLETED
            elif self.completed_steps > 0:
                self.status = ProgressStatus.IN_PROGRESS
            else:
                self.status = ProgressStatus.NOT_STARTED

    @property
    def percent_complete(self) -> float:
        """Calculate percentage of completion based on steps"""
        return min(100.0, (self.completed_steps / self.total_steps) * 100.0) if self.total_steps else 0.0

    @classmethod
    def aggregate(cls, progresses: List["Progress"]) -> "Progress":
        """
        Aggregates multiple Progress objects for a user or module.
        - total_steps: sum across all objectives
        - completed_steps: sum across all objectives
        - status: COMPLETED if all are completed, otherwise IN_PROGRESS or NOT_STARTED
        """
        if not progresses:
            raise ValueError("No progress records provided for aggregation")
        user_id = progresses[0].user_id  # Assumes same user (could be module-level otherwise)
        objective_id = "aggregate"
        total_steps_sum = sum(p.total_steps for p in progresses)
        completed_steps_sum = sum(p.completed_steps for p in progresses)
        if all(p.status == ProgressStatus.COMPLETED for p in progresses):
            agg_status = ProgressStatus.COMPLETED
        elif any(p.completed_steps > 0 for p in progresses):
            agg_status = ProgressStatus.IN_PROGRESS
        else:
            agg_status = ProgressStatus.NOT_STARTED
        return cls(
            user_id=user_id,
            objective_id=objective_id,
            total_steps=total_steps_sum,
            completed_steps=completed_steps_sum,
            status=agg_status
        )

    def serialize(self) -> Dict[str, Any]:
        """Convert to dictionary for storage or API responses"""
        return {
            "user_id": self.user_id,
            "objective_id": self.objective_id,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "status": self.status.value,
            "extra": self.extra
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "Progress":
        """Construct a Progress object from dictionary data"""
        return cls(
            user_id=data["user_id"],
            objective_id=data["objective_id"],
            total_steps=data.get("total_steps", 1),
            completed_steps=data.get("completed_steps", 0),
            status=data.get("status", ProgressStatus.NOT_STARTED),
            extra=data.get("extra", {})
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.serialize())

    @classmethod
    def from_json(cls, json_str: str) -> "Progress":
        """Create Progress object from JSON string"""
        data = json.loads(json_str)
        return cls.deserialize(data)
