"""
Content model for AeroLearn AI (Topic, Module, Lesson, Quiz).

Location: app/models/content.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Handles Topic, Module, Lesson, Quiz logic; validation, serialization, and event integration.
"""

from app.core.db.schema import Topic, Module, Lesson, Quiz, Question
from integrations.events.event_bus import EventBus
from integrations.events.event_types import ContentEvent, ContentEventType, EventPriority
import re

class TopicModel:
    def __init__(self, sa_topic: Topic):
        self.sa_topic = sa_topic

    @property
    def id(self):
        return self.sa_topic.id

    def serialize(self, include_modules=True):
        d = {
            "id": self.id,
            "name": self.sa_topic.name,
            "description": self.sa_topic.description,
        }
        if include_modules:
            d["modules"] = [ModuleModel(m).serialize(include_lessons=False) for m in self.sa_topic.modules]
        return d

    def validate(self):
        if not self.sa_topic.name or len(self.sa_topic.name) < 2:
            raise ValueError("Topic name is required and must be at least 2 chars.")

class ModuleModel:
    def __init__(self, sa_module: Module):
        self.sa_module = sa_module

    @property
    def id(self):
        return self.sa_module.id

    def serialize(self, include_lessons=True):
        d = {
            "id": self.id,
            "title": self.sa_module.title,
            "description": self.sa_module.description,
            "difficulty_level": self.sa_module.difficulty_level
        }
        if include_lessons:
            d["lessons"] = [LessonModel(l).serialize(include_quizzes=False) for l in self.sa_module.lessons]
        return d

    def validate(self):
        if not self.sa_module.title or len(self.sa_module.title) < 3:
            raise ValueError("Module title must be at least 3 chars.")

class LessonModel:
    def __init__(self, sa_lesson: Lesson):
        self.sa_lesson = sa_lesson

    @property
    def id(self):
        return self.sa_lesson.id

    def serialize(self, include_quizzes=True):
        d = {
            "id": self.id,
            "title": self.sa_lesson.title,
            "content": self.sa_lesson.content,
        }
        if include_quizzes:
            d["quizzes"] = [QuizModel(q).serialize() for q in self.sa_lesson.quizzes]
        return d

    def validate(self):
        if not self.sa_lesson.title or len(self.sa_lesson.title) < 3:
            raise ValueError("Lesson title must be at least 3 chars.")
        if not self.sa_lesson.content or len(self.sa_lesson.content) < 10:
            raise ValueError("Lesson content is too short.")

class QuizModel:
    def __init__(self, sa_quiz: Quiz):
        self.sa_quiz = sa_quiz

    @property
    def id(self):
        return self.sa_quiz.id

    def serialize(self, include_questions=True):
        d = {
            "id": self.id,
            "title": self.sa_quiz.title,
        }
        if include_questions:
            d["questions"] = [QuestionModel(q).serialize(include_answers=False) for q in self.sa_quiz.questions]
        return d

    def validate(self):
        if not self.sa_quiz.title or len(self.sa_quiz.title) < 3:
            raise ValueError("Quiz title must be at least 3 chars.")

class QuestionModel:
    def __init__(self, sa_question: Question):
        self.sa_question = sa_question

    @property
    def id(self):
        return self.sa_question.id

    def serialize(self, include_answers=True):
        d = {
            "id": self.id,
            "text": self.sa_question.text,
        }
        if include_answers:
            d["answers"] = [
                {
                    "id": a.id,
                    "text": a.text,
                    "is_correct": a.is_correct,
                } for a in self.sa_question.answers
            ]
        return d

    def validate(self):
        if not self.sa_question.text or len(self.sa_question.text) < 3:
            raise ValueError("Question text must be at least 3 chars.")