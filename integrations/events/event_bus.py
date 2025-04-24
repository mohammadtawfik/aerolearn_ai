"""
Event bus implementation for the AeroLearn AI event system.

This module provides the central event bus for inter-component communication,
implementing the publisher-subscriber pattern with advanced event filtering
and asynchronous event handling.
"""
import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Set, Any

from .event_types import Event, EventPriority
from .event_subscribers import EventSubscriber, EventFilter


logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for the AeroLearn AI system.
    
    This class implements the Singleton pattern to ensure there is only one
    event bus instance in the application.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the event bus (only executed once due to Singleton pattern)."""
        if self._initialized:
            return
        
        self._subscribers: Dict[str, EventSubscriber] = {}
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_running: bool = False
        self._worker_task: Optional[asyncio.Task] = None
        self._persistent_events: List[Event] = []
        self._stats: Dict[str, Any] = {
            "events_published": 0,
            "events_processed": 0,
            "events_by_category": {},
            "events_by_priority": {},
            "subscriber_counts": 0,
        }
        self._initialized = True
    
    async def start(self) -> None:
        """Start the event processing loop."""
        if self._is_running:
            return
        
        self._is_running = True
        self._event_loop = asyncio.get_event_loop()
        self._worker_task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event processing loop."""
        if not self._is_running:
            return
        
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
        
        logger.info("Event bus stopped")
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._is_running:
            try:
                event = await self._event_queue.get()
                await self._dispatch_event(event)
                self._event_queue.task_done()
                self._stats["events_processed"] += 1
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _dispatch_event(self, event: Event) -> None:
        """Dispatch an event to all interested subscribers."""
        interested_subscribers = [
            sub for sub in self._subscribers.values()
            if sub.is_interested_in(event)
        ]
        
        if not interested_subscribers:
            logger.debug(f"No subscribers interested in event: {event.event_type}")
            return
        
        # Store persistent events
        if event.is_persistent:
            self._persistent_events.append(event)
            # Limit the number of stored persistent events
            if len(self._persistent_events) > 1000:  # Arbitrary limit
                self._persistent_events.pop(0)
        
        # Dispatch to subscribers in priority order
        tasks = []
        for subscriber in interested_subscribers:
            try:
                task = asyncio.create_task(subscriber.handle_event(event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error dispatching event to subscriber {subscriber.subscriber_id}: {e}")
        
        await asyncio.gather(*tasks)
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event: The event to publish
        """
        if not self._is_running:
            logger.warning("Attempting to publish event while event bus is not running")
            return
        
        # Update statistics
        self._stats["events_published"] += 1
        category = event.category.value
        if category in self._stats["events_by_category"]:
            self._stats["events_by_category"][category] += 1
        else:
            self._stats["events_by_category"][category] = 1
        
        priority = int(event.priority)
        if priority in self._stats["events_by_priority"]:
            self._stats["events_by_priority"][priority] += 1
        else:
            self._stats["events_by_priority"][priority] = 1
        
        # Queue the event
        await self._event_queue.put(event)
        logger.debug(f"Event published: {event.event_type}")
    
    def register_subscriber(self, subscriber: EventSubscriber) -> None:
        """
        Register a subscriber with the event bus.
        
        Args:
            subscriber: The subscriber to register
        """
        if subscriber.subscriber_id in self._subscribers:
            logger.warning(f"Subscriber already registered with ID: {subscriber.subscriber_id}")
            return
        
        self._subscribers[subscriber.subscriber_id] = subscriber
        self._stats["subscriber_counts"] = len(self._subscribers)
        logger.info(f"Subscriber registered: {subscriber.subscriber_id}")
        
        # Send persistent events to the new subscriber
        if self._persistent_events:
            async def send_persistent_events():
                for event in self._persistent_events:
                    if subscriber.is_interested_in(event):
                        await subscriber.handle_event(event)
            
            if self._event_loop and self._is_running:
                asyncio.run_coroutine_threadsafe(send_persistent_events(), self._event_loop)
    
    def unregister_subscriber(self, subscriber_id: str) -> bool:
        """
        Unregister a subscriber from the event bus.
        
        Args:
            subscriber_id: The ID of the subscriber to unregister
        
        Returns:
            True if the subscriber was unregistered, False if it was not found
        """
        if subscriber_id not in self._subscribers:
            logger.warning(f"Subscriber not found with ID: {subscriber_id}")
            return False
        
        del self._subscribers[subscriber_id]
        self._stats["subscriber_counts"] = len(self._subscribers)
        logger.info(f"Subscriber unregistered: {subscriber_id}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the event bus."""
        return self._stats.copy()
    
    def get_subscriber_count(self) -> int:
        """Get the number of registered subscribers."""
        return len(self._subscribers)
    
    def get_queue_size(self) -> int:
        """Get the current event queue size."""
        return self._event_queue.qsize()
    
    def clear_persistent_events(self) -> None:
        """Clear all persistent events."""
        self._persistent_events.clear()
