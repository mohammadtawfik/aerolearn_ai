"""
Integration tests for the Service Health Dashboard.
Day 19 plan: Verifies component status monitoring, dependency visualization,
real-time status updates, historical uptime tracking, and documentation presence.
Tests protocol compliance for registration, state transitions, dependency tracking,
alerting, and audit history.
"""

import pytest
from datetime import datetime, timedelta
from app.core.monitoring.ServiceHealthDashboard_Class import ServiceHealthDashboard
from integrations.registry.component_registry import ComponentRegistry
from integrations.monitoring.component_status_adapter import ComponentState

@pytest.fixture
def registry():
    # Each test gets a fresh registry (protocol: singleton pattern—reset between runs)
    reg = ComponentRegistry()
    reg.clear()  # assuming clear resets all state per protocol doc
    return reg

@pytest.fixture
def dashboard(registry):
    # Each test gets fresh dashboard
    dash = ServiceHealthDashboard(registry)
    return dash

def test_component_registration_and_initial_state(dashboard, registry):
    registry.register_component("compA", description="Test A", state=ComponentState.RUNNING)
    status = dashboard.status_for("compA")
    assert status == ComponentState.RUNNING

def test_status_update_and_real_time_sync(dashboard, registry):
    c = registry.register_component("compB", state=ComponentState.RUNNING)
    dashboard.update_component_status("compB", ComponentState.DEGRADED)
    status = dashboard.status_for("compB")
    assert status == ComponentState.DEGRADED
    all_status = dashboard.get_all_component_statuses()
    assert all_status["compB"] == ComponentState.DEGRADED

def test_dependency_graph_reflection(dashboard, registry):
    registry.register_component("compC", state=ComponentState.RUNNING)
    registry.register_component("compD", state=ComponentState.RUNNING)
    registry.declare_dependency("compC", "compD")
    deps = dashboard.get_dependency_graph()  # must reflect declared deps
    assert "compC" in deps and "compD" in deps["compC"]

def test_state_history_tracking(dashboard, registry):
    registry.register_component("compE", state=ComponentState.RUNNING)
    dashboard.update_component_status("compE", ComponentState.DEGRADED)
    dashboard.update_component_status("compE", ComponentState.RUNNING)
    history = dashboard.get_component_history("compE")
    # Should include at least 2 records, latest is RUNNING, previous is DEGRADED
    assert len(history) >= 2
    assert history[-1].state == ComponentState.RUNNING
    assert history[-2].state == ComponentState.DEGRADED
    assert hasattr(history[-1], "timestamp")

def test_alert_callback_triggers_on_threshold_only(dashboard, registry):
    registry.register_component("compF", state=ComponentState.RUNNING)
    triggered = []
    def alert_cb(comp_id, state):
        triggered.append((comp_id, state))
    dashboard.register_alert_callback(alert_cb)
    # No alert on RUNNING→RUNNING
    dashboard.update_component_status("compF", ComponentState.RUNNING)
    assert not triggered
    # Alert on RUNNING→DEGRADED
    dashboard.update_component_status("compF", ComponentState.DEGRADED)
    assert triggered == [("compF", ComponentState.DEGRADED)]
    # No redundant alert on repeated DEGRADED
    dashboard.update_component_status("compF", ComponentState.DEGRADED)
    assert triggered == [("compF", ComponentState.DEGRADED)]
    # Alert again on DEGRADED→RUNNING→DEGRADED
    dashboard.update_component_status("compF", ComponentState.RUNNING)
    dashboard.update_component_status("compF", ComponentState.DEGRADED)
    assert triggered.count(("compF", ComponentState.DEGRADED)) == 2

def test_legacy_status_listener_callback(dashboard, registry):
    registry.register_component("compG", state=ComponentState.RUNNING)
    listener_calls = []
    def legacy_listener(comp_id, state):
        listener_calls.append((comp_id, state))
    dashboard.register_status_listener(legacy_listener)
    dashboard.update_component_status("compG", ComponentState.DEGRADED)
    dashboard.update_component_status("compG", ComponentState.FAILED)
    assert listener_calls[0][1] == ComponentState.DEGRADED
    assert listener_calls[1][1] == ComponentState.FAILED

def test_metric_and_message_in_history_records(dashboard, registry):
    registry.register_component("compH", state=ComponentState.RUNNING)
    metrics = {"cpu_pct": 12.3, "mem_mb": 456, "error_count": 1}
    msg = "Custom message"
    dashboard.update_component_status("compH", ComponentState.DEGRADED, metrics=metrics, message=msg)
    history = dashboard.get_component_history("compH")
    last = history[-1]
    assert last.metrics == metrics
    assert last.message == msg

def test_removal_and_error_handling(dashboard, registry):
    registry.register_component("compI", state=ComponentState.RUNNING)
    registry.unregister_component("compI")
    assert "compI" not in dashboard.get_all_component_statuses()
    with pytest.raises(KeyError):
        dashboard.status_for("compI")
    # Update non-existent component
    with pytest.raises(Exception):
        dashboard.update_component_status("compI", ComponentState.DEGRADED)

def test_audit_trail_timestamp_and_order(dashboard, registry):
    registry.register_component("compJ", state=ComponentState.RUNNING)
    dashboard.update_component_status("compJ", ComponentState.DEGRADED)
    dashboard.update_component_status("compJ", ComponentState.FAILED)
    hist = dashboard.get_component_history("compJ")
    t0, t1, t2 = hist[0].timestamp, hist[1].timestamp, hist[-1].timestamp
    assert t0 <= t1 <= t2
    assert isinstance(t2, datetime)

def test_dashboard_consistency_after_registry_clear(dashboard, registry):
    registry.register_component("compK", state=ComponentState.RUNNING)
    registry.clear()
    assert "compK" not in dashboard.get_all_component_statuses()

