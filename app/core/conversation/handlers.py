# File location: /app/core/conversation/handlers.py
"""
Example conversation handlers for component-specific tasks in AeroLearn AI.

Handlers implement (user_input, user_id, ConversationState, extra) -> str (bot-response).
Register with ConversationManager from /app/core/ai/conversation.py
"""

from app.core.ai.conversation import ConversationState

def professor_content_handler(user_input, user_id, state: ConversationState, extra):
    # Example: handles professor-specific queries
    state.context.set("last_professor_query", user_input)
    return "This is the professor upload/contribution handler. You said: " + user_input

def admin_handler(user_input, user_id, state: ConversationState, extra):
    # Example: handles admin control
    state.context.set("last_admin_cmd", user_input)
    return "Admin function called: " + user_input

def student_query_handler(user_input, user_id, state: ConversationState, extra):
    # Example: handles student queries about content
    history = state.history.get_history(5)
    return f"Student asked: {user_input}. Recent history: {history}"

# Can be expanded with real logic, knowledge, intent matching, etc.

# EXPLICIT SAVE LOCATION: Save this file as /app/core/conversation/handlers.py based on the official project structure.