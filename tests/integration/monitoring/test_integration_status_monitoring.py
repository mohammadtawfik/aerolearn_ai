"""
Integration Status Monitoring – Integration Tests
File Location: /tests/integration/monitoring/test_integration_status_monitoring.py

Covers Task 3.6.3 (Day 19 Plan), as specified by:
- /docs/architecture/service_health_protocol.md
- /docs/architecture/health_monitoring_protocol.md
- /docs/architecture/architecture_overview.md
- /docs/development/day19_plan.md
- /code_summary.md (module mapping/conventions)

Tests:
 - Integration point registry (register, list, info)
 - Transaction logging (success, failure, metadata)
 - Failure detection/alerting (event, callback contract)
 - Performance metrics (timings, throughput)
 - History and audit (historical query, event logging)
 - Protocol compliance (state/contract)

"""

import pytest
from datetime import datetime, timedelta

# Placeholder imports – must match actual doc-mapped source locations!
from app.core.monitoring.integration_monitor import IntegrationMonitor, IntegrationPointRegistry, IntegrationHealthEvent
from integrations.registry.component_registry import ComponentRegistry

@pytest.fixture
def integration_registry():
    return IntegrationPointRegistry()

@pytest.fixture
def monitor():
    return IntegrationMonitor()

def test_register_integration_point(integration_registry):
    integration_registry.register_integration_point("external_service_api", description="External Service API", version="1.0")
    points = integration_registry.get_all_points()
    assert "external_service_api" in points

def test_log_successful_transaction(monitor, integration_registry):
    integration_registry.register_integration_point("content_db")
    monitor.log_transaction("content_db", success=True, duration_ms=120, meta={"request_id": "testreq1"})
    tx = monitor.get_transaction("content_db")[-1]
    assert tx["success"] is True
    assert tx["duration_ms"] == 120
    assert tx["meta"]["request_id"] == "testreq1"

def test_log_failed_transaction_and_event(monitor, integration_registry):
    integration_registry.register_integration_point("ai_service")
    monitor.log_transaction("ai_service", success=False, duration_ms=250, meta={"error_msg": "Timeout"})
    failures = monitor.get_recent_failures("ai_service")
    assert len(failures) >= 1
    assert failures[-1]["error_msg"] == "Timeout"
    # Health event should be recorded as per protocol
    events = monitor.get_health_events("ai_service")
    assert any(isinstance(evt, IntegrationHealthEvent) for evt in events)

def test_performance_metrics(monitor, integration_registry):
    integration_registry.register_integration_point("course_api")
    for ms in [100, 200, 180]:
        monitor.log_transaction("course_api", success=True, duration_ms=ms)
    perf = monitor.get_performance_summary("course_api")
    assert perf["min_duration_ms"] == 100
    assert perf["max_duration_ms"] == 200
    assert perf["mean_duration_ms"] == pytest.approx((100 + 200 + 180) / 3)

def test_history_and_audit(monitor, integration_registry):
    now = datetime.utcnow()
    integration_registry.register_integration_point("sync_manager")
    monitor.log_transaction("sync_manager", success=True, duration_ms=50, meta={"ts": now})
    history = monitor.get_transaction_history("sync_manager", since=now - timedelta(minutes=10))
    assert any(tx["meta"].get("ts") == now for tx in history)

def test_alert_on_failure(monitor, integration_registry):
    alerts = []
    def alert_handler(point_id, state, error_msg=None):
        alerts.append((point_id, state, error_msg))
    monitor.register_alert_callback(alert_handler)
    integration_registry.register_integration_point("batch_uploader")
    monitor.log_transaction("batch_uploader", success=False, duration_ms=500, meta={"error_msg": "Bad Gateway"})
    # Protocol: Alert must be issued on failure/degraded state
    assert any(alert[0] == "batch_uploader" and alert[1] in ("FAILED", "DEGRADED") for alert in alerts)