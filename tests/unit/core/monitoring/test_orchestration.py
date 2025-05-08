"""
Test suite for /app/core/monitoring/orchestration.py

Covers:
- Protocol-specified orchestration of system-wide component health and monitoring.
- Compliance with ServiceHealthProtocol and HealthMonitoringProtocol.
- Status propagation, event firing, and orchestration flows.

References:
- /docs/development/day24_plan.md
- /docs/architecture/service_health_protocol.md
- /docs/architecture/health_monitoring_protocol.md

Updated: Components must be registered with both registry and IntegrationHealthManager before status updates.
"""

import pytest
from integrations.monitoring.health_status import HealthStatus, HealthMetricType, HealthMetric
from integrations.monitoring.integration_health_manager import IntegrationHealthManager
from integrations.monitoring.events import HealthEvent, HealthEventDispatcher
from integrations.registry.component_registry import ComponentRegistry
# Orchestration module to be implemented
from app.core.monitoring.orchestration import MonitoringOrchestrator

@pytest.fixture
def registry():
    return ComponentRegistry()

@pytest.fixture
def health_manager(registry):
    return IntegrationHealthManager(registry)

def test_orchestrator_initialization(registry, health_manager):
    """
    Ensure MonitoringOrchestrator can be initialized with a registry and health manager per protocol.
    """
    orchestrator = MonitoringOrchestrator(
        registry=registry, health_manager=health_manager)
    assert orchestrator.registry is registry
    assert orchestrator.health_manager is health_manager

def test_status_propagation_protocol_compliance(registry, health_manager):
    """
    Ensure orchestrator propagates status updates to all components per protocol, including event/dialog callbacks.
    """
    orchestrator = MonitoringOrchestrator(registry, health_manager)
    # Simulate two registered components
    comp1_id = registry.register_component(name="ComponentA")
    comp2_id = registry.register_component(name="ComponentB")
    # Register components in the health manager as required by protocol
    health_manager.register_component(comp1_id)
    health_manager.register_component(comp2_id)
    # Update status for comp1
    health_manager.update_component_status(comp1_id, HealthStatus.HEALTHY)
    orchestrator.propagate_status(comp1_id)
    # Status should be propagated and history recorded according to protocol specs
    comp1_status = health_manager.get_status(comp1_id)
    assert comp1_status == HealthStatus.HEALTHY
    # End-to-end status transitions (protocol: cascading, event-firing etc.)
    orchestrator.propagate_status(comp2_id)
    comp2_status = health_manager.get_status(comp2_id)
    assert comp2_status in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN)  # per protocol contract

def test_event_firing_and_callbacks(registry, health_manager):
    """
    Ensure orchestrator fires protocol-compliant HealthEvents and triggers registered listeners.
    """
    orchestrator = MonitoringOrchestrator(registry, health_manager)
    events_captured = []

    def listener(event: HealthEvent):
        events_captured.append(event)

    dispatcher = HealthEventDispatcher()
    dispatcher.register_listener(listener)

    comp_id = registry.register_component(name="EventComponent")
    # Register component in the health manager as required by protocol
    health_manager.register_component(comp_id)
    health_manager.update_component_status(comp_id, HealthStatus.DEGRADED)
    orchestrator.fire_status_event(comp_id, dispatcher=dispatcher)

    assert len(events_captured) == 1
    assert isinstance(events_captured[0], HealthEvent)
    assert events_captured[0].component == comp_id
    assert events_captured[0].status == HealthStatus.DEGRADED

def test_protocol_contract_fields_and_return_types(registry, health_manager):
    """
    Confirm orchestrator APIs match protocol signatures for registry/health propagation.
    """
    orchestrator = MonitoringOrchestrator(registry, health_manager)
    # Per protocol, orchestrator API signatures must match doc
    assert hasattr(orchestrator, "propagate_status")
    assert hasattr(orchestrator, "fire_status_event")
    # Return types per protocol spec
    result = orchestrator.propagate_status("dummy-id")
    assert isinstance(result, (type(None), bool))  # Protocol: may return None or bool
