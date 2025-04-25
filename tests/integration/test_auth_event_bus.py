import unittest
import asyncio
from integrations.events.event_bus import EventBus
from integrations.events.event_types import EventCategory
from integrations.events.event_subscribers import EventSubscriber, EventFilter
from app.core.auth.user_profile import UserProfile
from app.core.auth.authentication import LocalAuthenticationProvider

class AuthEventRecorder(EventSubscriber):
    def __init__(self, subscriber_id):
        super().__init__(subscriber_id)
        self.events = []

    async def handle_event(self, event):
        self.events.append(event)

class AsyncTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bus = EventBus()
        await self.bus.start()
        await asyncio.sleep(0.05)  # Allow loop to settle if needed

    async def asyncTearDown(self):
        await self.bus.stop()
        await asyncio.sleep(0.05)

class TestAuthEventBusIntegration(AsyncTestCase):
    async def test_login_and_logout_events_propagate(self):
        user_db = {
            "alice": {"password": "pw", "user_id": "u1", "roles": ["student"], "email": "alice@example.com"},
        }
        provider = LocalAuthenticationProvider(user_db)
        recorder = AuthEventRecorder("auth-recorder")
        recorder.add_filter(EventFilter(categories=[EventCategory.SYSTEM]))
        self.bus.register_subscriber(recorder)
        # Successful login
        user = provider.authenticate("alice", "pw")
        await asyncio.sleep(0.1)
        self.assertTrue(
            any(e.event_type == "auth.login.success" for e in recorder.events)
        )

        # Failed login
        provider.authenticate("alice", "wrongpw")
        await asyncio.sleep(0.1)
        self.assertTrue(
            any(e.event_type == "auth.login.failed" for e in recorder.events)
        )

        # Successful logout
        provider.logout(user)
        await asyncio.sleep(0.1)
        self.assertTrue(
            any(e.event_type == "auth.logout" for e in recorder.events)
        )

if __name__ == "__main__":
    unittest.main()