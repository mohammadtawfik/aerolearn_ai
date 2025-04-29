import uuid
import time
import logging
from typing import Dict, Optional, List
from app.core.auth.user_profile import UserProfile

logger = logging.getLogger(__name__)

class Session:
    """
    Represents an authenticated session.
    """
    def __init__(self, profile: UserProfile, timeout: int = 3600):
        self.session_id = str(uuid.uuid4())
        self.profile = profile
        self.created_at = int(time.time())
        self.last_active = self.created_at
        self.timeout = timeout  # seconds
        self.is_active_flag = True
        self.activity_log = []
        
        # Log session creation
        self.log_activity("Session created")

    def is_active(self) -> bool:
        if not self.is_active_flag:
            return False
        now = int(time.time())
        return (now - self.last_active) < self.timeout

    def touch(self, activity_description: str = "Session activity"):
        self.last_active = int(time.time())
        self.log_activity(activity_description)
        
    def log_activity(self, description: str):
        """Log an activity in this session"""
        timestamp = int(time.time())
        activity = {
            "timestamp": timestamp,
            "description": description,
            "user_id": self.profile.user_id,
            "role": self.profile.role
        }
        self.activity_log.append(activity)
        
        # Log admin activities to system logs
        if self.profile.role == "admin":
            logger.info(f"ADMIN ACTIVITY: {self.profile.user_id} - {description}")
            
    def deactivate(self, reason: str = "Session invalidated"):
        """Explicitly deactivate this session"""
        self.is_active_flag = False
        self.log_activity(reason)

class SessionManager:
    """
    Handles session creation, validation, and expiration.
    """
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self, profile: UserProfile, timeout: int = 3600) -> str:
        session = Session(profile, timeout)
        self._sessions[session.session_id] = session
        return session.session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.is_active():
            session.touch("Session accessed")
            return session
        elif session:
            # Expired session; cleanup
            session.log_activity("Session expired")
            del self._sessions[session_id]
        return None

    def invalidate_session(self, session_id: str, reason: str = "Session invalidated"):
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.deactivate(reason)
            del self._sessions[session_id]

    def cleanup_expired(self):
        expired = [sid for sid, sess in self._sessions.items() if not sess.is_active()]
        for sid in expired:
            self._sessions[sid].log_activity("Session expired during cleanup")
            del self._sessions[sid]
            
    def get_active_sessions(self, user_id: str = None) -> List[Session]:
        """
        Get all active sessions, optionally filtered by user_id
        """
        return [
            session for session in self._sessions.values()
            if session.is_active() and (user_id is None or session.profile.user_id == user_id)
        ]
        
    def get_admin_sessions(self) -> List[Session]:
        """
        Get all active admin sessions
        """
        return [
            session for session in self._sessions.values()
            if session.is_active() and session.profile.role == "admin"
        ]
