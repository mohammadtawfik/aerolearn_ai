"""
MigrationPlanner: Stub implementation for TDD-driven development of migration planning.

Location:
    /app/core/project_management/migration_planner.py

Rationale:
    - Required for the integration test under /tests/integration/registry/test_change_propagation_simulation.py.
    - Placed as per /code_summary.md guidance for project_management submodules.
    - Designed to match TDD contract from the current integration test, as well as requirements in /docs/development/day21_plan.md for migration planning tools.

Protocols/Docs:
    - /docs/architecture/architecture_overview.md (extensible, pluggable, interface-oriented tools)
    - /docs/architecture/dependency_tracking_protocol.md (impact & propagation, migration scenario may use this contract)
    - /docs/development/day21_plan.md (migration planning as explicit deliverable for 3.7.6)

Contract:
    - plan_migration(change, impacted) returns a dict containing at least:
        - "change" (echo of change object)
        - "impacted" (list of component_ids)
    - More detailed plans will be constructed as doc and requirement mature.

"""

class MigrationPlanner:
    @staticmethod
    def plan_migration(change, impacted):
        """
        Build a migration plan for the impacted components.

        Args:
            change:   Change object as returned by ChangeModeler.simulate_change
            impacted: List of component ids affected by the change (strings)

        Returns:
            Dict describing the migration plan (stub: just contains change and impacted keys)
        """
        return {
            "change": change,
            "impacted": list(impacted)
        }