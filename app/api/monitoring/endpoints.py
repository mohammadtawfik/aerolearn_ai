"""
API endpoint for operational dashboard reporting.

- Implements: /docs/architecture/service_health_protocol.md
- All returned fields strictly follow PROTOCOL_APPROVED_REPORT_FIELDS.
- Does not expose sensitive fields; see test for security/privacy contract.
"""

# Required imports; ensure ServiceHealthDashboard is in path (per project layout)
from app.core.monitoring.dashboard import ServiceHealthDashboard

# For demonstration, PROTOCOL_APPROVED_REPORT_FIELDS is imported here. 
# In reality, you may need to define these fields somewhere central, 
# or extract them directly from the protocol documentation.
try:
    from docs.architecture.service_health_protocol import PROTOCOL_APPROVED_REPORT_FIELDS
except ImportError:
    # Fallback: Define a typical list as per protocol doc, but mandate update if protocol changes
    PROTOCOL_APPROVED_REPORT_FIELDS = [
        "component",
        "state",
        "timestamp",
        "metrics",
        "reason",
        # Add other protocol-sanctioned fields here as updated in service_health_protocol.md
    ]

def get_operational_dashboard_report(dashboard: ServiceHealthDashboard):
    """
    Returns protocol-approved operational dashboard report as a dict.
    Only protocol-sanctioned fields are included, per service_health_protocol.md.
    Args:
        dashboard (ServiceHealthDashboard): The target dashboard instance
    Returns:
        dict: A dictionary containing only protocol-approved report fields.
    """
    # Assume dashboard has a method to fetch report data; adapt per real implementation.
    raw_report = dashboard.get_report_data()  # This should be protocol-compliant structure

    # Only keep protocol-approved fields
    report = {k: v for k, v in raw_report.items() if k in PROTOCOL_APPROVED_REPORT_FIELDS}

    # (Optionally pad missing, but required, protocol fields with None)
    for required_field in PROTOCOL_APPROVED_REPORT_FIELDS:
        if required_field not in report:
            report[required_field] = None

    return report