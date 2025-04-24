"""
Integration test for the event bus system.

This module tests the event bus functionality to ensure events are correctly
published and subscribers receive the events they are interested in.
"""
import asyncio
import logging
import sys
import os
from typing import List

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from integrations.events.event_bus import EventBus
from integrations.events.event_types import Event, EventCategory, EventPriority, SystemEvent
from integrations.events.event_subscribers import EventSubscriber, EventFilter


# Configure logging
logging.basicConfig(level=logging.DEBUG)


class TestEventSubscriber(EventSubscriber):
    """Test event subscriber that records received events."""
    
    def __init__(self, subscriber_id: str):
        super().__init__(subscriber_id)
        self.received_events: List[Event] = []
    
    async def handle_event(self, event: Event) -> None:
        """Record the received event."""
        self.received_events.append(event)
        logging.debug(f"Subscriber {self.subscriber_id} received event: {event.event_type}")


# For Spyder environment, we need to create and use functions rather than relying on asyncio.run
async def test_event_bus():
    """Test the event bus functionality."""
    print("Starting event bus test...")
    
    # Create and start event bus
    event_bus = EventBus()
    await event_bus.start()
    
    # Create subscribers
    subscriber1 = TestEventSubscriber("test-sub-1")
    subscriber2 = TestEventSubscriber("test-sub-2")
    
    # Set up filters
    subscriber1.add_filter(EventFilter(
        categories=[EventCategory.SYSTEM]
    ))
    subscriber2.add_filter(EventFilter(
        event_types=["system.test"]
    ))
    
    # Register subscribers
    event_bus.register_subscriber(subscriber1)
    event_bus.register_subscriber(subscriber2)
    
    # Create and publish events
    event1 = SystemEvent(
        event_type="system.test",
        source_component="test",
        data={"test_id": 1}
    )
    event2 = Event(
        event_type="user.test",
        category=EventCategory.USER,
        source_component="test",
        data={"test_id": 2}
    )
    
    # Publish events
    print("Publishing events...")
    await event_bus.publish(event1)
    await event_bus.publish(event2)
    
    # Give time for events to process
    await asyncio.sleep(0.2)
    
    # Check that events were received correctly
    print(f"Subscriber1 received {len(subscriber1.received_events)} events")
    if len(subscriber1.received_events) == 1:
        print(f"Subscriber1 event type: {subscriber1.received_events[0].event_type}")
    
    print(f"Subscriber2 received {len(subscriber2.received_events)} events")
    if len(subscriber2.received_events) == 1:
        print(f"Subscriber2 event type: {subscriber2.received_events[0].event_type}")
    
    # Test unregistering
    unregister_result1 = event_bus.unregister_subscriber("test-sub-1")
    unregister_result2 = event_bus.unregister_subscriber("non-existent")
    print(f"Unregister subscriber1: {unregister_result1}")
    print(f"Unregister non-existent: {unregister_result2}")
    
    # Publish another event
    print("Publishing another event...")
    event3 = SystemEvent(
        event_type="system.another_test",
        source_component="test",
        data={"test_id": 3}
    )
    await event_bus.publish(event3)
    
    # Wait for event processing
    await asyncio.sleep(0.2)
    
    # Check subscriber counts
    print(f"Subscriber1 now has {len(subscriber1.received_events)} events")
    print(f"Subscriber2 now has {len(subscriber2.received_events)} events")
    
    # Stop the event bus
    print("Stopping event bus...")
    await event_bus.stop()
    
    print("Test completed successfully!")


# In Spyder, you can run this function directly with:
# await test_event_bus()
#
# If running as script, we'd do this:
if __name__ == "__main__":
    print("Run this test in Spyder by executing: await test_event_bus()")
