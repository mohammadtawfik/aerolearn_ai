"""
File: manual_grading.py
Location: /app/core/assessment/
Purpose: Manual grading API for professors (rubric/scoring, annotation, batch grading support),
           fulfilling manual grading task in the Day 17 Plan.
         Service-layer ManualGradingService for assignment and grading integration, enabling orchestration
         and correct imports from tests/integration/test_assessment_engine_day17.py.
"""

from typing import List, Dict, Optional, Any, Tuple
from app.models.assessment import Answer, Rubric, ManualGrade, Submission, ManualGradingAssignment  # ALL correct imports
from app.models.user import User

class ManualGradingInterface:
    def view_submission(self, submission: Submission) -> Dict[str, Any]:
        return {
            "id": submission.id,
            "user_id": submission.user_id,
            "answers": submission.answers,
            "attachments": getattr(submission, 'attachments', []),
            "timestamp": submission.timestamp
        }

    def apply_rubric(self, answer: Answer, rubric: Rubric) -> ManualGrade:
        grade = 0.0
        details = {}
        for criterion in rubric.criteria:
            score = rubric.criteria[criterion].get('score', 0)
            details[criterion] = {
                'score': score,
                'comment': rubric.criteria[criterion].get('comment', '')
            }
            grade += score
        max_score = sum(r['score'] for r in rubric.criteria.values())
        percent = grade / max_score if max_score else 0.0
        return ManualGrade(score=grade, max_score=max_score, percent=percent, details=details)

    def annotate(self, answer: Answer, annotation: str) -> None:
        if not hasattr(answer, 'annotations'):
            answer.annotations = []
        answer.annotations.append(annotation)

    def batch_grade(self, submissions: List[Submission], rubric: Rubric) -> List[ManualGrade]:
        grades = []
        for submission in submissions:
            for answer in submission.answers.values():
                grades.append(self.apply_rubric(answer, rubric))
        return grades


class ManualGradingService:
    """
    Service-layer class for managing manual grading workflow:
    - Assigning submissions to professors for grading
    - Grading individual answers with a rubric (returns grade, feedback)
    - Handling batch grading
    - Notifying or recording graded assignments/feedback
    This enables test_assessment_engine_day17 and fits architecture pattern for Engines/Services.
    """
    _grading_interface = ManualGradingInterface()
    
    # In a real app this could be persisted or event-driven; here just in-memory tracking.
    _assignments: List[ManualGradingAssignment] = []

    @classmethod
    def assign(cls, assignment: ManualGradingAssignment) -> None:
        """
        Assign a manual grading task (assignment) to an assessor/professor.
        """
        cls._assignments.append(assignment)
        # In production, fire an event or log assignment.

    @classmethod
    def grade(cls, assignment: ManualGradingAssignment, answer: Any, rubric: Rubric) -> Tuple[float, str]:
        """
        Professor grades a student's answer using a rubric.
        Returns (score, feedback_text).
        """
        manual_grade = cls._grading_interface.apply_rubric(answer, rubric)
        feedback = cls._generate_feedback(answer, manual_grade)
        # In a real system, this would update DB and notify the user, possibly trigger further events.
        return manual_grade.score, feedback

    @classmethod
    def batch_grade(cls, assignments: List[ManualGradingAssignment], rubric: Rubric) -> List[Tuple[float, str]]:
        """
        Grade a batch of assignments.
        """
        results = []
        for assignment in assignments:
            for answer in assignment.session.answers.values():
                score, fb = cls.grade(assignment, answer, rubric)
                results.append((score, fb))
        return results

    @staticmethod
    def _generate_feedback(answer: Any, manual_grade: ManualGrade) -> str:
        """
        Simple feedback generator for demonstration.
        """
        # Customize based on grade, comments, or criteria
        feedback = f"Score: {manual_grade.score}/{manual_grade.max_score}. "
        if hasattr(answer, "text"):
            feedback += f"Answer Summary: {getattr(answer, 'text', '')[:40]}"
        # Aggregate criteria comments
        comments = [d.get("comment", "") for d in manual_grade.details.values() if d.get("comment")]
        if comments:
            feedback += " " + "; ".join(comments)
        return feedback
