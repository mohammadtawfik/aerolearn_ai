import pytest

# Assume these are the correct imports as per the destination package structure and code_summary.md
from app.core.monitoring.dashboard import ServiceHealthDashboard
from app.api.monitoring.endpoints import get_operational_dashboard_report
from app.api.monitoring.protocol_fields import PROTOCOL_APPROVED_REPORT_FIELDS

@pytest.fixture
def example_dashboard():
    # Setup a protocol-compliant dashboard with test data
    # (Can use mock or real, as permitted by other TDD tests)
    return ServiceHealthDashboard()

def test_dashboard_report_fields_protocol_compliance(example_dashboard):
    """
    Test that the GET dashboard report endpoint returns
    only protocol-approved fields as per service_health_protocol.md.
    """
    report = get_operational_dashboard_report(dashboard=example_dashboard)
    # The response dict (or object) must only include these fields
    assert set(report.keys()) <= set(PROTOCOL_APPROVED_REPORT_FIELDS), (
        "Dashboard report includes fields outside protocol-compliant set: %r" %
        (set(report.keys()) - set(PROTOCOL_APPROVED_REPORT_FIELDS))
    )

def test_dashboard_report_privacy_and_security(example_dashboard):
    """
    Test that dashboard/report API does not leak sensitive user or internal data.
    This test must be updated whenever fields change.
    """
    report = get_operational_dashboard_report(dashboard=example_dashboard)
    # Example security field checks (extend as new fields are added)
    forbidden = {"user_passwords", "access_tokens", "raw_logs", "debug_info"}
    assert forbidden.isdisjoint(report.keys()), (
        f"Dashboard report leaks sensitive/internal fields: {forbidden & set(report.keys())}"
    )
