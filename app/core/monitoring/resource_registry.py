from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

@dataclass
class ResourceAssignment:
    component: str
    period: Optional[Tuple[str, str]] = None  # (start_date, end_date)

@dataclass
class Resource:
    resource_id: str
    resource_type: str
    availability: List[Tuple[str, str]] = field(default_factory=list)
    assigned_to: Optional[str] = None
    assigned_periods: List[ResourceAssignment] = field(default_factory=list)
    status: str = "available"

class ResourceRegistry:
    """
    Resource Registry for tracking, assignment, availability, and conflict analysis.
    Fulfills requirements of /docs/development/day20_plan.md (Task 3.7.3) and all protocols.
    """
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.conflicts: Dict[str, List[Dict[str, Any]]] = {}

    def clear(self):
        self.resources.clear()
        self.conflicts.clear()

    def register_resource(self, resource_id: str, resource_type: str, availability: Optional[List[Tuple[str, str]]] = None):
        if resource_id not in self.resources:
            resource = Resource(
                resource_id=resource_id,
                resource_type=resource_type,
                availability=availability or [],
                status="available"
            )
            self.resources[resource_id] = resource
            self.conflicts[resource_id] = []
        return self.resources[resource_id]

    def assign_resource(self, resource_id: str, component: str, during: Optional[Tuple[str, str]] = None) -> bool:
        resource = self.resources.get(resource_id)
        if not resource:
            return False

        # Assignment period conflict
        if during:
            overlap = self._check_overlap(resource, during)
            if overlap:
                self.conflicts[resource_id].append({
                    "component": component,
                    "during": during
                })
                return False
            resource.assigned_periods.append(ResourceAssignment(component, during))
            resource.status = "assigned"
            resource.assigned_to = component
            return True
        else:
            if resource.status == "assigned":
                self.conflicts[resource_id].append({
                    "component": component,
                    "during": None
                })
                return False
            resource.status = "assigned"
            resource.assigned_to = component
            return True

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        return self.resources.get(resource_id)

    def is_resource_available(self, resource_id: str, at: str) -> bool:
        resource = self.resources.get(resource_id)
        if not resource or not resource.availability:
            return False
        at_dt = datetime.strptime(at, "%Y-%m-%d")
        for start, end in resource.availability:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            if start_dt <= at_dt <= end_dt:
                # Also, not assigned to cover this time period via assigned_periods
                for ap in resource.assigned_periods:
                    if ap.period:
                        astart, aend = [datetime.strptime(x, "%Y-%m-%d") for x in ap.period]
                        if astart <= at_dt <= aend:
                            return False
                return True
        return False

    def _check_overlap(self, resource: Resource, new_period: Tuple[str, str]) -> bool:
        new_start, new_end = [datetime.strptime(x, "%Y-%m-%d") for x in new_period]
        # Check against assigned periods
        for ap in resource.assigned_periods:
            if not ap.period:
                continue
            ap_start, ap_end = [datetime.strptime(x, "%Y-%m-%d") for x in ap.period]
            if (ap_start <= new_end and new_start <= ap_end):
                return True
        return False

    def get_conflicts(self, resource_id: str) -> List[Dict[str, Any]]:
        return self.conflicts.get(resource_id, [])

    def get_utilization(self, resource_id: str) -> float:
        resource = self.resources.get(resource_id)
        if not resource:
            return 0.0
        total_days = 0
        assigned_days = 0

        # Calculate days of availability
        for start, end in resource.availability:
            d0 = datetime.strptime(start, "%Y-%m-%d")
            d1 = datetime.strptime(end, "%Y-%m-%d")
            total_days += (d1 - d0).days + 1
        
        # Calculate assigned days
        for ap in resource.assigned_periods:
            if not ap.period:
                continue
            d0 = datetime.strptime(ap.period[0], "%Y-%m-%d")
            d1 = datetime.strptime(ap.period[1], "%Y-%m-%d")
            assigned_days += (d1 - d0).days + 1
        if total_days == 0:
            return 0.0
        return assigned_days / total_days