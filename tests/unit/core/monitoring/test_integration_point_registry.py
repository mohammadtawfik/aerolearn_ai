"""
Unit tests for /integrations/monitoring/integration_point_registry.py

Protocol References:
- IntegrationPointRegistry must register, store, and enumerate integration points.

Tests:
- Register integration point.
- Query integration points by name/key.
- Storage returns correct registered points.
"""

import unittest
from integrations.monitoring import integration_point_registry

class TestIntegrationPointRegistry(unittest.TestCase):
    def test_register_and_lookup(self):
        reg = integration_point_registry.IntegrationPointRegistry()
        reg.register("db", {"type": "sql", "uri": "sqlite://"})
        self.assertIn("db", reg.get_all_keys())
        value = reg.lookup("db")
        self.assertEqual(value["uri"], "sqlite://")

    def test_storage_returns_all(self):
        reg = integration_point_registry.IntegrationPointRegistry()
        reg.register("app_api", {"type": "rest"})
        all_points = reg.get_all()
        self.assertIn("app_api", all_points)
        self.assertEqual(all_points["app_api"]["type"], "rest")

if __name__ == "__main__":
    unittest.main()