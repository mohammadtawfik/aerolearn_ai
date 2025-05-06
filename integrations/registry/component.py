from enum import Enum

class ComponentState(Enum):
    """Component states for health monitoring"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"
    STOPPED = "stopped"

class Component:
    """
    Protocol-conformant Component as required by:
    - /docs/architecture/dependency_tracking_protocol.md
    - /docs/architecture/service_health_protocol.md
    
    Provides unique identification, state management, and dependency tracking
    for registration, health monitoring, and analytics.
    """
    def __init__(self, component_id, description=None, version=None, state=ComponentState.UNKNOWN):
        self._component_id = component_id
        self._description = description
        self._state = state
        self._version = version
        self._component_type = None
        self._dependencies = set()
        self._metadata = {}
        self._name = component_id  # Default name to component_id

    def declare_dependency(self, dep_id):
        """Add a dependency to this component's dependency set"""
        self._dependencies.add(dep_id)
        
    def get_dependencies(self):
        """Return the set of component dependencies"""
        return self._dependencies.copy()

    def set_state(self, state, details=None):
        """
        Update component state with optional metadata details
        """
        self._state = state
        if details:
            self._metadata.update(details)
        
    def get_id(self):
        """
        Protocol-mandated: Return the canonical component identifier.
        """
        return self._component_id
    
    def id(self):
        """Return the registry-assigned component id (never auto-generated)"""
        return self._component_id
    
    def get_name(self):
        """Return the component name"""
        return self._name
        
    def get_state(self):
        """
        Protocol-mandated: Return the current component state.
        """
        return self._state
        
    def get_version(self):
        """
        Protocol-mandated: Return the component version.
        """
        return self._version
        
    @property
    def version(self):
        """Return the component version"""
        return self._version
        
    def get_type(self):
        """
        Protocol-mandated: Return the component type.
        """
        return self._component_type
    
    def get_metadata(self):
        """Return a copy of the component's metadata dictionary"""
        return self._metadata.copy()
    
    def get_description(self):
        """Return the component description"""
        return self._description
        
    @property
    def description(self):
        """Return the component description"""
        return self._description
