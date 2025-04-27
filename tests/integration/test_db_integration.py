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
Tests for AeroLearn DB client, schema, migrations, and event hooks.
Run as:
    python -m pytest tests/integration/test_db_integration.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.core.db.db_client import DBClient
from app.core.db.schema import (
    DB_URL, Base, User, Module, Lesson, Quiz, Question, Answer,
    LearningPath, PathModule, ProgressRecord, UserProfile, Topic
)
from app.core.db.migrations import create_all_tables, drop_all_tables, list_tables
from app.core.db.event_hooks import install_event_hooks

from sqlalchemy.orm import joinedload
import pytest

@pytest.fixture(autouse=True, scope="module")
def reset_db():
    drop_all_tables()
    create_all_tables()
    yield
    drop_all_tables()

def test_schema_and_migration():
    tables = list_tables()
    expected = {
        'users', 'user_profiles', 'topics', 'modules', 'lessons', 'quizzes',
        'questions', 'answers', 'learning_paths', 'path_modules', 'progress_records'
    }
    # Table check (at least all these exist)
    for tab in expected:
        assert tab in tables

def test_user_module_lesson_crud():
    db = DBClient(DB_URL)
    # Create user
    user = User(username="janedoe", email="jane@example.com", password_hash="hashed_pw")
    db.add_object(user)
    assert user.id is not None

    # Add user profile
    profile = UserProfile(user_id=user.id, full_name="Jane Doe")
    db.add_object(profile)
    profiles = db.search(UserProfile, user_id=user.id)
    assert profiles[0].full_name == "Jane Doe"

    # Create and associate Topic, Module, Lesson
    topic = Topic(name="Physics", description="Physics basics")
    db.add_object(topic)
    module = Module(title="Newtonian Mechanics", topic_id=topic.id, difficulty_level=2)
    db.add_object(module)
    lesson = Lesson(title="Laws of Motion", content="...", module_id=module.id)
    db.add_object(lesson)

    # Confirm relationships (Lesson -> Module -> Topic)
    found_lesson = db.get_by_id(
        Lesson, lesson.id,
        eager_relations=[
            joinedload(Lesson.module).joinedload(Module.topic)
        ]
    )
    assert found_lesson.module.id == module.id
    assert found_lesson.module.topic.id == topic.id

    # Test ProgressRecord creation
    progress = ProgressRecord(user_id=user.id, module_id=module.id, lesson_id=lesson.id, completed=True, score=100)
    db.add_object(progress)
    pr = db.get_by_id(ProgressRecord, progress.id)
    assert pr.completed is True
    assert pr.score == 100

    # Clean up
    db.delete_object(progress)
    db.delete_object(lesson)
    db.delete_object(module)
    db.delete_object(topic)
    db.delete_object(profile)
    db.delete_object(user)

def test_relationships_and_queries():
    db = DBClient(DB_URL)
    # Create user and topic
    user = User(username="demo_user", email="demo@example.com", password_hash="pw")
    db.add_object(user)
    topic = Topic(name="AeroEng", description="Aeronautical Engineering")
    db.add_object(topic)

    # Module and lesson linkage
    module = Module(title="Aerodynamics", topic_id=topic.id, difficulty_level=4)
    db.add_object(module)
    lesson = Lesson(title="Lift and Drag", content="Bernoulli and more", module_id=module.id)
    db.add_object(lesson)

    # Make a learning path
    lp = LearningPath(title="Pilot Prep", creator_id=user.id)
    db.add_object(lp)
    path_mod = PathModule(learning_path_id=lp.id, module_id=module.id, order=1)
    db.add_object(path_mod)

    # Should be able to fetch learning path modules
    loaded_lp = db.get_by_id(
        LearningPath, lp.id,
        eager_relations=[
            joinedload(LearningPath.path_modules).joinedload(PathModule.module)
        ]
    )
    assert loaded_lp.path_modules[0].module.title == "Aerodynamics"

    # Clean up
    db.delete_object(path_mod)
    db.delete_object(lp)
    db.delete_object(lesson)
    db.delete_object(module)
    db.delete_object(topic)
    db.delete_object(user)

def test_event_hooks():
    print("=== test_event_hooks ===")
    install_event_hooks()
    db = DBClient(DB_URL)
    
    # Create a user and trigger events
    user = User(username="eventuser", email="events@example.com", password_hash="pw123")
    db.add_object(user)  # Should trigger create event
    
    # Update and delete
    user.username = "updated_user"
    db.add_object(user)  # Should trigger update event
    db.delete_object(user)  # Should trigger delete event

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
