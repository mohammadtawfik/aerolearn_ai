"""
Event bus implementation for the AeroLearn AI event system.

This module provides the central event bus for inter-component communication,
implementing the publisher-subscriber pattern with event filtering
and persistence for critical events.
"""
import threading
import logging
import json
import os
from typing import Dict, List, Optional, Callable, Any

from .event_types import EventType

# File path for persisting critical events
_EVENT_PERSISTENCE_FILE = "/tmp/aerolearn_critical_events.jsonl"

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for the AeroLearn AI system.
    
    This class implements the Singleton pattern to ensure there is only one
    event bus instance in the application.
    """
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get(cls):
        """Get the singleton instance of the EventBus."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = EventBus()
        return cls._instance
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the event bus (only executed once due to Singleton pattern)."""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._subscribers = []
        self._sub_lock = threading.Lock()
        self._stats = {
            "events_published": 0,
            "events_by_category": {},
            "subscriber_count": 0,
        }
        self._initialized = True
        logger.info("Event bus initialized")
    
    def subscribe(self, subscriber, event_filter: Optional[Callable[[EventType, dict], bool]]=None):
        """
        Subscribe to events on the bus.
        
        Args:
            subscriber: Object implementing .on_event(EventType, payload)
            event_filter: Optional predicate function (EventType, payload) -> bool
        """
        with self._sub_lock:
            self._subscribers.append((subscriber, event_filter))
            self._stats["subscriber_count"] = len(self._subscribers)
            logger.info(f"Subscriber registered: {subscriber}")
    
    def unsubscribe(self, subscriber) -> bool:
        """
        Unsubscribe from events on the bus.
        
        Args:
            subscriber: The subscriber to unregister
            
        Returns:
            True if the subscriber was unregistered, False if it was not found
        """
        with self._sub_lock:
            for i, (sub, _) in enumerate(self._subscribers):
                if sub == subscriber:
                    self._subscribers.pop(i)
                    self._stats["subscriber_count"] = len(self._subscribers)
                    logger.info(f"Subscriber unregistered: {subscriber}")
                    return True
            
            logger.warning(f"Subscriber not found: {subscriber}")
            return False
    
    def publish(self, event_type: EventType, payload: dict):
        """
        Publish an event to the bus.
        
        Args:
            event_type: The type of event
            payload: The event data
        """
        # Update statistics
        self._stats["events_published"] += 1
        category = event_type.category if hasattr(event_type, 'category') else 'default'
        if category in self._stats["events_by_category"]:
            self._stats["events_by_category"][category] += 1
        else:
            self._stats["events_by_category"][category] = 1
        
        # Persist critical events
        if hasattr(event_type, 'critical') and event_type.critical:
            self._persist_critical_event(event_type, payload)
        
        # Notify subscribers
        with self._sub_lock:
            for subscriber, event_filter in self._subscribers:
                if event_filter is None or event_filter(event_type, payload):
                    threading.Thread(
                        target=self._notify_subscriber,
                        args=(subscriber, event_type, payload)
                    ).start()
        
        logger.debug(f"Event published: {event_type}")
    
    def _notify_subscriber(self, subscriber, event_type, payload):
        """Safely notify a subscriber of an event."""
        try:
            subscriber.on_event(event_type, payload)
        except Exception as e:
            logger.error(f"Error notifying subscriber {subscriber}: {e}")
    
    def _persist_critical_event(self, event_type: EventType, payload: dict):
        """Persist critical events to disk for recovery."""
        try:
            event_data = json.dumps({
                "event_type": event_type.to_dict() if hasattr(event_type, 'to_dict') else str(event_type),
                "payload": payload
            })
            with open(_EVENT_PERSISTENCE_FILE, "a") as f:
                f.write(event_data + "\n")
        except Exception as e:
            logger.error(f"Error persisting critical event: {e}")
    
    def replay_critical_events(self):
        """Replay persisted critical events (for recovery/testing)."""
        if not os.path.exists(_EVENT_PERSISTENCE_FILE):
            logger.info("No critical events to replay")
            return []
        
        replayed_events = []
        try:
            with open(_EVENT_PERSISTENCE_FILE, "r") as f:
                lines = f.readlines()
                for line in lines:
                    j = json.loads(line)
                    if isinstance(j['event_type'], dict) and hasattr(EventType, 'from_dict'):
                        event_type = EventType.from_dict(j['event_type'])
                    else:
                        # Handle string event types or other formats
                        event_type = j['event_type']
                    
                    self.publish(event_type, j['payload'])
                    replayed_events.append((event_type, j['payload']))
            
            logger.info(f"Replayed {len(replayed_events)} critical events")
        except Exception as e:
            logger.error(f"Error replaying critical events: {e}")
        
        return replayed_events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the event bus."""
        return self._stats.copy()
    
    def get_subscriber_count(self) -> int:
        """Get the number of registered subscribers."""
        return len(self._subscribers)
    
    def clear_critical_events(self) -> bool:
        """Clear persisted critical events."""
        try:
            if os.path.exists(_EVENT_PERSISTENCE_FILE):
                os.remove(_EVENT_PERSISTENCE_FILE)
                logger.info("Critical events cleared")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing critical events: {e}")
            return False
