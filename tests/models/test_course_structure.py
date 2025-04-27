# /tests/models/test_course_structure.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.models.course import Base, Course, Module, Lesson
from app.models.category import Category
from app.models.tag import Tag

@pytest.fixture()
def in_memory_db():
    # Create a new in-memory database and bind model Base to it
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()
    clear_mappers()

def test_course_module_lesson_hierarchy(in_memory_db):
    session = in_memory_db

    course = Course(title="Physics", description="Advanced Physics")
    module1 = Module(title="Mechanics", order=1)
    module2 = Module(title="Optics", order=2)
    lesson1 = Lesson(title="Newton's Laws", order=1)
    lesson2 = Lesson(title="Conservation of Energy", order=2)
    module1.lessons.extend([lesson1, lesson2])
    course.modules.extend([module1, module2])

    session.add(course)
    session.commit()

    fetched_course = session.query(Course).filter_by(title="Physics").one()
    assert len(fetched_course.modules) == 2
    assert fetched_course.modules[0].lessons[0].title == "Newton's Laws"

def test_ordering_constraints(in_memory_db):
    session = in_memory_db
    course = Course(title="Math", description="Mathematics")
    module1 = Module(title="Algebra", order=2)
    module2 = Module(title="Calculus", order=1)
    course.modules.extend([module1, module2])
    session.add(course)
    session.commit()

    refreshed_course = session.query(Course).filter_by(title="Math").one()
    orders = [m.order for m in refreshed_course.modules]
    assert sorted(orders) == [1, 2]

def test_prerequisite_relationships(in_memory_db):
    session = in_memory_db
    pre_course = Course(title="Intro to CS", description="CS Basics")
    adv_course = Course(title="Advanced CS", description="CS Advanced", prerequisites=[pre_course])
    session.add_all([pre_course, adv_course])
    session.commit()

    adv = session.query(Course).filter_by(title="Advanced CS").one()
    assert adv.prerequisites[0].title == "Intro to CS"
    # Check reverse
    intro = session.query(Course).filter_by(title="Intro to CS").one()
    assert adv in intro.dependent_courses

def test_category_assignment(in_memory_db):
    session = in_memory_db
    course = Course(title="Biology", description="Bio 101")
    cat = Category(name="Science", slug="science")
    course.categories.append(cat)
    session.add(course)
    session.commit()
    fetched = session.query(Course).filter_by(title="Biology").one()
    assert fetched.categories[0].name == "Science"

def test_tag_assignment(in_memory_db):
    session = in_memory_db
    lesson = Lesson(title="Photosynthesis", order=1)
    tag1 = Tag(name="plants")
    tag2 = Tag(name="biology")
    lesson.tags.extend([tag1, tag2])
    session.add(lesson)
    session.commit()
    fetched = session.query(Lesson).filter_by(title="Photosynthesis").one()
    assert set(t.name for t in fetched.tags) == {"plants", "biology"}