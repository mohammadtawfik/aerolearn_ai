"""
Integration Test: Component Registry Registration
Location: /tests/integration/registry/test_component_registry_registration.py

Protocol coverage:
- /docs/architecture/dependency_tracking_protocol.md
- /docs/architecture/architecture_overview.md
- /docs/development/day22_plan.md

Tests:
- Registering new components (with/without state/version/description)
- Duplicate registration rejection (ValueError)
- Lookup by ID
- Listing all registered components
- Test isolation (clean registry for each test)
- Protocol-compliant usage (get_id(), get_state())
"""

import unittest
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component
from integrations.registry.component_state import ComponentState

class TestComponentRegistryRegistration(unittest.TestCase):
    def setUp(self):
        self.registry = ComponentRegistry()
        # Defensive registry clearing if protocol API exists
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        # Remove all old components if present
        if hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)
    
    def test_register_basic_component(self):
        cid = "my.test.component"
        comp = self.registry.register_component(cid)
        self.assertIsInstance(comp, Component)
        self.assertEqual(comp.get_id(), cid)
        self.assertEqual(comp.get_state(), ComponentState.UNKNOWN)
    
    def test_register_with_state_version_description(self):
        cid = "another.component"
        desc = "Component for testing"
        version = "0.1.2"
        state = ComponentState.RUNNING
        comp = self.registry.register_component(cid, description=desc, version=version, state=state)
        self.assertEqual(comp.get_id(), cid)
        self.assertTrue(getattr(comp, "description", None) == desc)  # Optional property
        self.assertTrue(getattr(comp, "version", None) == version)   # Optional property
        self.assertEqual(comp.get_state(), state)
    
    def test_duplicate_registration_should_fail(self):
        cid = "dupe.component"
        self.registry.register_component(cid)
        with self.assertRaises(ValueError):
            self.registry.register_component(cid)
    
    def test_lookup_by_id(self):
        cid = "lookup.component"
        self.registry.register_component(cid, state=ComponentState.DEGRADED)
        found = self.registry.get_component(cid)
        self.assertIsNotNone(found)
        self.assertEqual(found.get_id(), cid)
        self.assertEqual(found.get_state(), ComponentState.DEGRADED)

    def test_get_all_components(self):
        cids = ["comp1", "comp2", "comp3"]
        for cid in cids:
            self.registry.register_component(cid)
        all_comps = self.registry.get_all_components()
        self.assertIsInstance(all_comps, dict)
        # Should be superset of registered
        for cid in cids:
            self.assertIn(cid, all_comps)
            self.assertTrue(hasattr(all_comps[cid], "get_id"))
    
    def test_unregister_removes_component(self):
        cid = "to.remove"
        self.registry.register_component(cid)
        self.assertIn(cid, self.registry.get_all_components())
        self.registry.unregister_component(cid)
        comps_after = self.registry.get_all_components()
        self.assertNotIn(cid, comps_after)
        # Also ensure get_component returns None or equivalent for removed id
        found = self.registry.get_component(cid)
        self.assertTrue(found is None)
    
    def tearDown(self):
        # Safe cleanup: try full protocol/stateless reset
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        elif hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)

if __name__ == "__main__":
    unittest.main()
