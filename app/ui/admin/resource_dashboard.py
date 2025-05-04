from typing import List, Dict, Any, Optional
from app.core.monitoring.resource_registry import ResourceRegistry

class ResourceDashboard:
    """
    Minimal dashboard adapter for resource allocations.
    Plugs into the admin interface per architecture_overview.md.
    """

    def __init__(self, registry: Optional[ResourceRegistry] = None):
        self.registry = registry or ResourceRegistry()

    def get_resource_table(self) -> List[Dict[str, Any]]:
        # Returns all resources and key status for visualization
        return [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type,
                "status": r.status,
                "assigned_to": r.assigned_to,
                "assignments": [
                    {"component": ap.component, "period": ap.period}
                    for ap in r.assigned_periods
                ],
                "availability": r.availability,
                "utilization": self.registry.get_utilization(r.resource_id),
                "conflicts": self.registry.get_conflicts(r.resource_id),
            }
            for r in self.registry.resources.values()
        ]

    def get_utilization_summary(self) -> Dict[str, float]:
        return {
            r.resource_id: self.registry.get_utilization(r.resource_id)
            for r in self.registry.resources.values()
        }

    def get_constraints_overview(self) -> List[Dict[str, Any]]:
        rows = []
        for rid, res in self.registry.resources.items():
            conflicts = self.registry.get_conflicts(rid)
            if conflicts:
                rows.append({
                    "resource_id": rid,
                    "conflicts": conflicts,
                    "status": res.status
                })
        return rows