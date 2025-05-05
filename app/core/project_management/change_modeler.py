"""
ChangeModeler: Change simulation/modeling stub

Location:
    /app/core/project_management/change_modeler.py

Rationale:
    - Required by test_change_propagation_simulation.py for Task 3.7.6 integration TDD.
    - Placed according to /code_summary.md and architecture overview: project_management handles workflow, planning, and simulation tools.
    - Signature and functionality per integration test and documentation: provides simulate_change for representing code/config changes.

Protocols/Docs:
    - /docs/architecture/dependency_tracking_protocol.md
    - /docs/development/day21_plan.md

Initial Implementation:
    - Only a stub with an interface that allows test progress.
    - Returns a simple Change object with needed attributes (component_id, change_type, description).
    - The actual model/data contract can be expanded as more requirements are surfaced from the test or documentation.

"""

from dataclasses import dataclass

@dataclass
class Change:
    component_id: str
    change_type: str
    description: str

class ChangeModeler:
    @staticmethod
    def simulate_change(component_id: str, change_type: str, description: str) -> Change:
        """
        Simulate a code/config/component change.
        For TDD: provides a basic Change instance representing the change event.

        Args:
            component_id: ID of the changed component.
            change_type: The type of change ('code', 'config', etc.)
            description: Human-readable description.

        Returns:
            Change: A dataclass instance representing the change.
        """
        return Change(component_id=component_id, change_type=change_type, description=description)