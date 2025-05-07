import pytest

from integrations.monitoring.component_status_adapter import (
    ComponentState,
    ServiceHealthDashboard,
)
from integrations.registry.component_registry import ComponentRegistry

def test_monitoring_polling_interface_and_callback():
    """Monitoring subsystem exposes a polling/callback interface for status changes per protocol."""
    registry = ComponentRegistry()
    dashboard = ServiceHealthDashboard(registry)
    events = []

    def status_callback(cid, status):
        events.append((cid, status.state))

    dashboard.register_status_callback(status_callback)
    cid = 'endpoint'
    registry.register_component({'component_id': cid})
    dashboard.update_component_status(cid, ComponentState.HEALTHY, {})
    dashboard.update_component_status(cid, ComponentState.DEGRADED, {})

    assert events[0][0] == cid and events[0][1] == ComponentState.HEALTHY
    assert events[1][0] == cid and events[1][1] == ComponentState.DEGRADED

def test_programmatic_testability_and_reset_hooks():
    """Protocols require explicit test/reset hooks for isolation and functional validation."""
    registry1 = ComponentRegistry()
    dashboard1 = ServiceHealthDashboard(registry1)
    cid = 'resettable'
    registry1.register_component({'component_id': cid})
    dashboard1.update_component_status(cid, ComponentState.HEALTHY, {})
    dashboard1.reset_for_test()
    assert cid not in dashboard1.get_all_component_statuses()