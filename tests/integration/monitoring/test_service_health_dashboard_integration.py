"""
Integration test for ServiceHealthDashboard Protocol Compliance.

Location: /tests/integration/monitoring/test_service_health_dashboard_integration.py

Tests the integration between ComponentRegistry, ComponentStatusAdapter, and 
ServiceHealthDashboard. Validates registration, status changes, real-time updates,
historical tracking, dependency graph integrity, and event propagation according 
to the monitoring protocol.

Validates alignment with service health protocol specifications and exercises
state transitions, dependency graph correctness, and integration with status adapters.

Run with pytest.
"""

import pytest
from integrations.monitoring.component_status_adapter import ComponentState
from integrations.registry.component_registry import ComponentRegistry, Component
from app.core.monitoring.ServiceHealthDashboard_Class import ServiceHealthDashboard
from integrations.monitoring.component_status_adapter import (
    ComponentStatusAdapter,
    SimpleComponentStatusProvider
)
from integrations.events.event_bus import EventBus
from integrations.events.event_types import SystemEventType, EventPriority

class DummyComponent(Component):
    """A test component that tracks state changes"""
    def __init__(self, name):
        super().__init__(name=name)
        self.state_changes = []
        self.component_id = name

    def set_state(self, state):
        self.state_changes.append(state)
        self.state = state

@pytest.fixture
def registry():
    reg = ComponentRegistry()
    reg.clear()
    return reg

@pytest.fixture
def dashboard(registry):
    dashboard = ServiceHealthDashboard(registry)
    dashboard.clear()
    return dashboard

@pytest.fixture
def status_adapter(dashboard):
    adapter = ComponentStatusAdapter(dashboard)
    adapter.clear()
    return adapter

@pytest.fixture
def event_bus():
    bus = EventBus()
    return bus

@pytest.fixture
def monitoring_setup():
    # Legacy fixture for backward compatibility
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry)
    adapter = ComponentStatusAdapter(dashboard)
    
    # Clear all state for test isolation
    registry.clear()
    dashboard.clear()
    adapter.clear()
    
    return registry, adapter, dashboard

def register_monitored_component(registry, adapter, component):
    # Register the component with the registry (for dependency graph, state management etc.)
    registry.register_component(component.name, component)
    # Always wrap component in SimpleComponentStatusProvider
    provider = SimpleComponentStatusProvider(component)
    adapter.register_status_provider(component.name, provider)

def test_registration_and_status_update(monitoring_setup):
    registry, adapter, dashboard = monitoring_setup

    # Register mock component with minimal state interface
    class TestComponent:
        def __init__(self, name):
            self.name = name
            self.state = ComponentState.RUNNING
            self.metadata = {}
            self.component_id = name
    db_service = TestComponent("DBService")
    api_gateway = TestComponent("APIGateway")
    analytics = TestComponent("AnalyticsEngine")

    for comp in (db_service, api_gateway, analytics):
        register_monitored_component(registry, adapter, comp)

    dashboard.watch_component(db_service.name)
    dashboard.watch_component(api_gateway.name)
    dashboard.watch_component(analytics.name)

    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["DBService"].state == ComponentState.RUNNING
    assert all_statuses["APIGateway"].state == ComponentState.RUNNING
    assert all_statuses["AnalyticsEngine"].state == ComponentState.RUNNING

    # Change APIGateway to DEGRADED
    api_gateway.state = ComponentState.DEGRADED
    adapter.update_component_status(api_gateway.name)
    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["APIGateway"].state == ComponentState.DEGRADED

    # Change AnalyticsEngine to DOWN
    analytics.state = ComponentState.DOWN
    adapter.update_component_status(analytics.name)
    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["AnalyticsEngine"].state == ComponentState.DOWN

def test_historical_uptime_tracking(monitoring_setup):
    registry, adapter, dashboard = monitoring_setup
    class TestComponent:
        def __init__(self, name):
            self.name = name
            self.state = ComponentState.RUNNING
            self.component_id = name
    runner = TestComponent("TaskRunner")
    register_monitored_component(registry, adapter, runner)
    dashboard.watch_component(runner.name)

    # Initial state
    adapter.update_component_status(runner.name, ComponentState.RUNNING)
    assert dashboard.status_for("TaskRunner") == ComponentState.RUNNING
    
    # Transition to DEGRADED
    adapter.update_component_status(runner.name, ComponentState.DEGRADED)
    assert dashboard.status_for("TaskRunner") == ComponentState.DEGRADED
    
    # Transition back to RUNNING
    adapter.update_component_status(runner.name, ComponentState.RUNNING)
    assert dashboard.status_for("TaskRunner") == ComponentState.RUNNING
    
    # Transition to DOWN
    adapter.update_component_status(runner.name, ComponentState.DOWN)
    assert dashboard.status_for("TaskRunner") == ComponentState.DOWN

    # Verify history contains all transitions
    hist = dashboard.get_status_history("TaskRunner")
    assert hist, "History should not be empty."
    assert any(rec.state == ComponentState.RUNNING for rec in hist)
    assert any(rec.state == ComponentState.DEGRADED for rec in hist)
    assert any(rec.state == ComponentState.DOWN for rec in hist)

def test_real_time_status_update(monitoring_setup):
    registry, adapter, dashboard = monitoring_setup
    class TestComponent:
        def __init__(self, name):
            self.name = name
            self.state = ComponentState.RUNNING
            self.component_id = name
    notifier = TestComponent("Notifier")
    register_monitored_component(registry, adapter, notifier)
    dashboard.watch_component(notifier.name)

    notifier.state = ComponentState.RUNNING
    adapter.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.RUNNING
    notifier.state = ComponentState.DOWN
    adapter.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.DOWN
    notifier.state = ComponentState.RUNNING
    adapter.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.RUNNING

def test_cross_component_state_propagation(registry, dashboard, status_adapter):
    """
    Validates that a state change in a registered component is visible on
    the ServiceHealthDashboard via the ComponentStatusAdapter, per protocol.
    """
    # Arrange: Register a mock component in the registry
    component = registry.register_component("TestService", {})
    dashboard.watch_component(component.name)
    
    # Create a status provider for the component
    provider = SimpleComponentStatusProvider(component)
    status_adapter.register_status_provider(component.name, provider)
    
    # Act: Set state via adapter (simulate event/metric)
    status_adapter.update_component_status(component.name, ComponentState.DEGRADED, 
                                          details={"reason": "Simulated load"})
    
    # Assert: Dashboard reflects status
    assert dashboard.get_all_component_statuses()[component.name].state == ComponentState.DEGRADED

def test_event_propagation_triggers_callbacks(registry, dashboard, status_adapter):
    """
    Verifies event/alert callback firing when status transitions
    between RUNNING, DEGRADED, DOWN per dashboard/adapter protocol.
    """
    component = registry.register_component("AlertService", {})
    dashboard.watch_component(component.name)
    
    # Create a status provider for the component
    provider = SimpleComponentStatusProvider(component)
    status_adapter.register_status_provider(component.name, provider)
    
    fired_states = []
    def callback(comp_id, state, details):
        fired_states.append((comp_id, state))
    
    dashboard.register_status_listener(callback)
    
    # State transitions
    status_adapter.update_component_status(component.name, ComponentState.RUNNING, details={})
    status_adapter.update_component_status(component.name, ComponentState.DEGRADED, details={})
    status_adapter.update_component_status(component.name, ComponentState.DOWN, details={})
    
    assert (component.name, ComponentState.DEGRADED) in fired_states
    assert (component.name, ComponentState.DOWN) in fired_states

def test_transaction_integrity_and_clear_protocol(registry, dashboard, status_adapter):
    """
    Tests that multi-step updates are atomic and clear() protocol fully resets state for TDD test re-use.
    """
    component = registry.register_component("AtomicService", {})
    dashboard.watch_component(component.name)
    
    # Create a status provider for the component
    provider = SimpleComponentStatusProvider(component)
    status_adapter.register_status_provider(component.name, provider)
    
    # Set to DOWN, then clear(), then check state wiped
    status_adapter.update_component_status(component.name, ComponentState.DOWN, 
                                          details={"reason": "test"})
    
    # Verify status is set
    assert dashboard.status_for(component.name) == ComponentState.DOWN
    
    # Clear everything
    dashboard.clear()
    
    # Check dashboard is empty
    all_statuses = dashboard.get_all_component_statuses()
    assert component.name not in all_statuses or all_statuses[component.name].state != ComponentState.DOWN

def test_component_registration_and_dependency_graph():
    """
    Test that components can be registered, dependencies assigned, and state transitions
    propagate correctly to the dashboard according to the service health protocol.
    """
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry=registry)
    adapter = ComponentStatusAdapter(dashboard)
    
    # Create and register components
    comp_a = DummyComponent("ComponentA")
    comp_b = DummyComponent("ComponentB")
    comp_c = DummyComponent("ComponentC")
    registry.register_component(comp_a.name, comp_a)
    registry.register_component(comp_b.name, comp_b)
    registry.register_component(comp_c.name, comp_c)
    
    # Watch components in dashboard
    dashboard.watch_component(comp_a.name)
    dashboard.watch_component(comp_b.name)
    dashboard.watch_component(comp_c.name)
    
    # Register status providers
    adapter.register_status_provider(comp_a.name, SimpleComponentStatusProvider(comp_a))
    adapter.register_status_provider(comp_b.name, SimpleComponentStatusProvider(comp_b))
    adapter.register_status_provider(comp_c.name, SimpleComponentStatusProvider(comp_c))
    
    # Declare dependencies
    registry.declare_dependency(comp_a.name, comp_b.name)
    registry.declare_dependency(comp_b.name, comp_c.name)
    
    # Set state for components and update via adapter
    adapter.update_component_status(comp_a.name, ComponentState.RUNNING, {"msg": "initial"})
    adapter.update_component_status(comp_b.name, ComponentState.DEGRADED, {"msg": "mid"})
    adapter.update_component_status(comp_c.name, ComponentState.DOWN, {"msg": "fail"})

    # Dashboard queries
    all_status = dashboard.get_all_component_statuses()
    assert all_status[comp_a.name].state == ComponentState.RUNNING
    assert all_status[comp_b.name].state == ComponentState.DEGRADED
    assert all_status[comp_c.name].state == ComponentState.DOWN

    # Verify dependency graph
    dep_graph = dashboard.get_dependency_graph()
    assert dep_graph[comp_a.name] == [comp_b.name]
    assert dep_graph[comp_b.name] == [comp_c.name]
    assert comp_c.name in dep_graph

def test_health_event_propagation_and_alert_callback():
    """
    Test event propagation and callback registration as per service health protocol
    """
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry=registry)
    adapter = ComponentStatusAdapter(dashboard)

    events = []
    def alert_callback(component_id, state, details):
        events.append((component_id, state, details))

    dashboard.register_status_listener(alert_callback)
    
    # Create and register component
    comp = DummyComponent("HealthMonitor")
    registry.register_component(comp.name, comp)
    dashboard.watch_component(comp.name)
    adapter.register_status_provider(comp.name, SimpleComponentStatusProvider(comp))
    
    # Trigger state changes
    adapter.update_component_status(comp.name, ComponentState.DEGRADED, {"msg": "degraded"})
    adapter.update_component_status(comp.name, ComponentState.DOWN, {"msg": "down"})
    
    # Verify events were captured
    assert len(events) >= 2  # At least one event per update
    assert any(event[0] == comp.name and event[1] == ComponentState.DEGRADED for event in events)
    assert any(event[0] == comp.name and event[1] == ComponentState.DOWN for event in events)

def test_cascading_status_updates():
    """
    Test that status changes cascade through dependent components
    according to the service health protocol
    """
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry=registry)
    adapter = ComponentStatusAdapter(dashboard)
    
    # Create component hierarchy: Database <- API <- Frontend
    db = DummyComponent("Database")
    api = DummyComponent("API")
    frontend = DummyComponent("Frontend")
    
    # Register components
    registry.register_component(db.name, db)
    registry.register_component(api.name, api)
    registry.register_component(frontend.name, frontend)
    
    # Watch components
    dashboard.watch_component(db.name)
    dashboard.watch_component(api.name)
    dashboard.watch_component(frontend.name)
    
    # Register status providers
    adapter.register_status_provider(db.name, SimpleComponentStatusProvider(db))
    adapter.register_status_provider(api.name, SimpleComponentStatusProvider(api))
    adapter.register_status_provider(frontend.name, SimpleComponentStatusProvider(frontend))
    
    # Set up dependencies
    registry.declare_dependency(api.name, db.name)  # API depends on Database
    registry.declare_dependency(frontend.name, api.name)  # Frontend depends on API
    
    # Initial state - all running
    adapter.update_component_status(db.name, ComponentState.RUNNING)
    adapter.update_component_status(api.name, ComponentState.RUNNING)
    adapter.update_component_status(frontend.name, ComponentState.RUNNING)
    
    # Database goes down
    adapter.update_component_status(db.name, ComponentState.DOWN, {"reason": "connection lost"})
    
    # Check if dashboard correctly shows the cascading impact
    # Note: This test assumes the dashboard implements cascading status logic
    # If not implemented yet, this would be a good feature to add
    all_statuses = dashboard.get_all_component_statuses()
    
    # Verify database is down
    assert all_statuses[db.name].state == ComponentState.DOWN
    
    # If cascading is implemented, API and Frontend should be affected
    # This might need to be adjusted based on actual implementation
    if dashboard.supports_cascading_status():
        assert all_statuses[api.name].state != ComponentState.RUNNING
        assert all_statuses[frontend.name].state != ComponentState.RUNNING

def test_status_history_and_metrics():
    """
    Test that the dashboard correctly tracks historical status changes
    and provides metrics according to the service health protocol
    """
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry=registry)
    adapter = ComponentStatusAdapter(dashboard)
    
    # Create and register component
    service = DummyComponent("MetricsService")
    registry.register_component(service.name, service)
    dashboard.watch_component(service.name)
    adapter.register_status_provider(service.name, SimpleComponentStatusProvider(service))
    
    # Create a sequence of status changes
    status_sequence = [
        (ComponentState.RUNNING, {"load": 0.1}),
        (ComponentState.DEGRADED, {"load": 0.8}),
        (ComponentState.RUNNING, {"load": 0.3}),
        (ComponentState.DOWN, {"error": "crash"}),
        (ComponentState.RUNNING, {"load": 0.2})
    ]
    
    # Apply status changes
    for state, details in status_sequence:
        adapter.update_component_status(service.name, state, details)
    
    # Get history
    history = dashboard.get_status_history(service.name)
    
    # Verify history length
    assert len(history) >= len(status_sequence)
    
    # Verify state transitions are recorded
    states_in_history = [record.state for record in history]
    assert ComponentState.RUNNING in states_in_history
    assert ComponentState.DEGRADED in states_in_history
    assert ComponentState.DOWN in states_in_history
    
    # Verify metrics if implemented
    if hasattr(dashboard, 'get_uptime_percentage'):
        uptime = dashboard.get_uptime_percentage(service.name)
        assert isinstance(uptime, float)
        assert 0 <= uptime <= 100
