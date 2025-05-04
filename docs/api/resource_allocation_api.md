# Resource Allocation API & Best Practices

_AeroLearn AI – Resource Registry & Allocation Tools (Task 3.7.3)_

---

## Purpose

Provides a registry-driven API for defining, tracking, and analyzing project/team resource assignments across components, supporting robust audit, availability management, visualization, and conflict/constraint analysis.

## Main API Components

### ResourceRegistry

`Location: app/core/monitoring/resource_registry.py`

**Key Methods:**

- `register_resource(resource_id, resource_type, availability: List[(str, str)])`
    - Adds or registers a resource; availability is a list of (start, end) date ranges.
- `assign_resource(resource_id, component, during=(start, end))`
    - Assigns resource to a component for given period, enforces overlap/conflict checking.
- `is_resource_available(resource_id, at)`
    - Checks if resource is available at a specific date.
- `get_conflicts(resource_id)`
    - Returns a list of all current assignment conflicts.
- `get_utilization(resource_id)`
    - Returns utilization (assigned_days/available_days) as a float.

### Integration: ResourceDashboard

`Location: app/ui/admin/resource_dashboard.py`

- `get_resource_table()`  
    Returns a dict-per-resource with all key info for rendering.
- `get_utilization_summary()`
    - Map from resource to utilization value for viz.
- `get_constraints_overview()`
    - Lists resources with constraint/assignment conflicts.

### Example Usage

```python
from app.core.monitoring.resource_registry import ResourceRegistry

registry = ResourceRegistry()
registry.register_resource("dev_jane", resource_type="developer", availability=[("2024-06-12", "2024-06-16")])
registry.assign_resource("dev_jane", "API", during=("2024-06-12", "2024-06-14"))
util = registry.get_utilization("dev_jane")
print("Jane utilization:", util)
```

### Dashboard Example

```python
from app.ui.admin.resource_dashboard import ResourceDashboard
from app.core.monitoring.resource_registry import ResourceRegistry

rdash = ResourceDashboard(ResourceRegistry())
for row in rdash.get_resource_table():
    print(row)
```

---

## Best Practices

- **Always declare availability periods:** For audit and utilization calculations to work as intended.
- **Prevent overlapping assignments:** Use assignment and conflict analysis APIs to enforce project health.
- **Regularly query utilization and conflict maps:** Visualizations and project status dashboards should monitor for resource over/underuse.
- **Integrate the registry at project init** so all planned/projected allocations are kept up to date.
- **Test all cross-component assignments** using the recommended integration test structure (`tests/integration/monitoring/test_resource_allocation.py`).

---

## References

- See also:  
    - `/docs/development/day20_plan.md` (task 3.7.3)
    - `/docs/architecture/architecture_overview.md`
    - `/docs/architecture/service_health_protocol.md`
    - `/docs/architecture/dependency_tracking_protocol.md`

---