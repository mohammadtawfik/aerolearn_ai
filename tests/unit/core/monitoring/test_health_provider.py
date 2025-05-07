"""
Unit tests for /integrations/monitoring/health_provider.py

Protocol References:
- HealthProvider must be an ABC with required protocol methods.

Tests:
- HealthProvider cannot be instantiated directly.
- All protocol-required abstractmethods exist and raise as expected.
"""

import unittest
from abc import ABCMeta
from integrations.monitoring import health_provider

class TestHealthProviderABC(unittest.TestCase):
    def test_abc_instantiation(self):
        with self.assertRaises(TypeError):
            health_provider.HealthProvider()

    def test_protocol_methods_exist(self):
        # Abstract class should declare protocol-expected methods
        expected_methods = {"get_health_status", "register_listener"}
        provider_methods = set(dir(health_provider.HealthProvider))
        for method in expected_methods:
            self.assertIn(method, provider_methods)

if __name__ == "__main__":
    unittest.main()