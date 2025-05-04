"""
Integration tests for ComponentRegistry dependency tracking as required
by /docs/architecture/dependency_tracking_protocol.md and
/docs/development/day19_plan.md (Task 3.6.2).

Covers registration, dependency management, graph queries,
impact analysis, version compatibility stub, and removal.

Test coverage and scenarios follow the documented protocol and examples.
"""

import pytest

# Assuming interface locations per docs:
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component_state import ComponentState

@pytest.fixture
def registry():
    return ComponentRegistry()

def test_register_and_get_component(registry):
    cid = "Database"
    registry.register_component(cid, state=ComponentState.RUNNING, version="1.0")
    c = registry.get_component(cid)
    assert c is not None
    assert c.name == cid
    assert c.state == ComponentState.RUNNING
    assert c.version == "1.0"

def test_register_duplicate_component_fails(registry):
    cid = "API"
    registry.register_component(cid)
    with pytest.raises(ValueError):
        registry.register_component(cid)

def test_declare_dependency_success(registry):
    registry.register_component("API")
    registry.register_component("Database")
    assert registry.declare_dependency("API", "Database") is True
    deps = registry.get_dependencies("API")
    assert "Database" in deps

def test_declare_dependency_unknown_fails(registry):
    registry.register_component("API")
    assert registry.declare_dependency("API", "Database") is False

def test_dependency_graph_and_removal(registry):
    reg = registry
    reg.register_component("A")
    reg.register_component("B")
    reg.register_component("C")
    reg.declare_dependency("A", "B")
    reg.declare_dependency("A", "C")
    reg.declare_dependency("B", "C")
    graph = reg.get_dependency_graph()
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == ["C"]
    assert graph["C"] == []
    reg.unregister_component("C")
    # After removal C dependencies should update
    graph = reg.get_dependency_graph()
    assert graph["A"] == ["B"]
    assert "C" not in graph["A"]
    assert graph["B"] == []
    assert "C" not in graph

def test_analyze_dependency_impact(registry):
    reg = registry
    reg.register_component("A")
    reg.register_component("B")
    reg.register_component("C")
    reg.register_component("D")
    reg.declare_dependency("A", "B")
    reg.declare_dependency("A", "C")
    reg.declare_dependency("B", "C")
    reg.declare_dependency("C", "D")
    reg.declare_dependency("C", "A")  # cyclic for robustness
    impacted = set(reg.analyze_dependency_impact("D"))
    # All who depend directly/indirectly on D
    assert "C" in impacted
    assert "B" in impacted
    assert "A" in impacted

def test_version_compatibility_stub(registry):
    reg = registry
    reg.register_component("API", version="1.0")
    assert reg.check_version_compatibility("API") is True

def test_remove_updates_dependencies(registry):
    reg = registry
    reg.register_component("X")
    reg.register_component("Y")
    reg.register_component("Z")
    reg.declare_dependency("X", "Y")
    reg.declare_dependency("Y", "Z")
    reg.unregister_component("Y")
    # X should no longer list Y as a dependency
    graph = reg.get_dependency_graph()
    assert "Y" not in graph["X"]
    # Z remains (not removed)
    assert "Z" in graph

def test_get_dependencies_returns_empty_if_none(registry):
    reg = registry
    reg.register_component("Solo")
    deps = reg.get_dependencies("Solo")
    assert deps == []

def test_unregister_component_returns_false_if_absent(registry):
    reg = registry
    assert reg.unregister_component("ghost") is False

# Further tests should be added as the registry/protocol evolves, e.g., error on bad input, cyclic detection warnings, etc.