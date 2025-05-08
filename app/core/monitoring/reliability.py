import time
from integrations.monitoring.events import HealthEvent, HealthEventDispatcher
from integrations.monitoring.health_status import HealthStatus
from integrations.registry.component_state import ComponentState

class ReliabilityManager:
    """
    Protocol-compliant reliability/self-diagnosis manager for monitoring.
    Implements all API and event contract requirements per health monitoring protocol.
    """
    def __init__(self, component_id, registry, health_manager, dispatcher=None):
        self.component_id = component_id
        self.registry = registry  # Protocol interface: manages components/deps/state
        self.health_manager = health_manager  # Protocol interface: status/metrics
        self.dispatcher = dispatcher or HealthEventDispatcher()

    def self_diagnose(self, reason="periodic check"):
        """
        Protocol-mandated self-diagnosis surface, also triggers state/event/metrics.
        
        - Updates metrics/state via health_manager
        - Emits a HealthEvent
        - Notifies registry of any issues found
        
        Returns: True if healthy, False otherwise.
        """
        # 1. Read the current health status
        current_status = self.health_manager.get_component_status(self.component_id)
        
        # 2. If not healthy, mark as DEGRADED, notify, update metrics, emit event
        now = time.time()
        if current_status != HealthStatus.HEALTHY:
            new_state = HealthStatus.DEGRADED
            self.health_manager.update_component_status(self.component_id, new_state)
            
            # Notify registry of state change (protocol requirement)
            if hasattr(self.registry, 'notify_state_change'):
                self.registry.notify_state_change(self.component_id, new_state)
            if hasattr(self.registry, 'set_component_state'):
                self.registry.set_component_state(self.component_id, new_state)
                
            # Update metrics per protocol requirements (if supported)
            if hasattr(self.health_manager, "record_metric"):
                self.health_manager.record_metric(self.component_id, "health_state", new_state)
                
            # Protocol: emit HealthEvent
            event = HealthEvent(
                component=self.component_id,
                state=new_state,
                reason=f"Self-diagnosis detected issue: {reason}",
                timestamp=now
            )
            self.dispatcher.fire(event)
            return False
        else:
            # Everything healthy, emit event
            event = HealthEvent(
                component=self.component_id,
                state=HealthStatus.HEALTHY,
                reason=f"Self-diagnosis passed: {reason}",
                timestamp=now
            )
            self.dispatcher.fire(event)
            
            # Update metrics for healthy state too (if supported)
            if hasattr(self.health_manager, "record_metric"):
                self.health_manager.record_metric(self.component_id, "health_state", HealthStatus.HEALTHY)
                
            return True
    
    def check_dependencies(self):
        """
        Protocol-required dependency health check.
        Verifies all registered dependencies are healthy.
        
        Returns: True if all dependencies healthy, False otherwise.
        """
        if not hasattr(self.registry, 'get_dependencies'):
            return True  # No dependencies to check
            
        dependencies = self.registry.get_dependencies(self.component_id)
        if not dependencies:
            return True
            
        all_healthy = True
        for dep_id in dependencies:
            dep_status = self.health_manager.get_component_status(dep_id)
            if dep_status != HealthStatus.HEALTHY:
                all_healthy = False
                # Protocol: record dependency failure
                if hasattr(self.health_manager, "record_dependency_failure"):
                    self.health_manager.record_dependency_failure(
                        self.component_id, dep_id, dep_status
                    )
                
        return all_healthy
    
    def register_dependency(self, dependency_id):
        """
        Protocol-required dependency registration.
        Registers a component dependency in the registry.
        
        Args:
            dependency_id: ID of the component this component depends on
        """
        if hasattr(self.registry, 'declare_dependency'):
            self.registry.declare_dependency(self.component_id, dependency_id)
