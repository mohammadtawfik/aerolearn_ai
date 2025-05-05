"""
Database Client for AeroLearn AI
Handles SQLAlchemy engine and session management.
Edit DB_URL in schema.py as required for different environments.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
import threading
from contextlib import contextmanager
from typing import List, Dict, Any

class DBClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_url):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBClient, cls).__new__(cls)
                cls._instance._initialize(db_url)
            return cls._instance

    def _initialize(self, db_url):
        # Set expire_on_commit=False to prevent DetachedInstanceError
        self.engine = create_engine(db_url, echo=False, future=True)
        self.SessionLocal = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False  # Prevents DetachedInstanceError
            )
        )

    def get_session(self):
        """
        Returns a new SQLAlchemy session.
        Remember to close() or use as context manager.
        """
        return self.SessionLocal()

    def dispose(self):
        self.engine.dispose()
        self.SessionLocal.remove()
        
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def get_by_id(self, model, object_id, eager_relations=None):
        """
        Get an object by its primary key ID.
        Optionally eagerly loads given relationship attributes, using loader options.

        Args:
            model: SQLAlchemy ORM class.
            object_id: ID (primary key) of object to fetch.
            eager_relations: (optional) list of SQLAlchemy loader options, e.g. [joinedload(Model.relationship)]
        """
        with self.session_scope() as session:
            query = session.query(model)
            if eager_relations:
                query = query.options(*eager_relations)
            return query.get(object_id)
            
    def add_object(self, obj):
        """Add a new object to the database."""
        with self.session_scope() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
            
    def update_object(self, obj):
        """Update an existing object in the database."""
        with self.session_scope() as session:
            session.merge(obj)
            session.commit()
            return obj
            
    def delete_object(self, obj):
        """Delete an object from the database."""
        with self.session_scope() as session:
            session.delete(obj)
            
    def search(self, model, **kwargs):
        """Search for objects matching the given criteria."""
        with self.session_scope() as session:
            return session.query(model).filter_by(**kwargs).all()
            
    def execute_query(self, query_func):
        """Execute a custom query function within a session context."""
        with self.session_scope() as session:
            return query_func(session)
            
    # --- Integration methods for student/course operations ---
    
    def list_courses(self) -> List[Dict[str, Any]]:
        """
        Returns a list of available courses.
        
        In production, this will query the Course model from the database.
        Currently implemented as a stub for TDD purposes.
        """
        try:
            with self.session_scope() as session:
                # TODO: Replace with real ORM query when Course model is available
                # return session.query(Course).all()
                return [
                    {"id": "course-1", "name": "Introduction to Aerodynamics", "description": "Learn the basics of flight"},
                    {"id": "course-2", "name": "Advanced Aeronautical Engineering", "description": "Deep dive into aircraft design"}
                ]
        except Exception:
            # Fallback for testing
            return [
                {"id": "course-1", "name": "Introduction to Aerodynamics", "description": "Learn the basics of flight"},
                {"id": "course-2", "name": "Advanced Aeronautical Engineering", "description": "Deep dive into aircraft design"}
            ]

    def list_course_content(self, course_id: str) -> List[Dict[str, Any]]:
        """
        Returns a list of content items for a specific course.
        
        Args:
            course_id: The unique identifier for the course
            
        Returns:
            List of content items (lessons, modules, etc.)
        """
        # Stub implementation for TDD
        content_map = {
            "course-1": [
                {"id": "lesson-1", "title": "Fundamentals of Flight", "type": "lesson"},
                {"id": "lesson-2", "title": "Forces and Motion", "type": "lesson"},
                {"id": "quiz-1", "title": "Basic Concepts Quiz", "type": "assessment"}
            ],
            "course-2": [
                {"id": "module-1", "title": "Supersonic Flight", "type": "module"},
                {"id": "lesson-3", "title": "Jet Propulsion", "type": "lesson"},
                {"id": "project-1", "title": "Aircraft Design Project", "type": "project"}
            ]
        }
        
        return content_map.get(course_id, [])

    def list_courses_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Returns the courses available or enrolled for a specific user.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            List of course objects the user has access to
        """
        try:
            with self.session_scope() as session:
                # TODO: Replace with real ORM query when models are available
                # return session.query(Course).join(Enrollment).filter(Enrollment.user_id == user_id).all()
                
                # For now, return all courses (stub implementation)
                return self.list_courses()
        except Exception:
            # Fallback for testing
            return self.list_courses()

    def enroll_in_course(self, user_id: str, course_id: str) -> bool:
        """
        Enrolls a user in a specific course.
        
        Args:
            user_id: The unique identifier for the user
            course_id: The unique identifier for the course
            
        Returns:
            True if enrollment was successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                # TODO: Replace with real ORM logic when models are available
                # enrollment = Enrollment(user_id=user_id, course_id=course_id)
                # session.add(enrollment)
                
                # Stub implementation for TDD
                print(f"Enrolled user {user_id} in course {course_id}")
                return True
        except Exception as e:
            print(f"Error enrolling user {user_id} in course {course_id}: {str(e)}")
            return False

    def unenroll_from_course(self, user_id: str, course_id: str) -> bool:
        """
        Removes a user's enrollment from a specific course.
        
        Args:
            user_id: The unique identifier for the user
            course_id: The unique identifier for the course
            
        Returns:
            True if unenrollment was successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                # TODO: Replace with real ORM logic when models are available
                # enrollment = session.query(Enrollment).filter_by(
                #     user_id=user_id, course_id=course_id
                # ).first()
                # if enrollment:
                #     session.delete(enrollment)
                #     return True
                # return False
                
                # Stub implementation for TDD
                print(f"Unenrolled user {user_id} from course {course_id}")
                return True
        except Exception as e:
            print(f"Error unenrolling user {user_id} from course {course_id}: {str(e)}")
            return False

# Usage:
# from app.core.db.db_client import DBClient
# db = DBClient("sqlite:///app_database.db")
# session = db.get_session()
# ... use session ...
# session.close()
