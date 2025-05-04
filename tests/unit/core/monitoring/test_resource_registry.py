import pytest
from datetime import datetime, timedelta

# Assuming the ResourceRegistry and core interfaces are in app.core.monitoring.resource_registry
# All logic is strictly TDD—implementation will be stubbed until tests pass

def test_register_resource(registry):
    resource = registry.register_resource("dev_alice", resource_type="developer", availability=[("2024-06-12", "2024-06-18")])
    assert resource.resource_id == "dev_alice"
    assert resource.resource_type == "developer"
    assert resource.status == "available"

def test_resource_assignment_to_component(registry):
    registry.register_resource("dev_bob", resource_type="developer")
    assigned = registry.assign_resource("dev_bob", "course_builder")
    assert assigned is True
    # The resource entry now references the component
    res = registry.get_resource("dev_bob")
    assert res.assigned_to == "course_builder"
    assert res.status == "assigned"

def test_resource_availability_tracking(registry):
    registry.register_resource("designer_eve", resource_type="designer", availability=[("2024-06-15", "2024-06-20")])
    # Resource should be available in date range
    assert registry.is_resource_available("designer_eve", at="2024-06-16")
    # Should not be available outside
    assert not registry.is_resource_available("designer_eve", at="2024-06-22")

def test_detect_conflict_in_assignment(registry):
    registry.register_resource("dev_cara", resource_type="developer", availability=[("2024-06-12", "2024-06-18")])
    # Assign Cara to two overlapping component tasks
    result1 = registry.assign_resource("dev_cara", "api_upgrade", during=("2024-06-13", "2024-06-14"))
    result2 = registry.assign_resource("dev_cara", "dashboard_refactor", during=("2024-06-13", "2024-06-15"))
    assert result1 is True
    assert result2 is False  # There should be a conflict with overlapping assignment
    # Confirm conflict info is available
    conflicts = registry.get_conflicts("dev_cara")
    assert len(conflicts) == 1
    assert conflicts[0]["component"] == "dashboard_refactor"

def test_resource_utilization_metrics(registry):
    # Register resource with real availability for utilization calculation
    registry.register_resource(
        "intern_dan",
        resource_type="intern",
        availability=[("2024-06-12", "2024-06-16")]
    )
    registry.assign_resource("intern_dan", "doc_update", during=("2024-06-12", "2024-06-16"))
    # Utilization metric: days assigned / total available days
    util = registry.get_utilization("intern_dan")
    assert isinstance(util, float)
    assert util > 0.0

@pytest.fixture
def registry():
    # Import locally as implementation will be developed after tests; reset for each test
    from app.core.monitoring.resource_registry import ResourceRegistry
    reg = ResourceRegistry()
    reg.clear()  # Ensure clean state
    return reg
