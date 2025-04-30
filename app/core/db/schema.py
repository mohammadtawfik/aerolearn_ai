"""
Schema configuration for AeroLearn AI: PRUNED VERSION
Defines only test/demo objects not participating in app-wide FKs.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
# If you need the User model, import from app.models.user:
from app.models.user import User

# Use SQLite for development; replace with production DB URL as needed
# Replace the former hardcoded DB_URL with:
DB_URL = os.getenv("DB_URL", "sqlite:///app_database.db")  # fallback stays compatible

Base = declarative_base()

# Content models for testing/demo purposes only
class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    
    # Self-referential relationship
    subtopics = relationship("Topic", backref="parent", remote_side=[id])

# Example usage:
# from app.core.db.schema import Base, Topic
# from app.models.user import User
# 
# # Create a new topic
# new_topic = Topic(name="Aerodynamics", description="Study of air movement")
