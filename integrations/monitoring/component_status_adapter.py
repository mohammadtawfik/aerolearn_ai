# File: /integrations/monitoring/component_status_adapter.py

from enum import Enum
from datetime import datetime
from integrations.monitoring.component_status import ComponentStatusProvider, ComponentStatusTracker

# --- ComponentState as used everywhere ---
class ComponentState(Enum):
    UNKNOWN = "unknown"
    RUNNING = "running"
    DEGRADED = "degraded"
    DOWN = "down"
    HEALTHY = "healthy"
    FAILED = "failed"

# Robust import with fallback for testing environments
try:
    from integrations.registry.component_registry import Component
except ImportError:
    # Mock Component for testing
    class Component:
        def __init__(self, name, state=None, component_type=None, version=None):
            self.name = name
            self.state = state
            self.component_type = component_type or name
            self.version = version
            self.metadata = {}

class SimpleComponentStatusProvider(ComponentStatusProvider):
    """
    Simple adapter between a Component and ComponentStatusProvider interface.
    Used to allow status tracking of registry-registered components.
    
    Always maintains a live reference to the component to ensure state changes
    are immediately reflected.
    """
    def __init__(self, component: Component):
        self.component = component  # Live reference to component

    def get_component_state(self):
        """
        Always reads the current live state from the component and converts to ComponentState enum.
        """
        # Get the current state directly from the component
        current_state = getattr(self.component, "state", ComponentState.UNKNOWN)
        
        # Ensure we're returning a proper ComponentState enum
        if isinstance(current_state, ComponentState):
            return current_state
        elif isinstance(current_state, str):
            try:
                return ComponentState[current_state.upper()]
            except KeyError:
                return ComponentState.UNKNOWN
        return ComponentState.UNKNOWN

    def get_status_details(self):
        """
        Always reads the current live metadata from the component.
        """
        return getattr(self.component, 'metadata', {})
        
    def get_status(self):
        """
        Return a ComponentStatus object representing the current status of the component.
        This method is used for compatibility with the test framework.
        Always reads fresh state and error_message at call time.
        """
        component_id = getattr(self.component, "component_id", getattr(self.component, "name", "unknown"))
        # Always get the current error_message
        error_message = getattr(self.component, "error_message", "")
        return ComponentStatus(
            component_id,
            self.get_component_state(),
            self.get_status_details(),
            error_message=error_message
        )
        
    def provide_status(self):
        """
        Return a ComponentStatus object representing the current status of the component.
        This method is used by the EnhancedComponentStatusTracker.
        Always uses the live component state and error message.
        """
        # Simply delegate to get_status to avoid duplication and ensure consistency
        return self.get_status()

class ComponentStatus:
    """
    Represents the operational status of a monitored component.
    Guarantees that error_message is never None.
    """
    def __init__(self, component_id, state=ComponentState.UNKNOWN, details=None, timestamp=None, error_message=None):
        self.component_id = component_id
        # Always use the provided enum (do not coerce between values like DEGRADED/DOWN)
        self.state = state
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
        # Always ensure error_message is a string, never None
        self.error_message = error_message if error_message is not None else ""

    def to_dict(self):
        result = {
            "component_id": self.component_id,
            "state": self.state.name if isinstance(self.state, Enum) else str(self.state),
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result

# --- Enhanced ComponentStatusTracker with explicit dependency injection ---
class EnhancedComponentStatusTracker(ComponentStatusTracker):
    """
    Enhanced version of ComponentStatusTracker that ensures faithful propagation
    of ComponentState enum values.
    
    Designed for explicit dependency injection to ensure test isolation.
    
    Provides methods for test isolation and proper component unregistration.
    """
    
    def __init__(self, registry=None):
        """
        Initialize with an optional registry instance for dependency tracking.
        
        Args:
            registry: Optional ComponentRegistry instance for dependency tracking
        """
        self.status_providers = {}
        self.status_history = {}
        self.last_state_change = {}
        self._status = {}  # component_id -> ComponentStatus
        self._registry = registry  # Use provided registry or None
        self.__dependency_graph = {}  # For get_dependency_graph compatibility
        
    @property
    def _providers(self):
        """Expose providers for test access"""
        return self.status_providers
    
    def register_status_provider(self, component_id, provider):
        """
        Register a component with a status provider. On registration, immediately update status from provider.
        """
        self.status_providers[component_id] = provider
        if component_id not in self.status_history:
            self.status_history[component_id] = []
        self.last_state_change[component_id] = datetime.now()
        
        # Initialize status by calling update_component_status with just the component_id
        # This will automatically fetch the status from the provider
        self.update_component_status(component_id)
    
    def update_component_status(self, component_id, *args, **kwargs):
        """
        Update a component's status with proper enum handling.
        Supports two calling patterns:
        - update_component_status(component_id): Gets status from provider
        - update_component_status(component_id, state, details=None): Uses provided state
        
        Always syncs with the component registry to ensure consistent state.
        """
        # First check if component exists in registry
        component = self._registry.get_component(component_id)
        
        # Determine if we're using a provider or explicit state
        if not args:
            # No state provided, try to get from provider
            if component_id in self.status_providers:
                provider = self.status_providers[component_id]
                status = provider.provide_status()
                state = status.state
                details = status.details
            elif component:
                # No provider but component exists in registry, use its state
                state = component.state
                details = getattr(component, 'metadata', {})
            else:
                # No provider registered and no component in registry
                state = ComponentState.UNKNOWN
                details = None
        else:
            # State explicitly provided
            state = args[0]
            details = kwargs.get('details') or (args[1] if len(args) > 1 else None)
            
            # If component exists in registry, update its state too
            if component:
                component.state = state
                if details and hasattr(component, 'metadata'):
                    component.metadata.update(details)
            
        # Ensure state is a ComponentState enum
        if isinstance(state, str):
            try:
                state = ComponentState[state.upper()]
            except KeyError:
                state = ComponentState.UNKNOWN
                
        status = ComponentStatus(component_id, state, details)
        self._status[component_id] = status
        self.status_history.setdefault(component_id, []).append(status)
        self.last_state_change[component_id] = datetime.now()
        return True
        
    def get_component_status(self, component_id):
        """
        Get the current status of a component.
        Always re-queries the provider for the latest status if available.
        Guarantees fresh data by forcing a provider re-query.
        """
        if component_id in self.status_providers:
            # Always re-query for latest data directly from the provider
            provider = self.status_providers[component_id]
            status = provider.provide_status()
            # Update our cached status
            self._status[component_id] = status
            return status
        # If not registered, remove any old status data and do not return
        if component_id in self._status:
            del self._status[component_id]
        return None
        
    def get_status_history(self, component_id):
        """Get the status history of a component"""
        return self.status_history.get(component_id, [])
        
    def update_all_statuses(self):
        """
        Update and return all component statuses.
        Only keeps statuses for components that are currently registered.
        Guarantees fresh data by querying each provider directly.
        """
        new_status = {}
        for component_id, provider in self.status_providers.items():
            # Get fresh status directly from provider
            status = provider.provide_status()
            new_status[component_id] = status
        
        # Replace all statuses with fresh data
        self._status = new_status
        return dict(self._status)
        
    def unregister_status_provider(self, component_id):
        """
        Unregister a component's status provider.
        Removes the component from providers, current statuses, and history.
        """
        if component_id in self.status_providers:
            del self.status_providers[component_id]
        if component_id in self._status:
            del self._status[component_id]
        if component_id in self.status_history:
            del self.status_history[component_id]
        if component_id in self.last_state_change:
            del self.last_state_change[component_id]
            
    def clear(self):
        """Clear all status providers and statuses for test isolation"""
        self.status_providers.clear()
        self.status_history.clear()
        self.last_state_change.clear()
        self._status.clear()
        
    def get_all_component_statuses(self):
        """
        Get all current component statuses.
        Only returns statuses for components that are still registered as providers.
        Always re-queries all providers for the latest status.
        Guarantees fresh data by forcing a complete refresh.
        """
        # Force update all statuses to ensure we have the latest data
        return self.update_all_statuses()
        
    @property
    def _dependency_graph(self):
        # If we have a registry with dependency information, use it
        if self._registry and hasattr(self._registry, 'get_dependency_graph'):
            return self._registry.get_dependency_graph()
        # Otherwise fall back to our internal graph
        return self.__dependency_graph
        
    @_dependency_graph.setter
    def _dependency_graph(self, graph):
        self.__dependency_graph = graph

# --- Registry with explicit instantiation ---
class ComponentRegistry:
    """
    Implementation of ComponentRegistry with dependency tracking support.
    
    Designed for explicit instantiation to ensure test isolation.
    """
    
    def __init__(self):
        """Initialize a new ComponentRegistry instance."""
        self.components = {}
        self.dependencies = {}  # e.g. {A: [B, C]}
        
    def clear(self):
        """Clear all components and dependencies for test isolation"""
        self.components.clear()
        self.dependencies.clear()
        
    def register_component(self, name, state=None, metadata=None, component_type=None, version=None):
        """
        Register a component with the registry.
        If component already exists, updates its state.
        """
        obj = self.components.get(name)
        if obj is None:
            # Only pass supported args to Component constructor
            obj = Component(name, state=state)
            self.components[name] = obj
        else:
            obj.state = state
            
        # Set metadata as field assignment after creation for compatibility
        if metadata is not None:
            obj.metadata = metadata
        return obj
        
    def declare_dependency(self, component, depends_on=None):
        """Declare that component depends on depends_on"""
        if depends_on is not None:
            self.dependencies.setdefault(component, []).append(depends_on)
            
    def get_dependency_graph(self):
        """Return the dependency graph"""
        return dict(self.dependencies)
        
    def get_component(self, name):
        """Get a component by name"""
        return self.components.get(name)
        
    def unregister_component(self, name):
        """Unregister a component from the registry"""
        if name in self.components:
            del self.components[name]
        # Also clean up dependencies
        if name in self.dependencies:
            del self.dependencies[name]
        # Remove from reverse dependencies
        for component, deps in list(self.dependencies.items()):
            if name in deps:
                self.dependencies[component].remove(name)

# --- Factory functions for creating instances ---
def make_registry():
    """Create a new ComponentRegistry instance."""
    return ComponentRegistry()

def make_tracker(registry=None):
    """
    Create a new EnhancedComponentStatusTracker instance.
    
    Args:
        registry: Optional ComponentRegistry instance to use for dependency tracking
    """
    return EnhancedComponentStatusTracker(registry)

# --- Default instances for backwards compatibility ---
COMPONENT_REGISTRY_SINGLETON = make_registry()
SYSTEM_STATUS_TRACKER = make_tracker(COMPONENT_REGISTRY_SINGLETON)

# For backwards compatibility and explicit test access
MOCK_REGISTRY = COMPONENT_REGISTRY_SINGLETON
MOCK_SYSTEM_STATUS_TRACKER = SYSTEM_STATUS_TRACKER

def clear_all_status_tracking():
    """
    Clear all status tracking data for test isolation.
    Clears both the registry and status tracker.
    
    Usage in tests:
    
    In your pytest/conftest.py or at start of every test, add:
    
    import integrations.monitoring.component_status_adapter as cs_adapter
    
    @pytest.fixture(autouse=True)
    def reset_dashboard_state_and_tracking():
        cs_adapter.clear_all_status_tracking()
    
    This ensures all state is wiped between tests.
    """
    COMPONENT_REGISTRY_SINGLETON.clear()
    SYSTEM_STATUS_TRACKER.clear()

def reset_tracking(status_tracker=None, registry=None):
    """
    Reset tracking for specific instances or the default ones.
    
    Args:
        status_tracker: The status tracker to reset, or None to use the default
        registry: The registry to reset, or None to use the default
    """
    if status_tracker is None and registry is None:
        # Legacy behavior - clear the default instances
        clear_all_status_tracking()
    else:
        # Clear the provided instances
        if status_tracker is not None:
            status_tracker.clear()
        if registry is not None:
            registry.clear()

def register_with_status_tracker(component: Component, system_status_tracker=None, registry=None):
    """
    Register a component with the status tracker.
    This function allows core components to be registered with the monitoring system
    without requiring core to directly import monitoring.
    
    Args:
        component: The component to register for status tracking
        system_status_tracker: Optional status tracker to use, defaults to SYSTEM_STATUS_TRACKER
        registry: Optional registry to use, defaults to COMPONENT_REGISTRY_SINGLETON
    """
    # Use provided instances or defaults
    status_tracker = system_status_tracker or SYSTEM_STATUS_TRACKER
    component_registry = registry or COMPONENT_REGISTRY_SINGLETON
    
    # First ensure component is in registry
    if component.name not in component_registry.components:
        component_registry.register_component(
            component.name, 
            state=component.state,
            metadata=getattr(component, 'metadata', {})
        )
    
    # Always use the live component reference
    provider = SimpleComponentStatusProvider(component)
    status_tracker.register_status_provider(component.name, provider)
    
    # Force an initial status update to ensure consistency
    status_tracker.update_component_status(component.name)
    
# Export singleton instances for direct access if needed
def get_system_status_tracker():
    """Get the default instance of the system status tracker"""
    return SYSTEM_STATUS_TRACKER
    
def get_component_registry():
    """Get the default instance of the component registry"""
    return COMPONENT_REGISTRY_SINGLETON

# Add a new class for dashboard functionality
class ServiceHealthDashboard:
    """
    Dashboard for monitoring component health with explicit dependency injection.
    """
    def __init__(self, status_tracker=None, registry=None):
        """
        Initialize with explicit tracker and registry instances.
        
        Args:
            status_tracker: The status tracker to use, or None to create a new one
            registry: The registry to use, or None to create a new one
        """
        self.status_tracker = status_tracker or make_tracker()
        self.registry = registry or make_registry()
        
        # Connect tracker to registry if not already connected
        if self.status_tracker._registry is None:
            self.status_tracker._registry = self.registry
    
    def get_all_component_statuses(self):
        """Get all current component statuses"""
        return self.status_tracker.get_all_component_statuses()
    
    def get_dependency_graph(self):
        """Get the dependency graph from the registry"""
        return self.registry.get_dependency_graph()
    
    def clear(self):
        """Clear all status tracking data"""
        self.status_tracker.clear()
        self.registry.clear()

# Export classes and factory functions for direct use
ComponentRegistry = ComponentRegistry

def unregister_from_status_tracker(component_id, system_status_tracker=None):
    """
    Unregister a component from the status tracker.
    This function allows components to be properly removed from monitoring.
    
    Args:
        component_id: The ID of the component to unregister
        system_status_tracker: Optional status tracker to use, defaults to SYSTEM_STATUS_TRACKER
    """
    status_tracker = system_status_tracker or SYSTEM_STATUS_TRACKER
    status_tracker.unregister_status_provider(component_id)
