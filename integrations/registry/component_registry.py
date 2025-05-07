"""
Protocol-compliant ComponentRegistry implementation.

This implementation aligns with:
  - Service health protocol
  - Dependency tracking protocol
  
Key Features:
  - Register/unregister components using component.component_id (per protocol)
  - Deterministic insertion order for dependencies and dependents
  - Delegation of dependency management to DependencyGraph
  - Lifecycle management for components (initialize, start, stop)
  - Impact analysis for component dependencies
"""

from .component import Component
from .component_state import ComponentState
from .dependency_graph import DependencyGraph
import asyncio
from typing import Dict, Optional, List, Union, Any

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
        
    def _extract_id(self, component_or_id):
        """
        Extract the protocol 'component_id' from object, string, or dict (legacy).
        Protocol requires attribute for all registered objects.
        
        Args:
            component_or_id: Either a string ID or a component with component_id attribute
            
        Returns:
            String component_id
        """
        # Accept string IDs directly
        if isinstance(component_or_id, str):
            return component_or_id
        # Accept real protocol objects (preferred)
        if hasattr(component_or_id, 'component_id'):
            return getattr(component_or_id, 'component_id', None)
        # Accept dict (legacy/testing only)
        if isinstance(component_or_id, dict):
            return component_or_id.get('component_id', None)
        return None

    def register_component(self, component):
        """
        Register a component with the registry.
        
        Args:
            component: Component object with .component_id attribute (protocol), 
                or dict with 'component_id' key (auto-wrapped for legacy/test compatibility).
            
        Returns:
            The Component instance if registration succeeds
            
        Raises:
            ValueError: If component is not protocol-compliant or lacks component_id
            ValueError: If component.component_id already exists
        """
        # Convert dict to protocol object before extracting id
        if isinstance(component, dict):
            if 'component_id' not in component:
                raise ValueError("Dict component must have a 'component_id' key per protocol")
            # Convert to protocol Component
            component = Component(
                component_id=component['component_id'],
                state=component.get('state'),
                version=component.get('version'),
                component_type=component.get('component_type')
            )
            
        component_id = self._extract_id(component)
        if not component_id:
            # Debug aid for persistent failures: print full object details for postmortem
            print("DEBUG Component registration failure:")
            print("Type:", type(component))
            print("Dir:", dir(component))
            print("Vars:", vars(component) if hasattr(component, '__dict__') else "(no __dict__)")
            raise ValueError("Component must have a 'component_id' attribute per protocol")
            
        if component_id in self._components:
            raise ValueError(f"Component {component_id} already registered")
                             
        # Store component in all relevant data structures
        self._components[component_id] = component
        self._dependency_graph.add_node(component_id)
        self._registration_order.append(component_id)  # Track registration order
        return component

    def unregister_component(self, component_or_id):
        """
        Unregister a component from the registry.
        Returns True if successful, False otherwise.
        
        Args:
            component_or_id: Either a Component instance or a component_id string
        """
        component_id = self._extract_id(component_or_id)
            
        if not component_id or component_id not in self._components:
            return False
            
        # Remove from all internal data structures
        del self._components[component_id]
        self._dependency_graph.remove_node(component_id)
        if component_id in self._registration_order:
            self._registration_order.remove(component_id)
        return True

    def declare_dependency(self, src_component_or_id, dep_component_or_id):
        """
        Declare that source depends on dependency.
        Both components must exist in the registry.
        
        Args:
            src_component_or_id: Source component or its ID
            dep_component_or_id: Dependency component or its ID
            
        Returns:
            True if successful
            
        Raises:
            Exception: If either component is not registered
        """
        src_id = self._extract_id(src_component_or_id)
        dep_id = self._extract_id(dep_component_or_id)
        
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

    def get_component(self, component_or_id):
        """
        Get a component by its ID (from component.component_id).
        Returns the component if found, None otherwise.
        """
        component_id = self._extract_id(component_or_id)
        return self._components.get(component_id)
        
    def get_all_components(self):
        """
        Returns all registered components as a dict mapping component.id to component,
        preserving insertion order.
        """
        # Return a new dict that preserves insertion order
        return {cid: self._components[cid] for cid in self._registration_order}

    # --- Lifecycle management ---

    async def initialize_component(self, component_or_id):
        component_id = self._extract_id(component_or_id)
        component = self.get_component(component_id)
        if component and hasattr(component, "initialize") and asyncio.iscoroutinefunction(component.initialize):
            return await component.initialize()
        return None

    async def start_component(self, component_or_id):
        component_id = self._extract_id(component_or_id)
        component = self.get_component(component_id)
        if component and hasattr(component, "start") and asyncio.iscoroutinefunction(component.start):
            return await component.start()
        return None

    async def stop_component(self, component_or_id):
        component_id = self._extract_id(component_or_id)
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
        
    def analyze_dependency_impact(self, component_or_id):
        """
        Returns list of all direct dependents of component_id, per protocol.
        The list is ordered by registration order.
        
        Args:
            component_or_id: Component or its ID
            
        Returns:
            List of component_ids that directly depend on the given component
        """
        component_id = self._extract_id(component_or_id)
        if component_id not in self._components:
            return []
            
        # Get all components that directly depend on this component
        impacted = []
        dependency_graph = self.get_dependency_graph()
        
        # Iterate through all components in registration order
        for dependent_id in self._registration_order:
            # Check if this component depends on our target component
            if component_id in dependency_graph.get(dependent_id, []):
                impacted.append(dependent_id)
                
        return impacted
        
    def check_version_compatibility(self, component_or_id):
        """
        Stub: Always returns True in current implementation (future extension possible).
        
        Args:
            component_or_id: Component or its ID
        """
        component_id = self._extract_id(component_or_id)
        if component_id not in self._components:
            return False
        return True
        
    def get_dependencies(self, component_or_id):
        """
        Get all dependencies for a component.
        Returns a list of component_ids that this component depends on.
        
        Args:
            component_or_id: Component or its ID
        """
        component_id = self._extract_id(component_or_id)
        return self._dependency_graph.get_dependencies(component_id)
        
    def get_dependents(self, component_or_id):
        """
        Get all components that depend on this component.
        Returns a list of component_ids that depend on this component.
        
        Args:
            component_or_id: Component or its ID
        """
        component_id = self._extract_id(component_or_id)
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
