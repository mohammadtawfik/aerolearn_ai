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

import asyncio
import pytest

# Event Bus Tests

from integrations.events.event_bus import EventBus
from integrations.events.event_types import (
    Event, EventPriority, EventCategory, SystemEvent, SystemEventType
)
from integrations.events.event_subscribers import (
    EventSubscriber, EventFilter, CallbackEventSubscriber
)

@pytest.mark.asyncio
async def test_event_bus_publish_and_subscribe():
    bus = EventBus()
    await bus.start()

    results = []

    class SimpleSubscriber(EventSubscriber):
        async def handle_event(self, event):
            results.append(event.event_type)

    sub = SimpleSubscriber("demo_sub")
    event_filter = EventFilter(event_types=[SystemEventType.STARTUP])
    sub.add_filter(event_filter)
    bus.register_subscriber(sub)

    event = SystemEvent(
        event_type=SystemEventType.STARTUP,
        source_component="core",
        data={}
    )
    await bus.publish(event)
    await asyncio.sleep(0.1)  # Let event loop process

    assert SystemEventType.STARTUP in results
    await bus.stop()

@pytest.mark.asyncio
async def test_event_bus_serialization():
    # Check event serialization/deserialization
    event = SystemEvent(
        event_type=SystemEventType.SHUTDOWN,
        source_component="core",
        data={"reason": "maintenance"},
        priority=EventPriority.CRITICAL
    )
    serialized = event.serialize()
    deserialized = SystemEvent.deserialize(serialized)
    assert deserialized.event_type == event.event_type
    assert deserialized.category == event.category
    assert deserialized.data["reason"] == "maintenance"
    assert deserialized.priority == EventPriority.CRITICAL

def test_event_filter_matching():
    # Filtering by event type, category, and priority
    event = Event(
        event_type="fake.type",
        category=EventCategory.CONTENT,
        source_component="mod",
        data={},
        priority=EventPriority.LOW
    )
    f = EventFilter(event_types=["fake.type"], categories=[EventCategory.CONTENT], min_priority=EventPriority.LOW)
    assert f.matches(event)
    f2 = EventFilter(event_types=["other"], categories=[EventCategory.AI])
    assert not f2.matches(event)

# Component Registry/Dependency Tracker

from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.dependency_tracker import DependencyTracker

def test_component_registry_and_discovery():
    registry = ComponentRegistry()
    c1 = {'id': 'c1', 'version': '1.0.0'}
    registry.register_component(c1['id'], c1['version'])
    assert registry.get_component(c1['id'])['version'] == '1.0.0'
    assert c1['id'] in registry.list_components()

def test_dependency_tracking_validation():
    tracker = DependencyTracker()
    tracker.declare_dependency('mod1', ['mod2'])
    assert tracker.has_dependency('mod1', 'mod2')
    # No false positive
    assert not tracker.has_dependency('mod1', 'modX')

# Interface Contracts (base_interface example)

from integrations.interfaces.base_interface import BaseInterface

def test_base_interface_signature_validation():
    class Dummy(BaseInterface):
        interface_name = "dummy"
        interface_version = "0.1"
        @BaseInterface.interface_method
        def hello(self, arg): return arg
    d = Dummy()
    # signature validation: should not raise
    assert d.hello("ok") == "ok"

# Monitoring System: Basic test stubs

from integrations.monitoring.integration_health import IntegrationHealth
from integrations.monitoring.component_status import ComponentStatus
from integrations.monitoring.transaction_logger import TransactionLogger

def test_integration_health_collect():
    health = IntegrationHealth()
    health.collect_metric("test_metric", 1)
    assert health.get_metric("test_metric") == 1

def test_component_status_tracking():
    status = ComponentStatus()
    status.set_status("compA", "up")
    assert status.get_status("compA") == "up"

def test_transaction_logger():
    logger = TransactionLogger()
    logger.log_transaction("core", "modA", "sync", {"action": "demo"})
    logs = logger.get_logs()
    assert logs and "sync" in logs[-1]["type"]
