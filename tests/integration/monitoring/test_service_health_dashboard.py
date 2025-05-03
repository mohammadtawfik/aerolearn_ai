"""
Integration tests for the Service Health Dashboard.
Day 19 plan: Verifies component status monitoring, dependency visualization,
real-time status updates, historical uptime tracking, and documentation presence.
"""

import os
import pytest

# Import the monitoring dashboard/main service health logic under test.
from app.core.monitoring.metrics import ServiceHealthDashboard
from integrations.registry.component_registry import ComponentRegistry, ComponentState
from integrations.monitoring.component_status_adapter import (
    register_with_status_tracker,
    SYSTEM_STATUS_TRACKER,
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
    assert os.path.exists("docs/architecture/service_health_protocol.md") or \
           os.path.exists("docs/api/service_health_protocol.md")
