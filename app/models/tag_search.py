# /app/models/tag_search.py

from sqlalchemy.orm import Session
from app.models.course import Course, Module, Lesson
from app.models.tag import Tag

def search_courses_by_tag(session: Session, tag_name: str):
    """Return all courses tagged with the given tag name (case-insensitive exact)."""
    return session.query(Course).join(Course.tags).filter(Tag.name.ilike(tag_name)).all()

def search_modules_by_tag(session: Session, tag_name: str):
    """Return all modules tagged with the given tag name."""
    return session.query(Module).join(Module.tags).filter(Tag.name.ilike(tag_name)).all()

def search_lessons_by_tag(session: Session, tag_name: str):
    """Return all lessons tagged with the given tag name."""
    return session.query(Lesson).join(Lesson.tags).filter(Tag.name.ilike(tag_name)).all()

def search_courses_by_tag_partial(session: Session, tag_fragment: str):
    """Return all courses with a tag *containing* the given string."""
    return session.query(Course).join(Course.tags).filter(Tag.name.ilike(f"%{tag_fragment}%")).all()

def search_courses_by_tags(session: Session, tags_list):
    """Return all courses matching ANY tag in the list."""
    return session.query(Course).join(Course.tags).filter(Tag.name.in_(tags_list)).all()