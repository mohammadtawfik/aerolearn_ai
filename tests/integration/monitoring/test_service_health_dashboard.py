"""
Integration tests for the Service Health Dashboard.
Day 19 plan: Verifies component status monitoring, dependency visualization,
real-time status updates, historical uptime tracking, and documentation presence.
Tests protocol compliance for registration, state transitions, dependency tracking,
alerting, and audit history.
"""

import os
import pytest
from datetime import datetime, timedelta

# Import the monitoring dashboard/main service health logic under test.
from app.core.monitoring.metrics import ServiceHealthDashboard, StatusRecord
from integrations.registry.component_registry import ComponentRegistry, ComponentState
from integrations.monitoring.component_status_adapter import (
    register_with_status_tracker,
    SYSTEM_STATUS_TRACKER,
    ComponentStatusAdapter,
)

@pytest.fixture
def component_registry():
    """Get a (singleton) component registry."""
    return ComponentRegistry()

@pytest.fixture
def dashboard():
    """Service health dashboard using shared tracker."""
    return ServiceHealthDashboard()

def test_component_status_reporting(dashboard, component_registry):
    """
    Verify all registered components report their status, dashboard displays correct info.
    """
    db = component_registry.register_component("TestDB", state=ComponentState.RUNNING)
    ai = component_registry.register_component("TestAI", state=ComponentState.DOWN)
    register_with_status_tracker(db)
    register_with_status_tracker(ai)
    SYSTEM_STATUS_TRACKER.update_component_status("TestDB")
    SYSTEM_STATUS_TRACKER.update_component_status("TestAI")
    statuses = dashboard.get_all_component_statuses()
    assert statuses["TestDB"].state == ComponentState.RUNNING
    assert statuses["TestAI"].state == ComponentState.DOWN

def test_dependency_visualization(dashboard, component_registry):
    """
    Dashboard reflects dependencies (integration graph).
    """
    api = component_registry.register_component("API", state=ComponentState.RUNNING)
    db = component_registry.register_component("DB", state=ComponentState.RUNNING)
    register_with_status_tracker(api)
    register_with_status_tracker(db)
    component_registry.declare_dependency("API", depends_on="DB")
    SYSTEM_STATUS_TRACKER.update_component_status("API")
    SYSTEM_STATUS_TRACKER.update_component_status("DB")
    graph = dashboard.get_dependency_graph()
    assert "API" in graph
    assert "DB" in graph["API"], "API should depend on DB"

def test_real_time_status_updates(dashboard, component_registry):
    """
    Dashboard updates instantly when a component state changes.
    """
    cache = component_registry.register_component("Cache", state=ComponentState.RUNNING)
    register_with_status_tracker(cache)
    dashboard.watch_component("Cache")
    SYSTEM_STATUS_TRACKER.update_component_status("Cache")
    # Change component state in registry
    component_registry.set_component_state("Cache", ComponentState.DOWN)
    SYSTEM_STATUS_TRACKER.update_component_status("Cache")
    assert dashboard.status_for("Cache") == ComponentState.DOWN

def test_historical_uptime_tracking(dashboard, component_registry):
    """
    Dashboard maintains/exposes a history of component status.
    """
    scheduler = component_registry.register_component("Scheduler", state=ComponentState.RUNNING)
    register_with_status_tracker(scheduler)
    dashboard.watch_component("Scheduler")
    SYSTEM_STATUS_TRACKER.update_component_status("Scheduler")
    component_registry.set_component_state("Scheduler", ComponentState.DOWN)
    SYSTEM_STATUS_TRACKER.update_component_status("Scheduler")
    component_registry.set_component_state("Scheduler", ComponentState.RUNNING)
    SYSTEM_STATUS_TRACKER.update_component_status("Scheduler")
    history = dashboard.get_status_history("Scheduler")
    running_count = sum(
        1 for entry in history if getattr(entry, 'state', None) == ComponentState.RUNNING or getattr(entry, 'state', None) == "RUNNING"
    )
    assert running_count >= 2
    down_exists = any(
        getattr(entry, 'state', None) == ComponentState.DOWN or getattr(entry, 'state', None) == "DOWN"
        for entry in history
    )
    assert down_exists

def test_health_status_integration(dashboard, component_registry):
    """
    All components report their status to the dashboard; dashboard aggregates correctly.
    """
    components = {
        "API": ComponentState.RUNNING,
        "Database": ComponentState.RUNNING,
        "Cache": ComponentState.DEGRADED,
        "Queue": ComponentState.DOWN
    }
    for name, state in components.items():
        comp = component_registry.register_component(name, state=state)
        register_with_status_tracker(comp)
        SYSTEM_STATUS_TRACKER.update_component_status(name)
    statuses = dashboard.get_all_component_statuses()
    for name, state in components.items():
        assert name in statuses
        assert statuses[name].state == state

def test_component_health_protocol_documentation_exists():
    """
    Protocol documentation for health monitoring must exist and be discoverable.
    """
    path1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../docs/architecture/service_health_protocol.md"))
    path2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../docs/api/service_health_protocol.md"))
    assert os.path.exists(path1) or os.path.exists(path2)

@pytest.fixture
def status_adapter(dashboard):
    """Component status adapter for protocol testing."""
    return ComponentStatusAdapter(dashboard=dashboard)

def test_protocol_state_transition_and_audit_trail(dashboard, component_registry):
    """
    Verify state transitions are properly tracked with audit trail.
    Protocol compliance: Components must maintain state history with timestamps.
    """
    # Register a component for testing
    component_id = "protocol.test.component"
    comp = component_registry.register_component(component_id, state=ComponentState.UNKNOWN)
    register_with_status_tracker(comp)
    
    # Initial state should be UNKNOWN
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    status = dashboard.status_for(component_id)
    assert status == ComponentState.UNKNOWN
    
    # State change to RUNNING
    component_registry.set_component_state(component_id, ComponentState.RUNNING)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    status = dashboard.status_for(component_id)
    assert status == ComponentState.RUNNING
    
    # State change to DEGRADED
    component_registry.set_component_state(component_id, ComponentState.DEGRADED)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    status = dashboard.status_for(component_id)
    assert status == ComponentState.DEGRADED
    
    # State change to DOWN and then back to RUNNING
    component_registry.set_component_state(component_id, ComponentState.DOWN)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    component_registry.set_component_state(component_id, ComponentState.RUNNING)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    # Check history contains all state transitions
    history = dashboard.get_status_history(component_id)
    states = [getattr(record, 'state', None) for record in history]
    
    assert ComponentState.UNKNOWN in states or "UNKNOWN" in states
    assert ComponentState.RUNNING in states or "RUNNING" in states
    assert ComponentState.DEGRADED in states or "DEGRADED" in states
    assert ComponentState.DOWN in states or "DOWN" in states
    
    # All status records must be timestamped
    for record in history:
        assert hasattr(record, 'timestamp')
        if isinstance(record, StatusRecord):
            assert isinstance(record.timestamp, datetime)

def test_protocol_dependency_tracking_and_impact(dashboard, component_registry):
    """
    Verify dependency tracking and impact analysis.
    Protocol compliance: System must track dependencies and analyze impact.
    """
    # Register components with dependency
    main_component = "main.service"
    dependent_component = "dependent.service"
    
    comp1 = component_registry.register_component(main_component, state=ComponentState.RUNNING)
    comp2 = component_registry.register_component(dependent_component, state=ComponentState.RUNNING)
    register_with_status_tracker(comp1)
    register_with_status_tracker(comp2)
    
    # Declare dependency
    component_registry.declare_dependency(main_component, depends_on=dependent_component)
    
    # Update statuses
    SYSTEM_STATUS_TRACKER.update_component_status(main_component)
    SYSTEM_STATUS_TRACKER.update_component_status(dependent_component)
    
    # Check dependency graph
    graph = dashboard.get_dependency_graph()
    assert main_component in graph
    assert dependent_component in graph[main_component], f"{main_component} should depend on {dependent_component}"
    
    # Test impact analysis - when dependent service goes down
    component_registry.set_component_state(dependent_component, ComponentState.DOWN)
    SYSTEM_STATUS_TRACKER.update_component_status(dependent_component)
    
    # The main service should be impacted (in a real system, this would trigger alerts)
    impacted = component_registry.get_impacted_components(dependent_component)
    assert main_component in impacted, f"{dependent_component} outage should impact {main_component}"

def test_protocol_alert_callback_on_critical_state(dashboard, component_registry):
    """
    Verify alert callbacks are triggered on critical state changes.
    Protocol compliance: System must support alert callbacks for state transitions.
    """
    alert_triggered = []
    component_id = "alertable.component"
    
    # Register alert callback
    def alert_handler(comp_id, state):
        alert_triggered.append((comp_id, state))
    
    dashboard.register_alert_callback(alert_handler)
    
    # Register component
    comp = component_registry.register_component(component_id, state=ComponentState.RUNNING)
    register_with_status_tracker(comp)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    # Transition to DEGRADED (should trigger alert)
    component_registry.set_component_state(component_id, ComponentState.DEGRADED)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    assert len(alert_triggered) > 0
    assert alert_triggered[-1][0] == component_id
    assert alert_triggered[-1][1] == ComponentState.DEGRADED
    
    # Transition to DOWN
    prev_count = len(alert_triggered)
    component_registry.set_component_state(component_id, ComponentState.DOWN)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    # Transition back to RUNNING and again to DEGRADED (should trigger alert again)
    component_registry.set_component_state(component_id, ComponentState.RUNNING)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    component_registry.set_component_state(component_id, ComponentState.DEGRADED)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    assert len(alert_triggered) > prev_count
    assert alert_triggered[-1][0] == component_id
    assert alert_triggered[-1][1] == ComponentState.DEGRADED

def test_protocol_component_registration_lifecycle(dashboard, component_registry):
    """
    Verify component registration and unregistration lifecycle.
    Protocol compliance: Components must support full lifecycle management.
    """
    # Register component
    component_id = "lifecycle.test.component"
    comp = component_registry.register_component(component_id, state=ComponentState.RUNNING)
    register_with_status_tracker(comp)
    SYSTEM_STATUS_TRACKER.update_component_status(component_id)
    
    # Verify it's in the dashboard
    statuses = dashboard.get_all_component_statuses()
    assert component_id in statuses
    
    # Unregister component
    component_registry.unregister_component(component_id)
    
    # Component should no longer be in dependency graph
    graph = component_registry.get_dependency_graph()
    assert component_id not in graph
    assert all(component_id not in deps for deps in graph.values())
