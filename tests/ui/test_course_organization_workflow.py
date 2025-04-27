# /tests/ui/test_course_organization_workflow.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.models.course import Base, Course, Module, Lesson
from app.models.category import Category
from app.models.tag import Tag
from app.models.tag_search import (
    search_courses_by_tag, search_courses_by_tag_partial
)

@pytest.fixture()
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()
    clear_mappers()

def test_full_course_organization_workflow(in_memory_db):
    session = in_memory_db

    # 1. Create Course Structure
    c1 = Course(title="Data Science")
    m1 = Module(title="Python", order=1)
    m2 = Module(title="ML", order=2)
    l1 = Lesson(title="Intro Python", order=1)
    l2 = Lesson(title="NumPy", order=2)
    m1.lessons.extend([l1, l2])
    c1.modules.extend([m1, m2])
    session.add(c1)
    session.commit()
    # Check hierarchy
    got = session.query(Course).filter_by(title="Data Science").one()
    assert len(got.modules) == 2 and got.modules[0].lessons[0].title == "Intro Python"

    # 2. Assign Categories and Tags
    cat_ds = Category(name="Data Science", slug="data-science")
    tag_python = Tag(name="python")
    tag_machine = Tag(name="machine learning")
    c1.categories.append(cat_ds)
    c1.tags.append(tag_python)
    m2.tags.append(tag_machine)
    session.commit()
    # Category propagation test
    assert cat_ds in got.categories
    assert tag_python in got.tags

    # 3. Search with tags
    found = search_courses_by_tag(session, "python")
    assert got in found

    found_partial = search_courses_by_tag_partial(session, "learn")
    assert got not in found_partial  # 'machine learning' tag on module only so course not matched

    # 4. Edit (remove/add) categories/tags and check propagation
    got.categories.remove(cat_ds)
    session.commit()
    got2 = session.query(Course).filter_by(title="Data Science").one()
    assert not got2.categories

    # 5. Cross-boundary: Assign module tag to course and search
    got2.tags.append(tag_machine)
    session.commit()
    found2 = search_courses_by_tag_partial(session, "learn")
    assert got2 in found2