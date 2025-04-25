from abc import ABC, abstractmethod
from typing import Optional
from app.core.auth.user_profile import UserProfile

# Import event system
from integrations.events.event_bus import EventBus
from integrations.events.event_types import Event, EventCategory

class AuthEvent(Event):
    """
    Event representing authentication-related changes (login, logout, failure).
    """
    def __init__(self, event_type: str, user_profile: Optional[UserProfile], source_component: str, data: Optional[dict] = None):
        super().__init__(
            event_type=event_type,
            category=EventCategory.SYSTEM,
            source_component=source_component,
            data=data or {}
        )
        # Add user information to event data if available
        if user_profile:
            self.data["user_id"] = user_profile.user_id
            self.data["username"] = user_profile.username

class AuthenticationProvider(ABC):
    """
    Interface for authentication providers.
    """
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[UserProfile]:
        """
        Attempt to authenticate the user. Returns UserProfile if successful, else None.
        """
        pass

class LocalAuthenticationProvider(AuthenticationProvider):
    """
    Simple authentication provider with in-memory user verification and event emission.
    Replace with secure store/database integration as appropriate.
    """
    def __init__(self, user_db: dict, component_name: str = "auth.local"):
        self._user_db = user_db  # {username: {password: ..., ...other attributes...}}
        self._component_name = component_name
        self._event_bus = EventBus()

    def authenticate(self, username: str, password: str) -> Optional[UserProfile]:
        user = self._user_db.get(username)
        if user and user.get("password") == password:
            # Build user profile from user dict
            profile = UserProfile(
                user_id=user.get("user_id", username),
                username=username,
                full_name=user.get("full_name", ""),
                email=user.get("email", ""),
                roles=user.get("roles", []),
                extra=user.get("extra", {})
            )
            # Emit login success event
            try:
                import asyncio
                if self._event_bus._is_running:
                    asyncio.create_task(
                        self._event_bus.publish(
                            AuthEvent(
                                event_type="auth.login.success",
                                user_profile=profile,
                                source_component=self._component_name
                            )
                        )
                    )
            except Exception:
                pass  # If the event bus isn't started or event system unavailable, proceed silently
            return profile
        else:
            # Emit login failed event
            try:
                import asyncio
                if self._event_bus._is_running:
                    asyncio.create_task(
                        self._event_bus.publish(
                            AuthEvent(
                                event_type="auth.login.failed",
                                user_profile=None,
                                source_component=self._component_name,
                                data={"attempted_username": username}
                            )
                        )
                    )
            except Exception:
                pass
            return None
            
    def logout(self, user_profile: UserProfile):
        """
        Handle user logout and emit appropriate event.
        """
        # Emit logout event
        try:
            import asyncio
            if self._event_bus._is_running:
                asyncio.create_task(
                    self._event_bus.publish(
                        AuthEvent(
                            event_type="auth.logout",
                            user_profile=user_profile,
                            source_component=self._component_name
                        )
                    )
                )
        except Exception:
            pass
