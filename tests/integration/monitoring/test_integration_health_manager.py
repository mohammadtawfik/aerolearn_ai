import unittest
from unittest.mock import Mock
from integrations.monitoring.integration_health_manager import IntegrationHealthManager
from integrations.monitoring.health_status import HealthStatus, HealthMetric

class TestIntegrationHealthManager(unittest.TestCase):
    def setUp(self):
        self.manager = IntegrationHealthManager()
        self.component_id = "core.api"
        self.manager.register_component(self.component_id, "API Service", "1.0")

    def test_update_and_get_status(self):
        self.manager.update_component_status(self.component_id, HealthStatus.RUNNING)
        status = self.manager.get_component_status(self.component_id)
        self.assertEqual(status.state, HealthStatus.RUNNING)

    def test_metric_tracking(self):
        self.manager.update_component_status(self.component_id, HealthStatus.RUNNING)
        self.manager.record_metric(self.component_id, HealthMetric(type="UPTIME", value=99.9))
        metrics = self.manager.get_component_metrics(self.component_id)
        self.assertTrue(any(m.type == "UPTIME" for m in metrics))

    def test_alert_callback(self):
        calls = []
        def alert_cb(component, state):
            calls.append((component, state))
        self.manager.register_alert_callback(alert_cb)
        self.manager.update_component_status(self.component_id, HealthStatus.DEGRADED)
        self.assertTrue(calls and calls[0][1] == HealthStatus.DEGRADED)

if __name__ == '__main__':
    unittest.main()