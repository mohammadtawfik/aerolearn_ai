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
    """
    
    def __init__(self):
        """Initialize storage containers."""
        self._components: Dict[str, Component] = {}
        self._components_by_type: Dict[str, Dict[str, Component]] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
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
            
        Raises:
            ValueError: If a component with the same name is already registered
        """
        if name in self._components:
            raise ValueError(f"Component already registered with name: {name}")
        
        component_type = component_type or name
        comp = Component(name=name, component_type=component_type, version=version, state=state)
        self._components[name] = comp
        
        # Register by type
        if component_type not in self._components_by_type:
            self._components_by_type[component_type] = {}
        self._components_by_type[component_type][name] = comp
        
        # Initialize dependency tracking
        if name not in self._dependency_graph:
            self._dependency_graph[name] = set()
        
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
        if name not in self._components:
            logger.warning(f"Component not found with name: {name}")
            return False
        
        component = self._components[name]
        
        # Unregister component
        del self._components[name]
        
        # Unregister by type
        if component.component_type in self._components_by_type:
            if name in self._components_by_type[component.component_type]:
                del self._components_by_type[component.component_type][name]
                if not self._components_by_type[component.component_type]:
                    del self._components_by_type[component.component_type]
        
        # Remove from dependency graph
        if name in self._dependency_graph:
            del self._dependency_graph[name]
        
        # Remove as dependency from other components
        for deps in self._dependency_graph.values():
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
        return self._components.get(name)
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Component]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The type of components to get
            
        Returns:
            Dictionary of components of the specified type
        """
        return self._components_by_type.get(component_type, {}).copy()
    
    def set_component_state(self, name: str, state: ComponentState) -> bool:
        """
        Set the state of a component.
        
        Args:
            name: The name of the component
            state: The new state
            
        Returns:
            True if successful, False if component not found
        """
        if name not in self._components:
            logger.warning(f"Cannot set state: Component not found with name: {name}")
            return False
        
        self._components[name].state = state
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
        if name not in self._components:
            logger.warning(f"Cannot declare dependency: Component not found with name: {name}")
            return False
        
        if depends_on not in self._components:
            logger.warning(f"Cannot declare dependency: Target component not found with name: {depends_on}")
            return False
        
        # Update both the component's internal dependencies and the registry's dependency graph
        self._components[name].declare_dependency(depends_on)
        self._dependency_graph[name].add(depends_on)
        logger.info(f"Dependency declared: {name} -> {depends_on}")
        return True
    
    def get_dependencies(self, name: str) -> List[str]:
        """
        Get the dependencies of a component.
        
        Args:
            name: The name of the component
            
        Returns:
            Sorted list of component names that this component depends on
        """
        if name not in self._components:
            return []
        # Return sorted list for consistent test results
        return sorted(list(self._dependency_graph.get(name, set())))
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get a graph representation of component dependencies.
        
        Returns:
            Dictionary mapping component names to sorted lists of dependencies
        """
        # Convert sets to sorted lists for better serialization and API consistency
        return {name: sorted(list(deps)) for name, deps in self._dependency_graph.items() 
                if name in self._components}
    
    def analyze_dependency_impact(self, name: str) -> List[str]:
        """
        Find all components that depend on the specified component,
        directly or indirectly through dependency chains.
        
        Args:
            name: The name of the component
            
        Returns:
            List of component names that depend on the specified component
        """
        impacted = set()
        for comp in self._components:
            if comp == name:
                continue
            if self._depends_on(comp, name):
                impacted.add(comp)
        return sorted(list(impacted))
    
    def _depends_on(self, comp: str, target: str, visited: Optional[Set[str]]=None) -> bool:
        """
        Helper method to check if a component depends on a target component,
        directly or through a dependency chain.
        
        Args:
            comp: The component to check
            target: The target dependency
            visited: Set of already visited components to prevent cycles
            
        Returns:
            True if comp depends on target, False otherwise
        """
        if visited is None:
            visited = set()
        if comp in visited:
            return False
        visited.add(comp)
        
        # Check direct dependency
        if target in self._dependency_graph.get(comp, set()):
            return True
        
        # Check indirect dependencies
        for dep in self._dependency_graph.get(comp, set()):
            if self._depends_on(dep, target, visited):
                return True
        
        return False
    
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
        return list(self._components.keys())
