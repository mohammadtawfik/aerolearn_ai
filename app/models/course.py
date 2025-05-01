"""
Course model for AeroLearn AI.

Location: app/models/course.py
Depends on: integrations/events/event_bus.py, integrations/events/event_types.py, app/models/user.py

Covers ORM models, relationships, validation, serialization, and event emission.
"""

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean,
    Table, Text, UniqueConstraint, DateTime, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship, backref, Session
from app.models.base import Base
from integrations.events.event_bus import EventBus
from integrations.events.event_types import ContentEvent, ContentEventType, EventPriority
import re
import datetime
import enum
from typing import List, Optional, Dict

class EnrollmentStatus(enum.Enum):
    """Status of an enrollment request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

# Association table for course prerequisites (M2M self-relationship)
course_prerequisite = Table(
    'course_prerequisite', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('course.id'), primary_key=True)
)

# Association tables for taxonomy and tagging
course_category_link = Table(
    'course_category_link', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)

module_category_link = Table(
    'module_category_link', Base.metadata,
    Column('module_id', Integer, ForeignKey('module.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)

lesson_category_link = Table(
    'lesson_category_link', Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lesson.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)

course_tag_link = Table(
    'course_tag_link', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

module_tag_link = Table(
    'module_tag_link', Base.metadata,
    Column('module_id', Integer, ForeignKey('module.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

lesson_tag_link = Table(
    'lesson_tag_link', Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lesson.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)  # for ordering among courses
    
    # Template and archiving fields
    is_template = Column(Boolean, default=False)
    template_parent_id = Column(Integer, ForeignKey('course.id'), nullable=True)
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime, nullable=True)

    # Modules (hierarchical organization)
    modules = relationship('Module', back_populates='course', order_by="Module.order")

    # Prerequisites (many-to-many, self-ref)
    prerequisites = relationship(
        'Course',
        secondary=course_prerequisite,
        primaryjoin=id == course_prerequisite.c.course_id,
        secondaryjoin=id == course_prerequisite.c.prerequisite_id,
        backref='dependent_courses'
    )
    
    # Template parent relationship
    template_parent = relationship("Course", remote_side=[id], foreign_keys=[template_parent_id])
    
    # Enrollments relationship
    enrollments = relationship("Enrollment", back_populates="course")

    # Category and Tag relationships
    categories = relationship('Category', secondary=course_category_link, back_populates='courses')
    tags = relationship('Tag', secondary=course_tag_link, back_populates='courses')

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}')>"
    
    def serialize(self):
        """Serialize course and modules."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "modules": [module.serialize() for module in self.modules],
            "prerequisites": [{"id": course.id, "title": course.title} for course in self.prerequisites],
            "is_template": self.is_template,
            "template_parent_id": self.template_parent_id,
            "is_archived": self.is_archived,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "enrollment_count": len([e for e in self.enrollments if e.status == EnrollmentStatus.APPROVED])
        }

    def validate(self):
        """Ensure course has a title and at least one module."""
        if not self.title or not isinstance(self.title, str) or len(self.title) < 3:
            raise ValueError("Course title must be at least 3 characters.")
        if len(self.modules) == 0:
            raise ValueError("Course must include at least one module.")
        return True

    async def on_created(self, source="course"):
        bus = EventBus()
        if hasattr(bus, "publish") and bus._is_running:
            event = ContentEvent(
                event_type=ContentEventType.CREATED,
                source_component=source,
                data={"course_id": self.id, "title": self.title},
                priority=EventPriority.NORMAL,
                is_persistent=True
            )
            await bus.publish(event)
            
    def archive(self, session: Session):
        """Archive this course."""
        self.is_archived = True
        self.archived_at = datetime.datetime.utcnow()
        session.commit()
        
    def restore(self, session: Session):
        """Restore an archived course."""
        self.is_archived = False
        self.archived_at = None
        session.commit()
        
    def create_from_template(self, session: Session):
        """Create a course instance copying from this template."""
        if not self.is_template:
            raise ValueError("Can only create from a template course")
            
        new_course = Course(
            title=f"Copy of {self.title}",
            description=self.description,
            is_template=False,
            template_parent_id=self.id,
            order=self.order
        )
        session.add(new_course)
        session.flush()  # assign id

        # Copy modules, lessons, etc.
        for module in self.modules:
            module_copy = Module(
                course_id=new_course.id,
                title=module.title,
                description=module.description,
                order=module.order
            )
            session.add(module_copy)
            session.flush()
            
            # Copy lessons
            for lesson in module.lessons:
                lesson_copy = Lesson(
                    module_id=module_copy.id,
                    title=lesson.title,
                    description=lesson.description,
                    content=lesson.content,
                    order=lesson.order
                )
                session.add(lesson_copy)
                
        session.commit()
        return new_course
        
    def enroll_bulk(self, session: Session, user_ids: list[int], approver_id: int = None):
        """Bulk enroll users; skip already-enrolled."""
        from sqlalchemy import select
        
        for user_id in user_ids:
            # Check if enrollment already exists
            existing = session.execute(
                select(Enrollment).filter_by(user_id=user_id, course_id=self.id)
            ).first()
            
            if not existing:
                enrollment = Enrollment(
                    user_id=user_id, 
                    course_id=self.id, 
                    enrolled_at=datetime.datetime.utcnow(),
                    status=EnrollmentStatus.APPROVED if approver_id else EnrollmentStatus.PENDING,
                    approved_by=approver_id,
                    status_history=[{
                        "status": EnrollmentStatus.APPROVED.value if approver_id else EnrollmentStatus.PENDING.value,
                        "at": datetime.datetime.utcnow().isoformat(),
                        "by": approver_id
                    }]
                )
                session.add(enrollment)
                
        session.commit()
        
    def request_enrollment(self, session: Session, user_id: int):
        """Request enrollment in this course."""
        from sqlalchemy import select
        
        # Check if enrollment already exists
        existing = session.execute(
            select(Enrollment).filter_by(user_id=user_id, course_id=self.id)
        ).first()
        
        if existing:
            return existing[0]  # Return existing enrollment
            
        enrollment = Enrollment(
            user_id=user_id,
            course_id=self.id,
            enrolled_at=datetime.datetime.utcnow(),
            status=EnrollmentStatus.PENDING,
            status_history=[{
                "status": EnrollmentStatus.PENDING.value,
                "at": datetime.datetime.utcnow().isoformat(),
                "by": user_id
            }]
        )
        session.add(enrollment)
        session.commit()
        return enrollment
        
    def approve_enrollment(self, session: Session, enrollment_id: int, approver_id: int):
        """Approve an enrollment request."""
        from sqlalchemy import select
        
        enrollment = session.execute(
            select(Enrollment).filter_by(id=enrollment_id, course_id=self.id)
        ).scalar_one_or_none()
        
        if enrollment and enrollment.status == EnrollmentStatus.PENDING:
            enrollment.approve(approver_id)
            session.commit()
            return enrollment
        return None
        
    def reject_enrollment(self, session: Session, enrollment_id: int, approver_id: int):
        """Reject an enrollment request."""
        from sqlalchemy import select
        
        enrollment = session.execute(
            select(Enrollment).filter_by(id=enrollment_id, course_id=self.id)
        ).scalar_one_or_none()
        
        if enrollment and enrollment.status == EnrollmentStatus.PENDING:
            enrollment.reject(approver_id)
            session.commit()
            return enrollment
        return None
        
    def cancel_enrollment(self, session: Session, enrollment_id: int, user_id: int):
        """Cancel an enrollment request."""
        from sqlalchemy import select
        
        enrollment = session.execute(
            select(Enrollment).filter_by(id=enrollment_id, course_id=self.id)
        ).scalar_one_or_none()
        
        if enrollment and enrollment.status == EnrollmentStatus.PENDING:
            enrollment.cancel(user_id)
            session.commit()
            return enrollment
        return None
        
    def get_enrollment_requests(self, session: Session, status: EnrollmentStatus = None):
        """Get all enrollment requests for this course, optionally filtered by status."""
        from sqlalchemy import select
        
        query = select(Enrollment).filter_by(course_id=self.id)
        if status:
            query = query.filter_by(status=status)
            
        return session.execute(query).scalars().all()
        
    def is_enrolled(self, session: Session, user_id: int) -> bool:
        """Check if a user is enrolled in this course."""
        from sqlalchemy import select
        
        enrollment = session.execute(
            select(Enrollment).filter_by(
                user_id=user_id, 
                course_id=self.id,
                status=EnrollmentStatus.APPROVED
            )
        ).scalar_one_or_none()
        
        return enrollment is not None
        
    def enrollment_status(self, session: Session, user_id: int) -> Optional[EnrollmentStatus]:
        """Get enrollment status for a user."""
        from sqlalchemy import select
        
        enrollment = session.execute(
            select(Enrollment).filter_by(user_id=user_id, course_id=self.id)
        ).scalar_one_or_none()
        
        return enrollment.status if enrollment else None

# Module prerequisites (self-ref)
module_prerequisite = Table(
    'module_prerequisite', Base.metadata,
    Column('module_id', Integer, ForeignKey('module.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('module.id'), primary_key=True)
)

class Module(Base):
    __tablename__ = 'module'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)  # ordering inside the course

    course = relationship('Course', back_populates='modules')
    lessons = relationship('Lesson', back_populates='module', order_by="Lesson.order")

    prerequisites = relationship(
        'Module',
        secondary=module_prerequisite,
        primaryjoin=id == module_prerequisite.c.module_id,
        secondaryjoin=id == module_prerequisite.c.prerequisite_id,
        backref='dependent_modules'
    )

    # Category / Tag relationships
    categories = relationship('Category', secondary=module_category_link, back_populates='modules')
    tags = relationship('Tag', secondary=module_tag_link, back_populates='modules')

    def __repr__(self):
        return f"<Module(id={self.id}, title='{self.title}', course_id={self.course_id})>"
    
    def serialize(self):
        """Serialize module and lessons."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "order": self.order,
            "lessons": [lesson.serialize() for lesson in self.lessons],
            "prerequisites": [{"id": module.id, "title": module.title} for module in self.prerequisites]
        }
        
    def copy(self, new_course_id):
        """Create a copy of this module for template cloning."""
        new_module = Module(
            course_id=new_course_id,
            title=self.title,
            description=self.description,
            order=self.order
        )
        return new_module

class Lesson(Base):
    __tablename__ = 'lesson'
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('module.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)
    order = Column(Integer, default=0)  # ordering inside the module

    module = relationship('Module', back_populates='lessons')

    # Category / Tag relationships
    categories = relationship('Category', secondary=lesson_category_link, back_populates='lessons')
    tags = relationship('Tag', secondary=lesson_tag_link, back_populates='lessons')

    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', module_id={self.module_id})>"
    
    def serialize(self):
        """Serialize lesson."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "order": self.order
        }

class Enrollment(Base):
    """Enrollment model for tracking user enrollments in courses."""
    __tablename__ = 'enrollment'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.PENDING)
    approved_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    status_history = Column(JSON, default=list)
    
    # Relationship to course
    course = relationship("Course", back_populates="enrollments")
    # Relationship to user (student)
    user = relationship("User", 
                        back_populates="enrollments", 
                        foreign_keys=[user_id])
    # Relationship to approver (professor/admin)
    approver = relationship("User", 
                           back_populates="approved_enrollments", 
                           foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Enrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, status={self.status})>"
    
    def approve(self, approver_id: int):
        """Approve an enrollment request."""
        self.status = EnrollmentStatus.APPROVED
        self.approved_by = approver_id
        if not self.status_history:
            self.status_history = []
        self.status_history.append({
            "status": self.status.value,
            "at": datetime.datetime.utcnow().isoformat(),
            "by": approver_id
        })
    
    def reject(self, approver_id: int):
        """Reject an enrollment request."""
        self.status = EnrollmentStatus.REJECTED
        self.approved_by = approver_id
        if not self.status_history:
            self.status_history = []
        self.status_history.append({
            "status": self.status.value,
            "at": datetime.datetime.utcnow().isoformat(),
            "by": approver_id
        })
    
    def cancel(self, user_id: int):
        """Cancel an enrollment request."""
        self.status = EnrollmentStatus.CANCELLED
        if not self.status_history:
            self.status_history = []
        self.status_history.append({
            "status": self.status.value,
            "at": datetime.datetime.utcnow().isoformat(),
            "by": user_id
        })
    
    def serialize(self):
        """Serialize enrollment."""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "user_id": self.user_id,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "status": self.status.value,
            "approved_by": self.approved_by,
            "status_history": self.status_history
        }

# CourseModel for backward compatibility
class CourseModel:
    def __init__(self, course: Course):
        self.course = course

    @property
    def id(self):
        return self.course.id

    @property
    def title(self):
        return self.course.title

    @property
    def description(self):
        return self.course.description

    @property
    def modules(self):
        return [
            {
                "module_id": module.id,
                "title": module.title,
                "order": module.order,
            }
            for module in self.course.modules
        ]

    def serialize(self):
        """Serialize course and modules."""
        return self.course.serialize()

    def validate(self):
        """Ensure course has a title and at least one module."""
        return self.course.validate()

    async def on_created(self, source="course"):
        await self.course.on_created(source)
