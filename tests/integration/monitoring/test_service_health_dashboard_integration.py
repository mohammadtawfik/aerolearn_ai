"""
Integration test for ServiceHealthDashboard (using correct status provider registration).

Location: /tests/integration/monitoring/test_service_health_dashboard_integration.py

Uses the shared test harness from /tests/helpers/test_monitoring_fixtures.py to provide
a real ComponentRegistry, SYSTEM_STATUS_TRACKER, and dashboard. Covers registration,
status changes, real-time update, and historical tracking.

Run with pytest.
"""

import pytest
from integrations.monitoring.component_status_adapter import ComponentState
from tests.helpers.test_monitoring_fixtures import make_test_monitoring_fixtures

@pytest.fixture
def monitoring_setup():
    # Provides (registry, tracker, dashboard, SimpleComponentStatusProvider)
    return make_test_monitoring_fixtures()

def register_monitored_component(registry, tracker, StatusProvider, component):
    # Register both in registry and with tracker
    registry.register_component(component.name, component)
    tracker.register_status_provider(component.name, StatusProvider(component))

def test_registration_and_status_update(monitoring_setup):
    registry, tracker, dashboard, StatusProvider = monitoring_setup

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
        register_monitored_component(registry, tracker, StatusProvider, comp)

    dashboard.watch_component(db_service.name)
    dashboard.watch_component(api_gateway.name)
    dashboard.watch_component(analytics.name)

    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["DBService"].state == ComponentState.RUNNING
    assert all_statuses["APIGateway"].state == ComponentState.RUNNING
    assert all_statuses["AnalyticsEngine"].state == ComponentState.RUNNING

    # Change APIGateway to DEGRADED
    api_gateway.state = ComponentState.DEGRADED
    tracker.update_component_status(api_gateway.name)
    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["APIGateway"].state == ComponentState.DEGRADED

    # Change AnalyticsEngine to DOWN
    analytics.state = ComponentState.DOWN
    tracker.update_component_status(analytics.name)
    all_statuses = dashboard.get_all_component_statuses()
    assert all_statuses["AnalyticsEngine"].state == ComponentState.DOWN

def test_historical_uptime_tracking(monitoring_setup):
    registry, tracker, dashboard, StatusProvider = monitoring_setup
    class TestComponent:
        def __init__(self, name):
            self.name = name
            self.state = ComponentState.RUNNING
            self.component_id = name
    runner = TestComponent("TaskRunner")
    register_monitored_component(registry, tracker, StatusProvider, runner)
    dashboard.watch_component(runner.name)

    states = [ComponentState.RUNNING, ComponentState.DEGRADED, ComponentState.RUNNING, ComponentState.DOWN]
    for state in states:
        runner.state = state
        tracker.update_component_status(runner.name)

    hist = dashboard.get_status_history("TaskRunner")
    assert hist, "History should not be empty."
    assert any(rec.state == ComponentState.DOWN for rec in hist)

def test_real_time_status_update(monitoring_setup):
    registry, tracker, dashboard, StatusProvider = monitoring_setup
    class TestComponent:
        def __init__(self, name):
            self.name = name
            self.state = ComponentState.RUNNING
            self.component_id = name
    notifier = TestComponent("Notifier")
    register_monitored_component(registry, tracker, StatusProvider, notifier)
    dashboard.watch_component(notifier.name)

    notifier.state = ComponentState.RUNNING
    tracker.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.RUNNING
    notifier.state = ComponentState.DOWN
    tracker.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.DOWN
    notifier.state = ComponentState.RUNNING
    tracker.update_component_status(notifier.name)
    assert dashboard.status_for("Notifier") == ComponentState.RUNNING

# Optionally, test registered callbacks and alerting in later iterations
