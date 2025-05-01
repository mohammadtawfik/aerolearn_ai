"""
Conversation logic for AeroLearn AI —
Implements Conversation, ConversationManager, and start_new_conversation
Save this file as: /app/core/ai/conversation.py
"""

import uuid

# Dummy user validation — in real system, link to user DB or authentication
_VALID_USERS = set(['student123', 'prof456', 'student789'])

class Conversation:
    """
    Represents a single conversation session.
    """
    def __init__(self, user_id: str):
        self.conversation_id = str(uuid.uuid4())
        self.user_id = user_id
        self.history = []
        self.is_active = True

    def add_message(self, message):
        self.history.append(message)

    def end(self):
        self.is_active = False

class ConversationManager:
    """
    Manages active and past conversations.
    """
    def __init__(self):
        self._conversations = {}

    def create_conversation(self, user_id: str):
        if user_id not in _VALID_USERS:
            raise ValueError(f"User ID '{user_id}' not recognized.")
        conv = Conversation(user_id)
        self._conversations[conv.conversation_id] = conv
        return conv

    def get_conversation(self, conversation_id: str):
        return self._conversations.get(conversation_id)

    def list_active(self):
        return [c for c in self._conversations.values() if c.is_active]

def start_new_conversation(user_id: str) -> str:
    """
    Fast API to create new conversation and return its ID.
    You may want to wire this to ConversationManager singleton in real code.
    """
    # In real use, you may want a global or injected manager; here: singleton for demo/testing
    if not hasattr(start_new_conversation, "_manager"):
        start_new_conversation._manager = ConversationManager()
    manager = start_new_conversation._manager
    conv = manager.create_conversation(user_id)
    return conv.conversation_id