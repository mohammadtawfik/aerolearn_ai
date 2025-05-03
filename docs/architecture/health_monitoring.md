# AeroLearn AI – Service Health Monitoring Architecture

## Overview

The Service Health Dashboard provides comprehensive and real-time monitoring of AeroLearn’s internal components. Key features—**component status tracking, live state changes, dependency graphing, and historical uptime**—are TDD-verified through systematic integration tests.

---

## Architecture

- **Status Model:**  
  Each component is tracked via a status provider (`SimpleComponentStatusProvider`) bound to both the centralized registry and a status tracker.  
  The status tracker maintains live state and a time-stamped history for each registered component.

- **Dashboard:**  
  The `ServiceHealthDashboard` aggregates status from the tracker, exposes API for:
  - `get_all_component_statuses()`
  - `get_dependency_graph()`
  - `get_status_history(component_id)`
  - `status_for(component_id)`

- **Dependency Tracking:**  
  The dashboard visualizes component inter-dependencies via the registry's graph.

- **Real-Time Status Update:**  
  All state changes are visible “instantly” through the dashboard API after tracker update.

- **Historical Uptime:**  
  Every state change is recorded to a time-stamped history, supporting uptime/downtime analytics.

---

## Implementation & Test Protocol

- **Component Registration:**  
  - Register component instance to registry  
  - Register status provider (`SimpleComponentStatusProvider`) to the status tracker for that component
- **State Change Tracking:**  
  - Mutate state on the live component  
  - Call `tracker.update_component_status(component_id)` to record change
- **Test Coverage:**  
  - All code and TDD cycles are represented in `/tests/integration/monitoring/test_service_health_dashboard_integration.py`
  - Tests verify: registration, dependency graph, real-time updates, reliable historical recording

---

## Usage Example

```python
# Registration
registry.register_component('Worker', worker_component)
tracker.register_status_provider('Worker', SimpleComponentStatusProvider(worker_component))

# State Change
worker_component.state = ComponentState.DOWN
tracker.update_component_status('Worker')

# Dashboard Query
status = dashboard.status_for('Worker')
history = dashboard.get_status_history('Worker')
```

---

## Integration/API References

- **ComponentRegistry/Register:**  
  `/integrations/monitoring/component_status_adapter.py`
- **Dashboard/Tracker Classes:**  
  `/app/core/monitoring/metrics.py`, `/integrations/monitoring/component_status_adapter.py`
- **Tests:**  
  `/tests/integration/monitoring/test_service_health_dashboard_integration.py`
- **Factory Fixture:**  
  `/tests/helpers/test_monitoring_fixtures.py`

---

## Future Extensions

- Alerting on unhealthy state transitions (by registering dashboard callbacks)
- UI integration for live visualization
- Automated resynchronization of registry/tracker in highly dynamic environments

---

## Authors & Review

- Integration designed & TDD-refined by AeroLearn AI team.
- Last revised: [today's date]