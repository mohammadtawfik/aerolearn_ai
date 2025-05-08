"""
Unit tests for /integrations/monitoring/events.py

Protocol References:
- Must support HealthEvent, correct event fields, event type enums, listener logic.

Tests:
- Event creation/use with mandated fields.
- Listener registration, firing, and delivery match protocol.
"""

import pytest
from integrations.monitoring.events import HealthEvent, HealthEventDispatcher, register_health_event_listener
from integrations.monitoring.health_status import HealthStatus


def test_health_event_creation():
    """Test that HealthEvent can be created with required fields."""
    evt = HealthEvent(
        component="api", 
        state=HealthStatus.FAILED, 
        reason="timeout", 
        timestamp="2024-06-12T12:00:00Z"
    )
    assert evt.component == "api"
    assert evt.state == HealthStatus.FAILED
    assert evt.reason == "timeout"
    assert evt.timestamp == "2024-06-12T12:00:00Z"
    
    # Test with numeric timestamp
    evt2 = HealthEvent(
        component="db", 
        state=HealthStatus.HEALTHY, 
        reason="startup", 
        timestamp=1623499200.0
    )
    assert evt2.timestamp == 1623499200.0


def test_health_event_with_string_state():
    """Test that HealthEvent accepts string state values."""
    evt = HealthEvent(
        component="api", 
        state="FAILED", 
        reason="timeout", 
        timestamp="2024-06-12T12:00:00Z"
    )
    assert evt.state == HealthStatus.FAILED


def test_health_state_enum():
    """Test that HealthStatus enum has required values."""
    assert HealthStatus.HEALTHY.value == "HEALTHY"
    assert HealthStatus.DEGRADED.value == "DEGRADED"
    assert HealthStatus.FAILED.value == "FAILED"


def test_event_dispatcher_registration():
    """Test that listeners can be registered with the dispatcher."""
    dispatcher = HealthEventDispatcher()
    
    def listener(evt):
        pass
    
    dispatcher.add_listener(listener)
    assert listener in dispatcher.listeners
    
    # Test using the register_health_event_listener function
    def another_listener(evt):
        pass
    
    register_health_event_listener(dispatcher, another_listener)
    assert another_listener in dispatcher.listeners


def test_event_dispatcher_firing():
    """Test that events are delivered to registered listeners."""
    calls = []
    
    def listener(evt):
        calls.append(evt)
    
    dispatcher = HealthEventDispatcher()
    dispatcher.add_listener(listener)
    
    test_evt = HealthEvent(
        component="db", 
        state=HealthStatus.DEGRADED, 
        reason="overload", 
        timestamp="2024-06-12T13:00:00Z"
    )
    
    dispatcher.fire(test_evt)
    assert len(calls) == 1
    assert calls[0] == test_evt


def test_multiple_listeners():
    """Test that events are delivered to multiple registered listeners."""
    calls_a = []
    calls_b = []
    
    def listener_a(evt):
        calls_a.append(evt)
    
    def listener_b(evt):
        calls_b.append(evt)
    
    dispatcher = HealthEventDispatcher()
    dispatcher.add_listener(listener_a)
    dispatcher.add_listener(listener_b)
    
    test_evt = HealthEvent(
        component="cache", 
        state=HealthStatus.HEALTHY, 
        reason="recovered", 
        timestamp="2024-06-12T14:00:00Z"
    )
    
    dispatcher.fire(test_evt)
    assert len(calls_a) == 1
    assert len(calls_b) == 1
    assert calls_a[0] == test_evt
    assert calls_b[0] == test_evt


def test_remove_listener():
    """Test that listeners can be removed from the dispatcher."""
    calls = []
    
    def listener(evt):
        calls.append(evt)
    
    dispatcher = HealthEventDispatcher()
    dispatcher.add_listener(listener)
    dispatcher.remove_listener(listener)
    
    test_evt = HealthEvent(
        component="api", 
        state=HealthStatus.FAILED, 
        reason="timeout", 
        timestamp="2024-06-12T15:00:00Z"
    )
    
    dispatcher.fire(test_evt)
    assert len(calls) == 0
def test_dispatcher_only_accepts_health_event():
    """Test that dispatcher only accepts HealthEvent objects."""
    dispatcher = HealthEventDispatcher()
    
    with pytest.raises(TypeError):
        dispatcher.fire("not a HealthEvent")
    
    with pytest.raises(TypeError):
        dispatcher.fire({"component": "api", "state": "FAILED"})

def test_event_with_custom_attributes():
    """Test that HealthEvent can have custom attributes added."""
    evt = HealthEvent(
        component="api", 
        state=HealthStatus.HEALTHY, 
        reason="startup", 
        timestamp="2024-06-12T16:00:00Z"
    )
    
    # Add a custom attribute
    evt.captured = True
    assert evt.captured is True
    
    # Test in listener context
    def sample_listener(event):
        event.processed = True
    
    dispatcher = HealthEventDispatcher()
    dispatcher.add_listener(sample_listener)
    dispatcher.fire(evt)
    
    assert evt.processed is True

def test_register_health_event_listener_function():
    """Test the register_health_event_listener helper function."""
    dispatcher = HealthEventDispatcher()
    log = []
    
    def listener(evt):
        log.append(evt)
    
    register_health_event_listener(dispatcher, listener)
    
    evt = HealthEvent(
        component="core", 
        state=HealthStatus.HEALTHY, 
        reason="ok", 
        timestamp=1623499200.0
    )
    
    dispatcher.fire(evt)
    assert log and log[0] is evt
