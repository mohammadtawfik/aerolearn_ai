import pytest

# from app.core.ai.material_selection import select_personalized_materials

EXAMPLE_STUDENT = {
    "id": "stu-456",
    "level": "advanced",
    "completed_content": ["mod2", "read1"],
    "learning_style": "visual"
}

CANDIDATE_CONTENT = [
    {"id": "vid1", "type": "Lesson", "format": "video", "tags": ["visual"], "difficulty": "medium"},
    {"id": "read1", "type": "Reading", "format": "reading", "tags": ["reading"], "difficulty": "easy"},
    {"id": "quiz2", "type": "Quiz", "tags": ["applied"], "difficulty": "hard"},
]

def validate_material_selection_output(result, student_id, expected_len=None):
    # Required fields
    assert isinstance(result, dict)
    assert result.get("student_id") == student_id
    assert "selected_materials" in result and isinstance(result["selected_materials"], list)
    if expected_len is not None:
        assert len(result["selected_materials"]) == expected_len
    for idx, step in enumerate(result["selected_materials"], 1):
        assert isinstance(step["order"], int)
        assert step["order"] == idx
        assert "content_id" in step and isinstance(step["content_id"], str)
        assert "content_type" in step and isinstance(step["content_type"], str)
        assert "reason" in step and isinstance(step["reason"], str) and step["reason"]
    assert "generated_at" in result and isinstance(result["generated_at"], str)
    assert "selection_context" in result and isinstance(result["selection_context"], dict)
    # Test RFC3339 format for generated_at
    import re
    rfc_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z"
    assert re.match(rfc_pattern, result["generated_at"])

def test_style_filter_and_basic_contract():
    """Selection returns only items matching required learning style, correct fields, ordered/reasoned."""
    from app.core.ai.material_selection import select_personalized_materials
    context = {"required_style": "visual"}
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT, context=context, max_items=5)
    validate_material_selection_output(out, EXAMPLE_STUDENT["id"], expected_len=1)
    step = out["selected_materials"][0]
    assert step["content_id"] == "vid1"
    assert "visual" in step.get("reason", "")

def test_exclude_completed_and_explicit_exclusions():
    """Completed and explicitly excluded materials are not present in result."""
    from app.core.ai.material_selection import select_personalized_materials
    context = {"exclude_ids": ["quiz2"]}
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT, context=context, max_items=5)
    ids = {step["content_id"] for step in out["selected_materials"]}
    assert "quiz2" not in ids
    assert "read1" not in ids  # completed
    assert "vid1" in ids

def test_priority_tags_changes_order_or_score():
    """Materials with priority tags should get higher ranking/score."""
    from app.core.ai.material_selection import select_personalized_materials
    context = {"prioritize_tags": ["applied"]}
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT, context=context, max_items=3)
    # quiz2 should rank higher or have a higher score
    ids = [step["content_id"] for step in out["selected_materials"]]
    quiz2_idx = ids.index("quiz2") if "quiz2" in ids else None
    vid1_idx = ids.index("vid1") if "vid1" in ids else None
    assert (quiz2_idx is not None and vid1_idx is not None and quiz2_idx < vid1_idx) or (
        [step for step in out["selected_materials"] if step["content_id"] == "quiz2" and step.get("score", 0) > 0]
    )

def test_length_cap():
    """Enforces max_items and orders sequence integers."""
    from app.core.ai.material_selection import select_personalized_materials
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT * 5, max_items=2)
    assert len(out["selected_materials"]) == 2
    for i, step in enumerate(out["selected_materials"], 1):
        assert step["order"] == i

def test_reason_field_explanation():
    """Every selected material must have a non-empty rationale string."""
    from app.core.ai.material_selection import select_personalized_materials
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT)
    for step in out["selected_materials"]:
        assert step["reason"]

def test_timestamp_rfc3339():
    from app.core.ai.material_selection import select_personalized_materials
    out = select_personalized_materials(EXAMPLE_STUDENT, CANDIDATE_CONTENT)
    import re
    rfc_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z"
    assert re.match(rfc_pattern, out["generated_at"])