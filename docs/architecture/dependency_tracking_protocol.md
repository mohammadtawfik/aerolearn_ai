# AeroLearn AI Dependency Tracking Protocol

**Location:** `/docs/architecture/dependency_tracking_protocol.md`  
**Status:** Stable (as of Day 19 TDD cycle)

---

## Purpose

This document details the contract, usage guidelines, and caveats for the AeroLearn AI Component Registry's dependency tracking system. This protocol ensures that all components, and their interdependencies, can be programmatically declared, visualized, and analyzed for system health and upgrade risk.

---

## API Overview

### Main Class

- **ComponentRegistry** (`/integrations/registry/component_registry.py`)

### Key Methods

- `register_component(name, state=None, version=None, component_type=None)`
- `unregister_component(name)`
- `declare_dependency(name, depends_on)`
- `get_dependency_graph()`
- `get_dependencies(name)`
- `analyze_dependency_impact(name)`
- `check_version_compatibility(name)`

---

## Usage Patterns

### Registering Components

```python
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component_state import ComponentState

registry = ComponentRegistry()
registry.register_component("Database", state=ComponentState.RUNNING, version="1.0")
registry.register_component("API", state=ComponentState.PAUSED)
```

### Declaring Dependencies

```python
registry.declare_dependency("API", "Database")
# Now, "API" requires "Database"
```

### Querying the Dependency Graph

```python
graph = registry.get_dependency_graph()
# Returns: {'API': ['Database']}
```

### Impact Analysis

```python
impacted = registry.analyze_dependency_impact("Database")
# Returns: ['API']  # "API" depends on "Database"
```

### Version Compatibility

```python
compatible = registry.check_version_compatibility("API")
# Returns True (current implementation is a stub)
```

---

## Protocol Rules

- **All dependencies must be registered in advance**, or `declare_dependency` will return False.
- **Cyclic Dependencies** are supported, but currently not visually flagged; future improvements may include cycle warnings.
- **Component States:** See `/integrations/registry/component_state.py` for possible values:
  - `RUNNING`, `DOWN`, `PAUSED`, `DEGRADED`, `UNKNOWN`, `ERROR`
- **Singleton Pattern:** `ComponentRegistry` enforces one logical registry instance for the entire system.
- **Removal:** Removing a component will update both the registry and all other dependency relationships.

---

## Example (Complex Graph):

```python
# Register Components
reg = ComponentRegistry()
reg.register_component("A", state=ComponentState.RUNNING)
reg.register_component("B")
reg.register_component("C")
reg.register_component("D")
reg.register_component("E")

# Declare dependencies
reg.declare_dependency("A", "B")
reg.declare_dependency("A", "C")
reg.declare_dependency("B", "C")
reg.declare_dependency("C", "D")
reg.declare_dependency("C", "E")
reg.declare_dependency("E", "D")
# Query dependency graph for visualization or analysis
dc_graph = reg.get_dependency_graph()
impacted_by_d = reg.analyze_dependency_impact("D")
```

---

## Caveats / Limitations

- **Version compatibility** is currently not enforced programmatically—extend as needed!
- **Visualization** is not part of the registry but intended to be implemented at the dashboard/UI layer.
- **Atomic transactional updates** are not provided; all methods are best-effort and not thread-safe.
- **All relationships use component names as identifiers**; ensure uniqueness.

---

## For Contributors

- **Before altering core methods, add/extend integration tests** in `/tests/integration/registry/`.
- **When extending registry (e.g., for custom lifecycle hooks), document here.**
- **For version or cycle detection, update both the code and these docs.**

---

*For questions or pattern feedback: Submit a PR or start a thread in the `architecture` docs tree.*