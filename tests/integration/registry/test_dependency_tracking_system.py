"""
Test Suite: Dependency Tracking System Integration Tests
Location: /tests/integration/registry/test_dependency_tracking_system.py

Covers Day 19 Plan Task 3.6.2:
- Component dependency registry
- Dependency visualization tools
- Version compatibility checking
- Dependency impact analysis
- Validation with complex chains
- Declaration/validation specifications

These tests will drive changes in integrations/registry/component_registry.py, possible new modules, and related code.
"""

import pytest
from unittest.mock import MagicMock, patch
from integrations.registry.dependency_tracker import DependencyTracker
from integrations.registry.component_registry import ComponentRegistry

@pytest.fixture
def dependency_registry():
    """Create a dependency registry with some pre-configured components for testing."""
    registry = ComponentRegistry()
    tracker = DependencyTracker(registry)
    
    # Register some test components
    registry.register_component("comp_a", "1.0.0", {"description": "Component A"})
    registry.register_component("comp_b", "2.1.0", {"description": "Component B"})
    registry.register_component("comp_c", "0.9.5", {"description": "Component C"})
    
    # Register some dependencies
    tracker.add_dependency("comp_b", "comp_a", ">=1.0.0")
    tracker.add_dependency("comp_c", "comp_b", ">=2.0.0")
    
    return tracker

def test_register_and_retrieve_dependencies(dependency_registry):
    """
    Should be able to register and retrieve dependencies between components.
    """
    # Register a new dependency
    dependency_registry.add_dependency("comp_d", "comp_a", ">=1.0.0")
    
    # Retrieve and verify dependencies
    deps = dependency_registry.get_dependencies("comp_d")
    assert len(deps) == 1
    assert deps[0]["component"] == "comp_a"
    assert deps[0]["version_req"] == ">=1.0.0"
    
    # Verify reverse dependencies
    rev_deps = dependency_registry.get_dependents("comp_a")
    assert "comp_b" in rev_deps
    assert "comp_d" in rev_deps


def test_dependency_visualization(dependency_registry):
    """
    Should generate accurate dependency graph data for visualization.
    """
    # Generate visualization data
    graph_data = dependency_registry.generate_dependency_graph()
    
    # Verify nodes
    nodes = graph_data["nodes"]
    assert len(nodes) >= 3  # At least our 3 components
    
    # Verify edges
    edges = graph_data["edges"]
    assert any(e["source"] == "comp_b" and e["target"] == "comp_a" for e in edges)
    assert any(e["source"] == "comp_c" and e["target"] == "comp_b" for e in edges)
    
    # Verify metadata
    assert "metadata" in graph_data
    assert graph_data["metadata"]["format_version"] == "1.0"


def test_version_compatibility_verification(dependency_registry):
    """
    Should verify component version compatibility across dependencies.
    """
    # Register component with compatible version
    dependency_registry.registry.register_component("comp_d", "1.5.0", {})
    dependency_registry.add_dependency("comp_d", "comp_a", ">=1.0.0")
    
    # This should not raise any exceptions
    dependency_registry.verify_compatibility("comp_d")
    
    # Register component with incompatible version requirement
    dependency_registry.registry.register_component("comp_e", "0.9.0", {})
    dependency_registry.add_dependency("comp_e", "comp_b", ">=3.0.0")  # comp_b is 2.1.0
    
    # This should raise a compatibility exception
    with pytest.raises(ValueError, match=r".*version compatibility.*"):
        dependency_registry.verify_compatibility("comp_e")


def test_dependency_impact_analysis(dependency_registry):
    """
    Should perform impact analysis when changing/removing components.
    """
    # Analyze impact of changing comp_a
    impact = dependency_registry.analyze_impact("comp_a")
    
    # Should affect comp_b and comp_c (transitive dependency)
    assert "comp_b" in impact["affected_components"]
    assert "comp_c" in impact["affected_components"]
    assert impact["impact_level"] == "high"  # Affects multiple components
    
    # Analyze impact of changing comp_c
    impact = dependency_registry.analyze_impact("comp_c")
    
    # Should not affect other components
    assert len(impact["affected_components"]) == 0
    assert impact["impact_level"] == "low"


def test_complex_dependency_chain_validation(dependency_registry):
    """
    Registry should validate and handle complex, nested dependency chains.
    """
    # Create a more complex dependency chain
    dependency_registry.registry.register_component("comp_d", "1.0.0", {})
    dependency_registry.registry.register_component("comp_e", "1.0.0", {})
    dependency_registry.registry.register_component("comp_f", "1.0.0", {})
    
    # Create a diamond dependency pattern
    dependency_registry.add_dependency("comp_d", "comp_b", ">=2.0.0")
    dependency_registry.add_dependency("comp_d", "comp_c", ">=0.9.0")
    dependency_registry.add_dependency("comp_e", "comp_d", "==1.0.0")
    dependency_registry.add_dependency("comp_f", "comp_e", ">=1.0.0")
    dependency_registry.add_dependency("comp_f", "comp_b", ">=2.0.0")
    
    # Validate the entire dependency chain
    validation_result = dependency_registry.validate_dependency_chain("comp_f")
    
    # Should be valid
    assert validation_result["valid"] == True
    assert "comp_a" in validation_result["resolved_dependencies"]
    assert "comp_b" in validation_result["resolved_dependencies"]
    assert "comp_c" in validation_result["resolved_dependencies"]
    assert "comp_d" in validation_result["resolved_dependencies"]
    assert "comp_e" in validation_result["resolved_dependencies"]


def test_dependency_declaration_specifications_coverage(dependency_registry):
    """
    Should enforce/depend on spec-compliant dependency declarations.
    """
    # Test with valid version specification
    dependency_registry.add_dependency("comp_c", "comp_a", ">=1.0.0,<2.0.0")
    
    # Test with invalid version specification format
    with pytest.raises(ValueError, match=r".*Invalid version specification.*"):
        dependency_registry.add_dependency("comp_c", "comp_a", "latest")
    
    # Test with non-existent component
    with pytest.raises(ValueError, match=r".*Component not found.*"):
        dependency_registry.add_dependency("comp_c", "non_existent_comp", ">=1.0.0")
    
    # Test with circular dependency detection
    with pytest.raises(ValueError, match=r".*Circular dependency.*"):
        dependency_registry.add_dependency("comp_a", "comp_c", ">=0.9.0")
