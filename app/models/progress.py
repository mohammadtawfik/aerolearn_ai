"""
app/models/progress.py
======================

Data models for student progress tracking across modules, lessons, quizzes, with standardized metrics.

Location: app/models/progress.py
"""

from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class ProgressMetricType(Enum):
    COMPLETION_PERCENTAGE = "completion_percentage"
    TIME_SPENT = "time_spent"
    GRADE = "grade"
    ATTEMPTS = "attempts"

class ProgressEntry:
    """
    Represents progress data for a specific metric and time-point.
    """
    def __init__(self, metric: ProgressMetricType, value: float, timestamp: Optional[datetime] = None):
        self.metric = metric
        self.value = value
        self.timestamp = timestamp or datetime.now()

    def serialize(self):
        return {
            "metric": self.metric.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
        }

class ProgressTimeline:
    """
    Time-series progress for a specific user/content.
    """
    def __init__(self, user_id: str, content_id: str):
        self.user_id = user_id
        self.content_id = content_id
        self.entries: List[ProgressEntry] = []

    def add_entry(self, entry: ProgressEntry):
        self.entries.append(entry)

    def get_metric_over_time(self, metric: ProgressMetricType) -> List[ProgressEntry]:
        return [e for e in self.entries if e.metric == metric]

    def serialize(self):
        return {
            "user_id": self.user_id,
            "content_id": self.content_id,
            "entries": [e.serialize() for e in self.entries],
        }

class ComparativeProgress:
    """
    Supports comparison of progress metrics between users or groups.
    """
    def __init__(self, metric: ProgressMetricType):
        self.metric = metric
        self.values: Dict[str, float] = {}  # user_id/group_id -> value

    def set_value(self, entity_id: str, value: float):
        self.values[entity_id] = value

    def serialize(self):
        return {
            "metric": self.metric.value,
            "values": self.values,
        }