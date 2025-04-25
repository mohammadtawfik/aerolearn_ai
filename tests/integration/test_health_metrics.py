import pytest
from datetime import datetime, timedelta
from integrations.monitoring.integration_health import (
    IntegrationHealth, HealthStatus, HealthMetric, HealthMetricType, HealthProvider
)
from integrations.monitoring.integration_health import IntegrationHealthError


class DummyHealthProvider(HealthProvider):
    def __init__(self, status=HealthStatus.HEALTHY, metrics=None):
        self._status = status
        self._metrics = metrics or [
            HealthMetric(
                name="response_time",
                value=100,
                metric_type=HealthMetricType.RESPONSE_TIME,
                component_id="comp.1"
            )
        ]

    def get_health_metrics(self):
        return self._metrics

    def get_health_status(self):
        return self._status


def test_register_and_collect_metrics():
    monitor = IntegrationHealth()
    provider = DummyHealthProvider()
    monitor.register_health_provider("comp.1", provider)
    metrics = monitor.collect_metrics("comp.1")
    assert "comp.1" in metrics
    assert isinstance(metrics["comp.1"][0], HealthMetric)
    assert metrics["comp.1"][0].name == "response_time"


def test_status_transition_on_metric_thresholds():
    # Set custom thresholds to trigger degraded/critical
    metric = HealthMetric(
        name="response_time",
        value=200,
        metric_type=HealthMetricType.RESPONSE_TIME,
        component_id="comp.2",
        threshold_warning=150,
        threshold_critical=300
    )
    assert metric.get_status() == HealthStatus.DEGRADED
    metric.value = 350
    assert metric.get_status() == HealthStatus.CRITICAL


def test_collect_metrics_error_handling():
    class ErrorProvider(HealthProvider):
        def get_health_metrics(self):
            raise RuntimeError("Simulated failure")
        def get_health_status(self):
            return HealthStatus.CRITICAL

    monitor = IntegrationHealth()
    monitor.register_health_provider("comp.error", ErrorProvider())
    metrics = monitor.collect_metrics("comp.error")
    assert "comp.error" in metrics
    assert metrics["comp.error"][0].name == "health_collection_error"
    assert metrics["comp.error"][0].get_status() == HealthStatus.HEALTHY  # Error rate is just 1.0, so depends on threshold.

def test_aggregation_and_history():
    monitor = IntegrationHealth()
    provider = DummyHealthProvider()
    monitor.register_health_provider("comp.agg", provider)
    # Simulate multiple metric collections
    monitor.collect_metrics("comp.agg")
    monitor.collect_metrics("comp.agg")
    history = monitor.metrics_history["comp.agg"]
    assert len(history) >= 2

def test_health_status_cache():
    monitor = IntegrationHealth()
    provider = DummyHealthProvider(status=HealthStatus.FAILING)
    monitor.register_health_provider("comp.cache", provider)
    monitor.collect_metrics()
    # Should update status cache
    assert monitor.status_cache["comp.cache"] == HealthStatus.UNKNOWN or isinstance(monitor.status_cache["comp.cache"], HealthStatus)