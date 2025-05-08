import pytest
import datetime

# Import path to be replaced once implementation exists
# from app.core.ai.learning_path import generate_learning_path

# ---- Protocol Test: Input and Output Structures ---- #

# Protocol-compliant student profile example
EXAMPLE_STUDENT = {
    "id": "stu-123",
    "level": "intro",
    "completed_content": ["mod1", "less1"],
    "performance": {}
}

EXAMPLE_CANDIDATE_CONTENT = [
    {"id": "less2", "type": "Lesson", "prerequisites": ["less1"], "difficulty": "easy"},
    {"id": "quiz1", "type": "Quiz", "prerequisites": ["less2"], "difficulty": "medium"},
    {"id": "mod2", "type": "Module", "prerequisites": [], "difficulty": "easy"},
]

# ---- Utility: Output Field Validation ---- #

def validate_learning_path_output(output, student_id, max_length):
    # Root fields
    assert isinstance(output, dict)
    assert output["student_id"] == student_id
    assert "generated_at" in output and isinstance(output["generated_at"], str)
    # Steps contract
    steps = output["steps"]
    assert isinstance(steps, list)
    assert len(steps) <= max_length
    last_sequence = 0
    completed = set(EXAMPLE_STUDENT["completed_content"])
    for step in steps:
        # Required fields/type
        assert set(step.keys()).issuperset({
            "order", "content_id", "content_type", "justification", "difficulty", "prerequisites_satisfied"
        })
        assert isinstance(step["order"], int) and step["order"] > 0
        assert isinstance(step["content_id"], str)
        assert isinstance(step["content_type"], str)
        assert isinstance(step["justification"], str)
        assert isinstance(step["prerequisites_satisfied"], bool)
        # Sequencing
        if last_sequence:
            assert step["order"] == last_sequence + 1
        last_sequence = step["order"]
        # Prerequisite logic
        cid = step["content_id"]
        cdef = next(c for c in EXAMPLE_CANDIDATE_CONTENT if c["id"] == cid)
        prereqs_met = all(pid in completed for pid in cdef.get("prerequisites", []))
        assert step["prerequisites_satisfied"] == prereqs_met
        completed.add(cid)

# ---- Protocol Test Cases ---- #

def test_simple_recommendation_protocol_contract():
    """Test protocol contract for minimal input."""
    from app.core.ai.learning_path import generate_learning_path

    out = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT, max_length=3)
    validate_learning_path_output(out, EXAMPLE_STUDENT["id"], 3)
    # Path contains only content with prerequisites satisfied
    for step in out["steps"]:
        assert step["prerequisites_satisfied"]

def test_adaptive_path_changes_for_adaptivity_toggle():
    """Adaptive mode should alter the selected path or ordering when enabled."""
    from app.core.ai.learning_path import generate_learning_path

    ordering_off = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT, adaptivity=False)
    ordering_on = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT, adaptivity=True)
    assert ordering_off != ordering_on or len(ordering_off["steps"]) == 0

def test_path_respects_max_length():
    """Output never exceeds max_length, even if more candidates are available."""
    from app.core.ai.learning_path import generate_learning_path

    out = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT, max_length=1)
    assert len(out["steps"]) == 1

def test_justification_and_metadata_present():
    """Each path step should provide justification and required metadata fields."""
    from app.core.ai.learning_path import generate_learning_path

    out = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT)
    for step in out["steps"]:
        assert isinstance(step["justification"], str) and step["justification"]
        assert isinstance(step["difficulty"], (str, int))

def test_path_for_unsatisfiable_prerequisites():
    """Unreachable content must not appear if dependencies are not met."""
    from app.core.ai.learning_path import generate_learning_path

    # Candidate with unsatisfiable prereqs (never included)
    candidates = [{"id": "extra", "type": "Quiz", "prerequisites": ["nonexistent"], "difficulty": "easy"}]
    output = generate_learning_path(EXAMPLE_STUDENT, candidates)
    assert output["steps"] == []

def test_output_timestamp_format():
    from app.core.ai.learning_path import generate_learning_path

    out = generate_learning_path(EXAMPLE_STUDENT, EXAMPLE_CANDIDATE_CONTENT)
    # Basic RFC3339 format check for 'generated_at'
    import re
    rfc_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z"
    assert re.match(rfc_pattern, out["generated_at"])

# -- Extend with more test cases as protocol evolves --