import pytest

from app.core.ai.cross_course_recommendation import CrossCourseRecommendationEngine

@pytest.fixture
def reco_engine():
    return CrossCourseRecommendationEngine()

def test_aggregate_cross_course_data(reco_engine):
    student_id = "student001"
    course_ids = ["c1", "c2"]
    data = reco_engine.aggregate_cross_course_data(student_id, course_ids)
    assert isinstance(data, dict)

def test_generate_cross_course_recommendations(reco_engine):
    student_id = "student001"
    course_ids = ["c1", "c2"]
    recos = reco_engine.generate_cross_course_recommendations(student_id, course_ids)
    assert isinstance(recos, list)
    for item in recos:
        # protocol fields: content_id, course_id, title, justification, source, score, timestamp
        assert "content_id" in item
        assert "course_id" in item

def test_cross_reference_related_content(reco_engine):
    content_id = "contentX"
    res = reco_engine.cross_reference_related_content(content_id)
    assert isinstance(res, list)
    for related in res:
        assert "content_id" in related
        assert "course_id" in related
        assert "similarity_score" in related
        assert "link_reason" in related

def test_suggest_curriculum_optimizations(reco_engine):
    curriculum_id = "curr123"
    out = reco_engine.suggest_curriculum_optimizations(curriculum_id)
    assert isinstance(out, dict)
    assert "curriculum_id" in out
    assert "issues_found" in out
    assert "optimizations" in out
    assert "timestamp" in out

def test_clear(reco_engine):
    reco_engine.clear()
    # Should empty engine state or caches