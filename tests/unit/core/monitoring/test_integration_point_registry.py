"""
Unit tests for /integrations/monitoring/integration_point_registry.py

Protocol References:
- IntegrationPointRegistry must register, store, and enumerate integration points.
- Registry should prevent duplicate registrations of the same point.
- Points should be retrievable by name or as a complete list.

Tests:
- Register integration point.
- Query integration points by name/key.
- Storage returns correct registered points.
- Duplicate registrations are handled properly.
"""

import unittest
from integrations.monitoring import integration_point_registry

class TestIntegrationPointRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = integration_point_registry.IntegrationPointRegistry()
    
    def test_register_and_lookup(self):
        """Test that points can be registered and looked up by name."""
        self.registry.register_point("db", {"type": "sql", "uri": "sqlite://"})
        self.assertIn("db", self.registry.list_points())
        value = self.registry.get_point("db")
        self.assertEqual(value["uri"], "sqlite://")

    def test_register_simple_name(self):
        """Test registration with just a name and no metadata."""
        self.registry.register_point("core-db")
        self.assertIn("core-db", self.registry.list_points())
        
    def test_storage_returns_all(self):
        """Test that all registered points can be retrieved."""
        self.registry.register_point("app_api", {"type": "rest"})
        self.registry.register_point("core-db", {"type": "sql"})
        all_points = self.registry.get_all_points()
        self.assertEqual(len(all_points), 2)
        self.assertIn("app_api", all_points)
        self.assertIn("core-db", all_points)
        self.assertEqual(all_points["app_api"]["type"], "rest")
        
    def test_duplicate_registration(self):
        """Test that duplicate registrations are handled properly."""
        self.registry.register_point("api-gateway", {"version": "1.0"})
        self.registry.register_point("api-gateway", {"version": "2.0"})  # Should update or be ignored
        points = self.registry.list_points()
        self.assertEqual(points.count("api-gateway"), 1)
        
        # Check if the registry kept the first or last registration
        point_data = self.registry.get_point("api-gateway")
        # The protocol should define whether to keep first or last registration
        # This assertion may need adjustment based on the protocol
        self.assertIn(point_data["version"], ["1.0", "2.0"])

if __name__ == "__main__":
    unittest.main()
