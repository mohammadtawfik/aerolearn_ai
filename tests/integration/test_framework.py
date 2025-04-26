"""
Integration Test Framework for the AeroLearn Project
Location: tests/integration/test_framework.py

Includes:
- Interface compliance validation for components.
- Test scenario builder.
- Pytest-discoverable integration test functions.
"""

import inspect
from typing import Any, List, Dict, Callable, Type

from .component_harness import ComponentTestHarness, MockComponent, EventCaptureUtility

# -- Interface Compliance Test --

class InterfaceComplianceTest:
    """
    Validates that a component implements the required interface contract
    (i.e., has all required methods, with correct signatures).
    """
    def __init__(self, interface: Type, implementation: Any):
        self.interface = interface
        self.implementation = implementation

    def validate(self) -> bool:
        # Always compare unbound methods (i.e., from the classes)
        impl_cls = type(self.implementation)
        for name, value in inspect.getmembers(self.interface):
            if name.startswith("__"):
                continue
            if callable(value):
                impl_method = getattr(impl_cls, name, None)
                if impl_method is None or not callable(impl_method):
                    raise AssertionError(f"Missing implementation for method: {name}")
                # Compare signatures as unbound methods
                iface_sig = inspect.signature(value)
                impl_sig = inspect.signature(impl_method)
                if iface_sig != impl_sig:
                    raise AssertionError(f"Signature mismatch for {name}: {iface_sig} != {impl_sig}")
        return True

# -- Test Scenario Builder --

class TestScenarioBuilder:
    """
    Builds and runs structured integration test scenarios.
    """
    def __init__(self, harness: ComponentTestHarness):
        self.harness = harness
        self.steps: List[Callable] = []

    def add_step(self, description: str, func: Callable):
        self.steps.append((description, func))
        return self

    def run(self):
        for desc, func in self.steps:
            func()  # pytest will report by assertion, so print not required.

# === Pytest Integration Tests ===

def test_component_lifecycle():
    """
    Test: Component harness initializes, starts and tears down components.
    """
    harness = ComponentTestHarness()
    mock = MockComponent("demo_mock")
    harness.register_component("demo", mock)

    # Step 1: Initialization
    harness.init_all()
    assert getattr(mock, "initialized", False), "Mock component was not initialized"

    # Step 2: Starting
    harness.start_all()
    assert mock.started, "Mock component was not started"

    # Step 3: Teardown
    harness.teardown()
    assert not harness.components, "Harness did not clear components"


def test_event_capture_utility():
    """
    Test: EventCaptureUtility captures events via dummy event bus.
    """
    class DummyEventBus:
        def subscribe(self, handler):
            # Simulate an event fire
            handler({'type': 'SIM_EVENT', 'payload': 42})
            return lambda: None

    event_bus = DummyEventBus()
    capture = EventCaptureUtility()
    capture.subscribe(event_bus)
    events = capture.get_events()
    assert any(ev['type'] == 'SIM_EVENT' for ev in events), "No simulated event captured."
    capture.unsubscribe()

def test_interface_compliance():
    """
    Test: InterfaceComplianceTest properly checks interface contract.
    """
    # Fake interface class for demonstration
    class FakeInterface:
        def init(self): pass
        def start(self): pass
        def stop(self): pass

    class MatchingImpl:
        def init(self): pass
        def start(self): pass
        def stop(self): pass

    checker = InterfaceComplianceTest(FakeInterface, MatchingImpl())
    assert checker.validate() is True

def test_scenario_builder_runall():
    """
    Test: TestScenarioBuilder properly runs a sample scenario.
    """
    harness = ComponentTestHarness()
    mock = MockComponent("scenario_mock")
    harness.register_component("demo", mock)

    steps_run = []

    def step1():
        steps_run.append("a")
        harness.init_all()
        assert getattr(mock, "initialized", False)

    def step2():
        steps_run.append("b")
        harness.start_all()
        assert mock.started

    def step3():
        steps_run.append("c")
        mock.handle_event({'type': 'TEST_EVENT', 'msg': 'pytest'})
        assert mock.event_log and mock.event_log[-1]["type"] == "TEST_EVENT"

    def step4():
        steps_run.append("d")
        harness.teardown()
        assert not harness.components

    scenario = TestScenarioBuilder(harness)
    scenario.add_step("init", step1)\
            .add_step("start", step2)\
            .add_step("handle", step3)\
            .add_step("teardown", step4)
    scenario.run()
    assert steps_run == ["a", "b", "c", "d"]
