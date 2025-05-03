"""
Component status tracking for the AeroLearn AI system.

This module provides components for tracking and visualizing the status
of system components, including lifecycle state changes, health status,
and operational capability.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
import uuid
import time

from integrations.events.event_types import Event, EventCategory, EventPriority
from integrations.registry.component_state import ComponentState
from integrations.registry.component_registry import Component


class StatusSeverity(Enum):
    """Severity levels for component status changes."""
    INFO = auto()      # Normal operation, informational only
    WARNING = auto()   # Potential issue, degraded performance
    ERROR = auto()     # Significant problem requiring attention
    CRITICAL = auto()  # Severe issue, component cannot function


class StatusChangeEvent(Event):
    """Event fired when a component's status changes."""
    
    def __init__(
        self,
        component_id: str,
        old_state: Optional[str] = None,
        new_state: str = "",
        severity: StatusSeverity = StatusSeverity.INFO,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a status change event.
        
        Args:
            component_id: ID of the affected component
            old_state: Previous component state (if applicable)
            new_state: New component state
            severity: Severity level of the status change
            message: Human-readable description of the status change
            metadata: Additional data related to the status change
        """
        # Prepare data for parent Event class
        event_type = "status_change"
        category = EventCategory.SYSTEM
        source_component = component_id
        data = {
            "old_state": old_state,
            "new_state": new_state,
            "severity": severity.name,
            "message": message,
            "metadata": metadata or {},
        }
        
        # Initialize parent Event with required arguments
        super().__init__(
            event_type=event_type,
            category=category,
            source_component=source_component,
            data=data
        )
        
        # Set additional properties
        self.component_id = component_id
        self.old_state = old_state
        self.new_state = new_state
        self.severity = severity
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        
        # Set priority based on severity
        if severity == StatusSeverity.CRITICAL:
            self.priority = EventPriority.CRITICAL
        elif severity == StatusSeverity.ERROR:
            self.priority = EventPriority.HIGH
        elif severity == StatusSeverity.WARNING:
            self.priority = EventPriority.MEDIUM
        else:
            self.priority = EventPriority.LOW
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'component_id': self.component_id,
            'old_state': self.old_state,
            'new_state': self.new_state,
            'severity': self.severity.name,
            'message': self.message,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.name,
            'priority': self.priority.name
        }


class ComponentStatusProvider(ABC):
    """Interface for components that provide status information."""
    
    @abstractmethod
    def get_component_state(self) -> ComponentState:
        """
        Get the current state of the component.
        
        Returns:
            Current component state
        """
        pass
    
    @abstractmethod
    def get_status_details(self) -> Dict[str, Any]:
        """
        Get detailed status information about the component.
        
        Returns:
            Dictionary with status details and metrics
        """
        pass


class ComponentStatus:
    """Represents the status of a component at a specific point in time."""
    
    def __init__(
        self,
        component_id: str = "",
        state: Optional[ComponentState] = None,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a component status object.
        
        Args:
            component_id: ID of the component (optional for testing)
            state: Current state of the component (optional for testing)
            timestamp: Time the status was recorded (defaults to now)
            details: Detailed status information
        """
        self.component_id = component_id
        self.state = state
        self.timestamp = timestamp or datetime.now()
        self.details = details or {}
        self.statuses = {}  # For tracking multiple component statuses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        if not self.component_id:
            return {'statuses': {k: v for k, v in self.statuses.items()}}
        
        return {
            'component_id': self.component_id,
            'state': self.state.name if self.state else None,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    def set_status(self, component: str, status: Any) -> None:
        """
        Set status for a component in the tracking dictionary.
        
        Args:
            component: Component identifier
            status: Status value to set
        """
        self.statuses[component] = status
    
    def get_status(self, component: str, default: Any = "unknown") -> Any:
        """
        Get status for a component from the tracking dictionary.
        
        Args:
            component: Component identifier
            default: Default value if component not found
            
        Returns:
            The component's status or default if not found
        """
        return self.statuses.get(component, default)


class StatusHistoryEntry:
    """A historical status entry for a component."""
    
    def __init__(
        self,
        component_id: str,
        state: str,  # State name rather than enum to allow for custom states
        timestamp: datetime,
        severity: StatusSeverity,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a status history entry.
        
        Args:
            component_id: ID of the component
            state: State name
            timestamp: Time the status change occurred
            severity: Severity level of the status change
            message: Description of the status change
            metadata: Additional data related to the status change
        """
        self.component_id = component_id
        self.state = state
        self.timestamp = timestamp
        self.severity = severity
        self.message = message
        self.metadata = metadata or {}
        self.entry_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'entry_id': self.entry_id,
            'component_id': self.component_id,
            'state': self.state,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.name,
            'message': self.message,
            'metadata': self.metadata
        }


class ComponentStatusTracker(Component):
    """
    System for tracking component status changes over time.
    
    This class maintains current status for all registered components,
    records status history, and generates events for status changes.
    """
    
    def __init__(self, history_limit: int = 1000):
        """
        Initialize the component status tracker.
        
        Args:
            history_limit: Maximum number of status history entries to keep per component
        """
        super().__init__(
            "system.component_status_tracker",
            "monitoring",
            "1.0.0"
        )
        self.name = "Component Status Tracker"
        self.history_limit = history_limit
        self.status_providers: Dict[str, ComponentStatusProvider] = {}
        self.current_status: Dict[str, ComponentStatus] = {}
        self.status_history: Dict[str, List[StatusHistoryEntry]] = {}
        self.last_state_change: Dict[str, datetime] = {}
        self._component_dependencies: Dict[str, Set[str]] = {}
        self._component_dependents: Dict[str, Set[str]] = {}
    
    def register_status_provider(self, component_id: str, provider: ComponentStatusProvider) -> None:
        """
        Register a component that provides status information.
        
        Args:
            component_id: ID of the component
            provider: The component status provider implementation
        """
        self.status_providers[component_id] = provider
        
        # Initialize history list if needed
        if component_id not in self.status_history:
            self.status_history[component_id] = []
            self.last_state_change[component_id] = datetime.now()
            
        # Collect initial status
        self.update_component_status(component_id)
    
    def unregister_status_provider(self, component_id: str) -> None:
        """
        Unregister a status provider.
        
        Args:
            component_id: ID of the component to unregister
        """
        if component_id in self.status_providers:
            del self.status_providers[component_id]
            # Keep history and current status for reference
    
    def update_component_status(self, component_id: str) -> ComponentStatus:
        """
        Update status for a specific component.
        
        Args:
            component_id: ID of the component to update
            
        Returns:
            Updated component status
            
        Raises:
            ValueError: If component_id is not registered
        """
        if component_id not in self.status_providers:
            raise ValueError(f"Component {component_id} is not registered as a status provider")
            
        provider = self.status_providers[component_id]
        
        # Get new state and details
        try:
            state = provider.get_component_state()
            details = provider.get_status_details()
        except Exception as e:
            # If status collection fails, set to ERROR state
            state = list(ComponentState)[0]  # Use first available state as fallback
            details = {
                'error': str(e),
                'error_type': type(e).__name__
            }
        
        # Check if state has changed
        old_status = self.current_status.get(component_id)
        old_state = old_status.state if old_status else None
        
        # Create new status
        status = ComponentStatus(
            component_id=component_id,
            state=state,
            details=details
        )
        self.current_status[component_id] = status
        
        # Record state change if needed
        if old_state != state:
            self._record_state_change(
                component_id,
                str(old_state.name) if old_state else None,
                state.name,
                severity=self._determine_severity(old_state, state),
                message=self._generate_status_message(component_id, old_state, state)
            )
            
            # Update last change time
            self.last_state_change[component_id] = status.timestamp
            
            # Check dependent components that might be affected
            self._check_dependent_components(component_id, state)
        
        return status
    
    def update_all_statuses(self) -> Dict[str, ComponentStatus]:
        """
        Update status for all registered components.
        
        Returns:
            Dictionary mapping component IDs to their updated status
        """
        results = {}
        for component_id in list(self.status_providers.keys()):
            try:
                status = self.update_component_status(component_id)
                results[component_id] = status
            except Exception as e:
                print(f"Error updating status for component {component_id}: {str(e)}")
        
        return results
    
    def get_component_status(self, component_id: str) -> Optional[ComponentStatus]:
        """
        Get current status of a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            Current component status or None if not found
        """
        return self.current_status.get(component_id)
    
    def get_status_history(self, 
                           component_id: str, 
                           limit: Optional[int] = None,
                           severity_filter: Optional[List[StatusSeverity]] = None) -> List[StatusHistoryEntry]:
        """
        Get status history for a component.
        
        Args:
            component_id: ID of the component
            limit: Maximum number of entries to return (newest first)
            severity_filter: If provided, only include entries with these severities
            
        Returns:
            List of status history entries
        """
        if component_id not in self.status_history:
            return []
            
        history = self.status_history[component_id]
        
        # Apply severity filter if provided
        if severity_filter:
            history = [entry for entry in history if entry.severity in severity_filter]
            
        # Apply limit (newest first)
        if limit:
            return list(reversed(history[-limit:]))
        else:
            return list(reversed(history))
    
    def _record_state_change(
        self,
        component_id: str,
        old_state: Optional[str],
        new_state: str,
        severity: StatusSeverity,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a state change in the component's history.
        
        Args:
            component_id: ID of the component
            old_state: Previous state name
            new_state: New state name
            severity: Severity level of the change
            message: Description of the change
            metadata: Additional data about the change
        """
        # Create history entry
        entry = StatusHistoryEntry(
            component_id=component_id,
            state=new_state,
            timestamp=datetime.now(),
            severity=severity,
            message=message,
            metadata=metadata
        )
        
        # Add to history
        if component_id not in self.status_history:
            self.status_history[component_id] = []
        self.status_history[component_id].append(entry)
        
        # Trim history if needed
        if len(self.status_history[component_id]) > self.history_limit:
            self.status_history[component_id] = self.status_history[component_id][-self.history_limit:]
        
        # Create and publish event
        event = StatusChangeEvent(
            component_id=component_id,
            old_state=old_state,
            new_state=new_state,
            severity=severity,
            message=message,
            metadata=metadata
        )
        
        # Publish event - we'll integrate with EventBus later
        # For now we'll just print it for testing
        # In a real implementation, we would do:
        # from integrations.events.event_bus import EventBus
        # EventBus().publish(event)
        print(f"Status change for {component_id}: {old_state} -> {new_state} ({severity.name})")
    
    def _determine_severity(
        self,
        old_state: Optional[ComponentState],
        new_state: ComponentState
    ) -> StatusSeverity:
        """
        Determine the severity level of a state change.
        
        Args:
            old_state: Previous component state
            new_state: New component state
            
        Returns:
            Appropriate severity level
        """
        # Get all available states
        component_states = list(ComponentState)
        
        # Default severity is INFO
        severity = StatusSeverity.INFO
        
        # Check for states we know about
        for state in component_states:
            if state == new_state and "ERROR" in state.name:
                return StatusSeverity.ERROR
            elif state == new_state and "STOP" in state.name:
                return StatusSeverity.WARNING
        
        return severity
    
    def _generate_status_message(
        self,
        component_id: str,
        old_state: Optional[ComponentState],
        new_state: ComponentState
    ) -> str:
        """
        Generate a human-readable message for a state change.
        
        Args:
            component_id: ID of the component
            old_state: Previous component state
            new_state: New component state
            
        Returns:
            Human-readable message
        """
        component_name = component_id.split('.')[-1].replace('_', ' ').title()
        
        if old_state is None:
            return f"{component_name} is now {new_state.name.lower()}"
        
        # Use the state name for message generation
        state_name = new_state.name.lower()
        if "error" in state_name:
            return f"{component_name} has encountered an error"
        elif "start" in state_name:
            return f"{component_name} is starting up"
        elif "stop" in state_name and not "stopping" in state_name:
            return f"{component_name} has stopped"
        elif "stopping" in state_name:
            return f"{component_name} is shutting down"
        else:
            return f"{component_name} changed from {old_state.name.lower()} to {new_state.name.lower()}"
    
    def register_dependency(self, component_id: str, dependency_id: str) -> None:
        """
        Register a dependency relationship between components.
        
        Args:
            component_id: ID of the dependent component
            dependency_id: ID of the component it depends on
        """
        if component_id not in self._component_dependencies:
            self._component_dependencies[component_id] = set()
        self._component_dependencies[component_id].add(dependency_id)
        
        if dependency_id not in self._component_dependents:
            self._component_dependents[dependency_id] = set()
        self._component_dependents[dependency_id].add(component_id)
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Return the full dependency graph.
        
        Returns:
            Dictionary mapping component IDs to sets of dependency IDs
        """
        return self._component_dependencies
    
    def get_dependents_graph(self) -> Dict[str, Set[str]]:
        """
        Return the full dependents graph (inverse of dependency graph).
        
        Returns:
            Dictionary mapping component IDs to sets of dependent component IDs
        """
        return self._component_dependents
    
    def _check_dependent_components(self, component_id: str, state: ComponentState) -> None:
        """
        Check if dependent components need to be notified of a state change.
        
        Args:
            component_id: ID of the component that changed state
            state: New state of the component
        """
        if component_id not in self._component_dependents:
            return
        
        # Only process states that might indicate errors
        error_condition = False
        
        # Check state name for error indicators
        if "ERROR" in state.name:
            error_condition = True
            
        if not error_condition:
            return
            
        # For each dependent component, record a warning
        for dependent_id in self._component_dependents[component_id]:
            if dependent_id in self.current_status:
                self._record_state_change(
                    component_id=dependent_id,
                    old_state=self.current_status[dependent_id].state.name,
                    new_state=self.current_status[dependent_id].state.name,  # State doesn't change
                    severity=StatusSeverity.WARNING,
                    message=f"Dependency {component_id} is in {state.name} state",
                    metadata={
                        'dependency_id': component_id,
                        'dependency_state': state.name
                    }
                )
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all component statuses.
        
        Returns:
            Dictionary with status summary information
        """
        # Get all available state names
        state_names = [state.name for state in list(ComponentState)]
        
        result = {
            'components': {},
            'state_counts': {state_name: 0 for state_name in state_names},
            'timestamp': datetime.now().isoformat(),
            'total_components': len(self.current_status)
        }
        
        # Add component status summaries
        for component_id, status in self.current_status.items():
            result['components'][component_id] = {
                'state': status.state.name,
                'last_change': self.last_state_change.get(component_id, status.timestamp).isoformat(),
                'details': status.details
            }
            result['state_counts'][status.state.name] += 1
        
        return result
        
    def check_version_compatibility(self, component_versions: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Check version compatibility between components and their dependencies.
        
        Given a mapping {component_id: version}, returns a dict of incompatibilities.
        
        Args:
            component_versions: Dictionary mapping component IDs to their versions
            
        Returns:
            Dictionary mapping component IDs to lists of incompatible dependencies
        """
        incompatibilities = {}
        for comp, deps in self._component_dependencies.items():
            for dep in deps:
                if (comp in component_versions and dep in component_versions and
                        component_versions[comp] != component_versions[dep]):
                    incompatibilities.setdefault(comp, []).append(dep)
        return incompatibilities
    
    def impact_analysis(self, changed_component: str) -> List[str]:
        """
        Perform impact analysis for a changed component.
        
        Given a component_id, return all (transitive) dependents that will be
        affected by a change.
        
        Args:
            changed_component: ID of the component that changed
            
        Returns:
            List of component IDs that will be affected by the change
        """
        affected = set()
        
        # BFS to find all affected components
        queue = list(self._component_dependents.get(changed_component, []))
        while queue:
            current = queue.pop(0)
            if current not in affected:
                affected.add(current)
                queue.extend(self._component_dependents.get(current, []))
                
        return list(affected)
    
    def visualize_dependencies(self) -> Dict[str, Any]:
        """
        Generate a visualization-friendly representation of the dependency graph.
        
        Returns:
            Dictionary with nodes and links for visualization
        """
        nodes = []
        links = []
        
        # Create nodes for all components
        all_components = set(self._component_dependencies.keys()) | set(self._component_dependents.keys())
        for component_id in all_components:
            status = self.get_component_status(component_id)
            node = {
                'id': component_id,
                'name': component_id.split('.')[-1].replace('_', ' ').title(),
                'state': status.state.name if status else 'UNKNOWN'
            }
            nodes.append(node)
        
        # Create links for dependencies
        for component_id, dependencies in self._component_dependencies.items():
            for dependency_id in dependencies:
                link = {
                    'source': component_id,
                    'target': dependency_id,
                    'type': 'dependency'
                }
                links.append(link)
        
        return {
            'nodes': nodes,
            'links': links
        }
