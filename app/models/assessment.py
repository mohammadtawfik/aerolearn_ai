"""
Assessment model for AeroLearn AI.

Location: app/models/assessment.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Wraps ProgressRecord and assessment-related logic; provides validation, serialization, and event integration.
"""

from app.core.db.schema import ProgressRecord
from integrations.events.event_bus import EventBus
from integrations.events.event_types import UserEvent, UserEventType, EventPriority
from datetime import datetime

class AssessmentModel:
    def __init__(self, sa_record: ProgressRecord):
        self.sa_record = sa_record

    @property
    def id(self):
        return self.sa_record.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.sa_record.user_id,
            "module_id": self.sa_record.module_id,
            "lesson_id": self.sa_record.lesson_id,
            "completed": self.sa_record.completed,
            "score": self.sa_record.score,
            "completed_date": (self.sa_record.completed_date.isoformat() if self.sa_record.completed_date else None)
        }

    def validate(self):
        if not self.sa_record.user_id:
            raise ValueError("Assessment record must reference a user.")
        if not self.sa_record.module_id:
            raise ValueError("Assessment record must reference a module.")
        if self.sa_record.score is not None and (self.sa_record.score < 0 or self.sa_record.score > 100):
            raise ValueError("Score must be between 0 and 100.")

    async def on_progress_updated(self, source="assessment"):
        bus = EventBus()
        if hasattr(bus, "publish") and bus._is_running:
            event = UserEvent(
                event_type=UserEventType.PROGRESS_UPDATED,
                source_component=source,
                data={
                    "user_id": self.sa_record.user_id,
                    "module_id": self.sa_record.module_id,
                    "lesson_id": self.sa_record.lesson_id,
                    "completed": self.sa_record.completed,
                    "score": self.sa_record.score,
                    "completed_date": (self.sa_record.completed_date.isoformat() if self.sa_record.completed_date else None)
                },
                priority=EventPriority.NORMAL,
                is_persistent=False
            )
            await bus.publish(event)