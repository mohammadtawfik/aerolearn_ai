# Prompt Engineering User Guide

**Location:** `/docs/user_guides/prompt_engineering.md`  
**Subsystem:** Prompt Engineering System (AeroLearn AI)

---

## Overview

The Prompt Engineering subsystem provides a robust and extensible pipeline for generating, optimizing, and parsing prompts intended for large language models (LLMs). This system supports variable templating, context-aware assembly, optimization strategies, and structured response parsing—all adaptable to a wide range of educational, analytical, and assistant-driven scenarios.

## Core Features

- **Template-based prompt generation**: Define and register prompts using variable placeholders for user, task, or system context insertion.
- **Context awareness**: Automatically merges additional session or historical data into prompts where variables permit.
- **Prompt optimization**: Appliances for filtering, shortening, and continuous improvement of prompt phrasing.
- **Response parsing**: Structured extraction from common LLM output formats (JSON, Q/A pairs, etc).
- **Extensible registrations**: Add your own templates, optimizers, or parsers for custom workflows.

---

## Usage Patterns

### 1. Register a Prompt Template

A template can be added at runtime or loaded at application start.

```python
from app.core.prompts.template_engine import PromptTemplateEngine

engine = PromptTemplateEngine()
engine.register_template("motivate", "Welcome ${user_name}! Ready to learn about ${topic}?")
```

### 2. Render Prompt with Variables & Context

```python
variables = {"user_name": "Alice", "topic": "Aerodynamics"}
context = {"history": "Prior topic was propulsion."}
prompt = engine.render_template("motivate", variables, context)
# Output: "Welcome Alice! Ready to learn about Aerodynamics?"
```

### 3. Generate Optimized Prompt (Full Workflow)

```python
from app.core.ai.prompt_engineering import prompt_engineering

prompt = prompt_engineering.generate_prompt(
    template_name="motivate",
    variables={"user_name": "Bob", "topic": "Lift & Drag"},
    context={"minimize_length": True}
)
```

### 4. Parse LLM Responses

```python
response = '{"success": true, "next_lesson": "Control Surfaces"}'
parsed = prompt_engineering.parse_response(prompt, response, expected_format="json")
# parsed = {"success": True, "next_lesson": "Control Surfaces"}
```
For Q/A outputs:
```python
qa_response = "Q1: What is flight?\nA1: Movement through air\nQ2: How? Lift"
parsed = prompt_engineering.parse_response(prompt, qa_response, expected_format="qa")
# parsed = {"Q1": "What is flight?", "A1": "Movement through air", "Q2": "How?", "Lift": ""}
```

---

## Extending the Subsystem

- **Custom Templates:** Add new .register_template(...) calls or support loading from file.
- **Optimizers:** Subclass `PromptOptimizer` and inject your version into `PromptEngineering`.
- **Parsers:** Subclass `ResponseParser` for custom output parsing (e.g., tables, XML, markdown).

---

## Error Handling

- Missing variables in templates raise a `ValueError`.
- Malformed expected JSON responses result in an error dict (with `"error"` field).

---

## File Map Reference (For Contributors)

| Feature                | Code Location                               | Test Location                                 |
|------------------------|---------------------------------------------|-----------------------------------------------|
| Main Orchestrator      | `/app/core/ai/prompt_engineering.py`        | `/tests/core/ai/test_prompt_engineering.py`   |
| Templates              | `/app/core/prompts/template_engine.py`      | `/tests/core/prompts/test_template_engine.py` |
| Optimizers             | `/app/core/prompts/optimizers.py`           | `/tests/core/prompts/test_optimizers.py`      |
| Parsers                | `/app/core/prompts/parser.py`               | `/tests/core/prompts/test_parser.py`          |

---

## Further Reading

- [Prompt Templates API Documentation](/docs/api/prompt_templates.md)
- AeroLearn AI [Developer Guide](../development/)