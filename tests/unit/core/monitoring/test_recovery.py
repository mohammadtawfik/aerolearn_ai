import unittest
import time
from app.core.monitoring.recovery import RecoveryManager
from integrations.monitoring.health_status import HealthStatus
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
        self.integration_notified = False
    
    def notify_state_change(self, component_id, state):
        self.state_changes.append((component_id, state))
        self.states[component_id] = state
    
    def set_component_state(self, component_id, state):
        self.states[component_id] = state
    
    # IntegrationPointRegistry protocol simulation
    def notify_recovery_action(self, component_id, state, reason):
        self.integration_notified = True
        self.last_recovery = (component_id, state, reason)

class MockDispatcher:
    def __init__(self):
        self.events = []
    
    def fire(self, event):
        self.events.append(event)

class TestRecoveryModule(unittest.TestCase):
    """TDD tests for /app/core/monitoring/recovery.py as per protocol and Day24 documentation."""

    def setUp(self):
        self.component_id = "componentY"
        self.mock_health = MockHealthManager(HealthStatus.DEGRADED)
        self.mock_registry = MockRegistry()
        self.mock_dispatcher = MockDispatcher()
        self.recovery = RecoveryManager(
            self.component_id, self.mock_registry, self.mock_health, dispatcher=self.mock_dispatcher
        )

    def test_self_repair_api_surface(self):
        """Test API surface for self-repair/restore functions"""
        # Must have an API and recover state
        self.mock_health.status = HealthStatus.DEGRADED
        result = self.recovery.attempt_recovery(reason="unit test - repair")
        self.assertTrue(result)
        self.assertEqual(self.mock_health.status, HealthStatus.HEALTHY)

    def test_recovery_action_emission(self):
        """Test protocol event emissions on recovery actions"""
        # Must emit protocol-compliant recovery/health event
        self.mock_health.status = HealthStatus.DEGRADED
        self.recovery.attempt_recovery(reason="action emission test")
        self.assertTrue(self.mock_dispatcher.events)
        event = self.mock_dispatcher.events[-1]
        self.assertEqual(event.component, self.component_id)
        self.assertEqual(event.state, HealthStatus.HEALTHY)
        self.assertIn("Automatic recovery", event.reason)

    def test_metrics_update_and_propagation(self):
        """Test that recovery updates metrics/state via monitoring APIs"""
        # Must update metrics and state via health_manager
        self.mock_health.status = HealthStatus.DEGRADED
        self.recovery.attempt_recovery(reason="metrics/propagation test")
        self.assertIn((self.component_id, HealthStatus.HEALTHY), self.mock_health.updates)
        has_metric = any(self.component_id in args and "recovery_state" in args
                         for args, kwargs in self.mock_health.metrics)
        self.assertTrue(has_metric)

    def test_integration_points(self):
        """Test proper wiring to IntegrationPointRegistry"""
        # Must wire into registry integration point (if present)
        # Simulate IntegrationPointRegistry protocol method
        if hasattr(self.mock_registry, "notify_recovery_action"):
            self.mock_health.status = HealthStatus.DEGRADED
            # Patch RecoveryManager to call notify_recovery_action (simulate integration)
            self.recovery.attempt_recovery(reason="integration point")
            self.assertTrue(self.mock_registry.integration_notified)
            cid, state, reason = self.mock_registry.last_recovery
            self.assertEqual(cid, self.component_id)
            self.assertEqual(state, HealthStatus.HEALTHY)
            self.assertIn("integration point", reason)

if __name__ == "__main__":
    unittest.main()
