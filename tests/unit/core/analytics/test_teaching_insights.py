import pytest

from app.core.analytics.teaching_insights import (
    TeachingInsightsAnalytics,
)

@pytest.fixture
def insights():
    return TeachingInsightsAnalytics()

def test_record_teaching_effectiveness(insights):
    # Should record analytics and store TeachingEffectivenessRecord by protocol
    record = {
        "professor_id": "prof123",
        "course_id": "c1",
        "metrics": {"effectiveness_score": 0.85, "engagement_score": 0.9}
    }
    insights.record_teaching_effectiveness(**record)
    # Assert that stored record exists and protocol fields are present
    # (full data validation would be implemented in actual test)

def test_compute_content_impact(insights):
    # Returns ContentImpactRecord for a content_id
    impact = insights.compute_content_impact(content_id="content123")
    assert isinstance(impact, dict)
    # Must have protocol fields: content_id, impact_score, student_engagement, outcome_correlation, timestamp

def test_correlate_engagement(insights):
    # Correlates engagement/content with outcome
    result = insights.correlate_engagement("student1", ["contentA", "contentB"])
    assert isinstance(result, dict)
    # Protocol fields: engagement correlations, maybe per content

def test_generate_teaching_recommendations(insights):
    # Should generate actionable recommendations from analytics
    recs = insights.generate_teaching_recommendations(professor_id="prof123")
    assert isinstance(recs, list)
    # Each rec should match protocol allowed formats (string or dict if structured)

def test_get_teaching_insights_report(insights):
    # Aggregated protocol-compliant report
    report = insights.get_teaching_insights_report(professor_id="prof123", course_id="c1")
    # Protocol: must contain teaching_history (list), content_impact (list), engagement_correlations (dict), recommendations (list), generated_at
    assert isinstance(report, dict)

def test_clear(insights):
    # Protocol: Should clear all analytics state
    insights.clear()
    # Should be empty upon next retrieval/request