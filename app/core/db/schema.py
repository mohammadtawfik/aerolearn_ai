"""
Schema configuration for AeroLearn AI
Defines SQLAlchemy declarative base and example table definitions for testing relationships.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship

# Use SQLite for development; replace with production DB URL as needed
# Replace the former hardcoded DB_URL with:
DB_URL = os.getenv("DB_URL", "sqlite:///app_database.db")  # fallback stays compatible

Base = declarative_base()

# User and authentication models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="creator")
    progress_records = relationship("ProgressRecord", back_populates="user")

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    expertise_level = Column(String(20))  # beginner, intermediate, advanced
    
    # Relationships
    user = relationship("User", back_populates="profiles")

# Content models
class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    
    # Self-referential relationship
    subtopics = relationship("Topic", backref="parent", remote_side=[id])
    
    # Relationships
    modules = relationship("Module", back_populates="topic")

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer)  # 1-5 scale
    topic_id = Column(Integer, ForeignKey('topics.id'))
    
    # Relationships
    topic = relationship("Topic", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'))
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson")

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    
    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    
    # Relationships
    question = relationship("Question", back_populates="answers")

# Learning path and progress tracking
class LearningPath(Base):
    __tablename__ = 'learning_paths'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    creator = relationship("User", back_populates="learning_paths")
    path_modules = relationship("PathModule", back_populates="learning_path")

class PathModule(Base):
    __tablename__ = 'path_modules'
    id = Column(Integer, primary_key=True)
    learning_path_id = Column(Integer, ForeignKey('learning_paths.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    order = Column(Integer, nullable=False)
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="path_modules")
    module = relationship("Module")


class ProgressRecord(Base):
    __tablename__ = 'progress_records'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=True)
    completed = Column(Boolean, default=False)
    score = Column(Integer, nullable=True)
    completed_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress_records")
    module = relationship("Module")
    lesson = relationship("Lesson")  # ✅ CORRECT: nullable handled by lesson_id column


# Example usage:
# from app.core.db.schema import Base, User, Module
# 
# # Create a new user
# new_user = User(username="aerospace_student", email="student@example.com")
# 
# # Create a new module
# new_module = Module(title="Introduction to Aerodynamics", difficulty_level=2)
