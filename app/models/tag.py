# app/models/tag.py

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)

    courses = relationship('Course', secondary='course_tag_link', back_populates='tags')
    modules = relationship('Module', secondary='module_tag_link', back_populates='tags')
    lessons = relationship('Lesson', secondary='lesson_tag_link', back_populates='tags')

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
