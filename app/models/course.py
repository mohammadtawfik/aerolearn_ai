"""
Course model for AeroLearn AI.

Location: app/models/course.py
Depends on: integrations/events/event_bus.py, integrations/events/event_types.py

Covers ORM models, relationships, validation, serialization, and event emission.
"""

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean,
    Table, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from integrations.events.event_bus import EventBus
from integrations.events.event_types import ContentEvent, ContentEventType, EventPriority
import re

Base = declarative_base()

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
            "prerequisites": [{"id": course.id, "title": course.title} for course in self.prerequisites]
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
