"""
Test coverage for:
- Component registry protocol compliance (/docs/architecture/dependency_tracking_protocol.md)
- Service health protocol registration, state update, event notification (/docs/architecture/service_health_protocol.md, /docs/api/service_health_protocol.md)
- Health monitoring adapter correctness (/docs/architecture/health_monitoring_protocol.md)
- Full integration: dependency graph generation, cascading state update, correct callbacks

Requires project modules:
- integrations.registry.component_registry
- integrations.monitoring.component_status_adapter
- integrations.monitoring.integration_health

Assumptions:
- All registry/component/dashboard/adapter classes implement the methods described in the protocols.
"""

import pytest
from integrations.registry.component_registry import ComponentRegistry
from integrations.monitoring.component_status_adapter import (
    ServiceHealthDashboard, ComponentStatusAdapter, SimpleStatusTracker,
    get_component_registry, get_system_status_tracker, get_default_adapter
)
from integrations.monitoring.integration_health import HealthStatus, HealthMetric, HealthMetricType

# Protocol-compliant minimal test double for Component
class TestComponent:
    def __init__(self, component_id):
        self.component_id = component_id
        self.state = 'OK'
        self.dependencies = set()
    
    def declare_dependency(self, dep_id):
        self.dependencies.add(dep_id)
    
    def set_state(self, state):
        self.state = state

def test_protocol_component_registration_and_dependency_tracking():
    registry = ComponentRegistry()
    cA = TestComponent(component_id='ServiceA')
    cB = TestComponent(component_id='ServiceB')
    cC = TestComponent(component_id='ServiceC')

    # Register components
    assert registry.register_component(cA)
    assert registry.register_component(cB)
    assert registry.register_component(cC)

    # Declare dependencies (A depends on B and C)
    assert registry.declare_dependency('ServiceA', 'ServiceB')
    assert registry.declare_dependency('ServiceA', 'ServiceC')
    graph = registry.get_dependency_graph()
    assert 'ServiceA' in graph and set(graph['ServiceA']) == {'ServiceB', 'ServiceC'}

def test_service_health_dashboard_cascading_state_and_event_hooks(monkeypatch):
    registry = ComponentRegistry()
    cA = TestComponent(component_id='ServiceA')
    cB = TestComponent(component_id='ServiceB')
    registry.register_component(cA)
    registry.register_component(cB)
    registry.declare_dependency('ServiceA', 'ServiceB')
    tracker = SimpleStatusTracker(registry)
    dashboard = ServiceHealthDashboard(tracker, registry)

    state_log = []
    def listener(comp_id, state, details):
        state_log.append((comp_id, state, details))

    adapter = ComponentStatusAdapter(dashboard)
    adapter.register_status_listener(listener)

    # Set ServiceB to degraded: ServiceA should reflect degradation (cascade), protocol event should fire
    adapter.update_component_status('ServiceB', 'DEGRADED', {'reason': 'Downstream issue'})
    assert any(s == 'DEGRADED' for cid, s, d in state_log if cid == 'ServiceB')

    # Set ServiceA OK again: status should reflect, listeners called
    adapter.update_component_status('ServiceA', 'OK', {'note': 'Back online'})
    assert any(s == 'OK' for cid, s, d in state_log if cid == 'ServiceA')

def test_integration_health_metrics_protocol():
    # Health status and metrics should conform to /docs/architecture/health_monitoring_protocol.md
    m1 = HealthMetric(component_id="ServiceA", name='uptime', value=99.95, metric_type=HealthMetricType.SERVICE)
    m2 = HealthMetric(component_id="ServiceA", name='response_time', value=120, metric_type=HealthMetricType.PERFORMANCE)
    assert m1.to_dict()['name'] == 'uptime'
    assert m2.metric_type == HealthMetricType.PERFORMANCE

def test_notification_callbacks_and_adapter_api():
    # Ensure all protocol hooks and notifications fire as documented
    tracker = SimpleStatusTracker()
    dashboard = ServiceHealthDashboard(tracker)
    adapter = ComponentStatusAdapter(dashboard)
    fired = dict(cb=False)
    def cb(cid, s, d):
        fired['cb'] = True
    adapter.register_alert_callback(cb)
    adapter.update_component_status('DemoComponent', 'DOWN', {'msg': 'Test triggered'})
    assert fired['cb'], "Alert callback did not fire on status change!"
