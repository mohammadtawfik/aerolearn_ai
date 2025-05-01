# Location: /tests/core/ai/test_conversation.py
# Unit tests for ConversationManager, ConversationState and supporting classes in /app/core/ai/conversation.py
# Save this file as '/tests/core/ai/test_conversation.py' per code_summary.md and day14_plan.md.

import pytest
from app.core.ai.conversation import (
    ConversationManager,
    ConversationState,
    ConversationContext,
    ConversationHistory,
    InMemoryConversationStore,
)

def always_true_validator(user_id):
    return True

def always_false_validator(user_id):
    return False

def echo_handler(user_input, user_id, state, extra):
    return f"ECHO: {user_input} ({user_id})"

def make_manager(store=None, validator=always_true_validator):
    mgr = ConversationManager(store=store, user_validator=validator)
    mgr.register_handler("test_echo", echo_handler)
    mgr.set_default_handler("test_echo")
    return mgr

def test_session_creation_and_retrieval():
    mgr = make_manager()
    user_id = "student321"
    session_id = mgr.start_session(user_id)
    assert isinstance(session_id, str)
    state = mgr.get_state(session_id)
    assert state.user_id == user_id
    assert isinstance(state, ConversationState)
    assert isinstance(state.context, ConversationContext)
    assert isinstance(state.history, ConversationHistory)
    assert mgr.list_active_sessions() == [session_id]

def test_session_denies_invalid_user():
    mgr = make_manager(validator=always_false_validator)
    with pytest.raises(ValueError):
        mgr.start_session("bad_user")

def test_session_persistence_and_history():
    mgr = make_manager()
    session_id = mgr.start_session("stu42")
    # send two messages
    resp1 = mgr.handle_input(session_id, "Hi there")
    assert resp1.startswith("ECHO: Hi there")
    resp2 = mgr.handle_input(session_id, "What's the weather?")
    state = mgr.get_state(session_id)
    hist = state.history.get_history()
    # Each user input and bot reply = 2 per turn, 2 turns = 4
    assert len(hist) == 4
    assert hist[0]["role"] == "user"
    assert hist[1]["role"] == "bot"
    assert hist[-2]["text"] == "What's the weather?"
    assert hist[-1]["role"] == "bot"

def test_switch_handler():
    def handler1(inp, uid, state, extra): return "handled by 1"
    def handler2(inp, uid, state, extra): return "handled by 2"
    mgr = ConversationManager(user_validator=always_true_validator)
    mgr.register_handler("h1", handler1)
    mgr.register_handler("h2", handler2)
    mgr.set_default_handler("h1")
    sid = mgr.start_session("user9000")
    # Default handler
    assert mgr.handle_input(sid, "X") == "handled by 1"
    # Switch handler
    mgr.switch_handler(sid, "h2")
    assert mgr.handle_input(sid, "X") == "handled by 2"

def test_end_session_wipes_and_removes():
    mgr = make_manager()
    sid = mgr.start_session("wipe_test")
    mgr.handle_input(sid, "A first input")
    state = mgr.get_state(sid)
    assert len(state.history.get_history()) > 0
    mgr.end_session(sid, wipe_history=True)
    # State should be deleted from store
    assert mgr.get_state(sid) is None

def test_privacy_controls_clear_context_and_history():
    mgr = make_manager()
    sid = mgr.start_session("userZ")
    state = mgr.get_state(sid)
    # Fill up context and history
    state.context.set("location", "Moon")
    state.history.add_turn("user", "initiate privacy test")
    # End session explicitly wipe sensitive data
    mgr.end_session(sid, wipe_history=True)
    # After deletion state is gone, but if we manually check method:
    # Make a new state for simulation
    s = ConversationState(user_id="userZ")
    s.context.set("foo", "bar")
    s.history.add_turn("bot", "Hi")
    s.clear_privacy_sensitive()
    assert s.context.memory == {}
    assert s.history.get_history() == []

def test_set_and_update_privacy_level():
    mgr = make_manager()
    sid = mgr.start_session("alpha", privacy_level="locked")
    state = mgr.get_state(sid)
    assert state.history.privacy_level == "locked"
    mgr.set_privacy_level(sid, "relaxed")
    assert state.history.privacy_level == "relaxed"

def test_handle_input_invalid_session_fails():
    mgr = make_manager()
    with pytest.raises(ValueError):
        mgr.handle_input("not_a_real_id", "Hi bot")

def test_handler_registration_errors():
    mgr = ConversationManager(user_validator=always_true_validator)
    sid = mgr.start_session("bob")
    # No default handler set
    with pytest.raises(ValueError):
        mgr.handle_input(sid, "Should fail")

def test_conversation_context():
    context = ConversationContext()
    # Test setting and getting values
    context.set("name", "Alice")
    context.set("preferences", {"theme": "dark", "notifications": True})
    assert context.get("name") == "Alice"
    assert context.get("preferences")["theme"] == "dark"
    # Test default values
    assert context.get("nonexistent", "default") == "default"
    # Test clearing
    context.clear()
    assert context.memory == {}

def test_conversation_history():
    history = ConversationHistory()
    # Test adding turns
    history.add_turn("user", "Hello there")
    history.add_turn("bot", "Hi, how can I help?", metadata={"confidence": 0.95})
    hist = history.get_history()
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[0]["text"] == "Hello there"
    assert hist[1]["metadata"]["confidence"] == 0.95
    # Test clearing
    history.clear()
    assert history.get_history() == []

def test_in_memory_conversation_store():
    store = InMemoryConversationStore()
    state = ConversationState(user_id="test_user")
    state.context.set("key", "value")
    # Test saving and retrieving
    store.set("session1", state)
    retrieved = store.get("session1")
    assert retrieved.user_id == "test_user"
    assert retrieved.context.get("key") == "value"
    # Test listing sessions
    assert "session1" in store.all_sessions()
    # Test deleting
    store.delete("session1")
    assert store.get("session1") is None
    assert "session1" not in store.all_sessions()
