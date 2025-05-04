"""
Milestone Tracker and Registry

Implements Day 20 Plan (Task 3.7.2): milestone registry and management, supporting cross-component planning, dependency graph, progress, and risk.

Location: /app/core/project_management/milestone_tracker.py

Compliant with:
  - /docs/architecture/dependency_tracking_protocol.md
  - registry/protocol graph API conventions
  - status, audit, history, and error handling requirements

Follows: TDD, file structure, and naming rules per /code_summary.md and day20_plan.md
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set


class MilestoneStatus(Enum):
    PLANNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    BLOCKED = auto()
    ON_HOLD = auto()
    CANCELLED = auto()


@dataclass
class MilestoneHistoryRecord:
    status: MilestoneStatus
    timestamp: datetime


@dataclass
class Milestone:
    name: str
    components: Set[str]
    status: MilestoneStatus = MilestoneStatus.PLANNED
    dependencies: Set[str] = field(default_factory=set)
    status_history: List[MilestoneHistoryRecord] = field(default_factory=list)
    progress: float = 0.0  # 0 to 1.0

    def update_status(self, new_status: MilestoneStatus):
        self.status = new_status
        self.status_history.append(MilestoneHistoryRecord(
            status=new_status, timestamp=datetime.utcnow()
        ))

    def recalculate_progress(self, registry: 'MilestoneRegistry'):
        """
        Calculate overall progress as mean of dependency milestones' completion.
        If no dependencies, returns 1.0 if COMPLETED, else 0.0 or 0.5 if IN_PROGRESS.
        """
        if not self.dependencies:
            if self.status == MilestoneStatus.COMPLETED:
                self.progress = 1.0
            elif self.status == MilestoneStatus.IN_PROGRESS:
                self.progress = 0.5
            else:
                self.progress = 0.0
            return self.progress
        vals = []
        for dep in self.dependencies:
            dep_ms = registry.get_milestone(dep)
            vals.append(dep_ms.progress if dep_ms else 0.0)
        self.progress = sum(vals) / len(vals) if vals else 0.0
        return self.progress


class MilestoneRegistry:
    """
    Registry and manager for system/project milestones.

    - Register milestones (multi-component capable)
    - Set/query dependencies (dependency graph)
    - Calculate and retrieve milestone progress
    - Audit history, protocol-compliant error/cycle protection, risk
    """

    def __init__(self):
        self.milestones: Dict[str, Milestone] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def register_milestone(self, name: str, components: List[str], status: str = "PLANNED") -> Milestone:
        if name in self.milestones:
            raise ValueError(f"Milestone '{name}' is already registered.")
        status_enum = MilestoneStatus[status]
        ms = Milestone(name=name, components=set(components), status=status_enum)
        ms.status_history.append(MilestoneHistoryRecord(status=status_enum, timestamp=datetime.utcnow()))
        ms.recalculate_progress(self)
        self.milestones[name] = ms
        self.dependencies.setdefault(name, set())
        return ms

    def get_milestone(self, name: str) -> Optional[Milestone]:
        return self.milestones.get(name)

    def update_milestone_status(self, name: str, new_status: str):
        ms = self.get_milestone(name)
        if ms is None:
            raise KeyError(f"No milestone registered as '{name}'")
        status_enum = MilestoneStatus[new_status]
        ms.update_status(status_enum)
        ms.recalculate_progress(self)

    def declare_milestone_dependency(self, milestone_name: str, dependency_name: str) -> bool:
        if milestone_name not in self.milestones or dependency_name not in self.milestones:
            return False
        if milestone_name == dependency_name:
            return False
        if self._has_path(dependency_name, milestone_name):
            return False
        self.dependencies[milestone_name].add(dependency_name)
        self.milestones[milestone_name].dependencies.add(dependency_name)
        self.milestones[milestone_name].recalculate_progress(self)
        return True

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        return {name: list(deps) for name, deps in self.dependencies.items()}

    def _has_path(self, src: str, dst: str, visited=None) -> bool:
        if visited is None:
            visited = set()
        if src == dst:
            return True
        visited.add(src)
        for neighbor in self.dependencies.get(src, []):
            if neighbor not in visited:
                if self._has_path(neighbor, dst, visited):
                    return True
        return False

    def get_status_history(self, name: str) -> List[MilestoneHistoryRecord]:
        ms = self.get_milestone(name)
        return ms.status_history[:] if ms else []

    def get_progress(self, name: str) -> float:
        ms = self.get_milestone(name)
        return ms.progress if ms else 0.0

    def assess_risk(self, name: str) -> Dict[str, any]:
        """
        Example risk assessment: Returns info about any unresolved dependencies,
        at-risk status (blocked, on hold, etc.), and completion
        """
        ms = self.get_milestone(name)
        if not ms: return {}
        incomplete_deps = [
            dep for dep in ms.dependencies
            if self.milestones[dep].status != MilestoneStatus.COMPLETED
        ]
        risk = {
            "blocked": ms.status == MilestoneStatus.BLOCKED,
            "on_hold": ms.status == MilestoneStatus.ON_HOLD,
            "unresolved_dependencies": incomplete_deps,
            "completion": ms.progress,
        }
        return risk