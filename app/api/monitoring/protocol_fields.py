"""
Protocol-approved fields for dashboard/reporting API responses.
Derived from: /docs/architecture/service_health_protocol.md §Reporting Fields.
Update this list in sync with the protocol document.
"""

PROTOCOL_APPROVED_REPORT_FIELDS = [
    "component",
    "state",
    "timestamp",
    "metrics",
    "reason",
    # Add additional protocol-sanctioned fields as per the protocol doc.
]