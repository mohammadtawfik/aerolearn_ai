import unittest
import time
from app.core.monitoring.reliability import ReliabilityManager
from app.core.monitoring.recovery import RecoveryManager

from integrations.monitoring.health_status import HealthStatus

class MockHealthManager:
    def __init__(self, initial_status):
        self.status = initial_status
        self.updates = []
        self.metrics = []
    def get_component_status(self, component_id):
        return self.status
    def update_component_status(self, component_id, new_status):
        self.status = new_status
        self.updates.append((component_id, new_status))
    def record_metric(self, *args, **kwargs):
        self.metrics.append((args, kwargs))

class MockRegistry:
    def __init__(self):
        self.state_changes = []
        self.states = {}
        self.integration_notified = False
    def notify_state_change(self, component_id, state):
        self.state_changes.append((component_id, state))
        self.states[component_id] = state
    def set_component_state(self, component_id, state):
        self.states[component_id] = state
    def notify_recovery_action(self, component_id, state, reason):
        self.integration_notified = True
        self.last_recovery = (component_id, state, reason)

class MockDispatcher:
    def __init__(self):
        self.events = []
    def fire(self, event):
        self.events.append(event)

class TestReliabilityAndSelfHealingIntegration(unittest.TestCase):
    """Integration test for reliability and self-healing orchestration workflow."""

    def setUp(self):
        self.component_id = "componentZ"
        self.mock_health = MockHealthManager(HealthStatus.DEGRADED)
        self.mock_registry = MockRegistry()
        self.mock_dispatcher = MockDispatcher()
        self.reliability = ReliabilityManager(
            self.component_id, self.mock_registry, self.mock_health, dispatcher=self.mock_dispatcher)
        self.recovery = RecoveryManager(
            self.component_id, self.mock_registry, self.mock_health, dispatcher=self.mock_dispatcher)

    def test_full_self_healing_workflow(self):
        # Simulate reliability check (should detect not healthy)
        self.mock_health.status = HealthStatus.DEGRADED
        diag_result = self.reliability.self_diagnose(reason="integration selfhealing")
        self.assertFalse(diag_result)
        # The orchestrator would now trigger recovery
        recovery_result = self.recovery.attempt_recovery(reason="integration auto-repair")
        self.assertTrue(recovery_result)
        # Check that state is now healthy
        self.assertEqual(self.mock_health.status, HealthStatus.HEALTHY)
        # Validate events, registry, and metric propagation
        event_states = [event.state for event in self.mock_dispatcher.events]
        self.assertIn(HealthStatus.DEGRADED, event_states)
        self.assertIn(HealthStatus.HEALTHY, event_states)
        # Registry integration point callback should have been triggered
        self.assertTrue(self.mock_registry.integration_notified)
        rec_cid, rec_state, rec_reason = self.mock_registry.last_recovery
        self.assertEqual(rec_cid, self.component_id)
        self.assertEqual(rec_state, HealthStatus.HEALTHY)
        self.assertIn("auto-repair", rec_reason)

    def test_protocol_compliance_completed_flow(self):
        # Ensures proper argument/field propagation through workflow
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="contract test degraded")
        self.recovery.attempt_recovery(reason="contract test repair")
        # All events have expected fields and trace
        for event in self.mock_dispatcher.events:
            self.assertTrue(hasattr(event, "component"))
            self.assertTrue(hasattr(event, "state"))
            self.assertTrue(hasattr(event, "reason"))
            self.assertTrue(hasattr(event, "timestamp"))
            self.assertEqual(event.component, self.component_id)
        # Health manager and registry both show healthy post-recovery
        self.assertEqual(self.mock_health.status, HealthStatus.HEALTHY)
        self.assertEqual(self.mock_registry.states[self.component_id], HealthStatus.HEALTHY)

if __name__ == "__main__":
    unittest.main()