"""
Test Suite: Integration Status Monitoring Tests
Location: /tests/integration/monitoring/test_integration_status_monitoring.py

Covers Day 19 Plan Task 3.6.3:
- Integration point registry
- Transaction logging
- Failure detection
- Performance monitoring
- Real-time status monitoring
- Documentation checks

Targets integration points and monitoring modules (e.g. integrations/monitoring/, registry/, etc.)
"""

import pytest
import os
import time
from integrations.monitoring.integration_health import IntegrationMonitor, IntegrationPointRegistry

@pytest.fixture
def point_registry():
    """Ensure a clean registry for every test run"""
    registry = IntegrationPointRegistry()
    # Clear any existing points to ensure test isolation
    registry.clear_all_points()
    return registry

@pytest.fixture
def monitor():
    """Ensure a fresh monitor instance"""
    monitor = IntegrationMonitor()
    # Clear any existing transactions to ensure test isolation
    monitor.clear_all_transactions()
    return monitor

def test_integration_point_registry_tracks_points(point_registry):
    """Should register and retrieve all integration points in the system."""
    # Register multiple integration points with metadata
    point_registry.register_integration_point("database", {"type": "sql", "version": "1.1"})
    point_registry.register_integration_point("ai_service", {"type": "ml", "version": "3.2"})
    point_registry.register_integration_point("payment_gateway", {"type": "api", "version": "2.0"})
    
    # Verify all points are tracked
    points = point_registry.get_all_points()
    assert len(points) == 3
    assert "database" in points
    assert "ai_service" in points
    assert "payment_gateway" in points
    
    # Verify metadata is correctly stored
    db_details = point_registry.get_point_details("database")
    ai_details = point_registry.get_point_details("ai_service")
    payment_details = point_registry.get_point_details("payment_gateway")
    
    assert db_details["metadata"]["type"] == "sql"
    assert ai_details["metadata"]["version"] == "3.2"
    assert payment_details["metadata"]["type"] == "api"

def test_transaction_logging_at_integration_points(monitor):
    """Should log all transactions at integration points."""
    # Log multiple transactions with different statuses and durations
    txn_id1 = monitor.log_transaction("database", True, duration_ms=50)
    txn_id2 = monitor.log_transaction("ai_service", True, duration_ms=120)
    txn_id3 = monitor.log_transaction("payment_gateway", False, duration_ms=200)
    
    # Verify transaction details are correctly stored
    db_tx = monitor.get_transaction(txn_id1)
    ai_tx = monitor.get_transaction(txn_id2)
    payment_tx = monitor.get_transaction(txn_id3)
    
    assert db_tx["point"] == "database"
    assert db_tx["success"] is True
    assert db_tx["duration_ms"] == 50
    assert db_tx["timestamp"] is not None
    
    assert ai_tx["point"] == "ai_service"
    assert ai_tx["duration_ms"] == 120
    
    assert payment_tx["point"] == "payment_gateway"
    assert payment_tx["success"] is False
    
    # Test retrieving transactions by integration point
    db_txns = monitor.get_transactions_by_point("database")
    assert len(db_txns) == 1
    assert db_txns[0]["id"] == txn_id1

def test_integration_failure_detection(monitor):
    """Should detect/report failures at integration points."""
    # Log multiple failures with different error details
    txn_id1 = monitor.log_transaction("ai_service", False, duration_ms=200)
    monitor.report_failure("ai_service", error="prediction failed", severity="high")
    
    txn_id2 = monitor.log_transaction("database", False, duration_ms=150)
    monitor.report_failure("database", error="connection timeout", severity="critical")
    
    # Test failure detection and reporting
    ai_failures = monitor.get_recent_failures("ai_service")
    db_failures = monitor.get_recent_failures("database")
    
    assert len(ai_failures) >= 1
    assert "error" in ai_failures[-1]
    assert ai_failures[-1]["error"] == "prediction failed"
    assert ai_failures[-1]["severity"] == "high"
    
    assert len(db_failures) >= 1
    assert db_failures[-1]["error"] == "connection timeout"
    assert db_failures[-1]["severity"] == "critical"
    
    # Test failure rate calculation
    monitor.log_transaction("database", True, duration_ms=50)
    monitor.log_transaction("database", True, duration_ms=60)
    
    failure_rate = monitor.get_failure_rate("database")
    assert failure_rate == 1/3  # 1 failure out of 3 transactions

def test_real_time_monitoring_of_status_changes(point_registry, monitor):
    """Real-time monitoring should surface integration issues as they occur."""
    # Register integration point with health threshold
    point_registry.register_integration_point("ml_backend", {
        "type": "ml", 
        "health_threshold": 0.8,  # 80% success rate required for "healthy" status
        "latency_threshold_ms": 500
    })
    
    # Log successful transactions
    for i in range(8):
        monitor.log_transaction("ml_backend", True, duration_ms=30 + i * 10)
    
    # Check initial health status
    initial_status = monitor.get_health_status("ml_backend")
    assert initial_status["status"] == "healthy"
    assert initial_status["success_rate"] >= 0.8
    
    # Log failures to trigger status change
    for i in range(3):
        monitor.log_transaction("ml_backend", False, duration_ms=999)
    
    # Verify status change is detected immediately
    updated_status = monitor.get_health_status("ml_backend")
    assert updated_status["status"] == "degraded"
    assert updated_status["success_rate"] < 0.8
    
    # Test alert generation
    alerts = monitor.get_active_alerts()
    assert len(alerts) >= 1
    assert any(alert["integration_point"] == "ml_backend" for alert in alerts)

def test_integration_performance_monitoring(monitor):
    """Should provide metrics and analysis for integration performance."""
    # Log transactions with varying performance characteristics
    for i in range(10):
        monitor.log_transaction("api_gateway", True, duration_ms=30 + i * 20)
    
    # Log some slow transactions
    monitor.log_transaction("api_gateway", True, duration_ms=500)
    monitor.log_transaction("api_gateway", True, duration_ms=600)
    
    # Get performance metrics
    perf_stats = monitor.get_performance_stats("api_gateway")
    
    # Basic metrics validation
    assert perf_stats['count'] == 12
    assert perf_stats['avg_duration_ms'] > 0
    assert perf_stats['success_rate'] == 1.0
    
    # Advanced metrics validation
    assert 'p95_duration_ms' in perf_stats
    assert 'p99_duration_ms' in perf_stats
    assert 'min_duration_ms' in perf_stats
    assert 'max_duration_ms' in perf_stats
    assert perf_stats['max_duration_ms'] >= 600
    
    # Test performance trend analysis
    trend = monitor.get_performance_trend("api_gateway", time_window_minutes=60)
    assert 'trend_direction' in trend
    assert trend['trend_direction'] in ['improving', 'stable', 'degrading']

def test_integration_monitoring_documentation_coverage():
    """Validate documentation coverage for integration monitoring architecture."""
    # Check for existence of required documentation
    assert os.path.exists("docs/architecture/integration_monitoring.md") or \
           os.path.exists("docs/api/integration_monitoring.md"), \
           "Integration monitoring documentation is missing"
    
    # If documentation exists, verify it contains required sections
    doc_path = "docs/architecture/integration_monitoring.md" \
        if os.path.exists("docs/architecture/integration_monitoring.md") \
        else "docs/api/integration_monitoring.md"
    
    with open(doc_path, 'r') as doc_file:
        content = doc_file.read().lower()
        
        # Check for required documentation sections
        assert "registry" in content, "Documentation missing registry section"
        assert "transaction" in content, "Documentation missing transaction logging section"
        assert "failure" in content, "Documentation missing failure detection section"
        assert "performance" in content, "Documentation missing performance monitoring section"
        assert "real-time" in content or "realtime" in content, \
               "Documentation missing real-time monitoring section"
