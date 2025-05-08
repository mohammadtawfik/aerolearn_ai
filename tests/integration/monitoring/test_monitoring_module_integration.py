import unittest
from app.core.monitoring.dashboard import ServiceHealthDashboard
from app.core.monitoring.registry import MonitoringComponentRegistry, ComponentRegistry
from integrations.monitoring.health_status import HealthStatus, HealthMetricType, HealthMetric
from integrations.monitoring.integration_health_manager import IntegrationHealthManager
from integrations.monitoring.health_provider import HealthProvider
from integrations.monitoring.events import HealthEvent, HealthEventDispatcher

class MockHealthProvider(HealthProvider):
    """Test double for HealthProvider (TDD/protocol-compliant, minimal external dependencies)."""
    def __init__(self, component_id):
        self.component_id = component_id
        self._metrics = []
        self._listeners = []

    def add_metric(self, metric):
        self._metrics.append(metric)

    def get_metrics(self):
        return self._metrics

    def get_health_status(self):
        # For test purposes, just return HEALTHY or most recent state
        return HealthStatus.HEALTHY

    def register_listener(self, listener):
        self._listeners.append(listener)

class TestMonitoringIntegration(unittest.TestCase):
    def setUp(self):
        # Test protocol: registry injected into dashboard
        self.component_registry = ComponentRegistry()
        self.dashboard = ServiceHealthDashboard(registry=self.component_registry)
        self.health_manager = IntegrationHealthManager(registry=self.component_registry, dashboard=self.dashboard)
        self.event_dispatcher = HealthEventDispatcher()

    def test_register_and_status_update_flow(self):
        cid = "core.analytics"
        self.component_registry.register_component(cid, description="Analytics", version="1.1", state=HealthStatus.UNKNOWN)
        self.dashboard.update_component_status(cid, HealthStatus.RUNNING)
        self.assertEqual(self.dashboard.status_for(cid), HealthStatus.RUNNING)
        
        # Verify health manager integration
        self.health_manager.update_health(cid, HealthStatus.HEALTHY)
        status = self.dashboard.get_status(cid)
        self.assertEqual(status.state, HealthStatus.HEALTHY)

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
    
    def test_event_dispatch_and_orchestration(self):
        # Test event emission and callback
        event_list = []
        self.event_dispatcher.add_listener(lambda e: event_list.append(e))
        
        # Register component and emit event
        cid = "core.messaging"
        self.component_registry.register_component(cid, description="Messaging Service", version="1.0")
        
        # Create and fire health event
        event = HealthEvent(
            component=cid, 
            state=HealthStatus.DEGRADED, 
            reason="High latency", 
            timestamp="2024-01-01T00:00:01Z"
        )
        self.event_dispatcher.fire(event)
        
        # Verify event was dispatched
        self.assertEqual(len(event_list), 1)
        self.assertEqual(event_list[0], event)
        
        # Verify dashboard state is updated via orchestrator
        self.health_manager.process_health_event(event)
        status = self.dashboard.get_status(cid)
        self.assertEqual(status.state, HealthStatus.DEGRADED)
    
    def test_health_metrics_integration(self):
        # Test health metrics collection and reporting
        cid = "core.api"
        provider = MockHealthProvider(component_id=cid)
        
        # Register component with metrics
        self.component_registry.register_component(cid, description="API Gateway", version="2.0")
        
        # Add metrics to provider
        provider.add_metric(HealthMetric(
            name="response_time",
            type=HealthMetricType.RESPONSE_TIME,
            value=120
        ))
        
        # Update health with metrics
        self.health_manager.update_health_with_metrics(cid, provider.get_metrics())
        
        # Verify metrics are properly integrated
        status = self.dashboard.get_status(cid)
        self.assertIsNotNone(status)
        self.assertTrue(hasattr(status, "metrics"))
        self.assertIn("response_time", [m.name for m in status.metrics])

if __name__ == '__main__':
    unittest.main()
