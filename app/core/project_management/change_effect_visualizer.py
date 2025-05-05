"""
ChangeEffectVisualizer: Visualization interface stub

Location:
    /app/core/project_management/change_effect_visualizer.py

Rationale:
    - Required by the integration test for Task 3.7.6 (change propagation simulation).
    - Layer and location follow project conventions in /code_summary.md and architecture overview.
    - Output and contract guided by integration test and design doc: must visualize (or stub-visualize) the effects of a modeled change and impacted components.

Protocols/Docs:
    - /docs/architecture/architecture_overview.md (modularity, pluggability, api contract)
    - /docs/architecture/dependency_tracking_protocol.md ("visualization is not part of the registry but intended to be implemented at the dashboard/UI layer" – can be stubbed to std output or similar initially)

Contract:
    - visualize(change, impacted) returns a representation that includes all impacted components (at least their ids)
    - For stub, return a string for test assertion.

"""

class ChangeEffectVisualizer:
    @staticmethod
    def visualize(change, impacted):
        """
        Provide a representation of the change's effects for visualization.
        For TDD, returns a string listing all impacted components.

        Args:
            change:    Change object describing the source event
            impacted:  List of component ids that are impacted

        Returns:
            String containing info about change and impacted components (stub for now)
        """
        return f"Change on '{change.component_id}' affects: {', '.join(sorted(impacted))}"