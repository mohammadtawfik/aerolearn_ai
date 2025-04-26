"""
Event Bus hooks for publishing DB changes.
This uses real project models (User, Module, Lesson, etc).
"""

from sqlalchemy import event
from app.core.db.schema import User, Module, Lesson, ProgressRecord, Topic, Quiz, Question, Answer, UserProfile, LearningPath, PathModule

# Simplified stand-in for event bus
class EventBus:
    def publish(self, event_type, payload):
        print(f"EventBus: {event_type} -> {payload}")

event_bus = EventBus()

def after_insert(mapper, connection, target):
    event_bus.publish("db.insert", {"table": target.__tablename__, "id": getattr(target, 'id', None)})

def after_update(mapper, connection, target):
    event_bus.publish("db.update", {"table": target.__tablename__, "id": getattr(target, 'id', None)})

def after_delete(mapper, connection, target):
    event_bus.publish("db.delete", {"table": target.__tablename__, "id": getattr(target, 'id', None)})

def install_event_hooks():
    # Attach to ALL major models you wish to monitor
    models = [User, Module, Lesson, ProgressRecord, Topic, Quiz, Question, Answer, UserProfile, LearningPath, PathModule]
    for model in models:
        event.listen(model, 'after_insert', after_insert)
        event.listen(model, 'after_update', after_update)
        event.listen(model, 'after_delete', after_delete)
    print("Event hooks installed.")

# Usage: from app.core.db.event_hooks import install_event_hooks; install_event_hooks()
