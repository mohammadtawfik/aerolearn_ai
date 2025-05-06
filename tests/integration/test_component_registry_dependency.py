import pytest

from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component

class DummyComponent(Component):
    def __init__(self, component_id, component_type="dummy_type"):
        super().__init__(component_id, component_type)
        self._name = component_id
        self._type = component_type

    def name(self):
        return self._name

    def version(self):
        return "1.0"

def test_dependency_declaration_and_lookup():
    """Test declaring dependencies and retrieving them."""
    registry = ComponentRegistry()
    comp_a = DummyComponent("A")
    comp_b = DummyComponent("B")
    registry.register_component(comp_a)
    registry.register_component(comp_b)
    registry.declare_dependency(comp_a.get_id(), comp_b.get_id())
    deps = registry.get_dependency_graph().get_dependencies(comp_a.get_id())
    assert comp_b.get_id() in deps

def test_cycle_detection_permitted_by_protocol():
    """Protocol currently allows cycles; ensure cycles are possible, not blocked."""
    registry = ComponentRegistry()
    comp_a = DummyComponent("A")
    comp_b = DummyComponent("B")
    registry.register_component(comp_a)
    registry.register_component(comp_b)
    registry.declare_dependency(comp_a.get_id(), comp_b.get_id())
    # Protocol: No exception expected
    registry.declare_dependency(comp_b.get_id(), comp_a.get_id())
    # Validate cycle: both edges present in dependencies
    deps_a = registry.get_dependency_graph().get_dependencies(comp_a.get_id())
    deps_b = registry.get_dependency_graph().get_dependencies(comp_b.get_id())
    assert comp_b.get_id() in deps_a
    assert comp_a.get_id() in deps_b

def test_dependency_removal_and_state_restoration():
    """Test removing a dependency and protocol-compliant state after."""
    registry = ComponentRegistry()
    comp_a = DummyComponent("A")
    comp_b = DummyComponent("B")
    registry.register_component(comp_a)
    registry.register_component(comp_b)
    registry.declare_dependency(comp_a.get_id(), comp_b.get_id())
    graph = registry.get_dependency_graph()
    graph.remove_dependency(comp_a.get_id(), comp_b.get_id())
    deps = graph.get_dependencies(comp_a.get_id())
    assert comp_b.get_id() not in deps
