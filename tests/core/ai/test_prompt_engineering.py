import pytest

from app.core.ai.prompt_engineering import PromptEngineering

@pytest.fixture
def prompt_engineering():
    # Each test gets a fresh instance (not singleton) for isolation
    return PromptEngineering()

def test_end_to_end_prompt_generation(prompt_engineering):
    # Register a template
    prompt_engineering.template_engine.register_template(
        "welcome",
        "Hello, ${user_name}! Today is ${day}."
    )

    variables = {"user_name": "Alice", "day": "Monday"}
    context = {"history": "last prompt was a question."}

    prompt = prompt_engineering.generate_prompt("welcome", variables, context)
    assert "Hello, Alice! Today is Monday." in prompt

def test_prompt_optimization_shortening(prompt_engineering):
    prompt = " " * 20 + "Long prompt " * 2000
    optimized = prompt_engineering.optimizer.optimize(prompt, context={"minimize_length": True})
    assert len(optimized) <= 1003  # 1000 + "..."

def test_parse_response_json(prompt_engineering):
    prompt = "Give me JSON."
    response = '{"foo": "bar"}'
    parsed = prompt_engineering.parse_response(prompt, response, expected_format="json")
    assert parsed["foo"] == "bar"

def test_parse_response_invalid_json(prompt_engineering):
    prompt = "Give me JSON."
    response = '{foo: bar}'  # Invalid JSON
    parsed = prompt_engineering.parse_response(prompt, response, expected_format="json")
    assert "error" in parsed

def test_missing_template_raises(prompt_engineering):
    with pytest.raises(Exception):
        prompt_engineering.template_engine.render_template("not_exist", {}, {})