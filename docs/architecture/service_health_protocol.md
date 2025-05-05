# Service Health Monitoring Protocol

## Overview

The Service Health Monitoring Protocol defines how component and integration health is monitored, reported, and queried throughout the AeroLearn platform. It ensures that every subsystem can be health-checked, state-tracked, and visually integrated into dashboards and analytic systems.

## Status States

All monitored components and integrations must declare one of the following states (enum `ComponentState`):

- **UNKNOWN** — State cannot be determined (not monitored, not registered).
- **RUNNING** — Component is operational and healthy.
- **DEGRADED** — Component is operational but experiencing reduced functionality or performance.
- **DOWN** — Component is unreachable or not serving requests.
- **HEALTHY** — Synonym for RUNNING (sometimes used for integrations).
- **FAILED** — Irrecoverable error or unrecoverable state.

Component registry and adapters must enforce these state definitions and propagate state changes system-wide.

## Registration

- Each component must register itself in the **Component Registry** upon deployment or initialization.
- Registration includes unique IDs, version, description, and initial state.
- Example: `component = component_registry.register_component("API", state=ComponentState.RUNNING)`

## State Reporting

- Each component periodically updates its current `ComponentState` in the registry.
- Components report status changes via:
  - Direct calls (`update_component_status`)
  - Adapter/bus integration (e.g., `SYSTEM_STATUS_TRACKER`)
- The **System Status Tracker** queries the registry to sync and cache current state values.

## Status Retrieval and Dashboard

- The **Service Health Dashboard** provides a unified view of real-time state, dependency mapping, and history for all registered components.
- The dashboard issues pull synchronization from the registry, ensuring always-current results.
- Callers can query:
  - `dashboard.status_for("API")` → returns `ComponentState.DEGRADED`
  - `dashboard.get_all_component_statuses()` → dict of name: state object

## State Change Notification

- When a component state changes, the registry notifies monitoring adapters and the dashboard, triggering a history record append.
- All consumer APIs are guaranteed to expose the most recent known state.
- Status changes are published to the dashboard or listeners to enable live updates.

## Dependency Management

- Component dependencies are declared in the registry and rendered in the dashboard dependency graph.
- Each component declares its direct dependencies for system topology/graph visualization.

## History and Audit

- Every state transition (detected by the dashboard) is timestamped and stored per component for uptime/downtime audits.
- All health status changes are recorded with a timestamp for uptime analysis and audit.

## Data Model

### Component Status Message (example):
```json
{
  "component_id": "core.backend.serviceA",
  "status": "RUNNING",
  "updated_at": "2024-06-11T10:30:00Z",
  "metrics": {
    "cpu_pct": 22.5,
    "mem_mb": 431,
    "error_count": 0
  },
  "dependencies": ["core.db", "core.network"]
}
```

### Status Record Structure
```python
@dataclass
class StatusRecord:
    component_id: str
    state: ComponentState
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
```

## Implementation Requirements

### Component Registry Interface

```python
class ComponentRegistry:
    def register_component(self, component_id: str, description: str = None, 
                          version: str = None, state: ComponentState = ComponentState.UNKNOWN) -> Component:
        """Register a new component with the system"""
        pass
        
    def unregister_component(self, component_id: str) -> bool:
        """Remove a component from the registry"""
        pass
        
    def get_component(self, component_id: str) -> Optional[Component]:
        """Retrieve a component by ID"""
        pass
        
    def get_all_components(self) -> Dict[str, Component]:
        """Get all registered components"""
        pass
```

### Service Health Dashboard Interface

```python
class ServiceHealthDashboard:
    def update_component_status(self, component_id: str, state: ComponentState, 
                               metrics: Dict = None) -> bool:
        """Update a component's health status"""
        pass
        
    def status_for(self, component_id: str) -> ComponentState:
        """Get current status for a component"""
        pass
        
    def get_all_component_statuses(self) -> Dict[str, ComponentState]:
        """Get statuses for all components"""
        pass
        
    def register_status_listener(self, listener: Callable) -> str:
        """Register a callback for status changes"""
        pass
        
    def get_component_history(self, component_id: str, 
                             time_range: Tuple[datetime, datetime] = None) -> List[StatusRecord]:
        """Get historical status records for a component"""
        pass
```

## API Endpoints / Interfaces

- `POST /status-report` : Report current health (internal, not HTTP in monolith)
- `GET /dependencies`  : Get full system dependency graph
- `GET /status/{component_id}` : Get live/historical health data for component
- `GET /dashboard/health` : Get overall system health summary

## Reference Implementation Locations

- **Monitoring core:** 
  - `/app/core/monitoring/metrics.py` (system metrics, analytics, and non-dashboard utilities)
  - **`/app/core/monitoring/ServiceHealthDashboard_Class.py` (canonical implementation of ServiceHealthDashboard, health dashboard protocol)**
- **Component/registry:** `/integrations/registry/component_registry.py`
- **Status Adapter:** `/integrations/monitoring/component_status_adapter.py`
- **Component Status:** `/integrations/monitoring/component_status.py` (component status tracker, dependency registry)
- **Integration Health:** `/integrations/monitoring/integration_health.py` (integration points/events/failures)
- **Tests:** `/tests/integration/monitoring/test_service_health_dashboard.py`

_Note: As of May 2025, `ServiceHealthDashboard` is now exclusively implemented in `/app/core/monitoring/ServiceHealthDashboard_Class.py` for clarity and modularity._

## Testing Requirements

All components implementing this protocol must include:

1. Unit tests verifying state transitions
2. Integration tests with the dashboard
3. Mock implementations for testing dependent systems
4. Snapshot tests for dashboard visualization components

## Dashboard Compliance Requirements

To be considered dashboard-compliant, implementations must:

1. Register with the ComponentRegistry on startup
2. Report status changes in real-time
3. Expose health check endpoints
4. Provide accurate dependency information
5. Include proper error handling for status reporting failures

---
_This spec is a living document. All monitoring-related PRs must update this as protocol changes._
