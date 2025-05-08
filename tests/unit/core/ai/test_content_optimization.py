import pytest
import datetime

# from app.core.ai.content_optimization import suggest_content_optimizations

EXAMPLE_CONTENT = {
    "id": "less3",
    "type": "Lesson",
    "body": "The cat sat.",
    "metadata": {"difficulty": "easy"}
}

EXTRA_CONTEXT = {"editor_id": "prof001", "goals": ["clarity", "engagement"]}
TEMPLATES = ["clarity", "engagement"]

def validate_suggestion_output(result, content_id, require_suggestions=True):
    assert isinstance(result, dict)
    assert result.get("content_id") == content_id
    # Suggestions section always present as list
    assert "suggestions" in result and isinstance(result["suggestions"], list)
    if require_suggestions:
        assert len(result["suggestions"]) > 0
        for step in result["suggestions"]:
            assert set(step.keys()).issuperset({"template", "before", "after", "explanation"})
            assert isinstance(step["template"], str)
            assert isinstance(step["before"], str)
            assert isinstance(step["after"], str)
            assert isinstance(step["explanation"], str)
    else:
        assert result["suggestions"] == []

    # Overall analysis
    assert "overall_analysis" in result and isinstance(result["overall_analysis"], dict)
    oa = result["overall_analysis"]
    assert "tags" in oa and isinstance(oa["tags"], list)
    if "preview_html" in oa:
        assert isinstance(oa["preview_html"], str)
    assert "generated_at" in result
    # RFC3339 timestamp
    import re
    rfc_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z"
    assert re.match(rfc_pattern, result["generated_at"])

@pytest.mark.parametrize("content_item,templates,context", [
    (EXAMPLE_CONTENT, TEMPLATES, EXTRA_CONTEXT),
    (EXAMPLE_CONTENT, None, None),
])
def test_basic_contract_and_templates(content_item, templates, context):
    """Field contract and at least one suggestion (if templates present)."""
    from app.core.ai.content_optimization import suggest_content_optimizations

    result = suggest_content_optimizations(content_item, templates=templates, context=context)
    validate_suggestion_output(result, content_item["id"])

def test_no_op_when_content_already_optimized():
    """If body is already optimal for requested templates/goals, must return empty suggestion list."""
    from app.core.ai.content_optimization import suggest_content_optimizations
    # Heuristic: if 'body' already matches a set of template-tested phrases
    content = {
        "id": "opt1",
        "type": "Lesson",
        "body": "This content is already optimized for clarity and engagement!",
        "metadata": {}
    }
    # Request templates for which the content is presumed optimal
    result = suggest_content_optimizations(content, templates=["clarity", "engagement"])
    validate_suggestion_output(result, "opt1", require_suggestions=False)

def test_field_types_and_analysis_present():
    from app.core.ai.content_optimization import suggest_content_optimizations

    result = suggest_content_optimizations(EXAMPLE_CONTENT)
    assert isinstance(result["content_id"], str)
    assert isinstance(result["suggestions"], list)
    oa = result["overall_analysis"]
    assert isinstance(oa, dict)
    assert "tags" in oa and isinstance(oa["tags"], list)
    if "original_score" in oa:
        assert isinstance(oa["original_score"], (float, int))
    if "expected_score" in oa:
        assert isinstance(oa["expected_score"], (float, int))

def test_preview_html_present_if_supported():
    from app.core.ai.content_optimization import suggest_content_optimizations

    result = suggest_content_optimizations(EXAMPLE_CONTENT, templates=["clarity"])
    assert "preview_html" in result["overall_analysis"]
    assert isinstance(result["overall_analysis"]["preview_html"], str)

def test_timestamp_rfc3339():
    from app.core.ai.content_optimization import suggest_content_optimizations

    result = suggest_content_optimizations(EXAMPLE_CONTENT)
    import re
    rfc_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z"
    assert re.match(rfc_pattern, result["generated_at"])