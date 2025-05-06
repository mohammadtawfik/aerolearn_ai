import pytest
from integrations.registry.component_registry import ComponentRegistry

class TestComponentRegistration:
    """Test suite for component registration and lookup functionality."""
    
    def test_register_component_and_lookup(self):
        """Test registering a component and looking it up by ID."""
        registry = ComponentRegistry()
        comp = registry.register_component(
            component_id="test.service",
            description="Test Service Component",
            version="1.0.0"
        )
        
        # Verify component can be retrieved
        result = registry.get_component("test.service")
        assert result is comp
        assert result.id() == "test.service"
        assert result.version() == "1.0.0"
    
    def test_register_duplicate_component_fails(self):
        """Ensure duplicate registration fails, as required."""
        registry = ComponentRegistry()
        registry.register_component(
            component_id="dup.service",
            description="Dup Service",
            version="1.0.1"
        )
        
        # Second registration should raise an exception
        with pytest.raises(Exception):
            registry.register_component(
                component_id="dup.service",
                description="Dup Service Again",
                version="1.0.2"
            )
    
    def test_get_nonexistent_component_returns_none(self):
        """Retrieval of an unregistered component should return None."""
        registry = ComponentRegistry()
        assert registry.get_component("nonexistent_id") is None
    
    def test_get_all_components(self):
        """Test retrieving all registered components."""
        registry = ComponentRegistry()
        
        # Register multiple components
        c1 = registry.register_component(
            component_id="service1",
            description="Service 1",
            version="1.0.0"
        )
        c2 = registry.register_component(
            component_id="service2",
            description="Service 2",
            version="1.0.0"
        )
        c3 = registry.register_component(
            component_id="service3",
            description="Service 3",
            version="1.0.0"
        )
        
        # Get all components and verify
        all_components = registry.get_all_components()
        assert len(all_components) == 3
        assert "service1" in all_components
        assert "service2" in all_components
        assert "service3" in all_components
        assert all_components["service1"] is c1
        assert all_components["service2"] is c2
        assert all_components["service3"] is c3
    
    def test_registration_preserves_insertion_order(self):
        """Test that component registration order is preserved."""
        registry = ComponentRegistry()
        
        # Register components in specific order
        ids = ["service1", "service2", "service3"]
        for component_id in ids:
            registry.register_component(
                component_id=component_id,
                description="Test Service",
                version="1.0.0"
            )
        
        # Verify order is preserved in get_all_components
        all_components = registry.get_all_components()
        assert list(all_components.keys()) == ids
