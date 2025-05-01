# Prompt Templates API Documentation

**Location:** `/docs/api/prompt_templates.md`  
**Subsystem:** Prompt Engineering System (AeroLearn AI)

---

## Module: `app.core.prompts.template_engine`

### Class: `PromptTemplateEngine`

Handles template registration, variable/context merging, and rendering prompt strings.

#### Methods

- **`register_template(name: str, template_str: str)`**  
  Registers a new prompt template by `name`.  
  Example:
  ```python
  engine.register_template("my_template", "Hi, ${username}!")
  ```

- **`get_template(name: str) -> str`**  
  Retrieves the registered template string for `name`.  
  Raises `TemplateNotFoundError` if missing.

- **`render_template(name: str, variables: dict, context: dict = None) -> str`**  
  Renders the named template using the provided variables and (optionally) context dict.
  - Merges context into variables.
  - Raises `ValueError` if required variables are missing.
  - Raises `TemplateNotFoundError` if template not found.

#### Exceptions

- **`TemplateNotFoundError`**  
  Raised when the specified template is not registered.

---

## Module: `app.core.ai.prompt_engineering`

### Class: `PromptEngineering`

Orchestrator for prompt workflows, using template engine, optimizer, and response parser.

#### Methods

- **`generate_prompt(template_name: str, variables: dict, context: dict = None, optimize: bool = True) -> str`**  
  Generates a prompt by rendering a template, merging context, and optimizing.

- **`parse_response(prompt: str, llm_response: str, expected_format: str = None) -> dict`**  
  Parses a model (LLM) response into a dict, using the parser module.

#### Usage Example

```python
from app.core.ai.prompt_engineering import prompt_engineering
prompt = prompt_engineering.generate_prompt("my_template", {"username": "Bob"})
parsed = prompt_engineering.parse_response(prompt, '{"foo": "bar"}', expected_format="json")
```

---

## Module: `app.core.prompts.optimizers`

### Class: `PromptOptimizer`

Applies best-practice or custom-defined rules to improve prompt phrasing.

- **`optimize(prompt: str, context: dict = None) -> str`**  
  Shortens prompts, applies filters as needed.

---

## Module: `app.core.prompts.parser`

### Class: `ResponseParser`

Extracts structured meaning from raw LLM output.

- **`parse(response_text: str, expected_format: str = None) -> dict`**  
  Handles `"json"`, `"qa"`, or default fallback.  
  - For `"qa"`, see User Guide for exact keying rules.

---

## Extending the System

- Subclass `PromptTemplateEngine`, `PromptOptimizer`, or `ResponseParser` for advanced or custom behaviors.
- Register new templates at app-init or dynamically at runtime.

---

## Error Handling

- All template rendering errors propagate as `ValueError` for missing variables.
- Invalid template names throw `TemplateNotFoundError`.

---

## Test Coverage Reference

- `/tests/core/ai/test_prompt_engineering.py`
- `/tests/core/prompts/test_template_engine.py`
- `/tests/core/prompts/test_optimizers.py`
- `/tests/core/prompts/test_parser.py`