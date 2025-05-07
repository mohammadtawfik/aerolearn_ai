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
    get_component_registry, get_system_status_tracker, get_default_adapter,
    register_with_status_tracker, update_component_status, clear_all_status_tracking
)
from integrations.monitoring.integration_health import HealthStatus, HealthMetric, HealthMetricType
from app.core.monitoring.metrics import AlertLevel

# Protocol-compliant minimal test double for Component
class TestComponent:
    def __init__(self, component_id, version="1.0"):
        self.component_id = component_id  # Required by protocol
        self.id = component_id
        self.name = component_id  # Registry/adapter may use .name or .id
        self.version = version
        self.state = 'OK'
        self.dependencies = set()
    
    def declare_dependency(self, dep_id):
        self.dependencies.add(dep_id)
    
    def set_state(self, state):
        self.state = state
        
    def to_dict(self):
        return {"id": self.id, "component_id": self.component_id, "version": self.version, "name": self.name}

@pytest.fixture(autouse=True)
def clear_test_state():
    """Reset all tracking state between tests to ensure isolation"""
    clear_all_status_tracking()
    yield
    clear_all_status_tracking()

def test_protocol_component_registration_and_dependency_tracking():
    """Test component registration and dependency declaration per protocol"""
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
    
    # Dependencies should be tracked
    graph = registry.get_dependency_graph()
    assert 'ServiceA' in graph and set(graph['ServiceA']) == {'ServiceB', 'ServiceC'}
    
    # Verify reverse dependency lookup
    dependents = registry.get_dependents('ServiceB')
    assert 'ServiceA' in dependents

def test_service_health_dashboard_cascading_state_and_event_hooks():
    """Test cascading status updates and event notifications"""
    registry = get_component_registry()
    tracker = get_system_status_tracker()
    
    # Register components with dependencies
    comp_a = TestComponent(component_id='ServiceA')
    comp_b = TestComponent(component_id='ServiceB')
    comp_c = TestComponent(component_id='ServiceC')
    
    registry.register_component(comp_a)
    registry.register_component(comp_b)
    registry.register_component(comp_c)
    
    # ServiceA depends on B and C
    registry.declare_dependency('ServiceA', 'ServiceB')
    registry.declare_dependency('ServiceA', 'ServiceC')
    
    # Register with status tracker using protocol objects (not dicts)
    register_with_status_tracker(comp_a, tracker, registry)
    register_with_status_tracker(comp_b, tracker, registry)
    register_with_status_tracker(comp_c, tracker, registry)

    # Set up status listener
    adapter = get_default_adapter()
    event_log = []
    def listener(comp_id, state, details):
        event_log.append((comp_id, state, details))

    adapter.register_status_listener(listener)

    # Print dependency graph for diagnosis
    print("\n=== DEPENDENCY GRAPH ANALYSIS ===")
    print("DEPENDENCY IMPACT (ServiceB):", registry.analyze_dependency_impact('ServiceB'))
    print("DEPENDENCY IMPACT (ServiceC):", registry.analyze_dependency_impact('ServiceC'))
    print("DEPENDENCY IMPACT (ServiceA):", registry.analyze_dependency_impact('ServiceA'))
    print("FULL DEPENDENCY GRAPH:", registry.get_dependency_graph())
    
    # Set ServiceB to DOWN - ServiceA should cascade to IMPAIRED/FAILED
    print("\n=== UPDATING STATUS: ServiceB to DOWN ===")
    update_component_status('ServiceB', 'DOWN', {'reason': 'Downstream issue'})
    
    # Dump the full event log
    print("\n=== EVENT LOG DUMP ===")
    for idx, (cid, state, details) in enumerate(event_log):
        print(f"[{idx}] cid={cid!r} state={state!r} details={details}")
    
    # Verify direct status update
    assert any(s == 'DOWN' for cid, s, d in event_log if cid == 'ServiceB'), \
        "ServiceB status not updated to DOWN in event log"
    
    # Verify cascading status update to dependent services
    assert any(s in ('IMPAIRED', 'FAILED') for cid, s, d in event_log if cid == 'ServiceA'), \
        "Status did not cascade to dependent service ServiceA"

    # Set ServiceA OK again: status should reflect, listeners called
    print("\n=== UPDATING STATUS: ServiceA to OK ===")
    update_component_status('ServiceA', 'OK', {'note': 'Back online'})
    
    # Dump the updated event log
    print("\n=== UPDATED EVENT LOG DUMP ===")
    for idx, (cid, state, details) in enumerate(event_log):
        print(f"[{idx}] cid={cid!r} state={state!r} details={details}")
    
    assert any(s == 'OK' for cid, s, d in event_log if cid == 'ServiceA'), \
        "ServiceA status not updated to OK in event log"

def test_integration_health_metrics_protocol():
    """Test health metrics conform to protocol specifications"""
    tracker = get_system_status_tracker()
    registry = get_component_registry()
    comp = TestComponent("MetricsTarget")
    registry.register_component(comp)
    register_with_status_tracker(comp, tracker, registry)
    
    # Health status and metrics should conform to /docs/architecture/health_monitoring_protocol.md
    m1 = HealthMetric(component_id="ServiceA", name='uptime', value=99.95, metric_type=HealthMetricType.SERVICE)
    m2 = HealthMetric(component_id="ServiceA", name='response_time', value=120, metric_type=HealthMetricType.PERFORMANCE)
    
    # Verify metric serialization
    metric_dict = m1.to_dict()
    assert metric_dict['name'] == 'uptime'
    assert metric_dict['component_id'] == 'ServiceA'
    assert metric_dict['value'] == 99.95
    
    # Verify metric type
    assert m2.metric_type == HealthMetricType.PERFORMANCE
    
    # Simulate a status update (should appear in metrics)
    update_component_status("MetricsTarget", "HEALTHY", {"extra": "ok"})
    
    # If metrics manager is available, verify the status update is reflected
    try:
        from app.core.monitoring.metrics import SystemMetricsManager
        metrics_manager = SystemMetricsManager()
        m = metrics_manager.get_metric("MetricsTarget")
        assert m is not None
        assert m.value == "HEALTHY" or m.to_dict().get("status") == "HEALTHY"
    except ImportError:
        pass  # Skip this part if metrics system not available

def test_notification_callbacks_and_adapter_api():
    """Test alert callbacks fire according to protocol"""
    # Ensure all protocol hooks and notifications fire as documented
    adapter = get_default_adapter()
    
    # Track alert callbacks
    alerts = []
    def alert_callback(component_id, alert_level, message):
        alerts.append((component_id, alert_level, message))
    
    adapter.register_alert_callback(alert_callback)
    
    # Update status to trigger alert
    update_component_status('CriticalService', 'DOWN', {'reason': 'Service crashed'})
    
    # Verify alert was triggered
    assert any(a[0] == 'CriticalService' and (a[1] == AlertLevel.CRITICAL or a[1] == 'CRITICAL')
               for a in alerts), "Alert callback did not fire on critical status change!"

def test_status_history_and_recovery():
    """Test status history tracking and recovery detection"""
    registry = get_component_registry()
    tracker = get_system_status_tracker()
    
    # Register component
    comp = TestComponent(component_id='HistoryService')
    registry.register_component(comp)
    register_with_status_tracker(comp, tracker, registry)
    
    # Track status changes
    status_changes = []
    adapter = get_default_adapter()
    
    def status_listener(comp_id, state, details):
        status_changes.append((comp_id, state, details))
    
    adapter.register_status_listener(status_listener)
    
    # Create status history
    update_component_status('HistoryService', 'HEALTHY', {'message': 'Initial state'})
    update_component_status('HistoryService', 'DEGRADED', {'message': 'Slow responses'})
    update_component_status('HistoryService', 'FAILED', {'message': 'Connection lost'})
    update_component_status('HistoryService', 'HEALTHY', {'message': 'Recovered'})
    
    # Verify status history
    states = [s[1] for s in status_changes if s[0] == 'HistoryService']
    assert states == ['HEALTHY', 'DEGRADED', 'FAILED', 'HEALTHY']
    
    # Verify recovery detection (if protocol supports it)
    if hasattr(tracker, 'get_status_history'):
        history = tracker.get_status_history('HistoryService')
        assert len(history) >= 4
        assert history[-1][0] == 'HEALTHY'  # Latest status is HEALTHY
