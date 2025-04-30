"""
Admin System Config & Monitoring UI — AeroLearn AI
Save at: /app/ui/admin/system_config.py

Connects:
- SystemSettingsManager (from core.monitoring)
- SystemMetricsManager (from core.monitoring)
Provides:
- UI for viewing/editing validated system settings
- Interactive component dependency visualization (stub for integration)
- Health metrics/alerts dashboard
"""

from app.core.monitoring.settings_manager import system_settings
from app.core.monitoring.metrics import (
    system_metrics, MetricType, AlertLevel, Metric, MetricAlert
)
# If using Qt, PySide2, or Tkinter — below is a logic/controller stub, not a specific GUI framework.

class AdminSystemConfigController:
    """
    Controller for system settings/config and system monitoring dashboard.
    Connect UI widgets to settings_manager and metrics.
    """

    def get_all_settings(self):
        """Return dict of all current setting display values."""
        return system_settings.all()

    def update_setting(self, key, value):
        """Update a setting through the validated manager."""
        system_settings.set(key, value)
        return system_settings.all()

    def get_all_metrics(self):
        """Get a snapshot of all system metrics."""
        return {k: v.to_dict() for k, v in system_metrics.get_all_metrics().items()}

    def get_alerts(self):
        """Return real alert states by checking manager's threshold registrations."""
        alerts = []
        all_metrics = system_metrics.get_all_metrics()
        # Check against registered alerts in the manager
        for metric in all_metrics.values():
            triggered_levels = []
            for alert in system_metrics.get_alerts_for_metric(metric.name):
                if alert.level == AlertLevel.WARNING and metric.value >= alert.threshold:
                    triggered_levels.append(AlertLevel.WARNING.name)
                elif alert.level == AlertLevel.CRITICAL and metric.value >= alert.threshold:
                    triggered_levels.append(AlertLevel.CRITICAL.name)
            for level in triggered_levels:
                alerts.append({"name": metric.name, "level": level})
        return alerts

    def get_component_dependency_graph(self):
        """
        Returns data suitable for a frontend graph widget.
        Actual visualization wiring is frontend-specific.
        """
        # Dependency graph data — here as a stub; real impl would analyze live component registry.
        # Example:
        return {
            "nodes": [
                {"id": "api", "label": "API Server"},
                {"id": "db", "label": "DB"},
                {"id": "ai", "label": "AI Subsystem"},
                {"id": "ui", "label": "UI"},
            ],
            "edges": [
                {"source": "ui", "target": "api"},
                {"source": "api", "target": "db"},
                {"source": "api", "target": "ai"},
            ],
        }

    def apply_dependency_theme(self, theme_name):
        """Set theme for dependency graph in settings."""
        system_settings.set("dependency_visual_theme", theme_name)

    def simulate_metric_report(self, name, type_, value):
        """For testing/demo: report a metric. Accept MetricType, int, or str for type_."""
        metric_type = type_
        if not isinstance(type_, MetricType):
            # Accept int (index into enum) or string (enum member name)
            if isinstance(type_, int):
                # If not a valid MetricType index, fallback to CUSTOM
                try:
                    metric_type = list(MetricType)[type_]
                except IndexError:
                    metric_type = MetricType.CUSTOM
            elif isinstance(type_, str):
                try:
                    metric_type = MetricType[type_.upper()]
                except KeyError:
                    metric_type = MetricType.CUSTOM
        system_metrics.report_metric(name, metric_type, value)

    def register_metric_alert(self, metric_name, level, threshold):
        """Register an alert on a metric."""
        if not isinstance(level, AlertLevel):
            if isinstance(level, str):
                try:
                    level = AlertLevel[level.upper()]
                except KeyError:
                    raise ValueError("level must be AlertLevel or one of: normal, warning, critical")
        alert = MetricAlert(metric_name, level, threshold)
        system_metrics.register_alert(alert)

# If a GUI framework is in use, connect this controller to the UI widgets.

# Singleton for external (test/UI) use
system_config_controller = AdminSystemConfigController()

# Example usage (would be button handlers or API endpoints in real UI):
if __name__ == "__main__":
    # Demo: Print all settings and metrics
    print("Current Settings:", system_config_controller.get_all_settings())
    print("Current Metrics:", system_config_controller.get_all_metrics())
    # Test dependency graph data
    print("Dependency Graph:", system_config_controller.get_component_dependency_graph())
