# /integrations/monitoring/events.py
"""
Health monitoring events module — protocol entity and dispatcher per TDD and project modularization.
See /docs/development/integration_health_modularization_plan.md.
"""

from typing import Callable, List


class HealthEvent:
    """
    Entity representing a health/monitoring event.
    """
    def __init__(self, component, state, reason, timestamp):
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

    def register_listener(self, listener):
        """
        Register a listener callback: listener(event: HealthEvent)
        """
        self._listeners.append(listener)

    def fire_event(self, event):
        """
        Fire an event to all registered listeners in registration order.
        """
        for listener in self._listeners:
            listener(event)


# Module-global dispatcher
_global_dispatcher = HealthEventDispatcher()


def register_health_event_listener(listener):
    """
    Module-level API required by protocol/test—registers listener callback with global dispatcher.
    """
    _global_dispatcher.register_listener(listener)


# Stubs for other modules that will be implemented separately
# /integrations/monitoring/integration_health_manager.py
"""Stub for IntegrationHealthManager protocol module. Modularization target per documentation."""

# /integrations/monitoring/integration_monitor.py
"""Stub for IntegrationMonitor protocol module. Modularization target per documentation."""

# /integrations/monitoring/integration_point_registry.py
"""Stub for IntegrationPointRegistry protocol module. Modularization target per documentation."""
