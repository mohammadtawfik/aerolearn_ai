import pytest

from integrations.registry.component_registry import ComponentRegistry, ComponentState

@pytest.fixture
def component_registry():
    return ComponentRegistry()

def test_register_and_query_dependency(component_registry):
    """
    Register a dependency and ensure it is correctly registered and queryable.
    """
    component_registry.register_component("A", state=ComponentState.RUNNING)
    component_registry.register_component("B", state=ComponentState.RUNNING)
    component_registry.declare_dependency("A", depends_on="B")
    deps = component_registry.get_dependencies("A")
    assert "B" in deps

def test_dependency_visualization_data(component_registry):
    """
    Dependency graph/explorer returns the correct structure for visualization.
    """
    component_registry.register_component("X", state=ComponentState.RUNNING)
    component_registry.register_component("Y", state=ComponentState.RUNNING)
    component_registry.declare_dependency("X", depends_on="Y")
    graph = component_registry.get_dependency_graph()
    assert "Y" in graph.get("X", [])

def test_version_compatibility_verification(component_registry):
    """
    The registry can be queried to verify version compatibility across dependencies.
    """
    component_registry.register_component("Frontend", state=ComponentState.RUNNING, version="1.9.0")
    component_registry.register_component("Backend", state=ComponentState.RUNNING, version="1.8.0")
    component_registry.declare_dependency("Frontend", depends_on="Backend")
    assert component_registry.check_version_compatibility("Frontend")  # should return True/False

def test_dependency_impact_analysis(component_registry):
    """
    Determine the impact if a dependency goes offline or is upgraded.
    """
    component_registry.register_component("Service1", state=ComponentState.RUNNING)
    component_registry.register_component("Service2", state=ComponentState.RUNNING)
    component_registry.declare_dependency("Service1", depends_on="Service2")
    impact = component_registry.analyze_dependency_impact("Service2")
    assert "Service1" in impact

def test_dependency_declaration_specification_documentation():
    """
    Specification documentation for dependency declaration exists.
    """
    import os
    assert os.path.exists("docs/architecture/dependency_spec.md") or \
           os.path.exists("docs/api/dependency_spec.md")