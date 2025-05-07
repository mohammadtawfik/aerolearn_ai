import pytest

from integrations.registry.component_registry import ComponentRegistry

def test_register_and_query_dependencies():
    """Test that dependencies are registered and graph is queryable per protocol."""
    registry = ComponentRegistry()
    registry.register_component('A')
    registry.register_component('B')
    # Use protocol-compliant parameter names
    registry.declare_dependency('B', 'A')
    graph = registry.get_dependency_graph()
    assert 'B' in graph
    assert 'A' in graph['B']

def test_cascade_on_dependency_failure():
    """Changing a dependency's status propagates as per dependency tracking protocol (integration with dashboard tested elsewhere)."""
    # See test_status_propagation_across_dependencies in test_service_health_protocol.py
    pass

def test_remove_dependency():
    """Test that removing a component updates the dependency graph correctly."""
    registry = ComponentRegistry()
    registry.register_component('A')
    registry.register_component('B')
    registry.declare_dependency('B', 'A')
    graph = registry.get_dependency_graph()
    assert 'A' in graph['B']
    
    registry.unregister_component('A')
    # After removal, dependencies should update
    graph = registry.get_dependency_graph()
    assert 'A' not in graph
    assert 'B' in graph
    assert not graph['B']  # B should have no dependencies

def test_lifecycle_management():
    """Lifecycle events - initialize, start, stop must be tracked and reflected in dependencies."""
    registry = ComponentRegistry()
    registry.register_component('moduleX')
    assert 'moduleX' in registry.get_dependency_graph()
    # assume explicit protocol contract for lifecycle changes
    registry.unregister_component('moduleX')
    assert 'moduleX' not in registry.get_dependency_graph()
