import pytest

def test_multi_component_resource_assignment(registry):
    registry.register_resource(
        "qa_tina",
        resource_type="qa",
        availability=[("2024-06-15", "2024-06-20")]
    )
    assert registry.is_resource_available("qa_tina", at="2024-06-16")

    assigned = registry.assign_resource("qa_tina", "API", during=("2024-06-15", "2024-06-17"))
    assert assigned is True

    # Assign the same resource to a different component with a non-overlapping period: should work
    assigned2 = registry.assign_resource("qa_tina", "StudentDashboard", during=("2024-06-18", "2024-06-20"))
    assert assigned2 is True

    # Now, try to assign to an overlapping period: must conflict
    assigned3 = registry.assign_resource("qa_tina", "ProfessorUI", during=("2024-06-17", "2024-06-19"))
    assert assigned3 is False
    conflicts = registry.get_conflicts("qa_tina")
    assert any("ProfessorUI" in c["component"] for c in conflicts)

def test_resource_constraint_analysis(registry):
    # This demonstrates the constraint: no more resources than available
    registry.register_resource("dev_victor", resource_type="developer", availability=[("2024-06-12", "2024-06-19")])
    registry.assign_resource("dev_victor", "ComponentA", during=("2024-06-12", "2024-06-15"))
    registry.assign_resource("dev_victor", "ComponentB", during=("2024-06-16", "2024-06-18"))
    # Try to "overbook"
    assigned = registry.assign_resource("dev_victor", "ComponentC", during=("2024-06-14", "2024-06-17"))
    assert assigned is False
    # Constraint analysis: should show which assignments block others
    conflicts = registry.get_conflicts("dev_victor")
    assert len(conflicts) >= 1
    assert any(c["component"] == "ComponentC" for c in conflicts)

@pytest.fixture
def registry():
    from app.core.monitoring.resource_registry import ResourceRegistry
    reg = ResourceRegistry()
    reg.clear()
    return reg