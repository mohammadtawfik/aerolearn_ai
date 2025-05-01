"""
Unit tests for conversation initialization (task 12.4).
Save this file as: /tests/unit/core/ai/test_conversation.py

If your conversation module is elsewhere (e.g., core/conversation/), update the import paths and location appropriately.
"""

import pytest

# Import the conversation class/functionality to be tested
# Example import – update as appropriate to real module!
from app.core.ai.conversation import start_new_conversation, Conversation, ConversationManager

def test_start_new_conversation_returns_unique_id():
    """Test that starting a new conversation creates a new ID each time."""
    conv_id1 = start_new_conversation(user_id="student123")
    conv_id2 = start_new_conversation(user_id="student123")
    assert conv_id1 != conv_id2
    assert isinstance(conv_id1, str)
    assert isinstance(conv_id2, str)

def test_new_conversation_initial_state():
    """Test that a new conversation has an expected initial state (empty history, correct user ID, etc.)."""
    user_id = "prof456"
    manager = ConversationManager()
    conv = manager.create_conversation(user_id=user_id)
    assert conv.user_id == user_id
    assert conv.history == []
    assert conv.is_active

def test_conversation_manager_tracks_conversations():
    """Test that ConversationManager keeps track of active conversations."""
    manager = ConversationManager()
    user_id = "student789"
    conv = manager.create_conversation(user_id=user_id)
    found = manager.get_conversation(conv.conversation_id)
    assert found is conv

def test_error_on_invalid_user():
    """Test handling when starting a conversation with a nonexistent user."""
    manager = ConversationManager()
    invalid_user = "ghost999"
    with pytest.raises(ValueError):
        manager.create_conversation(user_id=invalid_user)