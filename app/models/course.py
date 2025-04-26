"""
Course model for AeroLearn AI.

Location: app/models/course.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Covers ORM integration, validation, serialization, and event emission.
"""

from app.core.db.schema import LearningPath as SALearningPath, PathModule, Module
from integrations.events.event_bus import EventBus
from integrations.events.event_types import ContentEvent, ContentEventType, EventPriority
import re

class CourseModel:
    def __init__(self, sa_path: SALearningPath):
        self.sa_path = sa_path

    @property
    def id(self):
        return self.sa_path.id

    @property
    def title(self):
        return self.sa_path.title

    @property
    def description(self):
        return self.sa_path.description

    @property
    def modules(self):
        # Ordered by PathModule.order
        ordered_pms = sorted(self.sa_path.path_modules, key=lambda pm: pm.order)
        return [
            {
                "module_id": pm.module.id,
                "title": pm.module.title,
                "order": pm.order,
            }
            for pm in ordered_pms if pm.module
        ]

    def serialize(self):
        """Serialize course and modules."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "modules": self.modules
        }

    def validate(self):
        """Ensure course has a title and at least one module."""
        if not self.title or not isinstance(self.title, str) or len(self.title) < 3:
            raise ValueError("Learning Path title must be at least 3 characters.")
        if len(self.sa_path.path_modules) == 0:
            raise ValueError("Learning Path must include at least one module.")
        return True

    async def on_created(self, source="course"):
        bus = EventBus()
        if hasattr(bus, "publish") and bus._is_running:
            event = ContentEvent(
                event_type=ContentEventType.CREATED,
                source_component=source,
                data={"path_id": self.id, "title": self.title},
                priority=EventPriority.NORMAL,
                is_persistent=True
            )
            await bus.publish(event)
