import pytest

# Assume registry interface must be named ComponentDependencyRegistry per protocol
# and located at 'app/registry/dependency_registry.py' as per code structure conventions.

from app.registry.dependency_registry import ComponentDependencyRegistry, DependencyRegistrationError, VersionCompatibilityError

@pytest.fixture
def registry():
    return ComponentDependencyRegistry()

def test_register_single_dependency(registry):
    """
    Components must be permitted to register their dependencies as per protocol structure.
    """
    registry.register(component_id="component-A", depends_on=["component-B"])
    assert registry.get_dependencies("component-A") == ["component-B"]

def test_register_multiple_dependencies(registry):
    """
    Allow registering multiple dependencies for a single component and retrieve as a set.
    """
    registry.register(component_id="component-A", depends_on=["component-B", "component-C"])
    assert set(registry.get_dependencies("component-A")) == {"component-B", "component-C"}

def test_register_dependency_chain(registry):
    """
    Support deep chains: dependency graph traversal must resolve full ancestry as per protocol.
    """
    registry.register(component_id="A", depends_on=["B"])
    registry.register(component_id="B", depends_on=["C"])
    registry.register(component_id="C", depends_on=[])
    assert registry.get_all_dependencies("A") == ["B", "C"]

def test_detect_circular_dependency(registry):
    """
    Circular dependencies must be detected upon registration and forbidden.
    """
    registry.register(component_id="X", depends_on=["Y"])
    registry.register(component_id="Y", depends_on=[])
    with pytest.raises(DependencyRegistrationError):
        registry.register(component_id="Y", depends_on=["X"])  # X <-> Y introduces a cycle

def test_version_compatibility_pass(registry):
    """
    Should allow registration if version constraints are compatible as defined in the protocol.
    """
    result = registry.register(
        component_id="foo",
        depends_on=["bar"],
        version_constraints={"foo": ">=1.0", "bar": ">=1.0,<2.0"},
        versions={"foo": "1.5.1", "bar": "1.8.0"},
    )
    assert result is True

def test_version_compatibility_fail(registry):
    """
    Should raise VersionCompatibilityError if constraints are violated.
    """
    registry.register(
        component_id="baz",
        depends_on=["qux"],
        version_constraints={"baz": ">=2.0", "qux": ">=1.0,<2.0"},
        versions={"baz": "2.1.0", "qux": "2.2.0"},
    )
    with pytest.raises(VersionCompatibilityError):
        registry.validate_versions()

def test_dependency_impact_analysis(registry):
    """
    Simulate a dependency removal/add and verify that impact analysis covers all affected components.
    """
    registry.register(component_id="A", depends_on=["B"])
    registry.register(component_id="B", depends_on=["C"])
    registry.register(component_id="C", depends_on=[])
    impact_summary = registry.analyze_impact(change={"remove": "C"})
    assert "A" in impact_summary["affected"]
    assert "B" in impact_summary["affected"]

def test_visualization_output_format(registry):
    """
    Registry must emit a data structure suitable for visualization (e.g., node/edge list as per protocol).
    """
    registry.register(component_id="alpha", depends_on=["beta", "gamma"])
    viz = registry.export_for_visualization()
    # Example expected:
    # viz = {"nodes": ["alpha", "beta", "gamma"], "edges": [("alpha", "beta"), ("alpha", "gamma")]}
    assert "nodes" in viz and "edges" in viz