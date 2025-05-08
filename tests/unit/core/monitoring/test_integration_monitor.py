"""
Unit tests for /integrations/monitoring/integration_monitor.py

Protocol References:
- Must support component registration, health state tracking, metrics collection,
  transaction recording, failure traces, pattern detection, and simulation.

Tests:
- Component registration and listing
- Health state updates and retrieval
- Metrics collection and retrieval
- Transaction recording and analysis
- Failure pattern detection
- Health scoring
"""

import pytest
from integrations.monitoring.integration_monitor import IntegrationMonitor

class TestComponentRegistration:
    def test_component_registration(self):
        """Test that components can be registered and listed"""
        monitor = IntegrationMonitor()
        monitor.register_component("payment_service")
        assert "payment_service" in monitor.list_components()
    
    def test_multiple_component_registration(self):
        """Test registering multiple components"""
        monitor = IntegrationMonitor()
        components = ["auth_service", "payment_service", "inventory_service"]
        for component in components:
            monitor.register_component(component)
        
        registered = monitor.list_components()
        for component in components:
            assert component in registered

class TestHealthStateManagement:
    def test_health_state_update(self):
        """Test updating and retrieving component health state"""
        monitor = IntegrationMonitor()
        monitor.register_component("database")
        monitor.update_health("database", "HEALTHY", {})
        
        state = monitor.get_component_state("database")
        assert state == "HEALTHY"
    
    def test_health_state_with_details(self):
        """Test health state with diagnostic details"""
        monitor = IntegrationMonitor()
        monitor.register_component("api_gateway")
        
        details = {"error_code": "CONN_TIMEOUT", "last_error": "Connection timed out"}
        monitor.update_health("api_gateway", "DEGRADED", details)
        
        state = monitor.get_component_state("api_gateway")
        details = monitor.get_health_details("api_gateway")
        
        assert state == "DEGRADED"
        assert "error_code" in details
        assert details["error_code"] == "CONN_TIMEOUT"

class TestMetricsCollection:
    def test_metrics_collection(self):
        """Test setting and retrieving component metrics"""
        monitor = IntegrationMonitor()
        monitor.register_component("cache_service")
        
        metrics = {
            "hit_ratio": 0.85,
            "latency_ms": 12,
            "error_rate": 0.02
        }
        
        monitor.set_metrics("cache_service", metrics)
        stored_metrics = monitor.get_metrics("cache_service")
        
        assert stored_metrics == metrics
    
    def test_metrics_history(self):
        """Test retrieving historical metrics"""
        monitor = IntegrationMonitor()
        monitor.register_component("message_queue")
        
        # Set metrics at different times
        monitor.set_metrics("message_queue", {"depth": 10, "consumers": 5})
        monitor.set_metrics("message_queue", {"depth": 15, "consumers": 6})
        
        history = monitor.get_metrics_history("message_queue")
        assert len(history) == 2
        assert history[-1]["depth"] == 15

class TestTransactionRecording:
    def test_transaction_recording(self):
        """Test recording and retrieving transactions"""
        monitor = IntegrationMonitor()
        monitor.register_component("payment_processor")
        
        monitor.record_transaction(
            "payment_processor", 
            status="success", 
            duration=120,
            details={"transaction_id": "tx123", "amount": 50.00}
        )
        
        transactions = monitor.get_transactions("payment_processor")
        assert len(transactions) == 1
        assert transactions[0]["status"] == "success"
        assert transactions[0]["duration"] == 120
    
    def test_failure_trace(self):
        """Test retrieving failure traces"""
        monitor = IntegrationMonitor()
        monitor.register_component("auth_service")
        
        # Record some successful and failed transactions
        monitor.record_transaction("auth_service", status="success", duration=50)
        monitor.record_transaction("auth_service", status="fail", duration=200, 
                                  details={"error": "Invalid credentials"})
        
        failures = monitor.get_failure_trace("auth_service")
        assert len(failures) == 1
        assert failures[0]["status"] == "fail"
        assert "error" in failures[0]["details"]

class TestHealthScoring:
    def test_health_score_calculation(self):
        """Test health score calculation based on transaction history"""
        monitor = IntegrationMonitor()
        monitor.register_component("database")
        
        # Record mix of successful and failed transactions
        for _ in range(8):
            monitor.record_transaction("database", status="success", duration=100)
        
        for _ in range(2):
            monitor.record_transaction("database", status="fail", duration=300)
        
        score = monitor.get_health_score("database")
        assert 0 <= score <= 1
        assert 0.7 <= score <= 0.9  # Should be around 0.8 (80% success rate)
    
    def test_health_score_with_no_transactions(self):
        """Test health score with no transaction history"""
        monitor = IntegrationMonitor()
        monitor.register_component("new_service")
        
        score = monitor.get_health_score("new_service")
        assert score is None or score == 1.0  # Either None or perfect score for no data
