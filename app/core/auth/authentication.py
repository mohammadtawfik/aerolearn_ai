import time
import uuid
import hashlib
from typing import Optional, Dict, Any

from .user_profile import UserProfile
from .credential_manager import CredentialManager
from .session import SessionManager, Session
from .authorization import Permission, Role, AuthorizationManager
from app.models.user import UserModel


from abc import ABC, abstractmethod
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


class MFAProvider:
    """Simple TOTP-like provider for MFA codes — placeholder, extend for hardware, SMS/email."""
    def __init__(self, secret:str):
        self.secret = secret

    def generate_code(self, timestamp=None) -> str:
        timestamp = timestamp or int(time.time())
        data = f"{self.secret}:{timestamp // 30}"  # 30-second window
        return hashlib.sha256(data.encode()).hexdigest()[:6]  # Simple 6-char code

    def verify_code(self, code:str, window=1) -> bool:
        now = int(time.time())
        for w in range(-window, window+1):
            expected = self.generate_code(now + (w*30))
            if expected == code:
                return True
        return False

class AdminAuthService:
    def __init__(self, user_model_cls=UserModel, cred_manager=None, session_manager=None, default_password="test_pw"):
        self.user_model_cls = user_model_cls
        # The "default_password" is suitable for dev/test; production should inject their own CredentialManager!
        self.cred_manager = cred_manager or CredentialManager(password=default_password)
        self.session_manager = session_manager or SessionManager()
        self.activity_log = []

    def authenticate_admin(self, username:str, password:str, mfa_code:str) -> Optional[Session]:
        # Support both async and sync user querying for testing
        import inspect
        user_obj = None
        user_getter = getattr(self.user_model_cls, "get_user_by_username", None)
        if not user_getter:
            raise Exception("User model missing get_user_by_username")
        if inspect.iscoroutinefunction(user_getter):
            import asyncio
            user_obj = asyncio.run(user_getter(username))
        else:
            user_obj = user_getter(username)
        if not user_obj or not user_obj.is_admin():
            self.log_activity('auth-fail', getattr(user_obj, "id", None), 'Not admin or user missing')
            return None
        if not self.cred_manager.verify_password(user_obj.id, password):
            self.log_activity('auth-fail', user_obj.id, 'Incorrect password')
            return None
        # MFA check (user_obj.mfa_secret must exist)
        mfa = MFAProvider(user_obj.mfa_secret)
        if not mfa.verify_code(mfa_code):
            self.log_activity('auth-fail', user_obj.id, 'MFA code incorrect')
            return None
        # Build UserProfile and pass to SessionManager
        profile = UserProfile(
            user_id=user_obj.id,
            username=getattr(user_obj, 'username', None),
            full_name=getattr(user_obj, 'full_name', ""),
            email=getattr(user_obj, 'email', ""),
            roles=getattr(user_obj, 'roles', [user_obj.role]) if hasattr(user_obj, 'role') else [],
            extra={
                "bio": getattr(user_obj, 'bio', ""),
                "expertise_level": getattr(user_obj, 'expertise_level', None)
            }
        )
        
        session_id = self.session_manager.create_session(profile)
        session = self.session_manager.get_session(session_id)
        self.log_activity('auth-success', user_obj.id, 'Admin login')
        return session

    def log_activity(self, event:str, user_id:str, detail:str):
        self.activity_log.append({
            "timestamp": time.time(),
            "event": event,
            "user_id": user_id,
            "detail": detail
        })
        # Extend: push to persistent storage or logging service

    def enforce_permission(self, session:Session, permission:str) -> bool:
        # The session must now have profile, not user_id!
        return AuthorizationManager.has_permission(session.profile.user_id, permission)

    def get_activity_log(self, filter_user=None):
        if filter_user:
            return [l for l in self.activity_log if l['user_id']==filter_user]
        return self.activity_log


# Extend/introduce these roles and permissions for admin if not present
class AdminRoles:
    ADMIN = 'admin'
    SUPERADMIN = 'superadmin'

class AdminPermissions:
    DASHBOARD_VIEW = 'admin_dashboard:view'
    USER_MANAGEMENT = 'admin:user_manage'
    COURSE_MANAGEMENT = 'admin:course_manage'
    SYSTEM_MONITOR = 'admin:system_monitor'
    SECURITY_CONFIG = 'admin:security_config'

# Tie into AuthorizationManager (sample registration pattern)
AuthorizationManager.register_role(AdminRoles.ADMIN, [
    AdminPermissions.DASHBOARD_VIEW,
    AdminPermissions.USER_MANAGEMENT,
    AdminPermissions.COURSE_MANAGEMENT,
    AdminPermissions.SYSTEM_MONITOR,
])

AuthorizationManager.register_role(AdminRoles.SUPERADMIN, [
    AdminPermissions.DASHBOARD_VIEW,
    AdminPermissions.USER_MANAGEMENT,
    AdminPermissions.COURSE_MANAGEMENT,
    AdminPermissions.SYSTEM_MONITOR,
    AdminPermissions.SECURITY_CONFIG
])
