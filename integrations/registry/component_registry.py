"""
Component registry for the AeroLearn AI system.

This module provides a minimal implementation of the component registry
for TDD purposes, focusing on registration, state management, and dependencies.
"""
import logging
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
from integrations.registry.component_state import ComponentState

logger = logging.getLogger(__name__)


class Component:
    """Base class for all registrable components in the system."""
    
    def __init__(self, name: str, component_type: str = None, version: str = None, 
                 state: ComponentState = ComponentState.UNKNOWN):
        """
        Initialize a component.
        
        Args:
            name: Unique identifier for this component instance
            component_type: Type identifier for this kind of component (defaults to name)
            version: Version string
            state: Initial component state
        """
        self.name = name
        self.component_type = component_type or name
        self.version = version
        self.state = state
        self.dependencies: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def declare_dependency(self, component_name: str) -> None:
        """
        Declare a dependency on another component.
        
        Args:
            component_name: The name of the required component
        """
        self.dependencies.add(component_name)
    
    def __getitem__(self, key):
        """Allow dict-style access to attributes for test compatibility."""
        if hasattr(self, key):
            return getattr(self, key)
        elif key in self.metadata:
            return self.metadata[key]
        raise KeyError(f"{key!r} not found in Component.")

class ComponentRegistry:
    """
    Central registry for AeroLearn AI system components.
    
    This class implements the Singleton pattern to ensure there is only one
    component registry instance in the application.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance
    
    def _init_storage(self):
        """Initialize storage containers."""
        self.components: Dict[str, Component] = {}
        self.components_by_type: Dict[str, Dict[str, Component]] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._initialized = True
    
    def register_component(self, name: str, state: ComponentState = ComponentState.UNKNOWN, 
                          version: str = None, component_type: str = None) -> Component:
        """
        Register a component in the registry.
        Status tracking must be registered outside of the core registry (adapter or service).
        
        Args:
            name: Unique identifier for this component
            state: Initial component state
            version: Version string
            component_type: Type of component (defaults to name)
            
        Returns:
            The registered component
        """
        if name in self.components:
            logger.warning(f"Component already registered with name: {name}")
            return self.components[name]
        
        component_type = component_type or name
        comp = Component(name=name, component_type=component_type, version=version, state=state)
        self.components[name] = comp
        
        # Register by type
        if component_type not in self.components_by_type:
            self.components_by_type[component_type] = {}
        self.components_by_type[component_type][name] = comp
        
        logger.info(f"Component registered: {name} (type: {component_type}, version: {version})")
        return comp
    
    def unregister_component(self, name: str) -> bool:
        """
        Unregister a component from the registry.
        
        Args:
            name: The name of the component to unregister
            
        Returns:
            True if unregistration successful, False if component not found
        """
        if name not in self.components:
            logger.warning(f"Component not found with name: {name}")
            return False
        
        component = self.components[name]
        
        # Unregister component
        del self.components[name]
        
        # Unregister by type
        if component.component_type in self.components_by_type:
            if name in self.components_by_type[component.component_type]:
                del self.components_by_type[component.component_type][name]
                if not self.components_by_type[component.component_type]:
                    del self.components_by_type[component.component_type]
        
        # Remove from dependency graph
        if name in self.dependency_graph:
            del self.dependency_graph[name]
        
        # Remove as dependency from other components
        for deps in self.dependency_graph.values():
            if name in deps:
                deps.remove(name)
        
        logger.info(f"Component unregistered: {name}")
        return True
    
    def get_component(self, name: str) -> Optional[Component]:
        """
        Get a component by name.
        
        Args:
            name: The name of the component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self.components.get(name)
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Component]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The type of components to get
            
        Returns:
            Dictionary of components of the specified type
        """
        return self.components_by_type.get(component_type, {}).copy()
    
    def set_component_state(self, name: str, state: ComponentState) -> bool:
        """
        Set the state of a component.
        
        Args:
            name: The name of the component
            state: The new state
            
        Returns:
            True if successful, False if component not found
        """
        if name not in self.components:
            logger.warning(f"Cannot set state: Component not found with name: {name}")
            return False
        
        self.components[name].state = state
        logger.info(f"Component state changed: {name} -> {state.value}")
        return True
    
    def declare_dependency(self, name: str, depends_on: str) -> bool:
        """
        Declare a dependency between components.
        
        Args:
            name: The dependent component name
            depends_on: The name of the component depended upon
            
        Returns:
            True if successful, False if either component not found
        """
        if name not in self.components:
            logger.warning(f"Cannot declare dependency: Component not found with name: {name}")
            return False
        
        if depends_on not in self.components:
            logger.warning(f"Cannot declare dependency: Target component not found with name: {depends_on}")
            return False
        
        # Update both the component's internal dependencies and the registry's dependency graph
        self.components[name].declare_dependency(depends_on)
        self.dependency_graph[name].add(depends_on)
        logger.info(f"Dependency declared: {name} -> {depends_on}")
        return True
    
    def get_dependencies(self, name: str) -> List[str]:
        """
        Get the dependencies of a component.
        
        Args:
            name: The name of the component
            
        Returns:
            List of component names that this component depends on
        """
        if name not in self.components:
            return []
        return list(self.components[name].dependencies)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get a graph representation of component dependencies.
        
        Returns:
            Dictionary mapping component names to lists of dependencies
        """
        # Convert sets to lists for better serialization and API consistency
        return {name: list(deps) for name, deps in self.dependency_graph.items()}
    
    def analyze_dependency_impact(self, name: str) -> List[str]:
        """
        Find all components that depend on the specified component.
        
        Args:
            name: The name of the component
            
        Returns:
            List of component names that depend on the specified component
        """
        impacted = [comp_name for comp_name, deps in self.dependency_graph.items() 
                   if name in deps]
        return impacted
    
    def check_version_compatibility(self, name: str) -> bool:
        """
        Check if a component's version is compatible with its dependencies.
        
        Args:
            name: The name of the component to check
            
        Returns:
            True if compatible, False otherwise
        """
        # For initial TDD implementation, always return True
        return True
    
    def list_components(self) -> List[str]:
        """
        Return a list of all registered component names.
        
        Returns:
            List of component names
        """
        return list(self.components.keys())
