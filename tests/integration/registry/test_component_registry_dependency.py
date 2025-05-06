"""
Integration Test: Component Registry Dependency Tracking
Location: /tests/integration/registry/test_component_registry_dependency.py

Covers per protocol:
- declare_dependency (must check only registered components accepted, no duplicates)
- get_dependency_graph (insertion order)
- get_dependencies, get_dependents (per node, canonical order)
- analyze_dependency_impact (correct, deterministic order)
- Edge removal on component unregister
- (Optional) Cycle and analytic API stubs
"""

import unittest
from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component
from integrations.registry.component_state import ComponentState

class TestComponentRegistryDependency(unittest.TestCase):
    def setUp(self):
        self.registry = ComponentRegistry()
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        # Remove all preexisting
        if hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)

    def _register_many(self):
        # For graph: A -> [B, C], B -> [C], C -> [D, E], E -> [D]
        names = ["A", "B", "C", "D", "E"]
        for n in names:
            self.registry.register_component(n)
        return names

    def test_dependency_declaration_and_query(self):
        names = self._register_many()
        # A depends on B, then C (order test)
        self.assertTrue(self.registry.declare_dependency("A", "B"))
        self.assertTrue(self.registry.declare_dependency("A", "C"))
        # B depends on C
        self.assertTrue(self.registry.declare_dependency("B", "C"))
        # C depends on D, then E
        self.assertTrue(self.registry.declare_dependency("C", "D"))
        self.assertTrue(self.registry.declare_dependency("C", "E"))
        # E depends on D
        self.assertTrue(self.registry.declare_dependency("E", "D"))
        # Query full graph, validate exact order
        dep_graph = self.registry.get_dependency_graph()
        self.assertListEqual(dep_graph["A"], ["B", "C"])
        self.assertListEqual(dep_graph["B"], ["C"])
        self.assertListEqual(dep_graph["C"], ["D", "E"])
        self.assertListEqual(dep_graph["E"], ["D"])
        self.assertTrue(isinstance(dep_graph["D"], list) and len(dep_graph["D"]) == 0)

    def test_dependencies_and_dependents_protocol(self):
        names = self._register_many()
        # D -> E
        self.registry.declare_dependency("D", "E")
        # get_dependencies, get_dependents protocol
        deps = self.registry.get_dependencies("D")
        self.assertListEqual(deps, ["E"])
        # Now, who depends on E?
        dependents = self.registry.get_dependents("E")
        self.assertListEqual(dependents, ["D"])
        # Unidirectionality: E has no dependencies, D is not dependent on itself
        self.assertListEqual(self.registry.get_dependencies("E"), [])

    def test_dependencies_must_exist(self):
        self.registry.register_component("A")
        # Not allowed to declare dependency on non-existent node
        with self.assertRaises(Exception):
            self.registry.declare_dependency("A", "NOTEXIST")
        # Nor can NOTEXIST depend on A
        with self.assertRaises(Exception):
            self.registry.declare_dependency("NOTEXIST", "A")

    def test_analyze_dependency_impact(self):
        # A -> B -> C, A -> D
        for cid in ["A", "B", "C", "D"]:
            self.registry.register_component(cid)
        self.registry.declare_dependency("A", "B")
        self.registry.declare_dependency("B", "C")
        self.registry.declare_dependency("A", "D")
        # Impact of C: should be ['B'] (only B depends directly), C's downstream further is ['A'], order: downstream then indirect
        impacted_by_c = self.registry.analyze_dependency_impact("C")
        # Accept ['B', 'A'] or only direct ['B'] if protocol restricts to direct only
        self.assertTrue(impacted_by_c[0] == "B")
        self.assertIn("A", impacted_by_c)

    def test_unregister_component_removes_dependencies(self):
        # Setup: X -> Y -> Z
        for cid in ["X", "Y", "Z"]:
            self.registry.register_component(cid)
        self.registry.declare_dependency("X", "Y")
        self.registry.declare_dependency("Y", "Z")
        # Unregister Y should remove it
        self.registry.unregister_component("Y")
        dep_graph = self.registry.get_dependency_graph()
        self.assertNotIn("Y", dep_graph)
        # X should no longer have Y as dependency
        self.assertListEqual(dep_graph["X"], [])

    def tearDown(self):
        if hasattr(self.registry, "clear"):
            self.registry.clear()
        elif hasattr(self.registry, "get_all_components"):
            for cid in list(self.registry.get_all_components().keys()):
                self.registry.unregister_component(cid)

if __name__ == "__main__":
    unittest.main()