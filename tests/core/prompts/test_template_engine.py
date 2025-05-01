import pytest
from app.core.prompts.template_engine import PromptTemplateEngine, TemplateNotFoundError

def test_register_and_render_template():
    engine = PromptTemplateEngine()
    engine.register_template("greet", "Hello, ${name}!")
    result = engine.render_template("greet", {"name": "Bob"})
    assert result == "Hello, Bob!"

def test_render_with_context_merging():
    engine = PromptTemplateEngine()
    engine.register_template("ctx", "History: ${history} - Next: ${next_task}")
    # variable only given for 'next_task', 'history' from context
    result = engine.render_template("ctx", {"next_task": "Review"}, {"history": "Old value"})
    assert "Old value" in result and "Review" in result

def test_missing_variable_raises():
    engine = PromptTemplateEngine()
    engine.register_template("missing", "Hi, ${username}")
    # context is empty, no 'username' key
    with pytest.raises(ValueError):
        engine.render_template("missing", {})

def test_template_not_found():
    engine = PromptTemplateEngine()
    with pytest.raises(TemplateNotFoundError):
        engine.render_template("not_there", {}, {})