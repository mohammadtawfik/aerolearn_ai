"""
Integration Test Harness, Mock Component System, and Event Capture Utility
Location: tests/integration/component_harness.py

This module provides the foundational tools required to do component-based integration testing in AeroLearn AI.
"""

from typing import Any, Callable, List, Dict
from threading import Lock
import inspect

# --- Base Harness ---

class ComponentTestHarness:
    """
    Generic test harness for initializing, managing, and verifying system component behavior in integration tests.
    """
    def __init__(self):
        self.components = {}
        self.started = False

    def register_component(self, name: str, component: Any):
        self.components[name] = component

    def init_all(self):
        for component in self.components.values():
            if hasattr(component, "init"):
                component.init()

    def start_all(self):
        self.init_all()
        for component in self.components.values():
            if hasattr(component, "start"):
                component.start()
        self.started = True

    def stop_all(self):
        for component in self.components.values():
            if hasattr(component, "stop"):
                component.stop()
        self.started = False

    def teardown(self):
        self.stop_all()
        self.components.clear()

# --- Simple Mock Component ---

class MockComponent:
    """
    Example mock component for use in harness-based tests.
    """
    def __init__(self, name="MockComponent"):
        self.name = name
        self.started = False
        self.event_log = []

    def init(self):
        self.initialized = True

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def handle_event(self, event):
        self.event_log.append(event)

# --- Event Capture Utility ---

class EventCaptureUtility:
    """
    Utility for subscribing to global events (such as via event bus)
    and capturing/inspecting them for assertions.
    Thread-safe for concurrent test runs.
    """
    def __init__(self):
        self.captured_events: List[Any] = []
        self._lock = Lock()
        self._subscribed = False
        self._unsubscribe_func: Callable = None

    def subscribe(self, event_bus, event_type=None):
        """
        Subscribe to all events or a filtered type from event_bus.
        """
        if hasattr(event_bus, "subscribe"):
            def handler(event):
                if (event_type is None) or isinstance(event, event_type):
                    with self._lock:
                        self.captured_events.append(event)
            self._unsubscribe_func = event_bus.subscribe(handler)
            self._subscribed = True

    def unsubscribe(self):
        if self._subscribed and self._unsubscribe_func:
            self._unsubscribe_func()
            self._subscribed = False

    def clear(self):
        with self._lock:
            self.captured_events.clear()

    def get_events(self) -> List[Any]:
        with self._lock:
            return list(self.captured_events)

    def assert_event_occurred(self, match_func: Callable[[Any], bool]):
        assert any(match_func(ev) for ev in self.get_events()), "No matching event captured."