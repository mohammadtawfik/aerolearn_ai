import uuid
import time
from typing import Dict, Optional
from app.core.auth.user_profile import UserProfile

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

    def is_active(self) -> bool:
        now = int(time.time())
        return (now - self.last_active) < self.timeout

    def touch(self):
        self.last_active = int(time.time())

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
            session.touch()
            return session
        elif session:
            # Expired session; cleanup
            del self._sessions[session_id]
        return None

    def invalidate_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def cleanup_expired(self):
        expired = [sid for sid, sess in self._sessions.items() if not sess.is_active()]
        for sid in expired:
            del self._sessions[sid]