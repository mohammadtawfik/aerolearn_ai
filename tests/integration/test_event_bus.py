# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Integration test for the event bus system.

This module tests the event bus functionality to ensure events are correctly
published, subscribers receive the correct events, filters work, and concurrent/event thread safety is maintained.
"""

import asyncio
import logging
import sys
import os
from typing import List

import pytest
import threading

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from integrations.events.event_bus import EventBus
from integrations.events.event_types import Event, EventCategory, EventPriority, SystemEvent
from integrations.events.event_subscribers import EventSubscriber, EventFilter

logging.basicConfig(level=logging.DEBUG)

class TestEventSubscriber(EventSubscriber):
    """Test subscriber that records received events for verification."""
    def __init__(self, subscriber_id: str):
        super().__init__(subscriber_id)
        self.received_events: List[Event] = []
        self.lock = threading.Lock()
    
    async def handle_event(self, event: Event) -> None:
        with self.lock:
            self.received_events.append(event)
        logging.debug(f"Subscriber {self.subscriber_id} received event: {event.event_type}")

    def reset(self):
        with self.lock:
            self.received_events.clear()

@pytest.mark.asyncio
async def test_event_bus_basic_routing():
    """Test publish/subscribe and filtering for multiple subscribers."""

    event_bus = EventBus()
    await event_bus.start()

    sub_system = TestEventSubscriber("system_subscriber")
    sub_user = TestEventSubscriber("user_subscriber")

    # Setup filters:
    sub_system.add_filter(EventFilter(categories=[EventCategory.SYSTEM]))
    sub_user.add_filter(EventFilter(event_types=["user.test"]))

    event_bus.register_subscriber(sub_system)
    event_bus.register_subscriber(sub_user)

    # Events to publish
    sys_event = SystemEvent(
        event_type="system.test",
        source_component="core",
        data={"key": "sys"}
    )
    user_event = Event(
        event_type="user.test",
        category=EventCategory.USER,
        source_component="ui",
        data={"key": "user"}
    )

    # Publish events
    await event_bus.publish(sys_event)
    await event_bus.publish(user_event)
    await asyncio.sleep(0.2)  # Allow event processing

    # Verification
    assert any(ev.event_type == "system.test" for ev in sub_system.received_events), "System subscriber should receive system.test event."
    assert not any(ev.event_type == "user.test" for ev in sub_system.received_events), "System subscriber should NOT receive user events."

    assert any(ev.event_type == "user.test" for ev in sub_user.received_events), "User subscriber should receive user.test event."
    assert not any(ev.event_type == "system.test" for ev in sub_user.received_events), "User subscriber should NOT receive system events."

    # Unregister and test
    event_bus.unregister_subscriber(sub_user.subscriber_id)
    sub_user.reset()
    await event_bus.publish(user_event)
    await asyncio.sleep(0.2)
    assert not sub_user.received_events, "Unregistered subscriber should receive no events."

    await event_bus.stop()

@pytest.mark.asyncio
async def test_event_bus_serialization_consistency():
    """Test event serialization and deserialization works properly."""
    data = {"foo": 123, "bar": "baz"}
    orig_event = Event(
        event_type="custom.serialize",
        category=EventCategory.SYSTEM,
        source_component="test",
        data=data,
        priority=EventPriority.NORMAL
    )
    serialized = orig_event.serialize()
    restored = Event.deserialize(serialized)
    assert restored.event_type == orig_event.event_type
    assert restored.category == orig_event.category
    assert restored.source_component == orig_event.source_component
    assert restored.data == orig_event.data
    assert restored.priority == orig_event.priority
    assert isinstance(restored.timestamp, type(orig_event.timestamp))
    assert restored.event_id == orig_event.event_id

@pytest.mark.asyncio
async def test_event_bus_filtering_logic():
    """Test advanced event filtering on subscribers."""
    event_bus = EventBus()
    await event_bus.start()

    prio_sub = TestEventSubscriber("priority_sub")
    # Accept only SYSTEM, EventPriority.HIGH or higher
    prio_sub.add_filter(EventFilter(categories=[EventCategory.SYSTEM], min_priority=EventPriority.HIGH))

    event_bus.register_subscriber(prio_sub)

    # Low prio event: Should NOT be delivered
    low_prio_event = Event(
        event_type="system.low",
        category=EventCategory.SYSTEM,
        source_component="core",
        data={},
        priority=EventPriority.NORMAL
    )
    # High prio event: SHOULD be delivered
    hi_prio_event = Event(
        event_type="system.high",
        category=EventCategory.SYSTEM,
        source_component="core",
        data={},
        priority=EventPriority.HIGH
    )

    await event_bus.publish(low_prio_event)
    await event_bus.publish(hi_prio_event)
    await asyncio.sleep(0.2)
    assert not any(ev.event_type == "system.low" for ev in prio_sub.received_events), "Low priority event was incorrectly delivered."
    assert any(ev.event_type == "system.high" for ev in prio_sub.received_events), "High priority event was NOT delivered."

    await event_bus.stop()

@pytest.mark.asyncio
async def test_event_bus_thread_safety_concurrent_publish():
    """Test thread safety for concurrent event publishing."""
    event_bus = EventBus()
    await event_bus.start()

    concurrent_sub = TestEventSubscriber("concurrent_subscriber")
    concurrent_sub.add_filter(EventFilter(categories=[EventCategory.SYSTEM, EventCategory.USER]))
    event_bus.register_subscriber(concurrent_sub)

    # Publish simultaneously from multiple tasks/threads
    def publish_events_sync(ev):
        asyncio.run(event_bus.publish(ev))

    events = [
        SystemEvent(
            event_type=f"system.concurrent.{i}",
            source_component="concurrent",
            data={"num": i},
        )
        for i in range(5)
    ]
    threads = [threading.Thread(target=publish_events_sync, args=(ev,)) for ev in events]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    await asyncio.sleep(0.5)  # Allow for all delivery

    # All events should have been received
    received_types = [ev.event_type for ev in concurrent_sub.received_events]
    for ev in events:
        assert ev.event_type in received_types, f"Event {ev.event_type} was not delivered."

    await event_bus.stop()

# For Spyder environment, we can still provide a manual test function
async def test_event_bus_manual():
    """Manual test function for running in Spyder or similar environments."""
    print("Starting event bus tests...")
    
    await test_event_bus_basic_routing()
    print("Basic routing test completed.")
    
    await test_event_bus_serialization_consistency()
    print("Serialization consistency test completed.")
    
    await test_event_bus_filtering_logic()
    print("Filtering logic test completed.")
    
    await test_event_bus_thread_safety_concurrent_publish()
    print("Thread safety test completed.")
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    # For pytest: pytest -xvs tests/integration/test_event_bus.py
    
    # For manual execution:
    print("Run tests with pytest or in Spyder by executing: await test_event_bus_manual()")
