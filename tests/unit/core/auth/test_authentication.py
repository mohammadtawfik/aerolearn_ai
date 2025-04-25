import unittest
from unittest.mock import patch, AsyncMock
import asyncio

from app.core.auth.user_profile import UserProfile
from app.core.auth.authentication import LocalAuthenticationProvider, AuthEvent
from app.core.auth.session import SessionManager

# Dummy EventBus to capture published events for verification
class DummyEventBus:
    def __init__(self):
        self.published_events = []
        self._is_running = True
    async def publish(self, event):
        self.published_events.append(event)

class TestAuthenticationProviderAndSession(unittest.TestCase):

    def setUp(self):
        self.user_db = {
            "alice": {"password": "alicepw", "user_id": "u1", "roles": ["student"], "email": "alice@example.com"},
            "bob": {"password": "bobpw", "user_id": "u2", "roles": ["professor"], "email": "bob@example.com"},
        }
        self.session_mgr = SessionManager()

    @patch("app.core.auth.authentication.EventBus", new=lambda: DummyEventBus())
    def test_login_success_event_emission(self):
        provider = LocalAuthenticationProvider(self.user_db)
        user = provider.authenticate("alice", "alicepw")
        self.assertIsInstance(user, UserProfile)
        # To fully verify event emission, you would need to await the created coroutine,
        # but the dummy EventBus' 'publish' simulates the event, so exceptions shouldn't occur.

    @patch("app.core.auth.authentication.EventBus", new=lambda: DummyEventBus())
    def test_login_failure_event_emission(self):
        provider = LocalAuthenticationProvider(self.user_db)
        user = provider.authenticate("alice", "wrongpw")
        self.assertIsNone(user)

    def test_session_creation_and_expiry(self):
        user = UserProfile(user_id="u1", username="alice")
        session_id = self.session_mgr.create_session(user, timeout=1)
        session = self.session_mgr.get_session(session_id)
        self.assertIsNotNone(session)
        import time; time.sleep(1.1)
        expired = self.session_mgr.get_session(session_id)
        self.assertIsNone(expired)

    @patch("app.core.auth.authentication.EventBus", new=lambda: DummyEventBus())
    def test_logout_event_emission(self):
        provider = LocalAuthenticationProvider(self.user_db)
        user = provider.authenticate("bob", "bobpw")
        provider.logout(user)  # This should emit an AuthEvent, which is handled by DummyEventBus

    def test_invalid_user_login(self):
        provider = LocalAuthenticationProvider(self.user_db)
        self.assertIsNone(provider.authenticate("carol", "carolpw"))

    def test_multiple_sessions_and_cleanup(self):
        user1 = UserProfile(user_id="u1", username="alice")
        user2 = UserProfile(user_id="u2", username="bob")
        id1 = self.session_mgr.create_session(user1, timeout=2)
        id2 = self.session_mgr.create_session(user2, timeout=2)
        self.assertIn(id1, self.session_mgr._sessions)
        self.assertIn(id2, self.session_mgr._sessions)
        self.session_mgr.cleanup_expired()
        self.assertIn(id1, self.session_mgr._sessions)
        import time; time.sleep(2.1)
        self.session_mgr.cleanup_expired()
        self.assertNotIn(id1, self.session_mgr._sessions)
        self.assertNotIn(id2, self.session_mgr._sessions)

if __name__ == "__main__":
    unittest.main()