from app.core.analytics.advanced import UsageAnalytics

# Singleton instance for simple in-memory implementation (doc/protocol)
_usage_analytics = UsageAnalytics()

def aggregate_usage():
    return _usage_analytics.aggregate_usage()

def feature_usage_report():
    return _usage_analytics.feature_usage_report()

def query_sessions():
    return _usage_analytics.query_sessions()

def get_usage_analytics():
    """
    For integration/TDD test harness: returns the singleton UsageAnalytics instance
    allowing the test to interact with analytics directly.
    """
    return _usage_analytics

# ...extend with more endpoints or input handlers per future protocol/test changes.
# This minimal version ensures each endpoint exposes only protocol-approved fields and structures.
