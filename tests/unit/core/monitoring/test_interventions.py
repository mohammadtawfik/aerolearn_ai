import pytest
from app.core.monitoring.interventions import early_warning_indicator, recommend_resources, suggest_learning_path, notify_professor_at_risk_students

class DummyStudent:
    def __init__(self, student_id, name, needs=None):
        self.student_id = student_id
        self.name = name
        self.needs = needs or []

class DummyProfessor:
    def __init__(self, name):
        self.name = name
        self.last_at_risk_notification = None

class DummyProgressRecord:
    def __init__(self, student, completion_rate, risk_score=None):
        self.student = student
        self.completion_rate = completion_rate  # float 0.0 - 1.0
        self.risk_score = risk_score

class TestInterventionSuggestionSystem:

    def test_early_warning_indicators(self):
        """
        Test early warning logic for at-risk students.
        
        Rule for test: Any student with `completion_rate` < 0.3 is at risk.
        """
        students = [
            DummyStudent(1, "Ali"),
            DummyStudent(2, "Samar"),
            DummyStudent(3, "Fatima"),
        ]
        progress_records = [
            DummyProgressRecord(students[0], completion_rate=0.2),
            DummyProgressRecord(students[1], completion_rate=0.8),
            DummyProgressRecord(students[2], completion_rate=0.25),
        ]
        at_risk = early_warning_indicator(progress_records)
        # Should find Ali and Fatima as at risk
        at_risk_ids = {s.student_id for s in at_risk}
        assert at_risk_ids == {1, 3}, f"Expected students 1 and 3 at risk, got {at_risk_ids}"

    def test_targeted_resource_recommendations(self):
        """
        Test resource recommendation logic.
        
        Test rule: If analytics shows 'topic_math' is 'low', recommend 'resource_math1'.
        If student has 'math' in needs, also recommend 'resource_math_advanced'.
        """
        # Test case 1: Student with math needs and low math score
        student1 = DummyStudent(10, "Sara", needs=['math'])
        analytics1 = {'topic_math': 'low', 'topic_science': 'high'}
        recs1 = recommend_resources(student1, analytics1)
        assert 'resource_math1' in recs1, f"Expected 'resource_math1' in recommendations, got {recs1}"
        assert 'resource_math_advanced' in recs1, f"Expected 'resource_math_advanced' for student with math needs, got {recs1}"
        
        # Test case 2: Student without math needs but low math score
        student2 = DummyStudent(11, "Omar")
        analytics2 = {'topic_math': 'low', 'topic_science': 'medium'}
        recs2 = recommend_resources(student2, analytics2)
        assert 'resource_math1' in recs2, f"Expected 'resource_math1' in recommendations, got {recs2}"
        assert 'resource_math_advanced' not in recs2, f"Did not expect 'resource_math_advanced' for student without math needs, got {recs2}"
        
        # Test case 3: Student with math needs but good math score
        student3 = DummyStudent(12, "Leila", needs=['math'])
        analytics3 = {'topic_math': 'high', 'topic_science': 'low'}
        recs3 = recommend_resources(student3, analytics3)
        assert 'resource_math1' not in recs3, f"Did not expect 'resource_math1' for high math score, got {recs3}"
        assert 'resource_science1' in recs3, f"Expected 'resource_science1' for low science score, got {recs3}"

    def test_personalized_learning_path_suggestions(self):
        """
        Test generation of personalized learning paths.

        Rule for test:
        - For each objective 'math' or 'science', the system suggests 'lesson_math1' or 'lesson_science1', etc.
        - Returns them in the order objectives are provided.
        """
        student = DummyStudent(20, "Zayd")
        objectives = ["math", "science"]
        path = suggest_learning_path(student, objectives)
        assert path == ["lesson_math1", "lesson_science1"], f"Expected ordered learning path for objectives, got {path}"

    def test_professor_notifications_for_at_risk(self):
        """Test at-risk notification triggers."""
        professor = DummyProfessor("Dr. Yaqub")
        students_at_risk = [
            {"id": 1, "name": "Zayd", "risk_level": "high"},
            {"id": 2, "name": "Layla", "risk_level": "medium"},
        ]

        # Call the notification logic
        result = notify_professor_at_risk_students(professor, students_at_risk)

        assert result is True, "Expected notify_professor_at_risk_students to return True"
        assert professor.last_at_risk_notification == students_at_risk, (
            f"Professor should be notified with the at-risk student data, got {professor.last_at_risk_notification}"
        )
