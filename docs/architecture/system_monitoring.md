# AeroLearn AI — System Monitoring & Configuration Architecture

_Saved at: `/docs/architecture/system_monitoring.md`_

---

## **Overview**

AeroLearn AI's admin subsystem integrates robust system configuration and monitoring tools, allowing administrators to:
- Visualize real-time component dependencies & health.
- Centrally manage and persist validated system settings.
- Define, monitor, and alert on a variety of operational and health metrics.
- Perform all operations through a unified admin UI with programmatic API access under the hood.

---

## **Module Structure**

- `/app/core/monitoring/settings_manager.py`: System configuration schema/manager (persistence & validation).
- `/app/core/monitoring/metrics.py`: Metrics registration, querying, alert threshold management.
- `/app/ui/admin/system_config.py`: Admin UI/controller entry for dependency graph visualization, settings, health dashboard.
- `/tests/ui/test_system_config.py`: Test suite for UI logic, config flows, metric/alert reporting.
- `system_settings.json` (auto-created): Persists settings in `/app/core/monitoring/`.

---

## **Admin UI Features**

1. **Component Dependency Graph**
   - Interactive, live graph (nodes: system components, edges: dependencies).
   - Data produced by `get_component_dependency_graph()` in the controller.

2. **System Settings Management**
   - All settings are centrally displayed and editable.
   - Each is validated against a strict schema (type/min/max/default).
   - Change notification supported via callbacks.

3. **Integration & Health Dashboard**
   - Health/operational metrics polled and visualized.
   - Alerts shown automatically when thresholds are breached, e.g., memory >80% (CRITICAL).

---

## **Architecture Diagram**

```mermaid
flowchart TD
  subgraph Admin_UI[/app/ui/admin/system_config.py/]
    SC[SystemConfigController]
  end
  subgraph Monitoring_Core[/app/core/monitoring/]
    SM[SystemSettingsManager]
    MM[SystemMetricsManager]
  end
    SC -- get/set settings --> SM
    SC -- get/report metrics --> MM
    SC -- get graph data --> SM
    SM ---|"persist JSON, validate"| File[(system_settings.json)]
```

---

## **APIs & Example Usage**

#### **Settings Management**
```python
from app.core.monitoring.settings_manager import system_settings

# Change an integer-limited setting
system_settings.set("max_upload_size_mb", 120)
print(system_settings.get("max_upload_size_mb"))  # 120

# See all settings (as dict)
print(system_settings.all())

# Register for change notifications
def on_setting_change(key, value):
    print(f"Setting changed: {key} = {value}")
system_settings.register_callback(on_setting_change)
```

#### **Metrics & Alerts**
```python
from app.core.monitoring.metrics import system_metrics, MetricType, AlertLevel, MetricAlert

# Register an alert threshold for memory
system_metrics.register_alert(MetricAlert(
    metric_name="memory",
    level=AlertLevel.CRITICAL,
    threshold=80
))

# Report a new metric (triggers alert if value >= threshold)
system_metrics.report_metric("memory", MetricType.MEMORY_USAGE, 85)
metrics = system_metrics.get_all_metrics()
print(metrics["memory"].to_dict())

# Get active alerts
alerts = system_metrics.get_active_alerts()
for alert in alerts:
    print(f"{alert.metric_name}: {alert.level.name} - {alert.current_value}%")
```

#### **Dependency Visualization**
The admin UI controller returns a graph data structure, which can be rendered via any network or dependency visualization library:
```python
from app.ui.admin.system_config import system_config_controller
graph_data = system_config_controller.get_component_dependency_graph()
print(graph_data)
# {"nodes": [
#   {"id": "auth_service", "label": "Authentication Service", "status": "healthy"},
#   {"id": "content_api", "label": "Content API", "status": "warning"},
#   ...
# ], 
# "edges": [
#   {"from": "auth_service", "to": "user_db", "label": "depends on"},
#   ...
# ]}
```

---

## **Settings Schema & Validation**

The system enforces a strict schema for all settings:

```python
SETTINGS_SCHEMA = {
    "max_upload_size_mb": {
        "type": int,
        "min": 1,
        "max": 500,
        "default": 100,
        "description": "Maximum file upload size in MB"
    },
    "session_timeout_minutes": {
        "type": int,
        "min": 5,
        "max": 1440,
        "default": 60,
        "description": "User session timeout in minutes"
    },
    "enable_advanced_analytics": {
        "type": bool,
        "default": False,
        "description": "Enable advanced analytics features"
    },
    # Additional settings...
}
```

Each setting is validated against its schema when set, ensuring type safety and value constraints.

---

## **Metric Types & Alert Levels**

```python
class MetricType(Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    ACTIVE_USERS = "active_users"
    CUSTOM = "custom"

class AlertLevel(Enum):
    INFO = 0
    WARNING = 1
    CRITICAL = 2
```

Metrics can be reported with any of these types, and alerts can be configured at different severity levels.

---

## **Testing & Validation**

- All config, metrics, and threshold logic is covered by `/tests/ui/test_system_config.py`.
- Includes:
  - Settings schema validation
  - Valid/invalid set operations
  - Metrics reporting and alerting logic
  - Dependency graph data structure integrity
  - Persistence and loading of settings

Example test cases:
```python
def test_settings_validation():
    # Should pass validation
    system_settings.set("max_upload_size_mb", 200)
    assert system_settings.get("max_upload_size_mb") == 200
    
    # Should fail validation (below min)
    with pytest.raises(ValueError):
        system_settings.set("max_upload_size_mb", 0)
        
def test_alert_triggering():
    # Register alert
    system_metrics.register_alert(MetricAlert(
        metric_name="cpu", 
        level=AlertLevel.WARNING,
        threshold=75
    ))
    
    # Report metric below threshold
    system_metrics.report_metric("cpu", MetricType.CPU_USAGE, 70)
    assert len(system_metrics.get_active_alerts()) == 0
    
    # Report metric above threshold
    system_metrics.report_metric("cpu", MetricType.CPU_USAGE, 80)
    alerts = system_metrics.get_active_alerts()
    assert len(alerts) == 1
    assert alerts[0].metric_name == "cpu"
```

---

## **Workflow for Admins**

1. Open System Config in the admin UI.
2. Review/change any validated system configuration value as appropriate.
3. Examine live system health/operational dashboards.
4. Respond to or trigger alerts for CPU/memory/other monitored resources.
5. Use dependency graph for rapid troubleshooting and impact analysis.
6. All operations also possible via REST/RPC API layer by wiring controller methods.

---

## **Extensibility**

- New settings are added by extending `SETTINGS_SCHEMA` in `settings_manager.py`.
- New metric types require only an enum addition and can be monitored immediately.
- Alert thresholds (for notifications, self-healing) can be registered on any metric at any time.
- The admin UI/controller APIs are modular and can be wired to any frontend.
- Custom metrics can be defined and reported using the `CUSTOM` metric type.

---

## **References and Further Reading**
- See `/docs/development/day11_done_criteria.md` for the original requirements and completion checklist.
- For test examples: `/tests/ui/test_system_config.py`
- For settings/metrics source: `/app/core/monitoring/settings_manager.py` and `/app/core/monitoring/metrics.py`
- For UI/entrypoint: `/app/ui/admin/system_config.py`

---

**This completes documentation for Task 11.4 and enables sprint review/acceptance.**
