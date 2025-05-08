import pytest

from app.core.ai.cross_course_recommendation import CrossCourseRecommendationEngine

@pytest.fixture
def reco_engine():
    return CrossCourseRecommendationEngine()

def test_full_cross_course_workflow(reco_engine):
    # Aggregate, recommend, cross-reference, optimize curriculum across boundaries
    sid = "studentABC"
    cids = ["c10", "c11"]
    reco_engine.aggregate_cross_course_data(sid, cids)
    recos = reco_engine.generate_cross_course_recommendations(sid, cids)
    # Should cover end-to-end, field cross-consistency

def test_cross_reference_and_optimization(reco_engine):
    # Cross-ref related content, then run curriculum optimization flow
    content_id = "contentY"
    reco_engine.cross_reference_related_content(content_id, scope=["c10", "c11"])
    reco_engine.suggest_curriculum_optimizations("curr555")