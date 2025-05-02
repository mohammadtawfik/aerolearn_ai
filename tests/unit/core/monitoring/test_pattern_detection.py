import pytest

from app.core.monitoring.pattern_detection import (
    detect_activity_sequences,
    detect_resource_utilization,
    infer_study_habits,
    classify_learning_style
)

class TestLearningPatternDetection:

    def test_activity_sequence_analysis(self):
        """Test activity sequencing detection."""
        activity_log = [
            {"user_id": "u1", "timestamp": 1, "activity": "read_content"},
            {"user_id": "u1", "timestamp": 2, "activity": "watch_video"},
            {"user_id": "u1", "timestamp": 3, "activity": "take_quiz"},
            {"user_id": "u1", "timestamp": 4, "activity": "read_content"},
            {"user_id": "u1", "timestamp": 5, "activity": "watch_video"},
        ]
        result = detect_activity_sequences(activity_log)
        
        # Should recognize 'read_content' → 'watch_video' as a frequent sequence
        assert ("read_content", "watch_video") in result["frequent_sequences"]
        assert result["frequent_sequences"][("read_content", "watch_video")] == 2

    def test_resource_utilization_patterns(self):
        """Test detection of resource usage patterns."""
        resource_log = [
            {"user_id": "u2", "resource_type": "video", "engaged": True},
            {"user_id": "u2", "resource_type": "video", "engaged": True},
            {"user_id": "u2", "resource_type": "document", "engaged": True},
            {"user_id": "u2", "resource_type": "quiz", "engaged": False},
        ]
        result = detect_resource_utilization(resource_log)
        
        # Should spot video as most engaged resource
        assert result["most_used_resource"] == "video"
        assert result["usage_counts"]["video"] == 2
        assert result["usage_counts"]["document"] == 1
        assert result["usage_counts"]["quiz"] == 0

    def test_study_habit_identification(self):
        """Test study habit detection."""
        study_sessions = [
            {"user_id": "u3", "start_time": 100, "end_time": 130},  # 30 min
            {"user_id": "u3", "start_time": 200, "end_time": 230},  # 30 min
            {"user_id": "u3", "start_time": 300, "end_time": 330},  # 30 min
        ]
        result = infer_study_habits(study_sessions)
        
        # Consistent short sessions = steady study, not cramming
        assert result["habit"] == "steady"
        
        cramming_sessions = [
            {"user_id": "u3", "start_time": 400, "end_time": 700},  # long session
        ]
        result2 = infer_study_habits(cramming_sessions)
        assert result2["habit"] == "cramming"

    def test_learning_style_classification(self):
        """Test learning style classification logic."""
        activities = [
            {"user_id": "u4", "activity": "watch_video"},
            {"user_id": "u4", "activity": "watch_video"},
            {"user_id": "u4", "activity": "read_content"},
            {"user_id": "u4", "activity": "take_quiz"},
        ]
        result = classify_learning_style(activities)
        
        # Should classify user as "visual" (favoring videos)
        assert result["classifier"] == "visual"
        
        # Test with different activity pattern
        activities2 = [
            {"user_id": "u4", "activity": "read_content"},
            {"user_id": "u4", "activity": "read_content"},
            {"user_id": "u4", "activity": "take_quiz"},
        ]
        result2 = classify_learning_style(activities2)
        assert result2["classifier"] == "reading"
