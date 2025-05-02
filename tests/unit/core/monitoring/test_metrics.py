import pytest
from datetime import timedelta

from app.core.monitoring.metrics import (
    track_learning_objective,
    monitor_time_on_task,
    calculate_completion_rate,
    analyze_performance_trends
)

class TestProgressTrackingMetrics:

    def test_learning_objective_achievement(self):
        """Test achievement tracking for learning objectives."""
        activities = [
            {"user_id": "u1", "objective_id": "obj1", "completed": True},
            {"user_id": "u1", "objective_id": "obj1", "completed": False},
            {"user_id": "u1", "objective_id": "obj1", "completed": True},
            {"user_id": "u1", "objective_id": "obj2", "completed": True},
            {"user_id": "u2", "objective_id": "obj1", "completed": True},
        ]
        # For u1/obj1: 2 completed of 3 total activities
        result = track_learning_objective("u1", "obj1", activities)
        assert abs(result - 2/3) < 1e-8

        # For u1/obj2: 1 completed of 1
        result = track_learning_objective("u1", "obj2", activities)
        assert result == 1.0

        # For u2/obj1: 1 completed of 1
        result = track_learning_objective("u2", "obj1", activities)
        assert result == 1.0

        # For missing user/obj, should be 0.0
        result = track_learning_objective("u1", "doesnotexist", activities)
        assert result == 0.0

    def test_time_on_task_monitoring(self):
        """Test time-on-task monitoring accuracy."""
        logs = [
            {
                "user_id": "u1",
                "start": "2024-06-14T09:00:00",
                "end": "2024-06-14T10:00:00",
            },
            {
                "user_id": "u1",
                "start": "2024-06-14T11:00:00",
                "end": "2024-06-14T11:30:00",
            },
            {
                "user_id": "u1",
                "start": "2024-06-14T12:00:00",
                "end": "2024-06-14T12:20:00",
            },
            {
                "user_id": "u2",
                "start": "2024-06-14T09:00:00",
                "end": "2024-06-14T11:00:00"
            },
            # Invalid/missing data should be ignored:
            {"user_id": "u1", "start": "bad", "end": "data"},
            {"user_id": "u1", }
        ]
        res = monitor_time_on_task("u1", logs)
        expected_seconds = 60*60 + 30*60 + 20*60  # 1h + 30m + 20m
        assert res.total_seconds() == expected_seconds

        # Different user: only 2h block
        res2 = monitor_time_on_task("u2", logs)
        assert res2.total_seconds() == 2 * 60 * 60

        # No logs for user
        res3 = monitor_time_on_task("nouser", logs)
        assert res3.total_seconds() == 0

    def test_completion_rate_analytics(self):
        """Test calculation of completion rates."""
        module_ids = ["m1", "m2", "m3"]
        completions = [
            {"user_id": "u1", "module_id": "m1", "completed": True},
            {"user_id": "u1", "module_id": "m2", "completed": True},
            {"user_id": "u1", "module_id": "m3", "completed": False},
            # Extra modules, not to be counted
            {"user_id": "u1", "module_id": "m4", "completed": True},
            # Different user
            {"user_id": "u2", "module_id": "m1", "completed": True}
        ]
        res = calculate_completion_rate("u1", module_ids, completions)
        assert abs(res - 2/3) < 1e-8

        res2 = calculate_completion_rate("u2", module_ids, completions)
        assert abs(res2 - 1/3) < 1e-8

        # No completions
        empty = calculate_completion_rate("nouser", module_ids, [])
        assert empty == 0.0

        # No modules
        assert calculate_completion_rate("u1", [], completions) == 0.0

    def test_performance_trend_analysis(self):
        """Test extraction of student performance trends."""
        hist = [
            {"user_id": "u1", "score": 50, "timestamp": "2024-06-10T09:00:00"},
            {"user_id": "u1", "score": 60, "timestamp": "2024-06-11T09:00:00"},
            {"user_id": "u1", "score": 70, "timestamp": "2024-06-12T09:00:00"},
            {"user_id": "u1", "score": 80, "timestamp": "2024-06-13T09:00:00"},
            {"user_id": "u1", "score": 85, "timestamp": "2024-06-14T09:00:00"},
            # u2, for test
            {"user_id": "u2", "score": 100, "timestamp": "2024-06-10T09:00:00"}
        ]
        out = analyze_performance_trends("u1", hist)
        assert out["trend"] == "improving"
        assert isinstance(out["details"]["first_half_mean"], float)
        assert isinstance(out["details"]["second_half_mean"], float)
        assert len(out["details"]["scores"]) == 5

        # Decline
        hist2 = [
            {"user_id": "u1", "score": 100, "timestamp": "2024-06-10T09:00:00"},
            {"user_id": "u1", "score": 75, "timestamp": "2024-06-13T09:00:00"},
        ]
        out2 = analyze_performance_trends("u1", hist2)
        assert out2["trend"] == "declining"

        # Stable
        hist3 = [
            {"user_id": "u1", "score": 60, "timestamp": "2024-06-10T09:00:00"},
            {"user_id": "u1", "score": 60, "timestamp": "2024-06-13T09:00:00"},
        ]
        out3 = analyze_performance_trends("u1", hist3)
        assert out3["trend"] == "stable"
        
        # Not enough data
        hist4 = [{"user_id": "u1", "score": 60, "timestamp": "2024-06-10T09:00:00"}]
        out4 = analyze_performance_trends("u1", hist4)
        assert out4["trend"] == "insufficient data"


class TestPerformanceMetricsCalculation:

    def test_assessment_performance_analytics(self):
        """Test analytics on assessment performance."""
        # Simulate assessment records: user, assessment_id, max_score, score, timestamp
        input_records = [
            {"user_id": "u1", "assessment_id": "a1", "score": 90, "max_score": 100, "timestamp": "2024-06-10T09:00:00"},
            {"user_id": "u1", "assessment_id": "a2", "score": 80, "max_score": 100, "timestamp": "2024-06-12T09:00:00"},
            {"user_id": "u1", "assessment_id": "a1", "score": 80, "max_score": 100, "timestamp": "2024-06-15T09:00:00"},
            {"user_id": "u1", "assessment_id": "a2", "score": 94, "max_score": 100, "timestamp": "2024-06-18T09:00:00"},
            {"user_id": "u2", "assessment_id": "a1", "score": 75, "max_score": 100, "timestamp": "2024-06-11T09:00:00"},
        ]
        
        from app.core.monitoring.metrics import assessment_performance_analytics
        output = assessment_performance_analytics("u1", input_records)

        expected_scores = [90, 80, 80, 94]
        expected_mean = sum(expected_scores) / len(expected_scores)
        assert abs(output["mean"] - expected_mean) < 1e-8
        assert output["min"] == min(expected_scores)
        assert output["max"] == max(expected_scores)
        assert output["count"] == len(expected_scores)

    def test_engagement_scoring_system(self):
        """Test generation of engagement scores."""
        # Simulate interactions with various weights
        interactions = [
            {"user_id": "u1", "interaction_type": "view", "count": 30},
            {"user_id": "u1", "interaction_type": "submit_quiz", "count": 5},
            {"user_id": "u1", "interaction_type": "post_forum", "count": 2},
        ]
        # Let's assume view=1pt, submit_quiz=5pt, post_forum=2pt
        from app.core.monitoring.metrics import engagement_score
        res = engagement_score("u1", interactions)
        expected = 30*1 + 5*5 + 2*2
        assert res == expected

        # Unknown type should default to 0 pts.
        interactions2 = [{"user_id": "u1", "interaction_type": "unknown", "count": 3}]
        assert engagement_score("u1", interactions2) == 0

    def test_competency_mapping(self):
        """Test competency mapping logic."""
        # Suppose each assessment maps to a competency and a threshhold.
        assessments = [
            {"user_id": "u1", "assessment_id": "a1", "score": 80, "competency_id": "c1", "threshold": 75},
            {"user_id": "u1", "assessment_id": "a2", "score": 50, "competency_id": "c2", "threshold": 60},
            {"user_id": "u1", "assessment_id": "a3", "score": 85, "competency_id": "c1", "threshold": 75},
        ]
        # Target: Should return set/list of competencies achieved
        from app.core.monitoring.metrics import competency_mapping
        res = competency_mapping("u1", assessments)
        assert set(res) == {"c1"}
        # c2 not achieved (score < threshold)

    def test_comparative_cohort_analytics(self):
        """Test cohort comparison metrics."""
        # Simulate user-level progress records
        group = [
            {"user_id": "u1", "progress": 0.8},
            {"user_id": "u2", "progress": 0.75},
            {"user_id": "u3", "progress": 0.9},
        ]
        group2 = [
            {"user_id": "u4", "progress": 0.2},
            {"user_id": "u5", "progress": 0.4},
            {"user_id": "u6", "progress": 0.3},
        ]
        from app.core.monitoring.metrics import comparative_cohort_analytics
        out = comparative_cohort_analytics(group, group2)
        assert abs(out["mean_1"] - (0.8+0.75+0.9)/3) < 1e-8
        assert abs(out["mean_2"] - (0.2+0.4+0.3)/3) < 1e-8
        # Cohort 1 should be marked 'higher'
        assert out["cohort_higher"] == 1
        # Swap means, cohort 2 is higher:
        swap = comparative_cohort_analytics(group2, group)
        assert swap["cohort_higher"] == 2
