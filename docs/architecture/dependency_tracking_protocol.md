# AeroLearn AI Dependency Tracking Protocol

**Location:** `/docs/architecture/dependency_tracking_protocol.md`  
**Status:** Stable (as of Day 22 TDD cycle)

## Status

> **NEW:**  
> All `ComponentState` enums MUST be imported from `/integrations/registry/component_state.py`. No circular (registry-to-monitoring) dependency is allowed.  
> All dependency/integration protocol tests are modularized and must be placed in `/tests/integration/registry/`.

---

## Purpose

This document details the contract, usage guidelines, and caveats for the AeroLearn AI Component Registry's dependency tracking system. This protocol ensures that all components, and their interdependencies, can be programmatically declared, visualized, and analyzed for system health and upgrade risk.

---

## Modular Implementation

The protocol-compliant component registry is implemented as a composite of three focused modules:

- `Component` (`/integrations/registry/component.py`): The canonical protocol entity used in registration and lookup; all instances must supply a `component_id` attribute.
- `DependencyGraph` (`/integrations/registry/dependency_graph.py`): Contains all logic for edge management and dependency queries, ensuring registry itself remains testable and minimal.
- `ComponentRegistry` (`/integrations/registry/component_registry.py`): The external-facing API, invoking component registration and dependency actions according to protocol, delegates backing logic appropriately.

**Usage:**  
Clients and downstream protocols should always treat the registry as the authority, using component_id (never object or name) as the canonical key.

**Compliance Testing:**  
Tests may substitute in their own `Component` implementations as long as they expose `component_id`.

All registry and dependency APIs are now verified by modular protocol integration tests:
- `/tests/integration/registry/test_component_registry_registration.py`
- `/tests/integration/registry/test_component_registry_lifecycle.py`
- `/tests/integration/registry/test_component_registry_dependency.py`

All protocol features pass TDD requirements as of Day 22.

---

## API Overview

### Main Classes

- **ComponentRegistry** (`/integrations/registry/component_registry.py`)
- **Component** (`/integrations/registry/component.py`)
- **DependencyGraph** (`/integrations/registry/dependency_graph.py`)
- **ComponentState** (`/integrations/registry/component_state.py`)
- **Dashboard** (Consumers of dependency/service health data)

### Key Registry Methods

- `register_component(component_id, state=None, version=None, component_type=None)`
- `unregister_component(component_id)`
- `declare_dependency(component_id, depends_on)`
- `get_dependency_graph()`
- `get_dependencies(component_id)`
- `analyze_dependency_impact(component_id)`
- `check_version_compatibility(component_id)`

### Component Methods

- `__init__(component_id, state=None, version=None, component_type=None)`
- `get_id()`
- `get_state()`
- `set_state(state)`
- `get_version()`
- `get_type()`

### DependencyGraph Methods

- `add_node(node_id)`
- `remove_node(node_id)`
- `add_edge(from_node, to_node)`
- `get_dependencies(node_id)`
- `get_dependents(node_id)`
- `get_all_edges()`
- `has_node(node_id)`
- `has_edge(from_node, to_node)`

### Required Dashboard Methods

- `get_dependency_graph()`
- `get_all_component_statuses()`
- `get_component_status(component_id)`
- `clear()`
- `supports_cascading_status()`

---

## Usage Patterns

### Dependency List Ordering

All AeroLearn AI dependency tracking APIs return **lists of dependencies or dependents in the exact order declared** by the user or test case.  
For example, if A declares B then C as dependencies, `get_dependency_graph()['A']` will be `['B', 'C']`—order is preserved and is not arbitrary.

Likewise, `get_dependents(node_id)` returns all nodes that depend on `node_id` in the original addition order.

> **Note:** Return values SHOULD NOT be sets or unordered lists—protocol, integration tests, and analytics depend on deterministic ordering.  
If you rely on implementation details, verify compliance with the latest protocol doc and sample test.

_This policy is enforced in all current TDD and test harnesses (June 2024)._

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

### Working with Components Directly

```python
from integrations.registry.component import Component
from integrations.registry.component_state import ComponentState

# Create a component
db_component = Component("Database", state=ComponentState.RUNNING, version="1.0")
print(db_component.get_id())  # "Database"
print(db_component.get_state())  # ComponentState.RUNNING
```

### Working with the Dependency Graph

```python
from integrations.registry.dependency_graph import DependencyGraph

# Create a graph
graph = DependencyGraph()
graph.add_node("API")
graph.add_node("Database")
graph.add_edge("API", "Database")
print(graph.get_dependencies("API"))  # ["Database"]
print(graph.get_dependents("Database"))  # ["API"]
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
- **Component States:** MUST be imported from `/integrations/registry/component_state.py` for possible values:
  - `RUNNING`, `DOWN`, `PAUSED`, `DEGRADED`, `UNKNOWN`, `ERROR`
- **Singleton Pattern:** `ComponentRegistry` enforces one logical registry instance for the entire system.
- **Removal:** Removing a component will update both the registry and all other dependency relationships.
- **Dashboard Integration:** All consumers of dependency/service health dashboards must assume an explicit registry argument is required at initialization.
- **Cascading Status:** If cascading logic is not present, `supports_cascading_status()` MUST exist and return `False`. Future implementations will require real cascading propagation.
- **Component Identity:** Always use `component_id` as the canonical identifier for components throughout the system.
- **Modular Design:** The registry delegates graph operations to the DependencyGraph class and component management to the Component class.
- **Ordered Lists:** All dependency and dependent lists maintain insertion order. Methods like `get_dependencies()`, `get_dependents()`, and the values in `get_dependency_graph()` return lists in the exact order dependencies were declared, not as unordered sets.

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

## Example (Using Modular Components):

```python
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component
from integrations.registry.component_state import ComponentState
from integrations.registry.dependency_graph import DependencyGraph

# Create components
comp_a = Component("A", state=ComponentState.RUNNING)
comp_b = Component("B")

# Register with registry
reg = ComponentRegistry()
reg.register_component(comp_a.get_id(), state=comp_a.get_state())
reg.register_component(comp_b.get_id())

# Declare dependencies
reg.declare_dependency(comp_a.get_id(), comp_b.get_id())

# Access the underlying graph directly if needed
graph = DependencyGraph()
graph.add_node("X")
graph.add_node("Y")
graph.add_edge("X", "Y")
```

---

## Caveats / Limitations

- **Version compatibility** is currently not enforced programmatically—extend as needed!
- **Visualization** is not part of the registry but intended to be implemented at the dashboard/UI layer.
- **Atomic transactional updates** are not provided; all methods are best-effort and not thread-safe.
- **All relationships use component_id as identifiers**; ensure uniqueness.
- **Dashboard API Compliance:** Tests will check for required protocol methods and will assert NO attribute/TypeError is possible for the required protocol methods.
- **Module Boundaries:** When extending functionality, respect the separation of concerns between Component, DependencyGraph, and ComponentRegistry.
- **Order Dependency:** Tests and implementations should not rely on arbitrary ordering of dependencies. The protocol guarantees insertion order is preserved, but changing the order of declarations will change the order of results.

---

## For Contributors

- **Before altering core methods, add/extend integration tests** in `/tests/integration/registry/`.
- **When extending registry (e.g., for custom lifecycle hooks), document here.**
- **For version or cycle detection, update both the code and these docs.**

## Protocol API: Enum, Tests, and Analytics

- All protocols that affect registry/component/dependency APIs must rely on enums/consts from the registry module.
- Modular integration tests for dependency graph API (add, remove, list, analytic methods, cycle detection) must be maintained in the `/tests/integration/registry/` directory. No monolithic "test_component_registry.py" or similar is allowed.

## Implementation Reference

- Component entity: `/integrations/registry/component.py`
- Registry API: `/integrations/registry/component_registry.py`
- Dependency graph: `/integrations/registry/dependency_graph.py`
- Component state enum: `/integrations/registry/component_state.py`
- **TESTS:** All protocol-mandated modular test files:
  - `/tests/integration/registry/test_component_registry_registration.py`
  - `/tests/integration/registry/test_component_registry_lifecycle.py`
  - `/tests/integration/registry/test_component_registry_dependency.py`

**Status:** All registry and dependency protocol modular tests pass (see day22 plan, code summary, and test results for details).

---

*For questions or pattern feedback: Submit a PR or start a thread in the `architecture` docs tree.*
