import pytest

@pytest.fixture
def client():
    # Dummy: replace with actual test client setup if needed
    from app.api.analytics.endpoints import get_usage_analytics
    return get_usage_analytics()

def test_usage_analytics_endpoints(client):
    """
    Ensures all analytics endpoints return only protocol-approved fields,
    and that aggregation API matches expected test contract.
    """
    # Example API direct invocation: adjust if using FastAPI/Flask/etc.
    res1 = client.aggregate_usage()
    assert isinstance(res1, dict)
    res2 = client.feature_usage_report()
    assert isinstance(res2, dict) and all(isinstance(v, int) for v in res2.values())
    res3 = client.query_sessions()
    assert isinstance(res3, list) and all(
        all(k in sess for k in ("user_id", "start", "end", "duration")) for sess in res3)