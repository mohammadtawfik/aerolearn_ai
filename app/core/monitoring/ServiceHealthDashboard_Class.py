from enum import Enum
from typing import Dict, Any, Callable, List, Optional, Set, Tuple
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

# Import ComponentState from the preferred location with fallback
try:
    from integrations.monitoring.component_status_adapter import ComponentState
except ImportError:
    from integrations.registry.component_state import ComponentState

from integrations.registry.component_registry import ComponentRegistry

# Module-level singleton instance with thread safety
_DASHBOARD_SINGLETON = None
_DASHBOARD_SINGLETON_LOCK = threading.Lock()


@dataclass
class StatusRecord:
    """
    Standardized record for component status tracking and audit logging.
    Used for health dashboard, status history, and compliance reporting.
    """
    component_id: str
    state: ComponentState  # Explicitly typed as ComponentState
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None


class ServiceHealthDashboard:
    """
    Protocol-compliant Service Health Dashboard.
    Monitors and visualizes component/service health across the AeroLearn system.

    Features:
    - Real-time status tracking and dependency visualization
    - Historical status records and audit trail
    - Health alerting with configurable callbacks
    - Component dependency graph and topology visualization

    Test compatibility:
    - status_for(name) returns the ComponentState enum
    - get_all_component_statuses returns a dict mapping name to ComponentStatus objects
    - Properly distinguishes between DEGRADED/DOWN/FAILED states for test assertions

    Health Alert Callbacks:
    - Use `register_alert_callback(cb)` to register alert callbacks
    - On a transition to DEGRADED/DOWN/FAILED, all registered callbacks are invoked with (component_id, new_state)

    Real-Time Update Callbacks:
    - Callbacks registered with watch_component are fired when component state changes
    - get_all_component_statuses provides real-time status for all components

    Metrics Support:
    - update_component_status accepts optional metrics dict for audit/dashboard/test compliance
    - get_status_history retrieves full status history for a component
    """

    def __new__(cls, status_tracker=None):
        global _DASHBOARD_SINGLETON
        with _DASHBOARD_SINGLETON_LOCK:
            if _DASHBOARD_SINGLETON is not None:
                return _DASHBOARD_SINGLETON
            inst = super().__new__(cls)
            _DASHBOARD_SINGLETON = inst
            return inst

    def __init__(self, status_tracker=None):
        # Only initialize once for singleton use
        if getattr(self, '_initialized', False):
            return
        self._initialized = True

        # Import status tracker from adapter module
        try:
            from integrations.monitoring.component_status_adapter import SYSTEM_STATUS_TRACKER
            self.status_tracker = status_tracker or SYSTEM_STATUS_TRACKER
            # Ensure bidirectional reference
            if self.status_tracker and hasattr(self.status_tracker, 'dashboard'):
                self.status_tracker.dashboard = self
        except ImportError:
            self.status_tracker = status_tracker

        self.registry = ComponentRegistry()
        self._component_history = {}  # name -> List[StatusRecord]
        self._watchers = set()
        self._listeners = {}  # Dict[str, Callable]

        # Alert callback registry
        self._alert_callbacks = []
        self._last_alerted_state = {}  # {component_id: ComponentState or None}

        # Track last notified state for real-time update callbacks
        self._last_notified_state = {}  # {component_id: ComponentState or None}
        
        # Legacy listeners for protocol compliance
        self._legacy_listeners = []

    def get_all_component_statuses(self) -> Dict[str, Any]:
        """
        Get the current (live) status of all registered components.
        Also fires real-time state update callbacks for watched components when state changes.

        :return: Dictionary mapping component names to ComponentStatus objects
                 for test compatibility
        """
        updated_statuses = {}

        if self.status_tracker and hasattr(self.status_tracker, "update_all_statuses"):
            all_statuses = self.status_tracker.update_all_statuses()
            # Process each component status
            for cid, status in all_statuses.items():
                # Unwrap status if needed
                if hasattr(status, "state"):
                    updated_statuses[cid] = status.state
                else:
                    updated_statuses[cid] = status
                
                # Fire real-time update callback if this is a watched component AND
                # the state has changed since last notification
                if cid in self._watchers:
                    last = self._last_notified_state.get(cid, None)
                    state_now = status.state if hasattr(status, "state") else status
                    if last != state_now:
                        self._notify_listeners(cid, status)
                        self._last_notified_state[cid] = state_now
            return updated_statuses

        # Fallback to registry only if status_tracker is None or missing method
        components = self.registry.components if hasattr(self.registry, 'components') else {}
        if not components and hasattr(self.registry, 'get_all_components'):
            components = self.registry.get_all_components()

        for name, comp in components.items():
            # Get component state with unwrapping if needed
            comp_state = comp.state if hasattr(comp, "state") else ComponentState.UNKNOWN
            if hasattr(comp_state, "state"):
                comp_state = comp_state.state
                
            # Create a ComponentStatus-like object for compatibility
            status = type("ComponentStatus", (), {
                "component_id": name,
                "state": comp_state,
                "timestamp": datetime.utcnow(),
                "metrics": getattr(comp, "metrics", {})
            })()
            updated_statuses[name] = comp_state  # Store unwrapped state

            if name in self._watchers:
                last = self._last_notified_state.get(name, None)
                if last != comp_state:
                    self._notify_listeners(name, status)
                    self._last_notified_state[name] = comp_state

        return updated_statuses

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency relationships between components.

        :return: Dictionary mapping component names to lists of dependencies
        """
        # Try status tracker first with both public and private access
        if self.status_tracker:
            if hasattr(self.status_tracker, "get_dependency_graph"):
                try:
                    return self.status_tracker.get_dependency_graph()
                except Exception:
                    pass
            elif hasattr(self.status_tracker, "_dependency_graph"):
                return self.status_tracker._dependency_graph

        # Fall back to registry
        if hasattr(self.registry, "get_dependency_graph"):
            return self.registry.get_dependency_graph()
        return {}

    def watch_component(self, component_id: str, callback=None) -> bool:
        """
        Register a component for active monitoring and status history tracking.
        Optionally register a callback for real-time update notifications.

        :param component_id: Component name to watch
        :param callback: Optional callback function for status updates
        :return: Success status
        """
        self._watchers.add(component_id)

        # Initialize history tracking if not already present
        if component_id not in self._component_history:
            self._component_history[component_id] = []

        # Record current state if component exists - try both access patterns
        comp = None
        if hasattr(self.registry, 'components') and component_id in self.registry.components:
            comp = self.registry.components.get(component_id)
        elif hasattr(self.registry, 'get_component'):
            comp = self.registry.get_component(component_id)

        if comp and hasattr(comp, 'state'):
            self._append_history(component_id, comp.state, getattr(comp, 'metrics', {}))

        # Register callback if provided
        if callback:
            cb_id = str(id(callback))
            self._listeners[cb_id] = (component_id, callback)

        return True

    def status_for(self, name: str) -> ComponentState:
        """
        Get the current status for a specific component.

        :param name: Component name
        :return: ComponentState enum value for test compatibility
        :raises: KeyError if component not found
        """
        # First try status tracker
        if self.status_tracker and hasattr(self.status_tracker, 'get_component_status'):
            try:
                status = self.status_tracker.get_component_status(name)
                if status:
                    # Return the state enum directly for test compatibility
                    if hasattr(status, 'state'):
                        return status.state
                    return status
            except (AttributeError, Exception):
                pass

        # Then try registry with both access patterns
        comp = None
        if hasattr(self.registry, 'components') and name in self.registry.components:
            comp = self.registry.components.get(name)
        elif hasattr(self.registry, 'get_component'):
            comp = self.registry.get_component(name)

        if comp and hasattr(comp, 'state'):
            state = comp.state
            # Unwrap state if it's a wrapper object
            if hasattr(state, 'state'):
                return state.state
            return state
            
        # Raise KeyError for strict protocol compliance
        raise KeyError(f"No such component registered: {name}")

    def get_status_history(self, component_id: str, time_range: Tuple[datetime, datetime] = None) -> List[StatusRecord]:
        """
        Get historical status records for a component.

        :param component_id: Component name
        :param time_range: Optional tuple of (start_time, end_time) to filter records
        :return: List of historical status records
        """
        if self.status_tracker and hasattr(self.status_tracker, "get_status_history"):
            history = self.status_tracker.get_status_history(component_id, time_range)
            if history:
                return history

        records = self._component_history.get(component_id, [])
        if time_range:
            start, end = time_range
            return [r for r in records if start <= r.timestamp <= end]
        return records
        
    def get_component_history(self, component_id: str, time_range: Tuple[datetime, datetime] = None) -> List[StatusRecord]:
        """
        Protocol-compliant alias for get_status_history.
        
        :param component_id: Component name
        :param time_range: Optional tuple of (start_time, end_time) to filter records
        :return: List of historical status records
        """
        return self.get_status_history(component_id, time_range)

    def update_component_status(self, component_id: str, state: ComponentState, metrics: Dict = None, message: str = None) -> bool:
        """
        Update a component's status and record in history if being watched.
        Notifies any registered listeners for this component.
        Accepts and stores metrics and message for audit and test compliance.

        :param component_id: Component name
        :param state: New state to record (ComponentState enum)
        :param metrics: Optional performance/resource metrics to associate
        :param message: Optional human-readable message about the status
        :return: Success status
        :raises: Exception if component not found
        """
        updated = False

        # Update registry directly - no status tracker calls to prevent recursion
        # Try both component access methods for compatibility
        comp = None
        if hasattr(self.registry, 'components') and component_id in self.registry.components:
            comp = self.registry.components.get(component_id)
        elif hasattr(self.registry, 'get_component'):
            comp = self.registry.get_component(component_id)

        # Strict: Raise if the component is absent (test expects this)
        if comp is None:
            raise Exception(f"Component not found: {component_id}")

        if hasattr(comp, 'state'):
            comp_state = getattr(comp, 'state')
            # If state is a wrapper class (ComponentStatus), set .state property if present; else set directly
            if hasattr(comp_state, 'state'):
                comp_state.state = state
            else:
                comp.state = state
            updated = True

        # Always record in history regardless of whether component is being watched
        self._append_history(component_id, state, metrics, message)
        
        # Add to watchers so listener/alert fire for all status-updated components
        self._watchers.add(component_id)

        # Health alerting logic - fire alerts only on transition to alert states
        alert_states = (ComponentState.DEGRADED, ComponentState.DOWN, ComponentState.FAILED)
        prev_state = self._last_alerted_state.get(component_id, None)
        
        # Fire alert only on transition into alert state (not on repeated alerts)
        if (state in alert_states) and (prev_state not in alert_states):
            self._fire_alert(component_id, state)
        
        # Always update the last alerted state
        self._last_alerted_state[component_id] = state

        # Notify listeners for all state changes
        self._notify_listeners(component_id, state)

        # Update last notified state for real-time updates
        self._last_notified_state[component_id] = state

        return updated

    def _append_history(self, component_id: str, state: ComponentState, metrics: Dict = None, message: str = None):
        """
        Add a status record to the component's history.

        :param component_id: Component name
        :param state: Component state
        :param metrics: Optional metrics dictionary
        :param message: Optional status message
        """
        if component_id not in self._component_history:
            self._component_history[component_id] = []

        # Unwrap state if it's a wrapper object
        if hasattr(state, 'state'):
            state = state.state

        record = StatusRecord(
            component_id=component_id,
            state=state,
            timestamp=datetime.utcnow(),
            metrics=metrics or {},
            message=message
        )
        self._component_history[component_id].append(record)

    def register_alert_callback(self, callback):
        """
        Register a callback function to be called when component health degrades.
        The callback will be called as callback(component_id, state) when a component
        transitions to a DEGRADED, DOWN, or FAILED state.

        :param callback: Function to call on health threshold crossing
        :return: Callback ID for potential future deregistration
        """
        cb_id = str(id(callback))
        self._alert_callbacks.append(callback)
        return cb_id

    def register_status_listener(self, callback):
        """
        Register a callback for all status updates.
        Compatible with protocol requirements.

        :param callback: Function to call on any status update
        :return: Callback ID for potential future deregistration
        """
        self._legacy_listeners.append(callback)
        cb_id = str(id(callback))
        return cb_id

    def _fire_alert(self, component_id, state):
        """
        Call all registered alert callbacks for a health threshold crossing.

        :param component_id: Component name that triggered the alert
        :param state: New component state that triggered the alert
        """
        for cb in list(self._alert_callbacks):
            try:
                cb(component_id, state)
            except Exception:
                pass  # Optionally log

    # Class method for test harness to reset singleton state
    @classmethod
    def _reset_singleton_for_test(cls):
        """Reset the singleton instance for testing purposes"""
        global _DASHBOARD_SINGLETON
        with _DASHBOARD_SINGLETON_LOCK:
            _DASHBOARD_SINGLETON = None

    def _notify_listeners(self, component_id, status):
        """
        Notify all registered listeners for a component.

        :param component_id: Component name
        :param status: New component status
        """
        # Notify component-specific listeners
        for listener_id, (cid, callback) in list(self._listeners.items()):
            if cid == component_id or cid == '*':  # '*' means all components
                try:
                    callback(component_id, status)
                except Exception:
                    pass  # Optionally log
                    
        # Notify legacy listeners (from register_status_listener)
        for lcb in getattr(self, '_legacy_listeners', []):
            try:
                lcb(component_id, status)
            except Exception:
                pass

    def get_all_history(self) -> Dict[str, List[StatusRecord]]:
        """
        Get all historical status records for all components.

        :return: Dictionary mapping component names to lists of status records
        """
        return self._component_history.copy()
        
# Module-level function for test reset (protocol compliance)
def _reset_for_test():
    """
    Reset (clear) the singleton for test isolation.
    Safe for pytest/integration use: resets registry as well.
    """
    global _DASHBOARD_SINGLETON
    with _DASHBOARD_SINGLETON_LOCK:
        if _DASHBOARD_SINGLETON is not None:
            # Clear internal state if needed
            if hasattr(_DASHBOARD_SINGLETON, "registry"):
                _DASHBOARD_SINGLETON.registry = None
        _DASHBOARD_SINGLETON = None

# For test teardown - protocol compliance
ServiceHealthDashboard._reset_for_test = staticmethod(_reset_for_test)
