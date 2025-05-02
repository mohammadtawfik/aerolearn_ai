"""
File: question_engine.py
Location: /app/core/assessment/
Purpose: Renders questions, validates answers, provides interface for user interaction and integrates into assessment sessions.
Imports fixed to match model structure.
"""

from typing import Dict, Any, Union

from app.models.content import Question  # Import Question from content.py
from app.models.assessment import Answer  # Import Answer from assessment.py

# Attempt to import QuestionType if it exists; if not, use strings in code as fallback.
try:
    from app.models.content import QuestionType
except ImportError:
    class QuestionType:
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
        TEXT = "TEXT"
        CODE = "CODE"

class QuestionRenderError(Exception):
    pass

class QuestionEngine:
    def render(self, question: Question) -> Dict[str, Any]:
        """
        Returns a dictionary representation of a question for rendering in any UI (web, mobile, etc.)
        """
        # Handle both object and dictionary access patterns
        if isinstance(question, dict):
            choices = question.get('choices')
            options = question.get('options')
            return {
                'id': question.get('id'),
                'prompt': question.get('prompt'),
                'type': question.get('type'),
                'choices': choices if choices is not None else options,
                'metadata': question.get('metadata', {})
            }
        else:
            # Get choices or options (if choices is None)
            choices = getattr(question, 'choices', None)
            options = getattr(question, 'options', None)
            
            return {
                'id': getattr(question, 'id', None),
                'prompt': getattr(question, 'prompt', None),
                'type': getattr(question, 'type', None),
                'choices': choices if choices is not None else options,
                'metadata': getattr(question, 'metadata', {})
            }

    def validate_answer(self, question: Question, answer: Any) -> bool:
        """
        Validates answer data structure for the given question.
        Strictly returns False for invalid types or values.
        For MCQ: Accepts answers that are in either 'options' or 'choices'.
        """
        # Get question type, handling both object and dict access patterns
        if isinstance(question, dict):
            q_type = question.get('type')
            choices = question.get('choices')
            options = question.get('options')
        else:
            q_type = getattr(question, 'type', None)
            choices = getattr(question, 'choices', None)
            options = getattr(question, 'options', None)
        
        # Ensure we have valid options, with proper fallback
        valid_options = (choices if choices is not None else options) or []
        
        # Handle standard Answer object (preferred)
        if hasattr(answer, "selected_option") or hasattr(answer, "text_response") or hasattr(answer, "code"):
            if q_type == "MULTIPLE_CHOICE" or q_type == getattr(QuestionType, "MULTIPLE_CHOICE", None):
                return hasattr(answer, "selected_option") and answer.selected_option in valid_options
            elif q_type == "TEXT" or q_type == getattr(QuestionType, "TEXT", None):
                return hasattr(answer, "text_response") and isinstance(answer.text_response, str)
            elif q_type == "CODE" or q_type == getattr(QuestionType, "CODE", None):
                return hasattr(answer, "code") and isinstance(answer.code, str)
            # Unknown type
            return False
        # Handle raw responses (test or direct user input)
        else:
            if q_type == "MULTIPLE_CHOICE" or q_type == getattr(QuestionType, "MULTIPLE_CHOICE", None):
                # Accept only string in valid options (choices or options)
                return isinstance(answer, str) and answer in valid_options
            elif q_type == "TEXT" or q_type == getattr(QuestionType, "TEXT", None):
                return isinstance(answer, str)
            elif q_type == "CODE" or q_type == getattr(QuestionType, "CODE", None):
                return isinstance(answer, str)
        # Explicitly return False for ANY unhandled cases!
        return False
