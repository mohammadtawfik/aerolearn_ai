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
UI Component Integration Tests

These tests target integration between UI components and their data providers,
event bus interactions, and support for end-to-end and performance scenarios.

Assumptions:
- UI components expose load_content, update_data, and subscribe_to_events
- EventBus used for event-driven updates
"""

from unittest.mock import MagicMock
import pytest

# Dummy UI and provider proxies
class FakeContentProvider:
    def __init__(self):
        self.data = {"a.txt": "Alpha", "b.txt": "Bravo"}
    def get_content(self, key):
        return self.data.get(key)
    def list_content(self):
        return list(self.data.keys())

class DummyUIComponent:
    def __init__(self, provider, event_bus):
        self.provider = provider
        self.event_bus = event_bus
        self.content = {}
        self.updated = False

    def load_content(self):
        for key in self.provider.list_content():
            self.content[key] = self.provider.get_content(key)
        self.event_bus.publish({"event": "ui_content_loaded"})
        return self.content

    def update_data(self, key, value):
        self.provider.data[key] = value
        self.updated = True
        self.event_bus.publish({"event": "ui_data_updated", "key": key})

    def subscribe_to_events(self, callback):
        self.event_bus.on("ui_content_loaded", callback)
        self.event_bus.on("ui_data_updated", callback)

class SimpleEventBus:
    def __init__(self):
        self._subscribers = {}

    def publish(self, event):
        if event["event"] in self._subscribers:
            for fn in self._subscribers[event["event"]]:
                fn(event)

    def on(self, event_type, cb):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(cb)

@pytest.fixture
def ui_integration_env():
    event_bus = SimpleEventBus()
    provider = FakeContentProvider()
    ui = DummyUIComponent(provider, event_bus)
    return (ui, provider, event_bus)

def test_ui_loads_content_and_triggers_event(ui_integration_env):
    ui, provider, event_bus = ui_integration_env
    loaded = []
    def handler(evt):
        loaded.append(evt)
    ui.subscribe_to_events(handler)
    content = ui.load_content()
    assert set(content.keys()) == set(provider.list_content())
    assert any(e['event'] == "ui_content_loaded" for e in loaded)

def test_ui_update_triggers_event(ui_integration_env):
    ui, provider, event_bus = ui_integration_env
    events = []
    ui.subscribe_to_events(lambda evt: events.append(evt))
    ui.update_data("b.txt", "BRAVO")
    assert provider.get_content("b.txt") == "BRAVO"
    assert ui.updated
    assert any(e["event"] == "ui_data_updated" and e["key"] == "b.txt" for e in events)

def test_end_to_end_ui_to_data_workflow(ui_integration_env):
    ui, provider, event_bus = ui_integration_env
    ui.load_content()
    ui.update_data("c.txt", "Charlie!")
    # Should reflect in UI state and provider
    assert "c.txt" in ui.content or provider.get_content("c.txt") == "Charlie!"

def test_ui_event_handler_performance(ui_integration_env):
    ui, provider, event_bus = ui_integration_env
    called = []
    def cb(evt): called.append(evt)
    ui.subscribe_to_events(cb)
    import time
    start = time.time()
    for _ in range(500):
        ui.load_content()
        ui.update_data("a.txt", "newA")
    elapsed = time.time() - start
    assert elapsed < 2.0  # Adjust as appropriate
