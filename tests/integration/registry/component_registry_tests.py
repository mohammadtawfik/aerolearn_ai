import pytest

from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component_state import ComponentState

@pytest.fixture(autouse=True)
def fresh_registry(monkeypatch):
    # Enforce protocol: reset singleton for test isolation
    ComponentRegistry._instance = None
    yield
    ComponentRegistry._instance = None

def test_register_components_and_states():
    registry = ComponentRegistry()
    c1 = registry.register_component("Database", state=ComponentState.RUNNING, version="1.0")
    assert c1.name == "Database"
    assert c1.state == ComponentState.RUNNING
    assert c1.version == "1.0"
    c2 = registry.register_component("API")
    assert c2.name == "API"

def test_declare_dependencies_and_query_graph():
    registry = ComponentRegistry()
    registry.register_component("API", state=ComponentState.PAUSED)
    registry.register_component("Database", state=ComponentState.RUNNING)
    assert registry.declare_dependency("API", "Database")
    graph = registry.get_dependency_graph()
    assert graph == {'API': ['Database']}
    # Protocol: cannot declare dependency on missing component
    assert not registry.declare_dependency("API", "NotExist")

def test_impact_analysis_simple():
    registry = ComponentRegistry()
    registry.register_component("Frontend")
    registry.register_component("Backend")
    registry.declare_dependency("Frontend", "Backend")
    impacted = registry.analyze_dependency_impact("Backend")
    assert impacted == ["Frontend"]

def test_cyclic_dependencies_supported():
    registry = ComponentRegistry()
    registry.register_component("A")
    registry.register_component("B")
    registry.declare_dependency("A", "B")
    registry.declare_dependency("B", "A")
    graph = registry.get_dependency_graph()
    assert "A" in graph and "B" in graph["A"]
    assert "B" in graph and "A" in graph["B"]

def test_unregister_component_cleans_relationships():
    registry = ComponentRegistry()
    registry.register_component("Main")
    registry.register_component("Dep")
    registry.declare_dependency("Main", "Dep")
    registry.unregister_component("Dep")
    graph = registry.get_dependency_graph()
    assert "Dep" not in registry.get_dependencies("Main")
    assert "Dep" not in graph

def test_version_compatibility_default_true():
    registry = ComponentRegistry()
    registry.register_component("Service", version="1.0")
    registry.register_component("Library", version="2.0")
    registry.declare_dependency("Service", "Library")
    assert registry.check_version_compatibility("Service") is True