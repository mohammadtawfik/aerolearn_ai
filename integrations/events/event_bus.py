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
import asyncio
from typing import Dict, List, Optional, Callable, Any, Awaitable, Union

from .event_types import EventType, Event

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
        self._started = False
        self._initialized = True
        logger.info("Event bus initialized")
        
    # --- Async lifecycle for test and future async compatibility ---
    
    async def start(self) -> None:
        """Start the event bus (async, for compatibility; no-op for now)."""
        self._started = True
        logger.info("Event bus started (async noop)")
        
    async def stop(self) -> None:
        """Stop the event bus (async, for compatibility; no-op for now)."""
        self._started = False
        logger.info("Event bus stopped (async noop)")
    
    # --- API unification for test code ---
    
    def register_subscriber(self, subscriber, event_filter: Optional[Callable[[EventType, dict], bool]]=None):
        """Register a subscriber (for test compatibility; maps to subscribe())."""
        self.subscribe(subscriber, event_filter)
        
    def unregister_subscriber(self, subscriber_or_id) -> bool:
        """
        Unregister a subscriber by instance or id (for test compatibility; maps to unsubscribe()).
        
        Args:
            subscriber_or_id: The subscriber instance or subscriber_id string.
        """
        # Try instance remove first
        found = self.unsubscribe(subscriber_or_id)
        if found:
            return True
        # Try by .subscriber_id
        with self._sub_lock:
            for i, (sub, _) in enumerate(self._subscribers):
                if hasattr(sub, "subscriber_id") and sub.subscriber_id == subscriber_or_id:
                    self._subscribers.pop(i)
                    self._stats["subscriber_count"] = len(self._subscribers)
                    logger.info(f"Subscriber unregistered by id: {subscriber_or_id}")
                    return True
        logger.warning(f"Subscriber not found for unregister: {subscriber_or_id}")
        return False
    
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
    
    async def publish(self, event_or_type: Union[Event, EventType], payload: dict = None):
        """
        Publish an event to the bus.
        
        Args:
            event_or_type: Either an Event object or an EventType
            payload: The event data (required when event_or_type is EventType)
        """
        # Normalize to Event object
        if isinstance(event_or_type, Event):
            event = event_or_type
            event_type = getattr(event, "event_type", event)
            # Create a payload for backward compatibility
            payload = {"event": event}
        elif isinstance(event_or_type, EventType):
            event_type = event_or_type
            if payload is None:
                payload = {}
            # Create an Event object for modern subscribers
            event = Event(
                event_type=getattr(event_type, "event_type", None) or str(event_type),
                category=getattr(event_type, "category", None),
                source_component=payload.get("source_component", "unknown"),
                data=payload.get("data", {}),
                priority=getattr(event_type, "priority", None)
            )
            payload["event"] = event
        else:
            raise TypeError("publish() expects an Event or EventType as first arg")
            
        # Update statistics
        self._stats["events_published"] += 1
        category = getattr(event_type, "category", None) or getattr(event, "category", "default")
        if category in self._stats["events_by_category"]:
            self._stats["events_by_category"][category] += 1
        else:
            self._stats["events_by_category"][category] = 1
        
        # Persist critical events
        is_critical = (hasattr(event_type, 'critical') and event_type.critical) or \
                     (hasattr(event, 'critical') and event.critical)
        if is_critical:
            self._persist_critical_event(event, payload)
        
        # Notify subscribers
        with self._sub_lock:
            for subscriber, event_filter in self._subscribers:
                # Check if subscriber has its own filter method
                filter_func = event_filter
                if hasattr(subscriber, "event_filter"):
                    filter_func = getattr(subscriber, "event_filter")
                
                should_notify = True
                if filter_func is not None:
                    # Support different filter implementations
                    if hasattr(filter_func, "filter"):  # EventFilter API
                        should_notify = filter_func.filter(event, payload)
                    elif callable(filter_func):
                        should_notify = filter_func(event_type, payload)
                    else:
                        should_notify = bool(filter_func)
                
                if should_notify:
                    threading.Thread(
                        target=self._notify_subscriber_threadsafe,
                        args=(subscriber, event, event_type, payload)
                    ).start()
        
        logger.debug(f"Event published: {event_type}")
    
    def _notify_subscriber_threadsafe(self, subscriber, event, event_type, payload):
        """Support both async and sync event handlers with both modern and legacy interfaces."""
        try:
            # Try modern Event-based interface first
            if hasattr(subscriber, "handle_event") and callable(getattr(subscriber, "handle_event")):
                handler = getattr(subscriber, "handle_event")
                if asyncio.iscoroutinefunction(handler):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(handler(event))
                    finally:
                        loop.close()
                else:
                    handler(event)
            # Fall back to legacy interface
            elif hasattr(subscriber, "on_event") and callable(getattr(subscriber, "on_event")):
                subscriber.on_event(event_type, payload)
            else:
                logger.warning(f"Subscriber {subscriber} has no compatible event handler")
        except Exception as e:
            logger.error(f"Error notifying subscriber {subscriber}: {e}")
    
    def _persist_critical_event(self, event, payload: dict):
        """Persist critical events to disk for recovery."""
        try:
            # Handle both Event objects and EventType
            if isinstance(event, Event):
                event_data = json.dumps({
                    "event_type": getattr(event, "event_type", str(event)),
                    "payload": event.__dict__
                })
            else:
                event_data = json.dumps({
                    "event_type": event.to_dict() if hasattr(event, 'to_dict') else str(event),
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
                    payload = j['payload']
                    
                    # Try to reconstruct an Event object if possible
                    if isinstance(payload, dict) and all(k in payload for k in ["event_type", "category", "source_component"]):
                        event = Event(
                            event_type=payload.get("event_type"),
                            category=payload.get("category"),
                            source_component=payload.get("source_component", "unknown"),
                            data=payload.get("data", {}),
                            priority=payload.get("priority"),
                            timestamp=payload.get("timestamp"),
                            event_id=payload.get("event_id"),
                            is_persistent=payload.get("is_persistent", True)
                        )
                        asyncio.run(self.publish(event))
                        replayed_events.append(event)
                    else:
                        # Fall back to legacy format
                        if isinstance(j['event_type'], dict) and hasattr(EventType, 'from_dict'):
                            event_type = EventType.from_dict(j['event_type'])
                        else:
                            # Handle string event types or other formats
                            event_type = j['event_type']
                        
                        asyncio.run(self.publish(event_type, j['payload']))
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
