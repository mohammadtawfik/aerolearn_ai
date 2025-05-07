"""
Unit tests for /integrations/monitoring/events.py

Protocol References:
- Must support HealthEvent, correct event fields, event type enums, listener logic.

Tests:
- Event creation/use with mandated fields.
- Listener registration, firing, and delivery match protocol.
"""

import unittest
from integrations.monitoring import events

class TestHealthEvent(unittest.TestCase):
    def test_event_fields(self):
        evt = events.HealthEvent(component="api", state="FAILED", reason="timeout", timestamp="2024-06-12T12:00:00Z")
        self.assertEqual(evt.component, "api")
        self.assertEqual(evt.state, "FAILED")
        self.assertEqual(evt.reason, "timeout")
        self.assertEqual(evt.timestamp, "2024-06-12T12:00:00Z")

    def test_listener_registration_and_firing(self):
        calls = []

        def listener(evt):
            calls.append(evt)

        dispatcher = events.HealthEventDispatcher()
        dispatcher.register_listener(listener)
        test_evt = events.HealthEvent(component="db", state="DEGRADED", reason="overload", timestamp="2024-06-12T13:00:00Z")
        dispatcher.fire_event(test_evt)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], test_evt)

if __name__ == "__main__":
    unittest.main()