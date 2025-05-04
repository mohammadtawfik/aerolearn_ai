import pytest
from datetime import datetime, timedelta
from app.core.monitoring.metrics import (
    SystemMetricsManager, PerformanceAnalyzer, ServiceHealthDashboard, MetricType
)
from integrations.registry.component_registry import ComponentRegistry, Component
from integrations.registry.component_state import ComponentState

@pytest.fixture
def setup_components():
    registry = ComponentRegistry()
    api_component = registry.register_component("API", description="API Service", version="1.0", state=ComponentState.RUNNING)
    db_component = registry.register_component("Database", description="DB Service", version="2.1", state=ComponentState.RUNNING)
    return registry, api_component, db_component

@pytest.fixture
def perf_analyzer():
    return PerformanceAnalyzer()

@pytest.fixture
def metrics_manager():
    return SystemMetricsManager()

@pytest.fixture
def dashboard():
    return ServiceHealthDashboard()

def test_component_benchmark_recording(setup_components, perf_analyzer):
    """
    The system must support benchmarking and retrieval of component performance over time.
    """
    registry, api_component, _ = setup_components
    # Simulate benchmark: e.g., "processing time", "requests/sec"
    perf_analyzer.benchmark_component("API", "requests_per_second", 1097.2)
    perf_analyzer.benchmark_component("API", "avg_latency_ms", 40.7)
    # Check that metrics can be retrieved
    metrics = perf_analyzer.get_resource_utilization("API")
    assert isinstance(metrics, dict)
    assert metrics["requests_per_second"] == 1097.2
    assert metrics["avg_latency_ms"] == 40.7

def test_cross_component_transaction_timing(setup_components, perf_analyzer):
    """
    The system must correctly time transactions that span multiple components.
    """
    registry, api_component, db_component = setup_components
    # Simulate transaction flow: API → DB
    transaction_id = "txn-001"
    start = datetime.utcnow()
    api_duration = 15.5  # ms
    db_duration = 32.2   # ms
    perf_analyzer.measure_transaction_flow(
        transaction_id=transaction_id,
        component_timings={
            "API": api_duration,
            "Database": db_duration,
        },
        started_at=start,
        completed_at=start + timedelta(milliseconds=api_duration + db_duration)
    )
    txn_metrics = perf_analyzer.get_transaction_metrics(transaction_id)
    assert txn_metrics["components"] == ["API", "Database"]
    assert abs(txn_metrics["total_duration_ms"] - (api_duration + db_duration)) < 1e-2

def test_resource_utilization_tracking(setup_components, perf_analyzer):
    """
    The system must aggregate, track, and return component resource utilization metrics.
    """
    registry, api_component, _ = setup_components
    # Report resource metrics at different timestamps
    now = datetime.utcnow()
    metrics_seq = [
        {"cpu_pct": 24.5, "mem_mb": 400},
        {"cpu_pct": 35.0, "mem_mb": 415},
        {"cpu_pct": 67.2, "mem_mb": 500}
    ]
    for record in metrics_seq:
        perf_analyzer.benchmark_component("API", "cpu_pct", record["cpu_pct"])
        perf_analyzer.benchmark_component("API", "mem_mb", record["mem_mb"])
    hist = perf_analyzer.get_resource_history("API")  # Expects list/dict of history entries
    assert isinstance(hist, list)
    # Should have recorded multiple entries with increasing CPU/mem
    cpu_values = [entry["cpu_pct"] for entry in hist if "cpu_pct" in entry]
    mem_values = [entry["mem_mb"] for entry in hist if "mem_mb" in entry]
    assert max(cpu_values) > min(cpu_values)
    assert max(mem_values) > min(mem_values)

def test_performance_bottleneck_detection_and_alerting(setup_components, perf_analyzer, dashboard):
    """
    If a component's performance drops below a threshold, it should be flagged, 
    and an alert should trigger for the dashboard (state change to DEGRADED or FAILED).
    """
    registry, api_component, db_component = setup_components
    alerts = []
    # Register alert callback to dashboard (follows /architecture/health_monitoring_protocol.md)
    def alert_handler(component_id, state):
        alerts.append((component_id, state.name))
    dashboard.register_alert_callback(alert_handler)

    # Simulate bottleneck: API latency spikes
    perf_analyzer.benchmark_component("API", "avg_latency_ms", 984.0)  # Far above normal
    dashboard.update_component_status("API", ComponentState.DEGRADED, metrics={"avg_latency_ms": 984.0})

    # System should emit an alert for the API going DEGRADED
    assert ("API", "DEGRADED") in alerts
    # Simulate recovery: API back to RUNNING
    dashboard.update_component_status("API", ComponentState.RUNNING, metrics={"avg_latency_ms": 42.1})
    # Should not re-emit DEGRADED alert unless another drop
    alerts.clear()
    dashboard.update_component_status("API", ComponentState.DEGRADED, metrics={"avg_latency_ms": 1110.0})
    assert ("API", "DEGRADED") in alerts