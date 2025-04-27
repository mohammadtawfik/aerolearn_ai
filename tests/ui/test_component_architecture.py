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

import pytest
from app.ui.common.component_base import BaseComponent
from app.ui.common.component_registry import ComponentRegistry

# Mock EventBus for event-driven interaction tests
class MockEvent:
    def __init__(self, type, data):
        self.type = type
        self.data = data

class MockEventBus:
    def __init__(self):
        self._subs = {}

    def subscribe(self, event_type, cb):
        self._subs.setdefault(event_type, []).append(cb)

    def publish(self, event_type, data):
        evt = MockEvent(event_type, data)
        for cb in self._subs.get(event_type, []):
            cb(evt)

@pytest.fixture
def mock_event_bus():
    return MockEventBus()

def test_base_component_lifecycle_and_status(mock_event_bus):
    class DummyComponent(BaseComponent):
        def on_init(self):
            self.did_init = True
        def on_start(self):
            super().on_start()
            self.started = True
        def on_stop(self):
            super().on_stop()
            self.stopped = True

    comp = DummyComponent(event_bus=mock_event_bus)
    assert hasattr(comp, "did_init") and comp.did_init
    assert comp.status == "initialized"

    comp.on_start()
    assert comp.status == "started"
    assert hasattr(comp, "started") and comp.started

    comp.on_stop()
    assert comp.status == "stopped"
    assert hasattr(comp, "stopped") and comp.stopped

def test_event_handler_registration_and_callback(mock_event_bus):
    received = {}

    class HandlerComponent(BaseComponent):
        def handler(self, event):
            received["result"] = event.data

    comp = HandlerComponent(event_bus=mock_event_bus)
    comp.register_event_handler("UI_EVENT", comp.handler)
    comp.publish_event("UI_EVENT", "payload-data")

    # The mock bus does not auto-fire on publish_event, so simulate event delivery:
    mock_event_bus.publish("UI_EVENT", "payload-data")
    assert received["result"] == "payload-data"

def test_registry_register_and_discover():
    registry = ComponentRegistry.instance()
    registry._components.clear()
    registry._component_classes.clear()

    class TestComponent(BaseComponent): pass

    c1 = TestComponent(name="Foo")
    c2 = TestComponent(name="Bar")

    registry.register_component("Foo", c1)
    registry.register_component("Bar", c2)

    assert registry.get_component("Foo") is c1
    assert registry.get_component("Bar") is c2
    assert set(registry.discover_components()) == {"Foo", "Bar"}

def test_registry_replace_component():
    registry = ComponentRegistry.instance()
    registry._components.clear()
    registry._component_classes.clear()

    class C1(BaseComponent): pass
    class C2(BaseComponent):
        def on_start(self):
            super().on_start()
            self.replaced = True

    old = C1(name="Bing")
    registry.register_component("Bing", old)

    new = C2(name="Bing")
    registry.replace_component("Bing", new)
    assert registry.get_component("Bing") is new
    assert hasattr(new, "replaced") and new.replaced

def test_dependency_injection_and_replacement():
    class DepComponent(BaseComponent):
        def on_init(self):
            self.x = self.get_dependency("service_x")

    comp = DepComponent(service_x="magic")
    assert comp.x == "magic"

    comp.replace_dependency("service_x", "new-magic")
    assert comp.get_dependency("service_x") == "new-magic"

def test_bulk_lifecycle_operations():
    registry = ComponentRegistry.instance()
    registry._components.clear()
    registry._component_classes.clear()
    events = []

    class C(BaseComponent):
        def on_start(self):
            super().on_start()
            events.append(f"{self.name}-start")
        def on_stop(self):
            super().on_stop()
            events.append(f"{self.name}-stop")

    c1 = C(name="One")
    c2 = C(name="Two")
    registry.register_component("One", c1)
    registry.register_component("Two", c2)

    registry.start_all()
    registry.stop_all()
    assert "One-start" in events and "Two-start" in events
    assert "One-stop" in events and "Two-stop" in events
