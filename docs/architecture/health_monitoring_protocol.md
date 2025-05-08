# AeroLearn AI Health Monitoring Protocol

_AeroLearn AI – Monitoring, Health, and Compatibility Modules Scope_  
**Last Updated: Day 23**

---

## Table of Contents

1. Overview
2. Error Logging Protocol
3. Usage Analytics Protocol
4. System Health Check Protocol
5. Alert Notification Protocol
6. Integration Failure Monitoring Protocol
7. Real-Time Compatibility Monitoring Protocol
8. Data Model & Field Contract Reference
9. Extensibility & Implementation Notes

---

## 1. Overview

This protocol defines the canonical, tested, and production-ready APIs, interfaces, and event/data fields for all AeroLearn AI monitoring, health, and compatibility systems. All implementations and integrations MUST adhere to the signatures, response formats, field lists, and event flows as specified here. Extensions must be reviewed and documented using the TDD paradigm.

---

## 2. Error Logging Protocol

### Class: `ErrorLogger`

- **API:**
    - `log_error(component, message: str, severity: ErrorSeverity, category: str, metadata: dict = None)`
    - `query_errors(component: str = None, severity: ErrorSeverity = None, category: str = None, limit: int = None) -> List[Dict]`
    - `aggregate_errors() -> Dict`
    - `register_notification_rule(rule: Callable[[Dict], bool], callback: Callable[[Dict], None])`
    - `clear()`

- **Error Severity Enum:**
    - `CRITICAL`, `WARNING`, `INFO`, `DEBUG`

- **Event Record Fields:**
    - `component`: str
    - `message`: str
    - `severity`: ErrorSeverity (enum)
    - `category`: str
    - `metadata`: dict (optional; protocol extension allowed)

- **Notification:**
    - Notification rules can be registered with a predicate and a synchronous callback; triggered on log entry matching rule.

---

## 3. Usage Analytics Protocol

### Class: `UsageAnalytics`

- **API:**
    - `track_activity(user, event: str, feature: str, timestamp: int)`
    - `query_activities(user_id: str = None) -> List[Dict]`
    - `aggregate_usage(user_id: str = None) -> Dict`
    - `feature_usage_report() -> Dict`
    - `query_sessions(user_id: str = None) -> List[Dict]`
    - `clear()`

- **Activity Event Fields:**
    - `user_id`: str
    - `event`: str
    - `feature`: str
    - `timestamp`: int

- **Session Record Fields:**
    - `user_id`: str
    - `start`: int
    - `end`: int
    - `duration`: int

---

## 4. System Health Check Protocol

### Class: `ServiceHealthDashboard`

- **API:**
    - `register_component(name: str)`
    - `declare_dependency(component: str, depends_on: str)`
    - `set_component_health(name: str, status: ComponentState)`
    - `get_system_health() -> Dict`
    - `get_health_dashboard() -> Dict`
    - `register_alert_callback(callback: Callable[[str, ComponentState], None])`
    - `watch_component(component_id: str, callback: Callable[[str, ComponentState], None])`
    - `clear()`

- **ComponentState Enum:**
    - `OK`, `DEGRADED`, `FAILED`

- **System Health Response:**
    - `status`: str
    - `components`: Dict[str, str]

- **Dashboard Response:**
    - `status_overview`: Dict[str, str]
    - `component_tree`: Dict[str, List[str]]
    - `status_history`: Dict[str, List[Dict]] (with keys `timestamp`, `status`)

- **Alert Callback Signature:**
    ```python
    def callback(component_id: str, state: ComponentState): ...
    ```

- **When Are Alerts Triggered?**
    - When a component transitions into one of the following states:
      - `ComponentState.DEGRADED`
      - `ComponentState.FAILED`
    - Duplicate alerts will NOT be sent repeatedly for the same state; the alert is only triggered on a **state transition.**
    - When the component returns to a non-critical state, any subsequent entry into either `DEGRADED` or `FAILED` will trigger the alert again.
    - Transitions between critical states (e.g., from `DEGRADED` to `FAILED` or vice versa) will also trigger alerts.

- **Integration Usage Example:**
    ```python
    dashboard = ServiceHealthDashboard()
    dashboard.register_alert_callback(lambda cid, state: print(
      f"[Monitor] {cid} critical: {state}"
    ))
    ```

- **Backward Compatibility:**
    - Legacy status listeners can still be used via `watch_component(component_id, callback)`, but that callback is invoked for *every* status update;  
    the alert callback is invoked **only on critical threshold transitions**.

- **Propagation:**
    - Status is propagated from dependencies to dependents, following the protocol's severity hierarchy.

---

## 5. Alert Notification Protocol

### Classes: `AlertNotification`, `AlertRule`

- **API:**
    - `register_rule(rule: AlertRule, callback: Callable[[Dict], None])`
    - `trigger_alert(component, message: str, severity: str, category: str)`
    - `escalate_alert(component_name: str)`
    - `query_alert_history() -> List[Dict]`
    - `clear()`

- **AlertLevel Enum:**
    - `INFO`, `WARNING`, `CRITICAL`

- **Alert Fields:**
    - `component`: str
    - `message`: str
    - `severity`: str
    - `category`: str
    - `timestamp`: float

- **Escalation:**
    - Repeated/burst conditions as documented trigger automatic escalation via protocol-approved workflows.

---

## 6. Integration Failure Monitoring Protocol

### Class: `IntegrationMonitor`

- **API:**
    - `register_component(component_id)`
    - `set_metrics(component_id, metric_record)`
        - **Updated**: Each call to `set_metrics` now appends the new metric_record to per-component historical metrics, so `get_metrics_history(component_id)` returns every version in set order (test-driven, compliance required).
    - `get_metrics_history(component_id)`
        - Returns a list of metric dicts, with each dict corresponding to a call of `set_metrics`. Older doc versions recorded only the previous value; now, each value, in order, is saved to history as specified by test and implementation.
    - `monitor_integration(integration)`
    - `record_transaction(integration, status: str, duration: int, details=None)`
    - `get_transactions(integration)`
        - **New API**: Returns list of all transaction records for the integration (per TDD/test compliance).
    - `get_failure_trace(integration) -> List[Dict]`
    - `detect_failure_patterns(integration) -> Dict`
    - `get_health_score(integration) -> float`
    - `simulate_failure(integration, fail_type: str)`
    - `clear()`

- **Transaction Fields:**
    - `integration`: str
    - `status`: "success" | "fail"
    - `duration`: int | None (None in simulated)
    - `timestamp`: float
    - `fail_type`: str (optional; only present if simulated/injected)
    - `details`: dict (optional; additional transaction metadata)

- **Pattern Fields:**
    - `pattern`: "repeated_failure" | "occasional_failure" | None
    - `count`: int

- **Health Score:**
    - Value between 0 and 1 (ratio of successful transactions to total)

### Class: `IntegrationPointRegistry`

- **API:**
    - `register_point(point_id, value=None)`
        - **Updated**: Accepts `value` as optional. If omitted, metadata is `None`. Repeated calls with the same point_id update the associated value and do NOT duplicate the id in the registry.
    - `get_point(point_id)`
        - **New API**: Returns the value/metadata for the named integration point; required by tests and covered by implementation.
    - `get_all_points()`
        - **New API**: Returns all points as a `{point_id: value}` dictionary.
    - `list_points()`
        - Returns list of all registered point ids in order of registration, deduplicated.
    - Legacy compatibility: `lookup`, `get_all`, and `get_all_keys` retained.

- **Behavioral Notes:**
    - Registering a point with the same id multiple times will always update the value but will never result in duplicate ids being returned from `list_points` or key queries.
    - If `register_point` is called with just an id and no value, the value will default to `None` (test and backward compatibility).

---

## 7. Real-Time Compatibility Monitoring Protocol

### Class: `CompatibilityMonitor`

- **API:**
    - `register_component(component)`
    - `validate_contract(name: str, contract: Dict[str, Any]) -> Dict`
    - `check_version_compatibility(name: str) -> Dict`
    - `verify_runtime_compatibility(name: str, contract: Dict[str, Any]) -> Dict`
    - `on_compatibility_issue(callback: Callable[[Dict[str, Any]], None])`
    - `clear()`

- **Fields:**
    - Registration: `name`, `version`, `contract`
    - Validation/check: `compatible` (bool), `versions` (List[str]), `conflict` (Tuple[str, str], optional), `diff` (Dict[str, tuple])
    - Alert: `name`, `diff`

- **Version Policy:**
    - Only one version is compatible by default.
    - Registration of a new, different version produces `compatible: False` and conflict output.

---

## 8. Data Model & Field Contract Reference

_All API events, payloads, and record fields must contain only the fields described above. No undocumented or extra fields are permitted in protocol-compliant interfaces or responses._

---

## 9. Extensibility & Implementation Notes

- All implementations must reside under `app/core/monitoring/` and align exactly with the class/field/API references above.
- Public API surfaces are final for inter-module consumption unless protocol is amended.
- Additional monitoring modules must append to this protocol documentation and undergo the same TDD flow: test → implementation → doc update.
- Registry, aggregation, notification, and dashboard APIs are to be integrated with higher-level service orchestration via the dependency/component registry systems, as described in the architecture overview.
- All APIs and fields are subject to the latest protocol revision as checked into version control with this document.

---

## TDD Compliance

**UPDATE:** Alert callback behavior is now fully test-verified. Callbacks registered via `dashboard.register_alert_callback(cb)` are guaranteed to:
- Fire on both `ComponentState.DEGRADED` and `ComponentState.FAILED` transitions
- Only trigger on true state transitions (entry into critical states)
- Retrigger when exiting and re-entering any critical state
- Retrigger when transitioning between different critical states

Please see `/app/core/monitoring/metrics.py` for the full implementation and `/tests/unit/core/monitoring/test_service_health_dashboard.py` for the reference implementation and protocol coverage.

**UPDATE Day24:** IntegrationMonitor and IntegrationPointRegistry APIs have been updated and fully test-verified. Every API, signature, and logic note above matches canonical test expectations as implemented in:
- `/tests/unit/core/monitoring/test_integration_monitor.py`
- `/tests/unit/core/monitoring/test_integration_point_registry.py`

**This documentation reflects the canonical reference as implemented and tested in Day 24 sessions. For any future changes, update both the test suite and this protocol document together, in accordance with strict TDD and protocol-driven practices.**
