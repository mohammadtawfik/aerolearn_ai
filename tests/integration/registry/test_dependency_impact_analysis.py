import pytest

from integrations.registry.component_registry import ComponentRegistry
from app.core.project_management.feature_tracker import FeatureRegistry, FeatureStatus

# --- Fixtures ---

@pytest.fixture
def populated_registry():
    reg = ComponentRegistry()
    reg.register_component("API", version="1.0")
    reg.register_component("Database", version="1.0")
    reg.register_component("Frontend", version="1.0")
    reg.declare_dependency("API", "Database")
    reg.declare_dependency("Frontend", "API")
    return reg

@pytest.fixture
def feature_registry():
    reg = FeatureRegistry()
    reg.register_feature("UserAuth", component="API", status="COMPLETED")
    reg.register_feature("ContentStorage", component="Database", status="COMPLETED")
    reg.register_feature("UI", component="Frontend", status="COMPLETED")
    reg.link_feature_dependency("UI", "UserAuth")
    reg.link_feature_dependency("UserAuth", "ContentStorage")
    return reg

# --- Tests: Change Detection ---

def test_api_change_detection_component_level(populated_registry):
    reg = populated_registry
    # Simulate API version bump (potentially breaking)
    reg.get_component("API").version = "2.0"
    changed, details = reg.detect_api_change("API")
    assert changed
    assert "version" in details

def test_impact_propagation_through_dependencies(populated_registry):
    reg = populated_registry
    reg.get_component("Database").state = "DOWN"
    impacted = reg.analyze_dependency_impact("Database")
    assert "API" in impacted
    assert "Frontend" in impacted

def test_compatibility_risk_scoring_simple(populated_registry):
    reg = populated_registry
    # A breaking change in Database
    reg.get_component("Database").version = "2.0"
    score, breakdown = reg.calculate_compatibility_risk("Database")
    assert isinstance(score, float)
    assert score > 0
    assert "API" in breakdown
    assert "Frontend" in breakdown

def test_backward_compatibility_verification(populated_registry):
    reg = populated_registry
    # Simulate backward-compatible change (minor version bump)
    reg.get_component("API").version = "1.1"
    compatible = reg.check_version_compatibility("API")
    assert compatible

def test_impact_prediction_accuracy(populated_registry):
    reg = populated_registry
    reg.get_component("API").version = "2.0"
    # Should predict UI is impacted (via Frontend)
    impacted = reg.analyze_dependency_impact("API")
    assert set(impacted) == {"Frontend"}

# --- Integration test with FeatureRegistry ---

def test_feature_level_impact_propagation(populated_registry, feature_registry):
    c_reg = populated_registry
    f_reg = feature_registry
    # Simulate breaking database API change
    c_reg.get_component("Database").version = "2.0"
    impacted = f_reg.analyze_feature_impact_from_component_change("Database", c_reg)
    assert "UserAuth" in impacted
    assert "UI" in impacted

def test_backward_compatibility_with_features(populated_registry, feature_registry):
    c_reg = populated_registry
    f_reg = feature_registry
    c_reg.get_component("API").version = "1.1"
    assert f_reg.check_feature_backward_compatibility("UserAuth", c_reg)

def test_risk_scoring_per_feature(populated_registry, feature_registry):
    c_reg = populated_registry
    f_reg = feature_registry
    c_reg.get_component("API").version = "2.0"
    score, details = f_reg.feature_compatibility_risk("UserAuth", c_reg)
    assert isinstance(score, float)
    assert score > 0
    assert "UserAuth" in details