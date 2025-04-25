"""
AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-25

This module provides monitoring capabilities for integration health, component status,
and cross-component transaction logging.

The monitoring package helps track system health, detect integration failures,
and provide visualization data for system administrators.
"""

# Re-export key classes for easier imports
from integrations.monitoring.integration_health import (
    HealthMetric,
    HealthStatus,
    HealthMetricType,
    HealthProvider,
    HealthEvent,
    IntegrationHealth,
    IntegrationHealthError
)

from integrations.monitoring.component_status import (
    ComponentStatusProvider,
    ComponentStatus,
    ComponentStatusTracker,
    StatusHistoryEntry,
    StatusChangeEvent,
    StatusSeverity
)

from integrations.monitoring.transaction_logger import (
    Transaction,
    TransactionStage,
    TransactionEvent,
    TransactionContext,
    TransactionLogger,
    TransactionError
)

__all__ = [
    # From integration_health.py
    'HealthMetric',
    'HealthStatus',
    'HealthMetricType',
    'HealthProvider',
    'HealthEvent',
    'IntegrationHealth',
    'IntegrationHealthError',
    
    # From component_status.py
    'ComponentStatusProvider',
    'ComponentStatus',
    'ComponentStatusTracker',
    'StatusHistoryEntry',
    'StatusChangeEvent',
    'StatusSeverity',
    
    # From transaction_logger.py
    'Transaction',
    'TransactionStage',
    'TransactionEvent',
    'TransactionContext',
    'TransactionLogger',
    'TransactionError'
]
