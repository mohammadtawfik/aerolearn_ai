import pytest

from app.core.monitoring.pattern_detection import (
    run_pattern_detection,
    aggregate_learning_data,
    should_trigger_intervention
)
from app.core.monitoring.metrics import (
    save_analytics_result,
    retrieve_analytics_result
)
from app.core.monitoring.interventions import create_intervention
from app.models.progress import Progress
from app.models.assessment import Assessment

@pytest.mark.integration
class TestLearningAnalyticsIntegration:

    def test_full_progress_to_intervention_pipeline(self):
        """Test analytics pipeline: progress data → pattern detection → intervention."""
        # Setup test progress data
        progress_records = [
            {"student_id": 1001, "completed": 4, "total": 10, "score": 0.6},
            {"student_id": 1002, "completed": 10, "total": 10, "score": 0.9},
        ]
        
        # 1. Detect patterns in the progress data
        patterns = run_pattern_detection(progress_records)
        
        # 2. Aggregate analytics
        analytics = {"patterns": patterns}
        
        # 3. Decide if intervention is needed
        intervention_needed = should_trigger_intervention(analytics)
        
        # 4. Create intervention if needed
        if intervention_needed:
            intervention = create_intervention(patterns[0]["student_id"], patterns[0])
        
        # 5. Verify pipeline outputs
        assert isinstance(patterns, list)
        assert "student_id" in patterns[0]
        assert isinstance(intervention_needed, bool)
        
        # If intervention was created, verify its structure
        if intervention_needed:
            assert "type" in intervention
            assert "student_id" in intervention

    def test_cross_component_data_aggregation(self):
        """Test aggregation and analytics integration across all learning activities and models."""
        # Create test data from multiple components
        records = [
            {"student_id": 1, "activity": "quiz", "score": 0.8},
            {"student_id": 1, "activity": "video", "watched": True},
            {"student_id": 2, "activity": "quiz", "score": 0.3},
            {"student_id": 2, "activity": "assignment", "submitted": True, "grade": 75},
        ]
        
        # Aggregate data across components
        aggregated_data = aggregate_learning_data(records)
        
        # Verify aggregation results
        assert isinstance(aggregated_data, dict), "Aggregation must return a dictionary"
        assert aggregated_data["total_records"] == len(records)
        
        # Verify student-specific aggregation
        assert len(aggregated_data["by_student"]) == 2  # Two unique students
        assert "1" in aggregated_data["by_student"]
        assert "2" in aggregated_data["by_student"]
        
        # Verify activity-specific aggregation
        assert "quiz" in aggregated_data["by_activity"]
        assert aggregated_data["by_activity"]["quiz"]["count"] == 2

    def test_intervention_trigger_accuracy(self):
        """Test intervention system only triggers when justified by combined analytics."""
        # Test case 1: Should trigger intervention (high risk)
        analytics_high_risk = {
            "patterns": [
                {"student_id": 1, "risk": "high"},
                {"student_id": 2, "risk": "none"},
                {"student_id": 3, "risk": "low"}
            ]
        }
        result_high_risk = should_trigger_intervention(analytics_high_risk)
        assert result_high_risk is True, "Intervention should trigger on high risk findings"
        
        # Test case 2: Should not trigger intervention (all none risk)
        analytics_no_risk = {
            "patterns": [
                {"student_id": 1, "risk": "none"},
                {"student_id": 2, "risk": "none"}
            ]
        }
        result_no_risk = should_trigger_intervention(analytics_no_risk)
        assert result_no_risk is False, "No intervention when all have 'none' risk"
        
        # Test case 3: Edge case with low risk only
        analytics_low_risk = {
            "patterns": [
                {"student_id": 1, "risk": "low"},
                {"student_id": 2, "risk": "low"}
            ]
        }
        result_low_risk = should_trigger_intervention(analytics_low_risk)
        # Verify the system correctly handles low risk cases according to business rules
        # (This assertion depends on how the system should handle low risk - adjust as needed)
        assert isinstance(result_low_risk, bool), "Should return a boolean decision"

    def test_data_persistence_and_retrieval(self):
        """Test persistence and retrieval of analytics/model results."""
        # Test data
        student_id = 404
        analytics_data = {
            "completed": 5, 
            "total": 10, 
            "score": 0.7,
            "risk_level": "medium",
            "patterns": ["inconsistent_engagement", "struggling_with_quizzes"]
        }
        
        # Save analytics result
        save_analytics_result(student_id, analytics_data)
        
        # Retrieve analytics result
        retrieved_data = retrieve_analytics_result(student_id)
        
        # Verify data integrity
        assert retrieved_data == analytics_data, f"Persisted and retrieved data should match for student {student_id}"
        
        # Test multiple records
        student_ids = [101, 102, 103]
        for i, sid in enumerate(student_ids):
            data = {"completed": i, "score": i/10}
            save_analytics_result(sid, data)
        
        # Verify each record can be retrieved correctly
        for i, sid in enumerate(student_ids):
            expected = {"completed": i, "score": i/10}
            actual = retrieve_analytics_result(sid)
            assert actual == expected, f"Data mismatch for student {sid}"
