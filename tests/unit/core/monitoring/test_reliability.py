import unittest
from app.core.monitoring.reliability import ReliabilityManager
from types import SimpleNamespace

# Canonical protocol enums
from integrations.monitoring.health_status import HealthStatus
from integrations.registry.component_state import ComponentState
from integrations.monitoring.events import HealthEvent

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

    def notify_state_change(self, component_id, state):
        self.state_changes.append((component_id, state))
        self.states[component_id] = state

    def set_component_state(self, component_id, state):
        self.states[component_id] = state

class MockDispatcher:
    def __init__(self):
        self.events = []
    
    def fire(self, event):
        self.events.append(event)

class TestReliabilityModule(unittest.TestCase):
    """TDD tests for /app/core/monitoring/reliability.py per protocols and Day24 plan."""

    def setUp(self):
        self.component_id = "componentX"
        self.mock_health = MockHealthManager(HealthStatus.HEALTHY)
        self.mock_registry = MockRegistry()
        self.mock_dispatcher = MockDispatcher()
        self.reliability = ReliabilityManager(
            self.component_id, self.mock_registry, self.mock_health, dispatcher=self.mock_dispatcher
        )

    def test_self_diagnosis_api_surface(self):
        # The API exists and returns True for healthy case
        result = self.reliability.self_diagnose(reason="tdd test healthy")
        self.assertTrue(result)
        # Now simulate degraded (per protocol enum)
        self.mock_health.status = HealthStatus.DEGRADED
        result = self.reliability.self_diagnose(reason="tdd test degraded")
        self.assertFalse(result)

    def test_protocol_event_emission(self):
        # Always emits an event with correct fields
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="emit event test")
        self.assertTrue(len(self.mock_dispatcher.events) > 0)
        event = self.mock_dispatcher.events[-1]
        # Protocol: event must have component, state, reason fields
        self.assertEqual(event.component, self.component_id)
        self.assertIn("Self-diagnosis", event.reason)
        self.assertIn(event.state, [HealthStatus.DEGRADED, HealthStatus.HEALTHY])

    def test_dependency_interaction(self):
        # Diagnosis should update registry with state changes
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="degraded dependency")
        # Check state change in registry (via either API)
        reg_states = list(self.mock_registry.states.values())
        self.assertIn(HealthStatus.DEGRADED, reg_states + [s for _, s in self.mock_registry.state_changes])

    def test_metrics_and_state_update(self):
        # Diagnosis should update health (metrics and status) as per protocol
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="metrics test")
        # Check health_manager update was called with DEGRADED
        self.assertIn((self.component_id, HealthStatus.DEGRADED), self.mock_health.updates)
        # Check metric recorded
        metric_found = any(
            self.component_id in args and (HealthStatus.DEGRADED in args or "health_state" in kwargs)
            for args, kwargs in self.mock_health.metrics
        )
        self.assertTrue(metric_found)
        
    def test_recovery_event_emission(self):
        # Emits event on recovery from degraded to healthy
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="prepare recovery")
        self.mock_health.status = HealthStatus.HEALTHY
        result = self.reliability.self_diagnose(reason="recovery event")
        self.assertTrue(result)
        event = self.mock_dispatcher.events[-1]
        self.assertEqual(event.state, HealthStatus.HEALTHY)
        self.assertIn("Self-diagnosis", event.reason)
        
    def test_automatic_recovery_detection(self):
        # Detects recovery to HEALTHY
        self.mock_health.status = HealthStatus.DEGRADED
        self.reliability.self_diagnose(reason="was degraded")
        # Now heal
        self.mock_health.status = HealthStatus.HEALTHY
        result = self.reliability.self_diagnose(reason="healed")
        self.assertTrue(result)
        last_event = self.mock_dispatcher.events[-1]
        self.assertEqual(last_event.state, HealthStatus.HEALTHY)

if __name__ == "__main__":
    unittest.main()
