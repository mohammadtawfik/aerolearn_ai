# /integrations/monitoring/events.py
"""
Health monitoring events module — protocol entity and dispatcher per TDD and project modularization.
See /docs/development/integration_health_modularization_plan.md.
"""

from typing import Callable, List, Any
from integrations.monitoring.health_status import HealthStatus


class HealthEvent:
    """
    Entity representing a health/monitoring event.
    """
    def __init__(self, component, state, reason, timestamp):
        # Accept either HealthStatus or string; always store as HealthStatus for protocol compliance
        if isinstance(state, str):
            try:
                state = HealthStatus[state.upper()]
            except KeyError:
                raise ValueError(f"Invalid state '{state}'. Must match a value in HealthStatus.")
        self.component = component
        self.state = state
        self.reason = reason
        self.timestamp = timestamp

    def __eq__(self, other):
        if not isinstance(other, HealthEvent):
            return False
        return (self.component == other.component and
                self.state == other.state and
                self.reason == other.reason and
                self.timestamp == other.timestamp)


class HealthEventDispatcher:
    """
    Dispatcher that manages listener registration and event firing.
    """
    def __init__(self):
        self._listeners: List[Callable[[HealthEvent], None]] = []
        
    @property
    def listeners(self):
        """Read-only view of currently registered listeners (tuple for safety)."""
        return tuple(self._listeners)

    def register_listener(self, listener):
        """
        Register a listener callback: listener(event: HealthEvent)
        """
        self._listeners.append(listener)
        
    def add_listener(self, listener):
        """
        Alias for register_listener to match test/protocol expectations.
        """
        self.register_listener(listener)
        
    def remove_listener(self, listener):
        """
        Remove a previously registered listener.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)

    def fire_event(self, event):
        """
        Fire an event to all registered listeners in registration order.
        """
        if not isinstance(event, HealthEvent):
            raise TypeError("Only HealthEvent objects can be fired")
        for listener in list(self._listeners):  # Use a copy in case listener removal happens during call
            listener(event)
            
    def fire(self, event):
        """
        Broadcast an event to all registered listeners.
        Protocol: Called by orchestrator/tests.
        """
        self.fire_event(event)


# Module-global dispatcher
_global_dispatcher = HealthEventDispatcher()


def register_health_event_listener(dispatcher, listener=None):
    """
    Protocol-driven API: Registers listener callback with the specified dispatcher instance.
    
    If only one argument is provided, it's treated as a listener for the global dispatcher
    for backward compatibility.
    """
    if listener is None:
        # Backward compatibility mode - first arg is the listener, use global dispatcher
        _global_dispatcher.register_listener(dispatcher)
    else:
        # Protocol-compliant mode - register with the specified dispatcher
        dispatcher.register_listener(listener)
    
    
def get_dispatcher():
    """
    Returns the global dispatcher instance for testing and external access.
    """
    return _global_dispatcher


# Stubs for other modules that will be implemented separately
# /integrations/monitoring/integration_health_manager.py
"""Stub for IntegrationHealthManager protocol module. Modularization target per documentation."""

# /integrations/monitoring/integration_monitor.py
"""Stub for IntegrationMonitor protocol module. Modularization target per documentation."""

# /integrations/monitoring/integration_point_registry.py
"""Stub for IntegrationPointRegistry protocol module. Modularization target per documentation."""
