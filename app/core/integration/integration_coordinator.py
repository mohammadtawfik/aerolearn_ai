"""
SAVE THIS FILE AT: /app/core/integration/integration_coordinator.py

Purpose:
- Core extension point for all major cross-component integrations.
- Allows app-layer to invoke week2 orchestrator cleanly and provides hooks for future integrations.

How to extend:
- Register additional orchestration routines as new integrations are added.
"""

from integrations.week2.orchestrator import Week2Orchestrator

class IntegrationCoordinator:
    """High-level integration controller; expose unified API for app core."""

    def __init__(self, orchestrator: Week2Orchestrator):
        self.orchestrator = orchestrator

    def perform_week2_integrations(self):
        """Run all week 2 orchestrations in sequence."""
        self.orchestrator.run_full_integration()