"""
Schema configuration for AeroLearn AI: DECOUPLED VERSION
No ORM Topic class defined here; it is now in app/models/topic.py.
This avoids circular import with app.models.content and enables clean layering.

Location: /app/core/db/schema.py (per code_summary.md: schema/config belong here.)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
# If you need the User model, import from app.models.user:
from app.models.user import User
# To use Topic, import from app.models.topic

# Use SQLite for development; replace with production DB URL as needed
# Replace the former hardcoded DB_URL with:
DB_URL = os.getenv("DB_URL", "sqlite:///app_database.db")  # fallback stays compatible

Base = declarative_base()

# Remove Topic from here—use:
#   from app.models.topic import Topic
# wherever the Topic ORM model is needed

# Example usage:
# from app.core.db.schema import Base
# from app.models.user import User
# from app.models.topic import Topic
# 
# # Create a new topic
# new_topic = Topic(name="Aerodynamics", description="Study of air movement")
