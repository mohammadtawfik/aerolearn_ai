# AeroLearn AI Health Monitoring Protocol

## ServiceHealthDashboard Health Alerts

### Overview

The AeroLearn "ServiceHealthDashboard" provides centralized monitoring of component and integration health.  
System integrators and tools may receive *real-time alerts* when a component transitions into a degraded or failed status.

### Registering for Health Alerts

To register for alert notifications:

```python
def alert_handler(component_id, new_state):
    print(f"ALERT! Component {component_id} entered state: {new_state}")

dashboard.register_alert_callback(alert_handler)
```

### When Are Alerts Triggered?

- When a component crosses into one of the following states:
  - `ComponentState.DEGRADED`
  - `ComponentState.FAILED`
- Duplicate alerts will NOT be sent repeatedly for the same state; the alert is only triggered on a **state transition.**
- When the component returns to a non-degraded/failed state, any subsequent entry into a degraded state will again trigger the alert.

### Alert Callback Signature

Alert callback functions MUST accept two parameters:

```python
def callback(component_id: str, state: ComponentState): ...
```

Where:
- `component_id`: The registry name for the affected component/service.
- `state`: The new `ComponentState` (usually `DEGRADED` or `FAILED`).

### Integration Usage Example

```python
dashboard = ServiceHealthDashboard()
dashboard.register_alert_callback(lambda cid, state: print(
  f"[Monitor] {cid} critical: {state}"
))
```

### Backward Compatibility

Legacy status listeners can still be used via `watch_component(component_id, callback)`, but that callback is invoked for *every* status update;  
the alert callback is invoked **only on critical thresholds**.

---

Please see `/app/core/monitoring/metrics.py` for the full implementation.