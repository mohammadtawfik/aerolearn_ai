# Location: /docs/user_guides/conversation_usage.md
# AeroLearn Conversational AI – User Guide

## Introduction

This guide shows how to work with AeroLearn AI’s Conversational system for both end-users and developers.

## For Users

### Starting a Conversation

- Conversations are started by your authenticated user/session.
- Each session returns a unique session ID.
- All your questions and AI’s replies are logged (with privacy controls in place).

### Privacy Controls

- Conversations can be ended at any moment, and all sensitive memory/history is wiped.
- Privacy levels can be set per session – e.g., “standard”, “locked”, “relaxed”.

## For Developers

### Starting and Managing Sessions

```python
from app.core.ai.conversation import ConversationManager

manager = ConversationManager()
session_id = manager.start_session("student123", privacy_level="standard")
```

### Adding Input and Handling Responses

```python
response = manager.handle_input(session_id, "What is Bernoulli's equation?")
print(response)  # Example: Echo or handler output
```

### Switching Handlers

```python
def my_tutor_handler(input, user_id, state, extra):
    # Custom response logic per component
    return "This is your tutoring handler!"

manager.register_handler("tutor", my_tutor_handler)
manager.switch_handler(session_id, "tutor")
response = manager.handle_input(session_id, "Show me module 2 content")
```

### Accessing Session State

```python
state = manager.get_state(session_id)
print(state.as_dict())
```

### Privacy & Cleanup

```python
manager.end_session(session_id, wipe_history=True)
```

## Testing and Extension

- See `/tests/core/ai/test_conversation.py` for unit tests and usage samples.
- Register new handlers for additional topics (e.g., admin, QA pairs).
- Extend for persistent storage and analytics as needed.

## Troubleshooting

- Ensure your environment includes all dependencies.
- Unit tests should pass for this module, confirming correct operation.