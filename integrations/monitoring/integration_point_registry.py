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
        self._points = []       # order-preserving, deduped IDs
        self._storage = {}      # point_id -> value

    def register_point(self, point_id, value=None):
        """
        Register an integration point by ID (and optional value) with deduplication.
        
        Args:
            point_id: Unique identifier for the integration point
            value: Metadata/value dictionary or object to associate (optional)
        """
        self._storage[point_id] = value
        if point_id not in self._points:
            self._points.append(point_id)

    def get_point(self, point_id):
        """
        Get the value/metadata for a given point_id.

        Args:
            point_id: ID to lookup

        Returns:
            The value associated or None.
        """
        return self._storage.get(point_id)

    def lookup(self, point_id):
        """
        Lookup an integration point's value by ID.
        
        Args:
            point_id: The unique ID of the integration point
            
        Returns:
            The value associated with the ID, or None if not found
        """
        return self._storage.get(point_id)

    def get_all_points(self):
        """
        Return all registered integration points as a dict.

        Returns:
            Dict mapping point_id -> value for all points.
        """
        return dict(self._storage)

    def get_all(self):
        """
        Return a dict of all registered integration points.
        
        Returns:
            A dictionary containing all registered {point_id: value}
        """
        return dict(self._storage)

    def get_all_keys(self):
        """
        Return a list of integration point IDs.
        
        Returns:
            A list of all registered keys/IDs
        """
        return list(self._storage.keys())
        
    def list_points(self):
        """
        Return a list of all registered point IDs (ordered).
        
        Returns:
            A list of all registered point IDs in registration order (deduped)
        """
        return list(self._points)
