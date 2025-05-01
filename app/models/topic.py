"""
File: /app/models/topic.py
Purpose: Defines the SQLAlchemy ORM Topic class for use in content-related models and schema.
Rationale: Moved out of /app/core/db/schema.py to break circular import (between content.py and schema.py).
           Per project structure in /code_summary.md, ORM models should reside in /app/models/.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    # Self-referential relationship
    subtopics = relationship("Topic", backref="parent", remote_side=[id])