"""
File: grading.py
Location: /app/core/assessment/
Purpose: Core auto-grading logic: MCQs, text/NLP, code (with stubbed runners), partial credit system.

Fulfills assessment grading requirements in the Day 17 Plan.
"""

import string
from typing import Dict, Any, Set
from app.models.content import Question
from app.models.assessment import Answer  # Corrected imports

# Try to import QuestionType, else use string type checks
try:
    from app.models.content import QuestionType
except ImportError:
    class QuestionType:
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
        TEXT = "TEXT"
        CODE = "CODE"

class GradingRuleError(Exception):
    pass

class GradingEngine:
    """
    Handles grading of assessment questions and sessions.
    """
    def grade_multiple_choice(self, question: Question, answer: Answer) -> float:
        return 1.0 if getattr(answer, "selected_option", None) == getattr(question, "correct_option", None) else 0.0

    def grade_text(self, question: Question, answer: Answer) -> float:
        """
        Grade text responses with the following rules:
        - 1.0 for exact phrase match with expected answer
        - Keyword match: full credit (1.0) if all keywords found, partial if some; 0.0 for empty
        - Default: award 0.5 for any non-empty answer
        """
        # Get text response
        text_response = getattr(answer, "text_response", "") or ""
        
        # If response is empty, return 0
        if not text_response or not text_response.strip():
            return 0.0
            
        # Check for exact match with expected answer
        expected_answer = getattr(question, "correct_answer", None) or getattr(question, "answer", None)
        if expected_answer and isinstance(expected_answer, str):
            if text_response.strip().lower() == expected_answer.strip().lower():
                return 1.0
        
        # If we have expected keywords, use keyword matching
        expected_keywords = getattr(question, "expected_keywords", [])
        if expected_keywords:
            # Normalize text by removing punctuation and converting to lowercase
            trans = str.maketrans('', '', string.punctuation)
            normalized_text = text_response.lower().translate(trans)
            
            # Count matching keywords
            matches = 0
            matched_keywords = set()
            
            for keyword in expected_keywords:
                if not keyword:  # Skip empty keywords
                    continue
                    
                keyword_lower = keyword.lower()
                # Try word boundary match first (more precise)
                import re
                regex = rf"\b{re.escape(keyword_lower)}\b"
                if re.search(regex, normalized_text):
                    matches += 1
                    matched_keywords.add(keyword_lower)
                # Fall back to substring match
                elif keyword_lower in normalized_text:
                    matches += 1
                    matched_keywords.add(keyword_lower)
            
            # Calculate score based on proportion of keywords found
            total_keywords = len([k for k in expected_keywords if k])  # Count non-empty keywords
            if total_keywords > 0:
                if matches == total_keywords:
                    return 1.0  # full credit if all keywords found
                elif matches > 0:
                    # partial credit; more generous scoring
                    return 0.5 + 0.5 * (matches / total_keywords)
                else:
                    return 0.5  # no keywords found but answer not empty
        
        # Default: award 0.5 for any non-empty answer
        return 0.5

    def grade_code(self, question: Question, answer: Answer) -> float:
        """
        Run code submission against question.test_cases (stub).
        If an expected answer is present, check for exact match.
        """
        # Get the submitted code
        code_response = getattr(answer, "code", None)
        
        # Look for exact match to expected answer if present
        expected_code = getattr(question, "correct_answer", None) or getattr(question, "solution_code", None)
        if expected_code:
            return 1.0 if isinstance(code_response, str) and code_response.strip() == expected_code.strip() else 0.0
        
        # In practice, this would run the code in a sandbox and check the results.
        # For security, would NOT use eval directly!
        # For now, return 0.0 if no expected answer is provided
        return 0.0

    def grade_partial_credit(self, question: Question, answer: Answer, rubric: Dict[str, float]) -> float:
        """
        Partial credit grading based on rubric (criteria:score mapping)
        """
        # Placeholder logic; real implementation would evaluate each rubric criterion
        achieved = sum(
            score for criteria, score in rubric.items()
            if hasattr(answer, "response_flags") and criteria in answer.response_flags
        )
        max_score = sum(rubric.values())
        return achieved / max_score if max_score else 0.0

    def grade(self, question: Question, answer: Answer, rubric: Dict[str, float]=None) -> float:
        q_type = getattr(question, 'type', None)
        if q_type == "MULTIPLE_CHOICE" or q_type == getattr(QuestionType, "MULTIPLE_CHOICE", None):
            return self.grade_multiple_choice(question, answer)
        elif q_type == "TEXT" or q_type == getattr(QuestionType, "TEXT", None):
            return self.grade_text(question, answer)
        elif q_type == "CODE" or q_type == getattr(QuestionType, "CODE", None):
            return self.grade_code(question, answer)
        elif rubric:
            return self.grade_partial_credit(question, answer, rubric)
        else:
            raise GradingRuleError("Unsupported question type or missing rubric.")
    
    @staticmethod
    def grade_session(session):
        """
        Grade a whole assessment session.
        
        Args:
            session: The assessment session object containing questions and answers
            
        Returns:
            dict: {'total': float, 'breakdown': {i: score}} where i is the question index
        """
        scores = {}
        total = 0.0
        questions = session.get_questions()
        
        for i, q in enumerate(questions):
            q_type = q.get("type", None) if isinstance(q, dict) else getattr(q, "type", None)
            qkey = q.get("id", None) or q.get("question") or str(q)
            answer_obj = session.answers.get(qkey)
            
            # Accept fallback: if answers has index key, grab by i
            if answer_obj is None:
                answer_obj = session.answers.get(i)

            # Handle different question types
            if q_type == "MULTIPLE_CHOICE":
                correct_answer = q.get("answer") if isinstance(q, dict) else getattr(q, "answer", None)
                selected = getattr(answer_obj, "selected_option", answer_obj) if answer_obj is not None else None
                score = 1.0 if selected == correct_answer else 0.0
            elif q_type == "TEXT":
                # Get expected answer if available
                target = None
                if isinstance(q, dict):
                    target = q.get("answer") or q.get("expected_answer")
                    expected_keywords = q.get("expected_keywords", [])
                else:
                    target = getattr(q, "answer", None)
                    expected_keywords = getattr(q, "expected_keywords", [])
                
                text_response = getattr(answer_obj, "text_response", answer_obj) or ""
                
                # 1.0 for exact match with expected answer
                if target and isinstance(target, str) and text_response.strip().lower() == target.strip().lower():
                    score = 1.0
                # If we have a non-empty response but no exact match, check keywords
                elif text_response and text_response.strip():
                    # Try keyword matching if available
                    expected_keys = [
                        k.lower() for k in expected_keywords
                        if k  # Skip empty keywords
                    ]
                    
                    if expected_keys:
                        # Normalize text by removing punctuation
                        trans = str.maketrans('', '', string.punctuation)
                        normalized_text = text_response.lower().translate(trans)
                        
                        # Count matching keywords
                        matches = 0
                        matched_keywords = set()
                        
                        for keyword in expected_keys:
                            # Try word boundary match first (more precise)
                            import re
                            regex = rf"\b{re.escape(keyword)}\b"
                            if re.search(regex, normalized_text):
                                matches += 1
                                matched_keywords.add(keyword)
                            # Fall back to substring match
                            elif keyword in normalized_text:
                                matches += 1
                                matched_keywords.add(keyword)
                        
                        # Calculate score based on proportion of keywords found
                        if matches == len(expected_keys):
                            score = 1.0  # Full credit if all keywords found
                        elif matches > 0:
                            # Partial credit with more generous scoring
                            score = 0.5 + 0.5 * (matches / len(expected_keys))
                        else:
                            # No keywords found but answer not empty
                            score = 0.5
                    else:
                        # No keywords to match, award 0.5 for non-empty answer
                        score = 0.5
                else:
                    # Empty response
                    score = 0.0
            elif q_type == "CODE":
                code_response = getattr(answer_obj, "code", answer_obj)
                # Look for exact match to expected answer if present
                expected_code = None
                if isinstance(q, dict):
                    expected_code = q.get("answer") or q.get("solution_code")
                else:
                    expected_code = getattr(q, "answer", None) or getattr(q, "solution_code", None)
                
                score = 1.0 if expected_code and isinstance(code_response, str) and code_response.strip() == expected_code.strip() else 0.0
            else:
                score = 0.0

            scores[i] = score  # Use integer index as key
            total += score

        return {"total": total, "breakdown": scores}
