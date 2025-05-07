"""
Unit tests for /integrations/monitoring/integration_monitor.py

Protocol References:
- Must support transaction recording, failure traces, failure pattern detection, health scoring, and simulation.

Tests:
- Monitor integration registration, transaction record, retrieval, failure trace, and scoring.
"""

import unittest
from integrations.monitoring import integration_monitor

class TestIntegrationMonitor(unittest.TestCase):
    def test_monitor_integration_registration(self):
        monitor = integration_monitor.IntegrationMonitor()
        monitor.monitor_integration("test_integration")
        self.assertIn("test_integration", monitor._monitored)

    def test_transaction_record_and_retrieval(self):
        monitor = integration_monitor.IntegrationMonitor()
        monitor.monitor_integration("integration1")
        monitor.record_transaction("integration1", status="success", duration=120)
        records = monitor.get_failure_trace("integration1")
        self.assertIsInstance(records, list)

    def test_health_score(self):
        monitor = integration_monitor.IntegrationMonitor()
        monitor.monitor_integration("int_bench")
        for _ in range(5):
            monitor.record_transaction("int_bench", status="success", duration=100)
        for _ in range(2):
            monitor.record_transaction("int_bench", status="fail", duration=50)
        score = monitor.get_health_score("int_bench")
        self.assertTrue(0 <= score <= 1)

if __name__ == "__main__":
    unittest.main()