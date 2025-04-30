"""
AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.

Ensures all SQLAlchemy ORM model classes are imported before any Base.metadata.create_all(engine)
so that inter-model relationships by string name are resolvable.

Fixes problems like: Course(..., categories = relationship('Category', ...)) failing,
since Category class wasn't registered at time of relationship setup.
"""

from .base import Base
from .user import User, UserProfile
from .course import Course, Module, Lesson, Enrollment, CourseModel
from .category import Category
from .tag import Tag
from .content import Content
from .assessment import Assessment
from .content_type_registry import ContentTypeRegistry
from .metadata_schema import *
from .metadata_manager import *
from .category_suggestion import *
from .tag_suggestion import *
from .tag_search import *

# Add other app/models/*.py ORM classes as needed.
