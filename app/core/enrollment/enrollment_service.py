"""
Location: /app/core/enrollment/enrollment_service.py

Handles all business logic and orchestration for course enrollment workflow.
"""

from app.models.course import Course, Enrollment, EnrollmentStatus
from typing import Optional, List
from datetime import datetime

class EnrollmentService:
    """
    Service class for managing course enrollments and enrollment requests.
    Uses in-memory store for illustration—replace with DB/session as needed.
    """

    def __init__(self, course_store=None, session=None, db_session=None):
        if db_session is not None and session is None:
            # Priority to db_session for backward compatibility
            self.session = db_session
        else:
            self.session = session            # SQLAlchemy session, assumed to be set for DB-backed ops
        self.course_store = course_store  # Dict[str, Course], keyed by course id (optional)

    def browse_courses(self) -> List[Course]:
        """
        Return all available courses.
        """
        if self.course_store is not None:
            return list(self.course_store.values())
        elif self.session:
            # DB query
            return self.session.query(Course).all()
        return []

    def search_courses(self, query: str) -> List[Course]:
        """
        Search courses by title/metadata.
        """
        if self.course_store is not None:
            return [
                course for course in self.course_store.values()
                if query.lower() in course.title.lower()
            ]
        elif self.session:
            return self.session.query(Course).filter(Course.title.ilike(f"%{query}%")).all()
        return []

    def request_enrollment(self, course_id: int, user_id: int) -> Optional[Enrollment]:
        if self.session:
            course = self.session.query(Course).filter_by(id=course_id).first()
            if not course:
                return None
            return course.request_enrollment(self.session, user_id)
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return None
            return course.request_enrollment(user_id)
        return None

    def approve_enrollment(self, course_id: int, user_id: int, approver_id: int) -> Optional[Enrollment]:
        if self.session:
            course = self.session.query(Course).filter_by(id=course_id).first()
            if not course:
                return None
            enrollment = course.approve_enrollment(self.session, user_id, approver_id)
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return None
            enrollment = course.approve_enrollment(user_id, approver_id)
        else:
            return None
            
        if enrollment:
            # Emit "enrollment_approved" event here if needed (see event bus in project)
            pass
        return enrollment

    def reject_enrollment(self, course_id: int, user_id: int, approver_id: int) -> Optional[Enrollment]:
        if self.session:
            course = self.session.query(Course).filter_by(id=course_id).first()
            if not course:
                return None
            enrollment = course.reject_enrollment(self.session, user_id, approver_id)
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return None
            enrollment = course.reject_enrollment(user_id, approver_id)
        else:
            return None
            
        if enrollment:
            # Emit "enrollment_rejected" event here if needed
            pass
        return enrollment

    def cancel_enrollment(self, course_id: int, user_id: int) -> Optional[Enrollment]:
        if self.session:
            course = self.session.query(Course).filter_by(id=course_id).first()
            if not course:
                return None
            from sqlalchemy import select
            enrollment_obj = self.session.execute(
                select(Enrollment).filter_by(user_id=user_id, course_id=course_id)
            ).scalar_one_or_none()
            if enrollment_obj:
                enrollment = course.cancel_enrollment(self.session, enrollment_obj.id, user_id)
            else:
                return None
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return None
            enrollment = course.cancel_enrollment(user_id)
        else:
            return None
            
        if enrollment:
            # Emit "enrollment_cancelled" event here if needed
            pass
        return enrollment

    def get_enrollment_status(self, course_id: int, user_id: int) -> Optional[EnrollmentStatus]:
        if self.session:
            course = self.session.query(Course).filter_by(id=course_id).first()
            if not course:
                return None
            status = course.enrollment_status(self.session, user_id)
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return None
            status = course.enrollment_status(user_id)
        else:
            return None
        return status if status else None

    def get_enrolled_students(self, course_id: int) -> List[int]:
        if self.session:
            # DB-side: get only approved enrollments
            enrollments = self.session.query(Enrollment).filter_by(
                course_id=course_id, status=EnrollmentStatus.APPROVED
            ).all()
            return [e.user_id for e in enrollments]
        elif self.course_store:
            course = self.course_store.get(str(course_id))
            if not course:
                return []
            return course.enrolled_students
        return []
