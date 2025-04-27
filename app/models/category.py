# app/models/category.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    slug = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    parent = relationship('Category', remote_side=[id], backref=backref('children', cascade='all, delete'))
    
    courses = relationship('Course', secondary='course_category_link', back_populates='categories')
    modules = relationship('Module', secondary='module_category_link', back_populates='categories')
    lessons = relationship('Lesson', secondary='lesson_category_link', back_populates='categories')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"