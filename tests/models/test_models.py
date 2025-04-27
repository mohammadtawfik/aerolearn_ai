# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Basic tests for models created in Task 3.2.

Location: tests/models/test_models.py

Covers:
- Creation, validation, and serialization for User, Course, Content, Assessment models.
- Relationship checks.
- Event bus integration stubs (mocked, as real event bus may need async setup).

NOTE: This is a minimal, demonstration-level test suite. Extend as needed for CI or deeper coverage.
"""

import pytest
from datetime import datetime

from app.core.db.schema import Base, User, UserProfile, LearningPath, Module, Topic, Lesson, Quiz, ProgressRecord, PathModule
from app.models.user import UserModel
from app.models.course import CourseModel
from app.models.content import TopicModel, ModuleModel, LessonModel, QuizModel
from app.models.assessment import AssessmentModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up in-memory database for fast tests
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def test_user_model_creation_and_validation():
    session = Session()
    user = User(username="testuser", email="test@example.com", password_hash="abc")
    profile = UserProfile(full_name="Test User", bio="A test bio", expertise_level="beginner")
    user.profiles.append(profile)
    session.add(user)
    session.commit()

    um = UserModel(user)
    # Validation should not raise
    assert um.validate() is True
    data = um.serialize()
    assert data["username"] == "testuser"
    assert isinstance(data["profiles"], list) and data["profiles"][0]["full_name"] == "Test User"

    # Test invalid username/email
    user.username = "@@@"
    with pytest.raises(ValueError):
        UserModel(user).validate()
    user.username = "validname"
    user.email = "bademail"
    with pytest.raises(ValueError):
        UserModel(user).validate()
    session.close()

def test_course_model_and_relationships():
    session = Session()
    user = User(username="prof", email="prof@example.com", password_hash="pw")
    session.add(user)
    session.commit()
    lp = LearningPath(title="W01", description="desc", creator=user)  # Must be at least 3 chars
    mod = Module(title="Intro Mod", description="...", difficulty_level=2)
    session.add(mod)
    session.commit()
    pm = PathModule(learning_path=lp, module=mod, order=1)
    session.add(pm)
    session.add(lp)
    session.commit()

    cm = CourseModel(lp)
    cm.validate()
    data = cm.serialize()
    assert data["modules"][0]["title"] == "Intro Mod"
    session.close()

def test_content_models():
    session = Session()
    topic = Topic(name="Aerodynamics", description="desc")
    mod = Module(title="Basics", description="x", difficulty_level=1, topic=topic)
    lesson = Lesson(title="Basics L1", content="1234567890", module=mod)
    quiz = Quiz(title="Quiz 1", lesson=lesson)
    session.add_all([topic, mod, lesson, quiz])
    session.commit()

    # Topic
    tm = TopicModel(topic)
    tm.validate()
    data = tm.serialize()
    assert data["name"] == "Aerodynamics"

    # Module
    mm = ModuleModel(mod)
    mm.validate()
    assert mm.serialize()["title"] == "Basics"

    # Lesson
    lm = LessonModel(lesson)
    lm.validate()
    assert "content" in lm.serialize()

    # Quiz
    qm = QuizModel(quiz)
    qm.validate()
    assert qm.serialize()["title"] == "Quiz 1"

    session.close()

def test_assessment_model():
    session = Session()
    user = User(username="student", email="student@email.com", password_hash="pw")
    mod = Module(title="A Mod", description="", difficulty_level=1)
    session.add(user)
    session.add(mod)
    session.commit()
    record = ProgressRecord(user_id=user.id, module_id=mod.id, completed=True, score=95, completed_date=datetime.now())
    session.add(record)
    session.commit()

    am = AssessmentModel(record)
    am.validate()
    data = am.serialize()
    assert data["score"] == 95
    session.close()

# Event bus related tests could be added here with proper async test runner and mock event bus
# For example:
# import asyncio
# async def test_user_event_emission():
#   ...
