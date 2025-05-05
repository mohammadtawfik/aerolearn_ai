# Change Propagation Simulation: API, Contracts, and Process

**Location:** `/docs/development/change_simulation_process.md`  
**Context:** Fulfills Task 3.7.6 completion requirements per `/docs/development/day21_plan.md`.

---

## Overview

The change propagation simulation subsystem enables modeling, analysis, visualization, and migration planning for component-level changes in the AeroLearn AI system, fully aligned with the architecture's protocol-driven, event-oriented integration standards.

---

## Key Components & API Contracts

| Module                                       | Responsibility                                                         | Key Methods/Attributes              |
|-----------------------------------------------|------------------------------------------------------------------------|-------------------------------------|
| `change_modeler.py`                          | Models a code, config, or component change                             | `simulate_change(component_id, ...)`|
| `change_propagation_analyzer.py`             | Analyzes dependency graph for impact propagation                       | `analyze(registry, change)`         |
| `change_effect_visualizer.py`                | Visualizes/effectively communicates change effects                     | `visualize(change, impacted)`       |
| `migration_planner.py`                       | Plans and describes downstream migrations and actions                  | `plan_migration(change, impacted)`  |
| Integration with Registry and Dashboard      | Ensures traceability, auditability, and real-time status integration   | Uses protocols from `/integrations/registry/`, `/core/monitoring/` |

---

## Simulation Process Flow

1. **Model the Change**
    - Use:  
      ```python
      from app.core.project_management.change_modeler import ChangeModeler
      change = ChangeModeler.simulate_change("ComponentX", change_type="config", description="Parameter tweak")
      ```
    - Returns a `Change` object with essential metadata.

2. **Analyze Propagation**
    - Use:
      ```python
      from app.core.project_management.change_propagation_analyzer import ChangePropagationAnalyzer
      impacted = ChangePropagationAnalyzer.analyze(registry, change)
      ```
    - Returns a list of impacted component IDs, using registry's dependency graph API.

3. **Visualize Effect**
    - Use:
      ```python
      from app.core.project_management.change_effect_visualizer import ChangeEffectVisualizer
      result_str = ChangeEffectVisualizer.visualize(change, impacted)
      ```

4. **Plan Migration**
    - Use:
      ```python
      from app.core.project_management.migration_planner import MigrationPlanner
      plan = MigrationPlanner.plan_migration(change, impacted)
      ```
    - Returns a plan dict containing the `change` and the list of `impacted` components.

5. **Registry/Dashboard Integration**
    - All state is auditable through the `ComponentRegistry` and visual dashboards, as required by
      `/docs/architecture/dependency_tracking_protocol.md` and `/docs/architecture/service_health_protocol.md`.

---

## Test-driven Process

- All core stubs and implementations are driven by `/tests/integration/registry/test_change_propagation_simulation.py`.
- No code is written without an initial test.
- Strict modularity and documentation alignment as mandated by `/docs/architecture/`.
- Unit and integration test expansion is encouraged for further change scenarios.

---

## Example: End-to-end Simulation

```python
from integrations.registry.component_registry import ComponentRegistry
from app.core.project_management.change_modeler import ChangeModeler
from app.core.project_management.change_propagation_analyzer import ChangePropagationAnalyzer
from app.core.project_management.change_effect_visualizer import ChangeEffectVisualizer
from app.core.project_management.migration_planner import MigrationPlanner

# Setup: Register components and dependencies
registry = ComponentRegistry()
registry.register_component("A")
registry.register_component("B")
registry.register_component("C")
registry.declare_dependency("A", "B")
registry.declare_dependency("B", "C")

# Simulate a change
change = ChangeModeler.simulate_change("B", "code", "Refactor algorithms")

# Analyze impact
impacted = ChangePropagationAnalyzer.analyze(registry, change)

# Visualize effects
print(ChangeEffectVisualizer.visualize(change, impacted))

# Plan migration
migration_plan = MigrationPlanner.plan_migration(change, impacted)
print(f"Migration Plan: {migration_plan}")
```

---

## References

- `/docs/architecture/architecture_overview.md`
- `/docs/architecture/dependency_tracking_protocol.md`
- `/docs/architecture/service_health_protocol.md`
- `/docs/development/day21_plan.md`
- `/tests/integration/registry/test_change_propagation_simulation.py`
- `/app/core/project_management/` (for all module source code)

---

**Maintainers**: Update this doc as implementation or API evolves.  
**Status**: Task 3.7.6 is complete when this doc and its APIs are present and all tests pass.