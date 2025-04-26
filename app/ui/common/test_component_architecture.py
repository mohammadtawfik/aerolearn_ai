# test_component_architecture.py

import pytest
from app.ui.common.component_base import BaseComponent
from app.ui.common.component_base import ComponentRegistry

# Mock EventBus to test event integration
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

def test_component_creation_and_lifecycle(mock_event_bus):
    class DummyComponent(BaseComponent):
        def on_init(self):
            self.init_called = True

        def on_start(self):
            super().on_start()
            self.started = True

        def on_stop(self):
            super().on_stop()
            self.stopped = True

    comp = DummyComponent(event_bus=mock_event_bus)
    assert hasattr(comp, "init_called") and comp.init_called
    assert comp.status == "initialized"

    comp.on_start()
    assert comp.status == "started"
    assert hasattr(comp, "started") and comp.started

    comp.on_stop()
    assert comp.status == "stopped"
    assert hasattr(comp, "stopped") and comp.stopped

def test_component_event_handler_and_publish(mock_event_bus):
    received = {}

    class EvComp(BaseComponent):
        def handler(self, event):
            received['val'] = event.data

    comp = EvComp(event_bus=mock_event_bus)
    comp.register_event_handler("UI_EVENT", comp.handler)
    comp.publish_event("UI_EVENT", "abc123")

    # Simulate event bus delivery
    mock_event_bus.publish("UI_EVENT", "abc123")
    assert received['val'] == "abc123"

def test_component_registry_add_discover_replace():
    reg = ComponentRegistry.instance()
    reg._components.clear()
    reg._component_classes.clear()

    class C1(BaseComponent): pass
    class C2(BaseComponent): pass

    c1 = C1(name="test1")
    c2 = C2(name="test2")

    reg.register_component("test1", c1)
    reg.register_component("test2", c2)

    assert reg.get_component("test1") is c1
    assert reg.get_component("test2") is c2
    assert set(reg.discover_components()) == {"test1", "test2"}

    # Test replace
    c2_new = C2(name="test2")
    reg.replace_component("test2", c2_new)
    assert reg.get_component("test2") is c2_new

def test_dependency_injection():
    class DIComponent(BaseComponent):
        def on_start(self):
            super().on_start()
            self.token = self.get_dependency("some_service")

    di = DIComponent(some_service="TOKEN")
    di.on_start()
    assert hasattr(di, "token") and di.token == "TOKEN"

    di.replace_dependency("some_service", "NEW_TOKEN")
    assert di.get_dependency("some_service") == "NEW_TOKEN"

def test_lifecycle_bulk_operations():
    reg = ComponentRegistry.instance()
    reg._components.clear()
    reg._component_classes.clear()

    events = []

    class C(BaseComponent):
        def on_start(self):
            super().on_start()
            events.append((self.name, "start"))
        def on_stop(self):
            super().on_stop()
            events.append((self.name, "stop"))

    c1 = C(name="A")
    c2 = C(name="B")
    reg.register_component("A", c1)
    reg.register_component("B", c2)
    reg.start_all()
    reg.stop_all()
    assert ("A", "start") in events and ("B", "start") in events
    assert ("A", "stop") in events and ("B", "stop") in events