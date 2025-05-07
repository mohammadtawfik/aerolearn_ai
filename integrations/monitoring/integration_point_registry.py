# /integrations/monitoring/integration_point_registry.py
"""
IntegrationPointRegistry — In-memory registry for integration points.

Fulfills:
- Modularization as detailed in /docs/development/integration_health_modularization_plan.md
- Test and protocol surface as exercised by /tests/unit/core/monitoring/test_integration_point_registry.py
"""


class IntegrationPointRegistry:
    """
    Registry for integration points with ability to register, lookup and enumerate all points.
    Protocol/docco-compliant.
    """
    def __init__(self):
        self._storage = {}

    def register(self, key, value):
        """
        Register an integration point (name and metadata/value).
        """
        self._storage[key] = value

    def lookup(self, key):
        """
        Lookup an integration point's value by name.
        """
        return self._storage.get(key)

    def get_all(self):
        """
        Return a dict of all registered integration points.
        """
        return dict(self._storage)

    def get_all_keys(self):
        """
        Return a list of integration point keys/names.
        """
        return list(self._storage.keys())
