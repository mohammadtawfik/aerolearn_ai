# Monitoring Integration Test Harness Factory

from integrations.monitoring.component_status_adapter import (
    ComponentRegistry, SYSTEM_STATUS_TRACKER, SimpleComponentStatusProvider
)
from app.core.monitoring.metrics import ServiceHealthDashboard

def make_test_monitoring_fixtures():
    # Always use the same instances for every test
    registry = ComponentRegistry()
    tracker = SYSTEM_STATUS_TRACKER
    dashboard = ServiceHealthDashboard(status_tracker=tracker)
    return registry, tracker, dashboard, SimpleComponentStatusProvider