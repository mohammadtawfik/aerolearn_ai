"""
Protocol-compliant ComponentRegistry implementation.

This implementation aligns with:
  - Service health protocol
  - Dependency tracking protocol
  
Key Features:
  - Register/unregister components with version, state, and unique id
  - Deterministic insertion order for dependencies and dependents
  - Delegation of dependency management to DependencyGraph
  - Lifecycle management for components (initialize, start, stop)
  - Impact analysis for component dependencies
"""

from .component import Component
from .component_state import ComponentState
from .dependency_graph import DependencyGraph
import asyncio
from typing import Dict, Optional, List

class ComponentRegistry:
    """
    Protocol-compliant registry for registering components and declaring dependencies.
    - Uses DependencyGraph for edge management
    - Components must provide .component_id
    - Maintains deterministic ordering of dependencies
    - Each instance has its own isolated state
    """
    
    def __init__(self):
        self._components = {}  # component_id -> Component instance
        self.components = self._components  # public alias (required by dashboard/tests)
        self._dependency_graph = DependencyGraph()
        self._registration_order = []  # Preserve registration order for deterministic operations

    def register_component(self, component_id, state=ComponentState.UNKNOWN, version=None, description=None):
        """
        Register a component with the registry.
        
        Args:
            component_id: Unique identifier for the component
            state: Initial component state (defaults to ComponentState.UNKNOWN)
            version: Component version string
            description: Human-readable description
            
        Returns:
            The Component instance if registration succeeds
            
        Raises:
            ValueError: If component_id is empty or already exists
        """
        if not component_id:
            raise ValueError("component_id must not be empty.")
            
        if component_id in self._components:
            raise ValueError(f"Component {component_id} already registered")
            
        # Create a Component with only protocol-compliant parameters
        component = Component(component_id, state=state, version=version, description=description)
                             
        # Store component in all relevant data structures
        self._components[component_id] = component
        self._dependency_graph.add_node(component_id)
        self._registration_order.append(component_id)  # Track registration order
        return component

    def unregister_component(self, component):
        """
        Unregister a component from the registry.
        Returns True if successful, False otherwise.
        
        Args:
            component: Either a Component instance or a component_id string
        """
        # Handle both component objects and component_id strings
        if isinstance(component, str):
            component_id = component
        else:
            component_id = getattr(component, "component_id", None)
            
        if not component_id or component_id not in self._components:
            return False
            
        # Remove from all internal data structures
        del self._components[component_id]
        self._dependency_graph.remove_node(component_id)
        if component_id in self._registration_order:
            self._registration_order.remove(component_id)
        return True

    def declare_dependency(self, src_id, dep_id):
        """
        Declare that src_id depends on dep_id.
        Both components must exist in the registry.
        
        Args:
            src_id: ID of the source component
            dep_id: ID of the dependency component
            
        Returns:
            True if successful
            
        Raises:
            Exception: If either component is not registered
        """
        # Strict protocol: must exist as registered components first!
        if src_id not in self._components or dep_id not in self._components:
            raise Exception("Both components must be registered before declaring dependency")
        result = self._dependency_graph.add_edge(src_id, dep_id)
        if result and hasattr(self._components[src_id], "declare_dependency"):
            self._components[src_id].declare_dependency(dep_id)
        return result

    def get_dependency_graph(self):
        """
        Returns a dict mapping each component_id to list of dependencies.
        List order must match declaration order, not be arbitrary.
        """
        # Delegate to dependency graph for edge management
        return self._dependency_graph.get_all_edges()

    def get_component(self, component_id):
        """
        Get a component by its ID.
        Returns the component if found, None otherwise.
        """
        return self._components.get(component_id)
        
    def get_all_components(self):
        """
        Returns all registered components as a dict, preserving insertion order.
        """
        # Return a new dict that preserves insertion order
        return {cid: self._components[cid] for cid in self._registration_order}

    # --- Lifecycle management ---

    async def initialize_component(self, component_id):
        component = self.get_component(component_id)
        if component and hasattr(component, "initialize") and asyncio.iscoroutinefunction(component.initialize):
            return await component.initialize()
        return None

    async def start_component(self, component_id):
        component = self.get_component(component_id)
        if component and hasattr(component, "start") and asyncio.iscoroutinefunction(component.start):
            return await component.start()
        return None

    async def stop_component(self, component_id):
        component = self.get_component(component_id)
        if component and hasattr(component, "stop") and asyncio.iscoroutinefunction(component.stop):
            return await component.stop()
        return None

    async def initialize_all_components(self):
        """
        Initialize all components in registration order.
        """
        tasks = []
        for component_id in self._registration_order:
            comp = self._components[component_id]
            if hasattr(comp, "initialize") and asyncio.iscoroutinefunction(comp.initialize):
                tasks.append(comp.initialize())
        if tasks:
            await asyncio.gather(*tasks)
        return None

    async def start_all_components(self):
        """
        Start all components in registration order.
        """
        tasks = []
        for component_id in self._registration_order:
            comp = self._components[component_id]
            if hasattr(comp, "start") and asyncio.iscoroutinefunction(comp.start):
                tasks.append(comp.start())
        if tasks:
            await asyncio.gather(*tasks)
        return None

    async def stop_all_components(self):
        """
        Stop all components in reverse registration order.
        """
        tasks = []
        # Reverse order for stopping to respect dependencies
        for component_id in reversed(self._registration_order):
            comp = self._components[component_id]
            if hasattr(comp, "stop") and asyncio.iscoroutinefunction(comp.stop):
                tasks.append(comp.stop())
        if tasks:
            await asyncio.gather(*tasks)
        return None
        
    def analyze_dependency_impact(self, component_id):
        """
        Returns list of all direct dependents of component_id, per protocol.
        The list is ordered by registration order.
        """
        if component_id not in self._components:
            return []
        return self._dependency_graph.analyze_dependency_impact(component_id)
        
    def check_version_compatibility(self, component_id):
        """
        Stub: Always returns True in current implementation (future extension possible).
        """
        if component_id not in self._components:
            return False
        return True
        
    def get_dependencies(self, component_id):
        """
        Get all dependencies for a component.
        Returns a list of component_ids that this component depends on.
        """
        return self._dependency_graph.get_dependencies(component_id)
        
    def get_dependents(self, component_id):
        """
        Get all components that depend on this component.
        Returns a list of component_ids that depend on this component.
        """
        return self._dependency_graph.get_dependents(component_id)
        
    def clear(self):
        """
        Protocol: in-place reset for TDD.
        """
        # Clear internal state
        self._components.clear()
        self.components = self._components  # refresh mapping in case of external references
        self._dependency_graph = DependencyGraph()  # Create a new instance for clean state
        self._registration_order.clear()
