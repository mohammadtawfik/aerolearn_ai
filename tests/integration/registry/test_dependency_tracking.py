"""
Integration Test: Dependency Tracking System

Location: /tests/integration/registry/test_dependency_tracking.py

Covers:
- Component registration and dependency declaration
- Dependency graph validation
- Dependency impact analysis
- (Optional) Version compatibility checks

Production features under test: /integrations/registry/component_registry.py
"""

import pytest

from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component_state import ComponentState

@pytest.fixture(autouse=True)
def fresh_registry(monkeypatch):
    # Patch singleton instance to force real reset per test for TDD isolation
    ComponentRegistry._instance = None
    yield
    ComponentRegistry._instance = None

def test_dependency_registration_and_graph():
    registry = ComponentRegistry()

    # Register components A, B, C, D, E with different types and versions
    comp_a = registry.register_component("A", state=ComponentState.RUNNING, version="1.0")
    comp_b = registry.register_component("B", state=ComponentState.RUNNING, version="1.0")
    comp_c = registry.register_component("C", state=ComponentState.RUNNING, version="2.0")
    comp_d = registry.register_component("D", state=ComponentState.PAUSED, version="1.1")
    comp_e = registry.register_component("E", state=ComponentState.UNKNOWN, version="0.9")

    # Declare dependencies:
    # A depends on B and C
    assert registry.declare_dependency("A", "B") is True
    assert registry.declare_dependency("A", "C") is True
    # B depends on C
    assert registry.declare_dependency("B", "C") is True
    # C depends on D and E
    assert registry.declare_dependency("C", "D") is True
    assert registry.declare_dependency("C", "E") is True
    # E depends on D
    assert registry.declare_dependency("E", "D") is True

    expected_graph = {
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["D", "E"],
        "E": ["D"],
    }
    got_graph = registry.get_dependency_graph()
    # Remove empty nodes from both for comparison
    got_graph = {k: v for k, v in got_graph.items() if v}
    assert got_graph == expected_graph

def test_dependency_impact_analysis():
    registry = ComponentRegistry()

    # Setup:
    # X -> Y -> Z
    # W -> Z
    registry.register_component("X")
    registry.register_component("Y")
    registry.register_component("Z")
    registry.register_component("W")
    assert registry.declare_dependency("X", "Y")
    assert registry.declare_dependency("Y", "Z")
    assert registry.declare_dependency("W", "Z")

    # Impact of breaking Z: Y and W both directly; X indirectly via Y
    # analyze_dependency_impact should only return direct dependents
    impacted = registry.analyze_dependency_impact("Z")
    assert set(impacted) == {"Y", "W"}

    # Now break Y and check who is impacted (should be X)
    impacted = registry.analyze_dependency_impact("Y")
    assert set(impacted) == {"X"}

def test_version_compatibility_is_true_for_now():
    registry = ComponentRegistry()
    registry.register_component("foo", state=ComponentState.RUNNING, version="1.0")
    registry.register_component("bar", state=ComponentState.RUNNING, version="2.0")
    assert registry.declare_dependency("foo", "bar") is True

    # The method for compatibility always returns True in current implementation
    assert registry.check_version_compatibility("foo") is True

def test_dependency_cycle_is_supported_or_documented():
    registry = ComponentRegistry()
    registry.register_component("X")
    registry.register_component("Y")
    # Support or at least don't crash on self-cycle
    registry.declare_dependency("X", "Y")
    registry.declare_dependency("Y", "X")
    got_graph = registry.get_dependency_graph()
    assert "Y" in got_graph["X"]
    assert "X" in got_graph["Y"]
