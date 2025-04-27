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
from datetime import datetime
from enum import Enum, auto
from integrations.monitoring.component_status import (
    ComponentStatusTracker,
    ComponentStatusProvider,
    StatusSeverity,
    ComponentStatus,
)
from integrations.registry.component_registry import ComponentState


class DummyComponentState(Enum):
    STARTING = auto()
    RUNNING = auto()
    ERROR = auto()


class DummyProvider(ComponentStatusProvider):
    def __init__(self, state=ComponentState.RUNNING, details=None):
        self._state = state
        self._details = details or {}

    def get_component_state(self):
        return self._state

    def get_status_details(self):
        return self._details


def test_register_status_provider_and_update():
    tracker = ComponentStatusTracker()
    provider = DummyProvider(state=ComponentState.RUNNING, details={"uptime": 42})
    tracker.register_status_provider("comp.1", provider)
    status = tracker.get_component_status("comp.1")
    assert isinstance(status, ComponentStatus)
    assert status.details["uptime"] == 42

def test_state_change_records_history_and_severity():
    tracker = ComponentStatusTracker()
    provider = DummyProvider(state=ComponentState.STARTING)
    tracker.register_status_provider("comp.2", provider)
    # Move to ERROR
    provider._state = ComponentState.ERROR
    tracker.update_component_status("comp.2")
    history = tracker.get_status_history("comp.2")
    assert any(entry.severity in (StatusSeverity.ERROR, StatusSeverity.WARNING) for entry in history)

def test_history_limit_and_filter():
    tracker = ComponentStatusTracker(history_limit=2)
    provider = DummyProvider(state=ComponentState.RUNNING)
    tracker.register_status_provider("comp.3", provider)
    # Simulate multiple state changes
    for i in range(5):
        provider._state = ComponentState.ERROR if i % 2 == 0 else ComponentState.RUNNING
        tracker.update_component_status("comp.3")
    history = tracker.get_status_history("comp.3")
    assert len(history) == 2

def test_dependency_tracking_and_warnings():
    tracker = ComponentStatusTracker()
    provider1 = DummyProvider(state=ComponentState.ERROR)
    provider2 = DummyProvider(state=ComponentState.RUNNING)
    tracker.register_status_provider("dep", provider1)
    tracker.register_status_provider("main", provider2)
    tracker.register_dependency("main", "dep")
    # When dep is ERROR, main should get a warning in its history
    tracker.update_component_status("dep")
    main_history = tracker.get_status_history("main")
    assert any("dependency" in (entry.metadata or {}) for entry in main_history)

def test_status_summary():
    tracker = ComponentStatusTracker()
    provider = DummyProvider(state=ComponentState.RUNNING)
    tracker.register_status_provider("comp.sum", provider)
    summary = tracker.get_status_summary()
    assert "comp.sum" in summary["components"]
