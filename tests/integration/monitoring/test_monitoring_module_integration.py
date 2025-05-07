import unittest
from app.core.monitoring.dashboard import ServiceHealthDashboard
from app.core.monitoring.registry import MonitoringComponentRegistry
from app.core.monitoring.registry import ComponentRegistry
from integrations.monitoring.health_status import HealthStatus

class TestMonitoringIntegration(unittest.TestCase):
    def setUp(self):
        # Test protocol: registry injected into dashboard
        self.component_registry = ComponentRegistry()
        self.dashboard = ServiceHealthDashboard(registry=self.component_registry)

    def test_register_and_status_update_flow(self):
        cid = "core.analytics"
        self.component_registry.register_component(cid, description="Analytics", version="1.1", state=HealthStatus.UNKNOWN)
        self.dashboard.update_component_status(cid, HealthStatus.RUNNING)
        self.assertEqual(self.dashboard.status_for(cid), HealthStatus.RUNNING)

    def test_status_listener_and_clear(self):
        changes = []
        def listener(cid, state):
            changes.append((cid, state))
        self.dashboard.register_status_listener(listener)
        cid = "core.db"
        self.component_registry.register_component(cid, description="Database", version="2.1")
        self.dashboard.update_component_status(cid, HealthStatus.DEGRADED)
        self.dashboard.clear()
        self.assertIn((cid, HealthStatus.DEGRADED), changes)

    def test_cascading_status_support(self):
        # Protocol: supports_cascading_status() must exist and return a boolean
        self.assertTrue(hasattr(self.dashboard, "supports_cascading_status"))
        self.assertIsInstance(self.dashboard.supports_cascading_status(), bool)

if __name__ == '__main__':
    unittest.main()
