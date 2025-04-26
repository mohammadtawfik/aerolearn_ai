"""
Event subscriber definitions and management for the AeroLearn AI event system.

This module provides the base classes and utilities for components to subscribe to
and handle events from the event bus. It also defines the EventFilter interface for selective event handling.
"""
from typing import Dict, Any, Callable, Optional, List, Set, Union

from .event_types import EventType, Event, EventPriority, EventCategory


class EventFilter:
    """
    EventFilter selects which events a subscriber is interested in 
    by event type(s), category(ies), and minimum priority.
    """
    def __init__(
        self, 
        event_types: Optional[List[str]] = None, 
        categories: Optional[List[EventCategory]] = None, 
        min_priority: Optional[EventPriority] = None
    ):
        """
        Initialize an event filter with optional filtering criteria.
        
        Args:
            event_types: List of event type strings to match
            categories: List of event categories to match
            min_priority: Minimum priority level for events
        """
        self.event_types: Optional[Set[str]] = set(event_types) if event_types else None
        self.categories: Optional[Set[EventCategory]] = set(categories) if categories else None
        self.min_priority: Optional[EventPriority] = min_priority

    def matches(self, event_or_type: Union[Event, EventType, str], category: Optional[EventCategory] = None, 
                priority: Optional[EventPriority] = None) -> bool:
        """
        Determine whether an event matches this filter's criteria.

        Args:
            event_or_type: The Event instance or event type to check
            category: The event category (if applicable, used when event_or_type is not an Event)
            priority: The event priority (if applicable, used when event_or_type is not an Event)

        Returns:
            True if the event matches filter criteria; False otherwise.
        """
        # Handle Event object case
        if isinstance(event_or_type, Event):
            event = event_or_type
            # Check event type
            if self.event_types is not None:
                etval = event.event_type
                # Accept both plain string and object with value attribute
                etval = etval.value if hasattr(etval, "value") else etval
                allowed = [et if isinstance(et, str) else getattr(et, "value", str(et)) for et in self.event_types]
                if etval not in allowed:
                    return False
            # Check category
            if self.categories is not None:
                if event.category not in self.categories:
                    return False
            # Check priority
            if self.min_priority is not None and hasattr(event, 'priority'):
                if event.priority < self.min_priority:
                    return False
            return True
        
        # Legacy case: separate event_type, category, priority
        # Check event type
        if self.event_types:
            event_type_str = event_or_type if isinstance(event_or_type, str) else getattr(event_or_type, "value", str(event_or_type))
            if event_type_str not in self.event_types:
                return False
                
        # Check category
        if self.categories and category:
            if category not in self.categories:
                return False
                
        # Check priority
        if self.min_priority and priority:
            if priority < self.min_priority:
                return False
                
        return True

    def filter(self, event_type: EventType, payload: Dict[str, Any]) -> bool:
        """
        Determine whether to accept or ignore an event.

        Args:
            event_type: The type of the event
            payload: Event data

        Returns:
            True if the event should be handled, False otherwise
        """
        # Check if payload contains an Event object
        event = payload.get('event')
        if isinstance(event, Event):
            return self.matches(event)
            
        # Legacy case: Extract category and priority from event_type if available
        category = getattr(event_type, 'category', None)
        priority = getattr(event_type, 'priority', None)
        
        # Use the matches method for consistent filtering logic
        return self.matches(event_type, category, priority)


class AcceptAllEventFilter(EventFilter):
    """
    Default event filter that accepts all events.
    """
    def __init__(self):
        """Initialize with no filtering criteria."""
        super().__init__()
        
    def matches(self, event_or_type: Union[Event, EventType, str], category: Optional[EventCategory] = None, 
                priority: Optional[EventPriority] = None) -> bool:
        """Always returns True to accept all events."""
        return True
        
    def filter(self, event_type: EventType, payload: Dict[str, Any]) -> bool:
        """Always returns True to accept all events."""
        return True


class EventSubscriber:
    """
    Abstract base class for components that subscribe to events from the EventBus.
    
    Subscribers implement the on_event method to handle events they are interested in.
    Optionally, they may provide an event_filter property for advanced filtering.
    """
    
    def on_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        """
        Handle an event from the EventBus.
        
        Args:
            event_type: The type of event that occurred
            payload: Data associated with the event
        """
        raise NotImplementedError()

    @property
    def event_filter(self) -> EventFilter:
        """
        Optional: Return an event filter instance to filter events for this subscriber.
        By default, no filtering (accept all).
        """
        return AcceptAllEventFilter()


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
        # Defensive print, EventType may not have category/action, print value directly
        print(f"Received event: {getattr(event_type, 'category', str(event_type))}/{getattr(event_type, 'action', '')} -> {payload}")


class CallbackEventSubscriber(EventSubscriber):
    """
    Event subscriber that uses a provided callback function for event processing.
    Optionally, an EventFilter can be provided to filter which events to receive.
    """
    def __init__(self, callback: Callable[[EventType, Dict[str, Any]], None], 
                 event_filter: Optional[EventFilter] = None):
        """
        Initialize with a callback and optional event filter.

        Args:
            callback: Function to invoke for each accepted event (event_type, payload)
            event_filter: Optional EventFilter, defaults to accepting all events
        """
        self._callback = callback
        self._event_filter = event_filter or AcceptAllEventFilter()

    def on_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        """Pass event to the callback function."""
        self._callback(event_type, payload)

    @property
    def event_filter(self) -> EventFilter:
        return self._event_filter
