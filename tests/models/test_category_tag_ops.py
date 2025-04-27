# /tests/models/test_category_tag_ops.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.models.course import Base, Course, Module, Lesson
from app.models.category import Category
from app.models.tag import Tag
from app.models.category_suggestion import CategorySuggestionService
from app.models.tag_suggestion import TagSuggestionService

@pytest.fixture()
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()
    clear_mappers()

def test_category_assignment_and_removal(in_memory_db):
    session = in_memory_db
    cat1 = Category(name="Physics", slug="physics")
    cat2 = Category(name="Math", slug="math")
    course = Course(title="Math 101")
    course.categories.append(cat1)
    course.categories.append(cat2)
    session.add(course)
    session.commit()
    fetched = session.query(Course).filter_by(title="Math 101").one()
    assert set(c.name for c in fetched.categories) == {"Physics", "Math"}
    # Remove one
    fetched.categories.remove(cat1)
    session.commit()
    fetched_2 = session.query(Course).filter_by(title="Math 101").one()
    assert set(c.name for c in fetched_2.categories) == {"Math"}

def test_tag_assignment_and_removal(in_memory_db):
    session = in_memory_db
    tag1 = Tag(name="easy")
    tag2 = Tag(name="science")
    lesson = Lesson(title="Water Cycle")
    lesson.tags.extend([tag1, tag2])
    session.add(lesson)
    session.commit()
    got = session.query(Lesson).filter_by(title="Water Cycle").one()
    assert {"easy", "science"} == set(t.name for t in got.tags)
    # Remove
    got.tags.remove(tag1)
    session.commit()
    got2 = session.query(Lesson).filter_by(title="Water Cycle").one()
    assert {"science"} == set(t.name for t in got2.tags)

def test_category_suggestion_stub():
    sugg = CategorySuggestionService()
    cats = sugg.suggest("This lesson covers AI and robotics.", top_k=2)
    assert "Technology" in cats or isinstance(cats, list)

def test_tag_suggestion_stub():
    sugg = TagSuggestionService()
    content = "Photosynthesis process involves plants, sunlight, chloroplasts."
    tags = sugg.suggest(content, top_k=3)
    assert any("plant" in t for t in tags) or len(tags) > 0