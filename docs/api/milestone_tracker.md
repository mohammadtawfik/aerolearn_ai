# Milestone Tracker – API & Usage Documentation

**Location:** `/app/core/project_management/milestone_tracker.py`  
**Docs:** `/docs/api/milestone_tracker.md`  
**Status:** Complete and protocol-compliant

---

## Purpose

The Milestone Tracker is a protocol-compliant registry and management module for project milestones.  
It enables:
- Milestone definition and registration (cross-component)
- Status and progress tracking
- Dependency mapping and impact/risk visualization
- Accurate, auditable planning for large and distributed projects

---

## API Overview

### MilestoneStatus Enum

```python
class MilestoneStatus(Enum):
    PLANNED
    IN_PROGRESS
    COMPLETED
    BLOCKED
    ON_HOLD
    CANCELLED
```

---

### Milestone Dataclass

```python
@dataclass
class Milestone:
    name: str
    components: Set[str]
    status: MilestoneStatus = MilestoneStatus.PLANNED
    dependencies: Set[str] = field(default_factory=set)
    status_history: List[MilestoneHistoryRecord] = field(default_factory=list)
    progress: float = 0.0

    def update_status(self, new_status: MilestoneStatus):
        ...
    def recalculate_progress(self, registry: 'MilestoneRegistry'):
        ...
```

---

### MilestoneRegistry Class

| Method | Description |
|--------|-------------|
| `register_milestone(name, components, status="PLANNED")` | Register new milestone with associated component(s) & status |
| `get_milestone(name)` | Retrieve a registered milestone |
| `update_milestone_status(name, new_status)` | Update milestone status and propagate to progress |
| `declare_milestone_dependency(milestone_name, dependency_name)` | Link milestones as dependencies (cycle-protected) |
| `get_dependency_graph()` | Get dependency mapping as a dict `{milestone: [deps...]}` |
| `get_status_history(name)` | Get timestamped milestone status transitions |
| `get_progress(name)` | Retrieve progress (float 0..1) for milestone |
| `assess_risk(name)` | Returns risks and unresolved dependencies for milestone |

#### Audit & Protocol Features
- All actions generate timestamped audit/history records (per `/docs/architecture/dependency_tracking_protocol.md`)
- Cycle and error protection per protocol
- Fully compatible with status/health monitoring and dashboards

---

## Usage Example

```python
from app.core.project_management.milestone_tracker import MilestoneRegistry

reg = MilestoneRegistry()
reg.register_milestone("Release 1.0", ["API", "UI"])
reg.register_milestone("Finish Docs", ["Documentation"])
reg.declare_milestone_dependency("Release 1.0", "Finish Docs")
reg.update_milestone_status("Finish Docs", "COMPLETED")
reg.get_progress("Release 1.0")   # Will reflect dependency completion

risk = reg.assess_risk("Release 1.0")
print(risk["unresolved_dependencies"])
```

---

## Dependency Model

- Dependency mapping is bidirectional and cycle-protected (protocol compliance)
- Milestones can depend on multiple milestones; visualized as a dependency graph
- Completion/progress propagates to dependents and is reflected in progress/risk APIs

---

## Progress and Risk Handling

- Progress is recalculated automatically based on completion of dependencies
- Risk assessment provides:
  - Blocked/on hold status
  - List of unresolved dependencies
  - Cumulative completion fraction
- All progress/risk info is retrievable for dashboard/automation integration

---

## Protocol/Design Compliance

- Registry interface, dependency model, and audit/history mechanism follow `/docs/architecture/dependency_tracking_protocol.md`
- Status enums/history ready for dashboard and cross-component reporting as in `/docs/architecture/service_health_protocol.md`
- Designed for extension into resource tracking, milestone aggregation, and reporting per `/docs/development/day20_plan.md`

---

## Extension & Integration

- Designed for dashboard, reporting, and risk visualization components
- Can be paired with feature/resource registries for comprehensive project planning
- Protocol- and audit-ready for compliance and cross-team use

---

## References

- `/app/core/project_management/milestone_tracker.py`
- `/tests/integration/registry/test_milestone_tracker.py`
- `/docs/architecture/dependency_tracking_protocol.md`
- `/docs/development/day20_plan.md`