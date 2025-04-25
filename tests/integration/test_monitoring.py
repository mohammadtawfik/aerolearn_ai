"""
Integration tests for the monitoring system.

This module tests the integration health, component status, and transaction logging
components to ensure they work together correctly.
"""

import unittest
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
print(f"Added project root to path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))}")

# First, let's directly import ComponentState to examine it
from integrations.registry.component_registry import Component, ComponentState

# Now the rest of the imports
from integrations.monitoring.integration_health import (
    HealthMetric, 
    HealthStatus,
    HealthMetricType, 
    HealthProvider,
    IntegrationHealth
)

from integrations.monitoring.component_status import (
    ComponentStatusProvider,
    ComponentStatus,
    ComponentStatusTracker,
    StatusSeverity
)

from integrations.monitoring.transaction_logger import (
    Transaction,
    TransactionStage,
    TransactionLogger
)

# Debug: Print out what values are available in ComponentState
print("Available ComponentState values:")
for state_name in dir(ComponentState):
    if not state_name.startswith('_'):
        print(f"  - {state_name}")

# Mock components for testing
class MockComponent(Component, HealthProvider, ComponentStatusProvider):
    """Mock component for testing monitoring systems."""
    
    def __init__(self, component_id: str, name: str):
        """Initialize mock component."""
        # Call the parent Component constructor with required arguments
        super().__init__(
            component_id=component_id,
            component_type="test", 
            version="1.0.0"
        )
        self.name = name
        self._health_status = HealthStatus.HEALTHY
        
        # Use the first available state from ComponentState
        # This assumes at least one state is defined
        for state_name in dir(ComponentState):
            if not state_name.startswith('_'):
                self._component_state = getattr(ComponentState, state_name)
                break
        self._metrics = []
    
    # HealthProvider implementation
    def get_health_metrics(self) -> List[HealthMetric]:
        """Get health metrics from the component."""
        # Add a current timestamp metric
        current_metric = HealthMetric(
            name="response_time",
            value=0.05,  # 50ms
            metric_type=HealthMetricType.RESPONSE_TIME,
            component_id=self.component_id
        )
        self._metrics.append(current_metric)
        return self._metrics
    
    def get_health_status(self) -> HealthStatus:
        """Get the overall health status."""
        return self._health_status
    
    def set_health_status(self, status: HealthStatus) -> None:
        """Set the health status for testing."""
        self._health_status = status
    
    # ComponentStatusProvider implementation
    def get_component_state(self) -> ComponentState:
        """Get the component state."""
        return self._component_state
    
    def get_status_details(self) -> Dict[str, Any]:
        """Get detailed component status."""
        return {
            'state': self._component_state.name,
            'last_update': datetime.now().isoformat(),
            'metrics': {
                'memory_usage': 1024,
                'active_connections': 5
            }
        }
    
    def set_component_state(self, state: ComponentState) -> None:
        """Set the component state for testing."""
        self._component_state = state


class TestMonitoringSystem(unittest.TestCase):
    """Test cases for the monitoring system components."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        # Create monitoring components
        self.health_monitor = IntegrationHealth(polling_interval=0.1)
        self.status_tracker = ComponentStatusTracker()
        self.transaction_logger = TransactionLogger()
        
        # Create mock components
        self.component1 = MockComponent("test.component1", "Test Component 1")
        self.component2 = MockComponent("test.component2", "Test Component 2")
        
        # Store the initial state for later comparison
        self.initial_state = self.component1.get_component_state()
        
        # Find a different state to use for state change tests
        self.different_state = None
        for state_name in dir(ComponentState):
            if (not state_name.startswith('_') and 
                getattr(ComponentState, state_name) != self.initial_state):
                self.different_state = getattr(ComponentState, state_name)
                break
        
        # If no different state was found, we'll need to skip some tests
        if self.different_state is None:
            print("WARNING: Could not find a different state for testing state changes")
        
        # Register components with monitoring systems
        self.health_monitor.register_health_provider(
            self.component1.component_id, 
            self.component1
        )
        self.health_monitor.register_health_provider(
            self.component2.component_id, 
            self.component2
        )
        
        self.status_tracker.register_status_provider(
            self.component1.component_id,
            self.component1
        )
        self.status_tracker.register_status_provider(
            self.component2.component_id,
            self.component2
        )
    
    def test_health_metrics_collection(self) -> None:
        """Test collecting health metrics from components."""
        # Collect metrics
        metrics = self.health_monitor.collect_metrics()
        
        # Verify metrics were collected for both components
        self.assertIn(self.component1.component_id, metrics)
        self.assertIn(self.component2.component_id, metrics)
        
        # Verify metrics content
        self.assertEqual(len(metrics[self.component1.component_id]), 1)
        self.assertEqual(
            metrics[self.component1.component_id][0].name, 
            "response_time"
        )
    
    def test_health_status_changes(self) -> None:
        """Test health status change detection."""
        # Initial status should be unknown until first check
        self.assertEqual(
            self.health_monitor.get_component_health_status(self.component1.component_id),
            HealthStatus.UNKNOWN
        )
        
        # Collect metrics to update status
        self.health_monitor.collect_metrics()
        
        # Status should now be HEALTHY
        self.assertEqual(
            self.health_monitor.get_component_health_status(self.component1.component_id),
            HealthStatus.HEALTHY
        )
        
        # Change component status to DEGRADED
        self.component1.set_health_status(HealthStatus.DEGRADED)
        
        # Collect metrics again
        self.health_monitor.collect_metrics()
        
        # Status should now be DEGRADED
        self.assertEqual(
            self.health_monitor.get_component_health_status(self.component1.component_id),
            HealthStatus.DEGRADED
        )
    
    def test_overall_system_health(self) -> None:
        """Test overall system health calculation."""
        # Initial overall health
        self.health_monitor.collect_metrics()
        self.assertEqual(
            self.health_monitor.get_overall_system_health(),
            HealthStatus.HEALTHY
        )
        
        # Set one component to DEGRADED
        self.component1.set_health_status(HealthStatus.DEGRADED)
        self.health_monitor.collect_metrics()
        
        # Overall health should be DEGRADED
        self.assertEqual(
            self.health_monitor.get_overall_system_health(),
            HealthStatus.DEGRADED
        )
        
        # Set one component to CRITICAL
        self.component2.set_health_status(HealthStatus.CRITICAL)
        self.health_monitor.collect_metrics()
        
        # Overall health should be CRITICAL
        self.assertEqual(
            self.health_monitor.get_overall_system_health(),
            HealthStatus.CRITICAL
        )
    
    def test_component_status_tracking(self) -> None:
        """Test component status tracking and history."""
        # Skip test if we couldn't find a different state
        if self.different_state is None:
            self.skipTest("Could not find a different ComponentState for testing")
        
        # Get initial status
        status1 = self.status_tracker.get_component_status(self.component1.component_id)
        self.assertIsNotNone(status1)
        self.assertEqual(status1.state, self.initial_state)
        
        # Change component state
        self.component1.set_component_state(self.different_state)
        
        # Update status
        self.status_tracker.update_component_status(self.component1.component_id)
        
        # Verify updated status
        status1 = self.status_tracker.get_component_status(self.component1.component_id)
        self.assertEqual(status1.state, self.different_state)
        
        # Check status history
        history = self.status_tracker.get_status_history(self.component1.component_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].state, self.different_state.name)
    
    def test_status_summary(self) -> None:
        """Test component status summary generation."""
        # Update all statuses
        self.status_tracker.update_all_statuses()
        
        # Get summary
        summary = self.status_tracker.get_status_summary()
        
        # Verify summary contents
        self.assertEqual(summary['total_components'], 2)
        self.assertIn(self.component1.component_id, summary['components'])
        self.assertIn(self.component2.component_id, summary['components'])
        self.assertEqual(
            summary['components'][self.component1.component_id]['state'], 
            self.initial_state.name
        )
    
    def test_transaction_logging(self) -> None:
        """Test transaction logging functionality."""
        # Create a transaction
        transaction = self.transaction_logger.create_transaction(
            name="Test Transaction",
            metadata={"key": "value"}
        )
        
        # Start the transaction
        transaction.start(self.component1.component_id)
        self.transaction_logger.update_transaction(transaction)
        
        # Verify transaction state
        self.assertEqual(transaction.stage, TransactionStage.STARTED)
        
        # Update transaction
        transaction.process(self.component2.component_id, "Processing data")
        self.transaction_logger.update_transaction(transaction)
        
        # Verify transaction state
        self.assertEqual(transaction.stage, TransactionStage.PROCESSING)
        
        # Complete transaction
        transaction.complete(self.component1.component_id, "Success")
        self.transaction_logger.update_transaction(transaction)
        
        # Verify transaction state
        self.assertEqual(transaction.stage, TransactionStage.COMPLETED)
        
        # Verify transaction retrieval
        tx = self.transaction_logger.get_transaction(transaction.transaction_id)
        self.assertIsNotNone(tx)
        self.assertEqual(tx.stage, TransactionStage.COMPLETED)
        
        # Verify components in transaction
        self.assertIn(self.component1.component_id, tx.components)
        self.assertIn(self.component2.component_id, tx.components)
    
    def test_transaction_context(self) -> None:
        """Test transaction context manager."""
        # Use transaction context
        with self.transaction_logger.transaction_context(
            component_id=self.component1.component_id,
            name="Context Transaction",
            action="Testing context"
        ) as tx:
            # Add metadata
            tx.add_metadata("test_key", "test_value")
            
            # Add component
            tx.process(self.component2.component_id, "Help with processing")
        
        # Transaction should be completed
        tx_id = tx.transaction_id
        tx = self.transaction_logger.get_transaction(tx_id)
        self.assertEqual(tx.stage, TransactionStage.COMPLETED)
        self.assertEqual(tx.metadata["test_key"], "test_value")
    
    def test_transaction_context_with_error(self) -> None:
        """Test transaction context manager with error."""
        try:
            with self.transaction_logger.transaction_context(
                component_id=self.component1.component_id,
                name="Failed Transaction",
                action="Will fail"
            ) as tx:
                # Add component
                tx.process(self.component2.component_id, "About to fail")
                
                # Raise exception
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected exception
        
        # Transaction should be failed
        tx_id = tx.transaction_id
        tx = self.transaction_logger.get_transaction(tx_id)
        self.assertEqual(tx.stage, TransactionStage.FAILED)
        self.assertEqual(len(tx.errors), 1)
        self.assertEqual(tx.errors[0]["type"], "ValueError")
    
    def test_transaction_summary(self) -> None:
        """Test transaction summary generation."""
        # Create several transactions
        for i in range(5):
            with self.transaction_logger.transaction_context(
                component_id=self.component1.component_id,
                name=f"Transaction {i}"
            ):
                # Just create and complete
                pass
        
        # Create a failed transaction
        try:
            with self.transaction_logger.transaction_context(
                component_id=self.component1.component_id,
                name="Will Fail"
            ):
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected exception
        
        # Get summary
        summary = self.transaction_logger.get_transaction_summary()
        
        # Verify summary
        self.assertEqual(summary['total_transactions'], 6)
        self.assertEqual(summary['stage_counts'][TransactionStage.COMPLETED.name], 5)
        self.assertEqual(summary['stage_counts'][TransactionStage.FAILED.name], 1)
    
    def test_health_visualization_data(self) -> None:
        """Test health visualization data generation."""
        # Collect metrics
        self.health_monitor.collect_metrics()
        
        # Set different health statuses
        self.component1.set_health_status(HealthStatus.HEALTHY)
        self.component2.set_health_status(HealthStatus.DEGRADED)
        self.health_monitor.collect_metrics()
        
        # Get visualization data
        viz_data = self.health_monitor.get_health_visualization_data()
        
        # Verify data
        self.assertEqual(viz_data['overall_status'], HealthStatus.DEGRADED.name)
        self.assertEqual(
            viz_data['component_status'][self.component1.component_id], 
            HealthStatus.HEALTHY.name
        )
        self.assertEqual(
            viz_data['component_status'][self.component2.component_id], 
            HealthStatus.DEGRADED.name
        )


if __name__ == '__main__':
    unittest.main()
