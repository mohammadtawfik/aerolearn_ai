"""
Integration Test: Component Registry Lifecycle
Location: /tests/integration/registry/test_component_registry_lifecycle.py

Covers per protocol:
- Component registration and all protocol state transitions
- Correct state update/retrieval
- Unregistration/removal and re-registration
- Isolation between components
- API surface only (no direct dict/touch)
"""

import unittest
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component
from integrations.registry.component_state import ComponentState

class TestComponentRegistryLifecycle(unittest.TestCase):
    def setUp(self):
        self.registry = ComponentRegistry()
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        # Ensure all components cleared
        if hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)

    def test_component_state_transitions(self):
        cid = "test.lifecycle.comp"
        comp = self.registry.register_component(cid, state=ComponentState.UNKNOWN)
        # Allowed transitions (protocol states)
        sequence = [
            ComponentState.RUNNING,
            ComponentState.DEGRADED,
            ComponentState.DOWN,
            ComponentState.FAILED,
            ComponentState.HEALTHY
        ]
        for state in sequence:
            comp.set_state(state)
            # Registry should yield up-to-date state for this component
            reg_comp = self.registry.get_component(cid)
            self.assertIsNotNone(reg_comp)
            self.assertEqual(reg_comp.get_state(), state)

    def test_state_is_isolated_between_components(self):
        cid1, cid2 = "lifecycle.comp1", "lifecycle.comp2"
        comp1 = self.registry.register_component(cid1, state=ComponentState.RUNNING)
        comp2 = self.registry.register_component(cid2, state=ComponentState.DEGRADED)
        comp1.set_state(ComponentState.FAILED)
        # comp2 must not be affected
        self.assertEqual(comp1.get_state(), ComponentState.FAILED)
        self.assertEqual(comp2.get_state(), ComponentState.DEGRADED)
        # Registry must agree
        reg1 = self.registry.get_component(cid1)
        reg2 = self.registry.get_component(cid2)
        self.assertEqual(reg1.get_state(), ComponentState.FAILED)
        self.assertEqual(reg2.get_state(), ComponentState.DEGRADED)

    def test_unregistration_and_reregistration(self):
        cid = "stateful.comp"
        self.registry.register_component(cid, state=ComponentState.RUNNING, version="v1")
        self.assertTrue(self.registry.unregister_component(cid))
        self.assertIsNone(self.registry.get_component(cid))
        # Re-register with different state/version
        comp2 = self.registry.register_component(cid, state=ComponentState.DEGRADED, version="v2")
        self.assertEqual(comp2.get_state(), ComponentState.DEGRADED)
        self.assertEqual(comp2.get_version(), "v2")

    def test_repeated_state_changes(self):
        cid = "restate.comp"
        comp = self.registry.register_component(cid)
        # Set state twice to the same value
        comp.set_state(ComponentState.DEGRADED)
        comp.set_state(ComponentState.DEGRADED)
        self.assertEqual(comp.get_state(), ComponentState.DEGRADED)
        # Now set to something else
        comp.set_state(ComponentState.HEALTHY)
        self.assertEqual(comp.get_state(), ComponentState.HEALTHY)

    def tearDown(self):
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        elif hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)

if __name__ == "__main__":
    unittest.main()