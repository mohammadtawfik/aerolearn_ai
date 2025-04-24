"""
Event subscriber definitions and management for the AeroLearn AI event system.

This module provides the base classes and utilities for components to subscribe to
and handle events from the event bus.
"""
import abc
import re
from typing import Callable, Dict, List, Optional, Pattern, Set, Type

from .event_types import Event, EventCategory, EventPriority


class EventFilter:
    """Filter for matching events based on various criteria."""
    
    def __init__(self, 
                 event_types: Optional[List[str]] = None,
                 categories: Optional[List[EventCategory]] = None,
                 source_components: Optional[List[str]] = None,
                 min_priority: Optional[EventPriority] = None,
                 pattern: Optional[str] = None):
        """
        Initialize an event filter with the given criteria.
        
        Args:
            event_types: List of exact event types to match
            categories: List of event categories to match
            source_components: List of source components to match
            min_priority: Minimum priority level to match
            pattern: Regex pattern to match against event type
        """
        self.event_types: Set[str] = set(event_types) if event_types else set()
        self.categories: Set[EventCategory] = set(categories) if categories else set()
        self.source_components: Set[str] = set(source_components) if source_components else set()
        self.min_priority: Optional[EventPriority] = min_priority
        self.pattern: Optional[Pattern] = re.compile(pattern) if pattern else None
    
    def matches(self, event: Event) -> bool:
        """Check if the given event matches this filter."""
        # Match by explicit event type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Match by category
        if self.categories and event.category not in self.categories:
            return False
        
        # Match by source component
        if self.source_components and event.source_component not in self.source_components:
            return False
        
        # Match by minimum priority
        if self.min_priority is not None and event.priority < self.min_priority:
            return False
        
        # Match by pattern
        if self.pattern and not self.pattern.match(event.event_type):
            return False
        
        return True


class EventSubscriber(abc.ABC):
    """Base class for components that subscribe to events."""
    
    def __init__(self, subscriber_id: str):
        """
        Initialize a new event subscriber.
        
        Args:
            subscriber_id: Unique identifier for this subscriber
        """
        self.subscriber_id = subscriber_id
        self.filters: List[EventFilter] = []
    
    def add_filter(self, event_filter: EventFilter) -> None:
        """Add a filter to this subscriber."""
        self.filters.append(event_filter)
    
    def remove_all_filters(self) -> None:
        """Remove all filters from this subscriber."""
        self.filters.clear()
    
    def is_interested_in(self, event: Event) -> bool:
        """Check if this subscriber is interested in the given event."""
        # If no filters, subscriber is interested in all events
        if not self.filters:
            return True
        
        # Check if any filter matches
        for event_filter in self.filters:
            if event_filter.matches(event):
                return True
        
        return False
    
    @abc.abstractmethod
    async def handle_event(self, event: Event) -> None:
        """
        Handle the given event. Must be implemented by subclasses.
        
        Args:
            event: The event to handle
        """
        pass


class CallbackEventSubscriber(EventSubscriber):
    """Event subscriber that delegates to a callback function."""
    
    def __init__(self, subscriber_id: str, callback: Callable[[Event], None]):
        """
        Initialize a new callback event subscriber.
        
        Args:
            subscriber_id: Unique identifier for this subscriber
            callback: Function to call when an event is received
        """
        super().__init__(subscriber_id)
        self.callback = callback
    
    async def handle_event(self, event: Event) -> None:
        """Handle the event by calling the callback."""
        self.callback(event)
