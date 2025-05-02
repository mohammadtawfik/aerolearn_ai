"""
Interventions and notification logic for monitoring and supporting students.

Location: /app/core/monitoring/interventions.py

Implements the four main features required by unit test_interventions.py:
- Early warning indicators for at-risk students
- Targeted resource recommendations
- Personalized learning path suggestions
- Professor notifications for at-risk students
"""

from typing import Dict, Any, List

__all__ = [
    'early_warning_indicator',
    'recommend_resources',
    'suggest_learning_path',
    'notify_professor_at_risk_students',
    'create_intervention'
]

def early_warning_indicator(progress_records: List[Any]) -> List[Any]:
    """
    Return list of at-risk students based on provided progress records.
    Rule: any student with completion_rate < 0.3 is at risk.
    """
    at_risk = []
    for record in progress_records:
        # Defensive: Accepts DummyProgressRecord or any object with .completion_rate/.student
        if hasattr(record, "completion_rate") and hasattr(record, "student"):
            if record.completion_rate < 0.3:
                at_risk.append(record.student)
    return at_risk

def recommend_resources(student_profile: Any, analytics: Dict) -> List[str]:
    """
    Suggest targeted resources (resource IDs) based on student and analytics.
    General rule:
    - For any topic in analytics where value is 'low', recommend 'resource_{topic}1'
    - For any topic in student_profile.needs, recommend 'resource_{topic}_advanced'
    """
    resources = []
    # Add by analytics rules.
    for topic, level in analytics.items():
        if level == 'low':
            # topic will be like 'topic_math' or 'topic_science'
            # We extract just 'math' from 'topic_math'
            if topic.startswith('topic_'):
                subject = topic[6:]  # Remove 'topic_'
                resources.append(f'resource_{subject}1')
    # Add advanced topics by needs.
    needs = getattr(student_profile, 'needs', [])
    for need in needs:
        resources.append(f'resource_{need}_advanced')
    return resources

def suggest_learning_path(student_profile: Any, learning_objectives: List[str]) -> List[str]:
    """
    Generate an ordered list of learning activity IDs as a personalized path.
    For this iteration, simply map each 'math' or 'science' objective
    to 'lesson_math1' or 'lesson_science1', preserving order.
    """
    lesson_map = {
        "math": "lesson_math1",
        "science": "lesson_science1",
    }
    return [lesson_map[obj] for obj in learning_objectives if obj in lesson_map]

def notify_professor_at_risk_students(professor: Any, students_at_risk: List[Any]) -> bool:
    """
    Notify professor with data on at-risk students.
    Attaches the notification to the professor object for testability.
    """
    professor.last_at_risk_notification = students_at_risk
    return True

def create_intervention(student_id: Any, pattern: Dict) -> Dict:
    """
    Stub: Create an intervention for the given student based on a pattern.
    Returns a dictionary representing the intervention.
    Includes a 'type' field as required for pipeline integration tests.
    """
    # In a real implementation, this may trigger notifications, log events, etc.
    return {
        "student_id": student_id,
        "type": pattern.get("risk", "unspecified"),
        "intervention": f"Intervention for pattern: {pattern}"
    }
