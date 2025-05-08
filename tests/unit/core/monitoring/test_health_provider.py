"""
Unit tests for /integrations/monitoring/health_provider.py

Protocol References:
- HealthProvider must be an ABC with required protocol methods as specified in 
  health_monitoring_protocol.md.

Tests:
- HealthProvider cannot be instantiated directly.
- All protocol-required abstractmethods exist.
- Any implementation must implement all required protocol methods.
- Complete implementations can be instantiated.
"""

import pytest
from integrations.monitoring.health_provider import HealthProvider

def test_health_provider_cannot_be_instantiated():
    """Protocol: HealthProvider is ABC and cannot be directly instantiated"""
    with pytest.raises(TypeError):
        HealthProvider()

def test_health_provider_required_methods():
    """Protocol: Required methods must be defined in the ABC"""
    required_methods = {"get_health_status", "get_metrics", "register_listener"}
    for method in required_methods:
        assert hasattr(HealthProvider, method), f"{method} missing from HealthProvider"

def test_incomplete_implementation_raises_error():
    """Protocol: Implementation must implement all required methods"""
    class IncompleteProvider(HealthProvider):
        def get_health_status(self):
            return {"status": "ok"}
    
    with pytest.raises(TypeError):
        IncompleteProvider()

def test_complete_implementation_can_be_instantiated():
    """Protocol: Complete implementation can be instantiated"""
    class CompleteProvider(HealthProvider):
        def get_health_status(self):
            return {"status": "ok"}
            
        def get_metrics(self):
            return {"metric1": 100}
            
        def register_listener(self, listener):
            pass
            
    provider = CompleteProvider()
    assert isinstance(provider, HealthProvider)
