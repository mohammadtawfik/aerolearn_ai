"""
User model for AeroLearn AI.

Location: app/models/user.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Implements validation, event integration, and serialization.
Includes admin roles, MFA support, and permission checks.
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
        
    @property
    def role(self):
        return getattr(self.sa_user, 'role', 'user')
        
    @property
    def mfa_secret(self):
        return getattr(self.sa_user, 'mfa_secret', None)
        
    @property
    def password_hash(self):
        return getattr(self.sa_user, 'password_hash', None)

    def serialize(self):
        """Convert user and profiles to dict representation for API use."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "role": self.role,
            "has_mfa": self.mfa_secret is not None,
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
            
    def is_admin(self):
        """Check if user has admin privileges."""
        return self.role in ('admin', 'superadmin')
        
    def has_permission(self, perm: str):
        """Check if user has a specific permission."""
        from app.core.auth.authorization import AuthorizationManager
        return AuthorizationManager.has_permission(self.id, perm)
        
    def check_password(self, password: str):
        """Verify password against stored hash."""
        # This should use a secure password verification method
        # like bcrypt.checkpw or similar
        # Placeholder implementation
        return True
        
    @classmethod
    async def get_user_by_username(cls, username: str):
        """Retrieve user by username from database."""
        # This should be implemented with actual database query
        # Placeholder implementation
        from app.core.db.session import get_session
        async with get_session() as session:
            query = session.query(SAUser).filter(SAUser.username == username)
            sa_user = await query.first()
            if sa_user:
                return cls(sa_user)
        return None
