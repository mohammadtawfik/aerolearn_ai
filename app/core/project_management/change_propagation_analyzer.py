"""
ChangePropagationAnalyzer: Stub implementation for TDD, supports change impact analysis

Location:
    /app/core/project_management/change_propagation_analyzer.py

Rationale:
    - Required by the test_change_propagation_simulation.py for Task 3.7.6 integration test.
    - Placed according to project conventions for project_management modules (see /code_summary.md).
    - Follows protocol for dependency graph/impact: /docs/architecture/dependency_tracking_protocol.md.

Responsibilities:
    - Accepts a component registry and a Change instance, determines all directly and transitively impacted components.
    - The returned value must be a list of component_ids.
    - For TDD: This stub implements only enough logic to drive the test and trigger next-step requirements.

Expected Expansion:
    - Down the line, this class will use registry's get_dependency_graph and impact analysis APIs, and more detailed Change attributes.

"""

class ChangePropagationAnalyzer:
    @staticmethod
    def analyze(registry, change):
        """
        Analyze which components would be impacted by the given change.

        Args:
            registry: Instance of ComponentRegistry (protocol-compliant)
            change:   Instance of Change (from change_modeler.py)

        Returns:
            List of component IDs impacted (for now: direct+transitive dependencies).
        """
        # This stub mimics a simplistic impact: Get dependency graph and find all transitively dependent components, including the changed one.
        try:
            graph = registry.get_dependency_graph()
            changed = change.component_id
            impacted = set()
            # DFS all nodes whose path to root traverses 'changed'
            def dfs(node, seen):
                if node in seen:
                    return
                seen.add(node)
                for dep in graph.get(node, []):
                    if dep == changed or dep in impacted:
                        impacted.add(node)
                    dfs(dep, seen)
            for node in graph:
                dfs(node, set())
            impacted.add(changed)
            return list(impacted)
        except Exception:
            # Minimal stub: just return the changed component
            return [change.component_id]