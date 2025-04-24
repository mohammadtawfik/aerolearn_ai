"""
Component registry for the AeroLearn AI system.

This module provides a centralized registry for all system components,
tracking their lifecycle, dependencies, and version information.
"""
import logging
import threading
from typing import Dict, List, Optional, Set, Any, Callable, Type, Tuple
import asyncio
import semver  # You may need to install this package: pip install semver

from ..events.event_bus import EventBus
from ..events.event_types import Event, EventCategory, EventPriority

logger = logging.getLogger(__name__)

# Define component registry events
class ComponentRegisteredEvent(Event):
    """Event fired when a component is registered."""
    def __init__(self, component_id: str, component_type: str, version: str):
        super().__init__(
            event_type="component.registered",
            category=EventCategory.SYSTEM,
            source_component="component_registry",  # Add this line
            priority=EventPriority.NORMAL,
            data={
                "component_id": component_id,
                "component_type": component_type,
                "version": version
            },
            is_persistent=True
        )

class ComponentUnregisteredEvent(Event):
    """Event fired when a component is unregistered."""
    def __init__(self, component_id: str, component_type: str):
        super().__init__(
            event_type="component.unregistered",
            category=EventCategory.SYSTEM,
            source_component="component_registry",  # Add this line
            priority=EventPriority.NORMAL,
            data={
                "component_id": component_id,
                "component_type": component_type
            }
        )

class ComponentStateChangedEvent(Event):
    """Event fired when a component's state changes."""
    def __init__(self, component_id: str, previous_state: str, new_state: str):
        super().__init__(
            event_type="component.state_changed",
            category=EventCategory.SYSTEM,
            source_component="component_registry",  # Add this line
            priority=EventPriority.NORMAL,
            data={
                "component_id": component_id,
                "previous_state": previous_state,
                "new_state": new_state
            }
        )

class ComponentState:
    """Enum-like class for component lifecycle states."""
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class Component:
    """Base class for all registrable components in the system."""
    
    def __init__(self, component_id: str, component_type: str, version: str):
        """
        Initialize a component.
        
        Args:
            component_id: Unique identifier for this component instance
            component_type: Type identifier for this kind of component
            version: Semantic version string (e.g., "1.0.0")
        """
        self.component_id = component_id
        self.component_type = component_type
        self.version = version
        self.state = ComponentState.REGISTERED
        self.dependencies: Dict[str, Dict[str, Any]] = {}
        self.required_interfaces: Set[str] = set()
        self.provided_interfaces: Dict[str, str] = {}  # interface_name -> version
        self.metadata: Dict[str, Any] = {}
    
    def declare_dependency(self, component_type: str, version_requirement: str, optional: bool = False) -> None:
        """
        Declare a dependency on another component.
        
        Args:
            component_type: The type of component required
            version_requirement: Semver requirement string (e.g., ">=1.0.0")
            optional: Whether this dependency is optional
        """
        self.dependencies[component_type] = {
            "version_requirement": version_requirement,
            "optional": optional
        }
    
    def require_interface(self, interface_name: str) -> None:
        """
        Declare a required interface.
        
        Args:
            interface_name: Name of the required interface
        """
        self.required_interfaces.add(interface_name)
    
    def provide_interface(self, interface_name: str, version: str) -> None:
        """
        Declare a provided interface.
        
        Args:
            interface_name: Name of the provided interface
            version: Version of the provided interface
        """
        self.provided_interfaces[interface_name] = version
    
    async def initialize(self) -> bool:
        """
        Initialize the component. Override this in derived classes.
        
        Returns:
            True if initialization successful, False otherwise
        """
        self.state = ComponentState.INITIALIZED
        return True
    
    async def start(self) -> bool:
        """
        Start the component. Override this in derived classes.
        
        Returns:
            True if startup successful, False otherwise
        """
        self.state = ComponentState.STARTED
        return True
    
    async def stop(self) -> bool:
        """
        Stop the component. Override this in derived classes.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        self.state = ComponentState.STOPPING
        self.state = ComponentState.STOPPED
        return True


class ComponentRegistry:
    """
    Central registry for AeroLearn AI system components.
    
    This class implements the Singleton pattern to ensure there is only one
    component registry instance in the application.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ComponentRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the component registry (only executed once due to Singleton pattern)."""
        if self._initialized:
            return
        
        self._components: Dict[str, Component] = {}  # component_id -> component
        self._components_by_type: Dict[str, Dict[str, Component]] = {}  # component_type -> {component_id -> component}
        self._interface_providers: Dict[str, Dict[str, Component]] = {}  # interface_name -> {component_id -> component}
        self._event_bus: Optional[EventBus] = None
        self._stats: Dict[str, Any] = {
            "total_components": 0,
            "components_by_type": {},
            "component_states": {},
            "interface_counts": {}
        }
        self._initialized = True
    
    async def initialize(self) -> None:
        """Initialize the component registry."""
        self._event_bus = EventBus()
        logger.info("Component registry initialized")
    
    def register_component(self, component: Component) -> bool:
        """
        Register a component with the registry.
        
        Args:
            component: The component to register
            
        Returns:
            True if registration successful, False otherwise
        """
        if component.component_id in self._components:
            logger.warning(f"Component already registered with ID: {component.component_id}")
            return False
        
        # Register component
        self._components[component.component_id] = component
        
        # Register by type
        if component.component_type not in self._components_by_type:
            self._components_by_type[component.component_type] = {}
        self._components_by_type[component.component_type][component.component_id] = component
        
        # Register interface providers
        for interface_name in component.provided_interfaces:
            if interface_name not in self._interface_providers:
                self._interface_providers[interface_name] = {}
            self._interface_providers[interface_name][component.component_id] = component
        
        # Update statistics
        self._update_stats()
        
        # Publish event
        if self._event_bus:
            event = ComponentRegisteredEvent(
                component.component_id,
                component.component_type,
                component.version
            )
            asyncio.create_task(self._event_bus.publish(event))
        
        logger.info(f"Component registered: {component.component_id} (type: {component.component_type}, version: {component.version})")
        return True
    
    def unregister_component(self, component_id: str) -> bool:
        """
        Unregister a component from the registry.
        
        Args:
            component_id: The ID of the component to unregister
            
        Returns:
            True if unregistration successful, False if component not found
        """
        if component_id not in self._components:
            logger.warning(f"Component not found with ID: {component_id}")
            return False
        
        component = self._components[component_id]
        
        # Unregister component
        del self._components[component_id]
        
        # Unregister by type
        if (component.component_type in self._components_by_type and
                component_id in self._components_by_type[component.component_type]):
            del self._components_by_type[component.component_type][component_id]
            if not self._components_by_type[component.component_type]:
                del self._components_by_type[component.component_type]
        
        # Unregister interface providers
        for interface_name in component.provided_interfaces:
            if (interface_name in self._interface_providers and
                    component_id in self._interface_providers[interface_name]):
                del self._interface_providers[interface_name][component_id]
                if not self._interface_providers[interface_name]:
                    del self._interface_providers[interface_name]
        
        # Update statistics
        self._update_stats()
        
        # Publish event
        if self._event_bus:
            event = ComponentUnregisteredEvent(
                component.component_id,
                component.component_type
            )
            asyncio.create_task(self._event_bus.publish(event))
        
        logger.info(f"Component unregistered: {component_id}")
        return True
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self._components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Component]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The type of components to get
            
        Returns:
            Dictionary of components of the specified type
        """
        return self._components_by_type.get(component_type, {}).copy()
    
    def get_interface_providers(self, interface_name: str) -> Dict[str, Component]:
        """
        Get all components providing a specific interface.
        
        Args:
            interface_name: The name of the interface
            
        Returns:
            Dictionary of components providing the specified interface
        """
        return self._interface_providers.get(interface_name, {}).copy()
    
    async def initialize_component(self, component_id: str) -> bool:
        """
        Initialize a specific component.
        
        Args:
            component_id: The ID of the component to initialize
            
        Returns:
            True if initialization successful, False otherwise
        """
        component = self.get_component(component_id)
        if not component:
            logger.error(f"Cannot initialize: Component not found with ID: {component_id}")
            return False
        
        if component.state != ComponentState.REGISTERED:
            logger.warning(f"Component {component_id} is already initialized")
            return True  # Not an error, but already initialized
        
        previous_state = component.state
        
        try:
            result = await component.initialize()
            
            if result:
                # Publish state change event
                if self._event_bus:
                    event = ComponentStateChangedEvent(
                        component.component_id,
                        previous_state,
                        component.state
                    )
                    await self._event_bus.publish(event)
                
                self._update_stats()
                logger.info(f"Component initialized: {component_id}")
                return True
            else:
                component.state = ComponentState.ERROR
                self._update_stats()
                logger.error(f"Component initialization failed: {component_id}")
                return False
        except Exception as e:
            component.state = ComponentState.ERROR
            self._update_stats()
            logger.error(f"Error initializing component {component_id}: {e}")
            return False
    
    async def start_component(self, component_id: str) -> bool:
        """
        Start a specific component.
        
        Args:
            component_id: The ID of the component to start
            
        Returns:
            True if startup successful, False otherwise
        """
        component = self.get_component(component_id)
        if not component:
            logger.error(f"Cannot start: Component not found with ID: {component_id}")
            return False
        
        if component.state != ComponentState.INITIALIZED:
            logger.error(f"Cannot start component {component_id}: Not in initialized state")
            return False
        
        previous_state = component.state
        
        try:
            result = await component.start()
            
            if result:
                # Publish state change event
                if self._event_bus:
                    event = ComponentStateChangedEvent(
                        component.component_id,
                        previous_state,
                        component.state
                    )
                    await self._event_bus.publish(event)
                
                self._update_stats()
                logger.info(f"Component started: {component_id}")
                return True
            else:
                component.state = ComponentState.ERROR
                self._update_stats()
                logger.error(f"Component start failed: {component_id}")
                return False
        except Exception as e:
            component.state = ComponentState.ERROR
            self._update_stats()
            logger.error(f"Error starting component {component_id}: {e}")
            return False
    
    async def stop_component(self, component_id: str) -> bool:
        """
        Stop a specific component.
        
        Args:
            component_id: The ID of the component to stop
            
        Returns:
            True if shutdown successful, False otherwise
        """
        component = self.get_component(component_id)
        if not component:
            logger.error(f"Cannot stop: Component not found with ID: {component_id}")
            return False
        
        if component.state != ComponentState.STARTED:
            logger.warning(f"Component {component_id} is not in started state")
            return True  # Not an error, but already stopped
        
        previous_state = component.state
        
        try:
            result = await component.stop()
            
            if result:
                # Publish state change event
                if self._event_bus:
                    event = ComponentStateChangedEvent(
                        component.component_id,
                        previous_state,
                        component.state
                    )
                    await self._event_bus.publish(event)
                
                self._update_stats()
                logger.info(f"Component stopped: {component_id}")
                return True
            else:
                component.state = ComponentState.ERROR
                self._update_stats()
                logger.error(f"Component stop failed: {component_id}")
                return False
        except Exception as e:
            component.state = ComponentState.ERROR
            self._update_stats()
            logger.error(f"Error stopping component {component_id}: {e}")
            return False
    
    async def initialize_all_components(self) -> Tuple[int, int]:
        """
        Initialize all registered components.
        
        Returns:
            Tuple of (successful initializations, failed initializations)
        """
        success_count = 0
        fail_count = 0
        
        for component_id in list(self._components.keys()):
            if await self.initialize_component(component_id):
                success_count += 1
            else:
                fail_count += 1
        
        return success_count, fail_count
    
    async def start_all_components(self) -> Tuple[int, int]:
        """
        Start all initialized components.
        
        Returns:
            Tuple of (successful starts, failed starts)
        """
        success_count = 0
        fail_count = 0
        
        for component_id, component in self._components.items():
            if component.state == ComponentState.INITIALIZED:
                if await self.start_component(component_id):
                    success_count += 1
                else:
                    fail_count += 1
        
        return success_count, fail_count
    
    async def stop_all_components(self) -> Tuple[int, int]:
        """
        Stop all started components.
        
        Returns:
            Tuple of (successful stops, failed stops)
        """
        success_count = 0
        fail_count = 0
        
        for component_id, component in self._components.items():
            if component.state == ComponentState.STARTED:
                if await self.stop_component(component_id):
                    success_count += 1
                else:
                    fail_count += 1
        
        return success_count, fail_count
    
    def _update_stats(self) -> None:
        """Update registry statistics."""
        self._stats["total_components"] = len(self._components)
        
        # Count components by type
        self._stats["components_by_type"] = {
            component_type: len(components)
            for component_type, components in self._components_by_type.items()
        }
        
        # Count components by state
        state_counts = {}
        for component in self._components.values():
            if component.state in state_counts:
                state_counts[component.state] += 1
            else:
                state_counts[component.state] = 1
        self._stats["component_states"] = state_counts
        
        # Count interfaces
        self._stats["interface_counts"] = {
            interface_name: len(providers)
            for interface_name, providers in self._interface_providers.items()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the component registry."""
        return self._stats.copy()
    
    def check_component_compatibility(self, component: Component) -> Dict[str, List[str]]:
        """
        Check if a component is compatible with registered components.
        
        Args:
            component: The component to check
            
        Returns:
            Dictionary mapping issues to lists of affected components
        """
        issues = {}
        
        # Check dependencies
        for dep_type, dep_info in component.dependencies.items():
            req = dep_info["version_requirement"]
            providers = self.get_components_by_type(dep_type)
            
            if not providers:
                if not dep_info["optional"]:
                    if "missing_dependencies" not in issues:
                        issues["missing_dependencies"] = []
                    issues["missing_dependencies"].append(f"Missing required dependency: {dep_type} {req}")
            else:
                compatible_providers = []
                for provider_id, provider in providers.items():
                    try:
                        if semver.match(provider.version, req):
                            compatible_providers.append(provider_id)
                    except ValueError:
                        logger.warning(f"Invalid version format: {provider.version}")
                
                if not compatible_providers and not dep_info["optional"]:
                    if "incompatible_dependencies" not in issues:
                        issues["incompatible_dependencies"] = []
                    issues["incompatible_dependencies"].append(
                        f"No compatible {dep_type} found, requires {req}"
                    )
        
        # Check required interfaces
        for interface_name in component.required_interfaces:
            providers = self.get_interface_providers(interface_name)
            if not providers:
                if "missing_interfaces" not in issues:
                    issues["missing_interfaces"] = []
                issues["missing_interfaces"].append(f"Missing required interface: {interface_name}")
        
        return issues
    
    def get_component_dependency_graph(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get a graph representation of component dependencies.
        
        Returns:
            Dictionary mapping component IDs to dictionaries of dependency types
            and lists of component IDs that satisfy those dependencies
        """
        graph = {}
        
        for component_id, component in self._components.items():
            graph[component_id] = {
                "dependencies": {},
                "interfaces": {}
            }
            
            # Map dependencies
            for dep_type, dep_info in component.dependencies.items():
                req = dep_info["version_requirement"]
                providers = self.get_components_by_type(dep_type)
                compatible_providers = []
                
                for provider_id, provider in providers.items():
                    try:
                        if semver.match(provider.version, req):
                            compatible_providers.append(provider_id)
                    except ValueError:
                        pass
                
                graph[component_id]["dependencies"][dep_type] = compatible_providers
            
            # Map required interfaces
            for interface_name in component.required_interfaces:
                providers = self.get_interface_providers(interface_name)
                graph[component_id]["interfaces"][interface_name] = list(providers.keys())
        
        return graph
