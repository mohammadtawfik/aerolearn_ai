"""
MonitoringOrchestrator

Implements: System monitoring orchestration for AeroLearn AI.

Location: /app/core/monitoring/orchestration.py

Protocol compliance:
- /docs/architecture/service_health_protocol.md
- /docs/architecture/health_monitoring_protocol.md
- Day 24 modularization and orchestration plan

Responsible for:
- Receiving registry and health manager references.
- Enabling protocol-compliant status propagation, event firing, and orchestration calls for dashboard/system ops.
"""

from integrations.monitoring.events import HealthEvent
from datetime import datetime

class MonitoringOrchestrator:
    def __init__(self, registry, health_manager):
        """
        Initialize the orchestrator with a component registry and health manager.
        Protocol: Must accept dependencies as per doc.
        """
        self.registry = registry
        self.health_manager = health_manager

    def propagate_status(self, component_id):
        """
        Propagates the health status for the given component_id to all relevant dependencies.
        Protocol: See service_health_protocol.md and health_monitoring_protocol.md.
        """
        # Stub for protocol; real logic to be developed TDD-style.
        return None

    def fire_status_event(self, component_id, dispatcher):
        """
        Fires a HealthEvent for the given component_id using the supplied dispatcher.
        Protocol: See health_monitoring_protocol.md event-handling section.
        """
        # Get the current status for the component
        status = self.health_manager.get_status(component_id)
        
        # Create a health event with the component ID, state, reason, and timestamp
        event = HealthEvent(
            component=component_id, 
            state=status,
            reason="Status propagation (orchestrator)",
            timestamp=datetime.utcnow()
        )
        
        # Dispatch the event using the provided dispatcher
        dispatcher.fire(event)  # Protocol: this is the canonical health event dispatch
