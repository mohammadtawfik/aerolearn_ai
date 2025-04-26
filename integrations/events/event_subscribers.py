"""
Event subscriber definitions and management for the AeroLearn AI event system.

This module provides the base classes and utilities for components to subscribe to
and handle events from the event bus.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

from .event_types import EventType


class EventSubscriber(ABC):
    """
    Abstract base class for components that subscribe to events from the EventBus.
    
    Subscribers implement the on_event method to handle events they are interested in.
    """
    
    @abstractmethod
    def on_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        """
        Handle an event from the EventBus.
        
        Args:
            event_type: The type of event that occurred
            payload: Data associated with the event
        """
        pass


class LoggingEventSubscriber(EventSubscriber):
    """Example event subscriber that logs all received events."""
    
    def __init__(self):
        """Initialize a new logging event subscriber."""
        self.events = []
    
    def on_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        """
        Log the received event.
        
        Args:
            event_type: The type of event that occurred
            payload: Data associated with the event
        """
        self.events.append((event_type, payload))
        print(f"Received event: {event_type.category}/{event_type.action} -> {payload}")
