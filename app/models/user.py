"""
User model for AeroLearn AI.

Location: app/models/user.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Implements validation, event integration, and serialization.
"""

from app.core.db.schema import User as SAUser, UserProfile
from integrations.events.event_bus import EventBus
from integrations.events.event_types import UserEvent, UserEventType, EventPriority
from datetime import datetime
import re

class UserModel:
    def __init__(self, sa_user: SAUser):
        self.sa_user = sa_user

    @property
    def id(self):
        return self.sa_user.id

    @property
    def username(self):
        return self.sa_user.username

    @property
    def email(self):
        return self.sa_user.email

    @property
    def is_active(self):
        return self.sa_user.is_active

    def serialize(self):
        """Convert user and profiles to dict representation for API use."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "profiles": [
                {
                    "id": profile.id,
                    "full_name": profile.full_name,
                    "bio": profile.bio,
                    "expertise_level": profile.expertise_level,
                }
                for profile in self.sa_user.profiles
            ]
        }

    def validate(self):
        """Basic validation for username and email."""
        if not self.username or not re.match(r"^[a-zA-Z0-9_\-]{3,30}$", self.username):
            raise ValueError("Invalid username. Must be 3+ characters, alphanumeric/underscore/hyphen.")
        if not self.email or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email address.")
        return True

    async def on_login(self, source="auth"):
        """Emit event on user login."""
        bus = EventBus()
        if hasattr(bus, "publish") and bus._is_running:
            event = UserEvent(
                event_type=UserEventType.LOGGED_IN,
                source_component=source,
                data={"user_id": self.id, "username": self.username},
                priority=EventPriority.NORMAL,
                is_persistent=True
            )
            await bus.publish(event)

    async def on_profile_update(self, source="profile"):
        """Emit event on user profile update."""
        bus = EventBus()
        if hasattr(bus, "publish") and bus._is_running:
            event = UserEvent(
                event_type=UserEventType.PROFILE_UPDATED,
                source_component=source,
                data={"user_id": self.id, "username": self.username},
                priority=EventPriority.NORMAL,
                is_persistent=False
            )
            await bus.publish(event)