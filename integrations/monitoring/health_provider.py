"""
Defines HealthProvider ABC for monitoring, as required by modularization and all monitoring protocol docs.
"""

from abc import ABC, abstractmethod

class HealthProvider(ABC):
    """
    Abstract base class for protocol-driven health/monitoring providers.
    Fulfills project modularization, TDD, and protocol documentation requirements.
    """

    @abstractmethod
    def get_health_status(self):
        """
        Abstract protocol method to get health status.
        """
        pass

    @abstractmethod
    def register_listener(self, listener):
        """
        Abstract protocol method to register a status/event listener.
        """
        pass
