"""
UNIT TESTS: Admin System Config/Monitoring
Save at: /tests/ui/test_system_config.py
"""

import pytest
from app.ui.admin.system_config import system_config_controller
from app.core.monitoring.settings_manager import SettingValidationError
from app.core.monitoring.metrics import MetricType, AlertLevel

def setup_module(module):
    # Register alerts for "memory" metric before related tests
    system_config_controller.register_metric_alert("memory", AlertLevel.WARNING, 60)
    system_config_controller.register_metric_alert("memory", AlertLevel.CRITICAL, 80)

def test_get_all_settings_defaults():
    settings = system_config_controller.get_all_settings()
    assert "max_upload_size_mb" in settings
    assert settings["max_upload_size_mb"] == 50  # default from schema

def test_update_setting_valid():
    prev = system_config_controller.get_all_settings()["max_upload_size_mb"]
    updated = system_config_controller.update_setting("max_upload_size_mb", 100)
    assert updated["max_upload_size_mb"] == 100
    # revert
    system_config_controller.update_setting("max_upload_size_mb", prev)

def test_update_setting_invalid():
    with pytest.raises(SettingValidationError):
        system_config_controller.update_setting("max_upload_size_mb", 10000)  # exceeds max

def test_get_all_metrics_report():
    system_config_controller.simulate_metric_report("cpu", MetricType.CPU_USAGE, 70)
    metrics = system_config_controller.get_all_metrics()
    assert "cpu" in metrics
    assert metrics["cpu"]["value"] == 70

def test_alerts_warnings_and_critical():
    system_config_controller.simulate_metric_report("memory", MetricType.MEMORY_USAGE, 70)
    warnings = system_config_controller.get_alerts()
    # Should create a warning or critical for "memory"
    found = any(alert["name"] == "memory" and alert["level"] in ["WARNING", "CRITICAL"] for alert in warnings)
    assert found

def test_dependency_graph_data():
    graph = system_config_controller.get_component_dependency_graph()
    assert "nodes" in graph
    assert "edges" in graph
    assert any(node["id"] == "api" for node in graph["nodes"])
