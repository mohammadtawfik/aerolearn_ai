from enum import Enum
from typing import Optional, Set, Dict, Any

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
    
    Fields:
      - component_id (str): Unique component identifier
      - name (str): Human-readable name of component
      - description (Optional[str]): Description of the component (purpose/type)
      - version (Optional[str]): Optional version string
      - component_type (Optional[str]): Type/category string
      - state (ComponentState): Current component state
    """
    def __init__(
        self, 
        component_id: str, 
        name: Optional[str] = None,
        description: Optional[str] = None, 
        version: Optional[str] = None, 
        state: ComponentState = ComponentState.UNKNOWN, 
        component_type: Optional[str] = None
    ):
        self._component_id = component_id
        self._name = name if name is not None else component_id  # Default name to component_id
        self._description = description
        self._state = state
        self._version = version
        self._component_type = component_type
        self._dependencies: Set[str] = set()
        self._metadata: Dict[str, Any] = {}

    def declare_dependency(self, dep_id: str) -> None:
        """Add a dependency to this component's dependency set"""
        self._dependencies.add(dep_id)
        
    def get_dependencies(self) -> Set[str]:
        """Return the set of component dependencies"""
        return self._dependencies.copy()

    def set_state(self, state: ComponentState, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Update component state with optional metadata details
        """
        self._state = state
        if details:
            self._metadata.update(details)
        
    @property
    def component_id(self) -> str:
        """
        Public protocol attribute for component identity.
        Required by all registry, monitoring, and protocol code.
        """
        return self._component_id
        
    def get_id(self) -> str:
        """
        Protocol-mandated: Return the canonical component identifier.
        """
        return self._component_id
    
    def id(self) -> str:
        """Return the registry-assigned component id (never auto-generated)"""
        return self._component_id
    
    @property
    def name(self) -> str:
        """Return the component name"""
        return self._name
        
    def get_name(self) -> str:
        """Return the component name"""
        return self._name
    
    @property
    def state(self) -> ComponentState:
        """Return the current component state"""
        return self._state
        
    def get_state(self) -> ComponentState:
        """
        Protocol-mandated: Return the current component state.
        """
        return self._state
        
    @property
    def version(self) -> Optional[str]:
        """Return the component version"""
        return self._version
        
    def get_version(self) -> Optional[str]:
        """
        Protocol-mandated: Return the component version.
        """
        return self._version
    
    @property
    def component_type(self) -> Optional[str]:
        """Return the component type"""
        return self._component_type
        
    def get_type(self) -> Optional[str]:
        """
        Protocol-mandated: Return the component type.
        """
        return self._component_type
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return a copy of the component's metadata dictionary"""
        return self._metadata.copy()
    
    @property
    def description(self) -> Optional[str]:
        """Return the component description"""
        return self._description
        
    def get_description(self) -> Optional[str]:
        """Return the component description"""
        return self._description
        
    def __repr__(self) -> str:
        """Return string representation for debugging"""
        return (
            f"Component(id={self._component_id!r}, name={self._name!r}, "
            f"ver={self._version!r}, type={self._component_type!r}, "
            f"state={self._state!r})"
        )
