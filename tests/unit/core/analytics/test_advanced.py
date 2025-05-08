import pytest

# In test-driven development, this test defines the expectation for the UsageAnalytics class API.
# It is based on the contract in /docs/architecture/health_monitoring_protocol.md:
#   - Method: track_activity(user, event: str, feature: str, timestamp: int)

@pytest.fixture
def analytics():
    # We will implement UsageAnalytics in /app/core/analytics/advanced.py
    from app.core.analytics.advanced import UsageAnalytics
    # Use a fresh instance for each test, as required by TDD discipline/documentation.
    return UsageAnalytics()

def test_track_activity_records_event(analytics):
    """
    Test that track_activity correctly records an event using protocol-compliant fields.
    """
    user_id = "user123"
    event = "login"
    feature = "dashboard"
    timestamp = 1717690000
    analytics.track_activity(user_id, event, feature, timestamp)
    activities = analytics.query_activities(user_id)
    # The documented activity fields in protocol: user_id, event, feature, timestamp
    assert len(activities) == 1
    activity = activities[0]
    assert activity["user_id"] == user_id
    assert activity["event"] == event
    assert activity["feature"] == feature
    assert activity["timestamp"] == timestamp

def test_aggregate_usage_protocol_compliance(analytics):
    """
    Tests that UsageAnalytics.aggregate_usage returns usage aggregates
    per the health_monitoring_protocol.md contract.
    """
    # Simulate some activity for 2 users, different features/events
    analytics.track_activity("user1", "login", "dashboard", 1717700000)
    analytics.track_activity("user1", "view", "course", 1717700020)
    analytics.track_activity("user2", "login", "dashboard", 1717700040)
    analytics.track_activity("user1", "edit", "dashboard", 1717700100)
    
    # Protocol: aggregate_usage(user_id=None) -> Dict summary for all users
    agg = analytics.aggregate_usage()
    
    # The actual fields in the return value aren't exhaustively specified in protocol,
    # but meaningful aggregation (total count, per-user/feature counts, etc.) is expected.
    assert isinstance(agg, dict)
    
    # Top-level: per-user or global stats must exist
    assert "user1" in agg and "user2" in agg
    
    # Each user summary must include counts of events and features (protocol-driven)
    for user in ("user1", "user2"):
        user_stats = agg[user]
        assert isinstance(user_stats, dict)
        assert "total_events" in user_stats
        assert "features" in user_stats
        assert isinstance(user_stats["features"], dict)
    
    # user1 did 3 events, user2 did 1
    assert agg["user1"]["total_events"] == 3
    assert agg["user2"]["total_events"] == 1
    
    # Features/activity mapping
    assert agg["user1"]["features"]["dashboard"] == 2
    assert agg["user1"]["features"]["course"] == 1
    assert agg["user2"]["features"]["dashboard"] == 1

    # Also test aggregate_usage(user_id)
    u1 = analytics.aggregate_usage("user1")
    assert u1["total_events"] == 3
    assert u1["features"]["dashboard"] == 2
    assert u1["features"]["course"] == 1

def test_clear_removes_all_data(analytics):
    """
    After calling clear(), all analytics activities and sessions are wiped.
    """
    # Add some test data
    analytics.track_activity("user1", "login", "dashboard", 1717700000)
    analytics.track_activity("user2", "view", "course", 1717700100)
    
    # Verify data exists
    assert len(analytics.query_activities()) > 0
    
    # Clear all data
    analytics.clear()
    
    # Verify all data has been removed
    assert analytics.query_activities() == []
    
    # Verify aggregation returns empty results
    agg = analytics.aggregate_usage()
    assert isinstance(agg, dict)
    assert len(agg) == 0
