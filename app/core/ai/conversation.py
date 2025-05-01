

# File location: /app/core/ai/conversation.py  
"""
Conversational AI entry point and session manager — AeroLearn AI.

This upgrade completes Task 14.1 requirements:
- Conversation flow management with state persistence
- Context tracking and memory
- Session & conversation history with privacy controls
- Pluggable, handler-based flow routing for component-specific logic

Supersedes previous basic Conversation/ConversationManager implementation.
"""

from typing import Dict, Any, Optional, List, Callable
import time
import uuid
import threading

# Pluggable user validation — allow swapping with real DB or IAM later
def default_user_validator(user_id: str) -> bool:
    # TODO: Integrate real user DB verification (now: allow nonempty)
    return bool(user_id)

class InMemoryConversationStore:
    """Pluggable (currently in-memory) session persistence."""
    def __init__(self):
        self._store = {}
        self._lock = threading.RLock()
        
    def get(self, session_id: str):
        with self._lock:
            return self._store.get(session_id)
    
    def set(self, session_id: str, state):
        with self._lock:
            self._store[session_id] = state
    
    def delete(self, session_id: str):
        with self._lock:
            self._store.pop(session_id, None)

    def all_sessions(self):
        with self._lock:
            return list(self._store.keys())

class ConversationContext:
    """Tracks per-session dynamic memory/state."""
    def __init__(self):
        self.memory = {}
        
    def set(self, key: str, value: Any):
        self.memory[key] = value
        
    def get(self, key: str, default=None):
        return self.memory.get(key, default)
    
    def clear(self):
        self.memory = {}

class ConversationHistory:
    """Tracks user-bot conversation with privacy settings.
    
    add_turn now accepts an optional 'metadata' field,
    which can store extra dict information for each turn.
    """
    def __init__(self, privacy_level: str = "standard"):
        self.turns = []  # List[Dict[str, Any]], e.g. {"role": "user", "text": "...", "metadata": {...}}
        self.privacy_level = privacy_level

    def add_turn(self, role: str, text: str, metadata: dict = None):
        entry = {
            "role": role, 
            "text": text, 
            "timestamp": time.time()
        }
        if metadata is not None:
            entry["metadata"] = metadata
        self.turns.append(entry)

    def get_history(self, limit: int = 20):
        return self.turns[-limit:]

    def clear(self):
        self.turns = []

class ConversationState:
    """
    Full persistent snapshot for user session.
    """
    def __init__(self, session_id: Optional[str]=None, user_id: Optional[str]=None, privacy_level: str="standard"):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.context = ConversationContext()
        self.history = ConversationHistory(privacy_level=privacy_level)
        self.last_active_ts = time.time()
        self.active_handler = None   # For handler routing
    
    def as_dict(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "context": self.context.memory,
            "history": self.history.get_history(),
            "last_active_ts": self.last_active_ts,
            "active_handler": self.active_handler,
        }
    
    def clear_privacy_sensitive(self):
        self.context.clear()
        self.history.clear()

class ConversationManager:
    """
    Main orchestrator for conversational AI sessions.
    Implements flow/component handler routing, privacy-aware state, and persistence.
    """
    def __init__(self, store: Optional[InMemoryConversationStore] = None, user_validator: Callable[[str], bool]=default_user_validator):
        self._store = store or InMemoryConversationStore()
        self._handlers: Dict[str, Callable[[str, str, ConversationState, Dict], str]] = {}
        self._default_handler = "default"
        self._user_validator = user_validator
    
    def register_handler(self, label: str, handler_fn: Callable[[str, str, ConversationState, Dict], str]):
        self._handlers[label] = handler_fn

    def set_default_handler(self, label: str):
        self._default_handler = label

    def start_session(self, user_id: Optional[str], privacy_level: str="standard") -> str:
        if not self._user_validator(user_id):
            raise ValueError(f"User ID '{user_id}' is not allowed.")
        state = ConversationState(user_id=user_id, privacy_level=privacy_level)
        self._store.set(state.session_id, state)
        return state.session_id

    def end_session(self, session_id: str, wipe_history: bool=True):
        state = self._store.get(session_id)
        if state and wipe_history:
            state.clear_privacy_sensitive()
        self._store.delete(session_id)

    def get_state(self, session_id: str) -> Optional[ConversationState]:
        return self._store.get(session_id)

    def list_active_sessions(self):
        return self._store.all_sessions()

    def handle_input(self, session_id: str, user_input: str, extra: Optional[Dict]=None) -> str:
        """
        Route user input: look up session, route to current or default handler, return bot response.
        """
        extra = extra or {}
        state = self._store.get(session_id)
        if not state:
            raise ValueError(f"No session with id {session_id}")
        state.last_active_ts = time.time()
        state.history.add_turn('user', user_input)
        handler_label = state.active_handler or self._default_handler
        handler = self._handlers.get(handler_label)
        if handler is None:
            raise ValueError(f"No handler registered for label '{handler_label}'")
        response = handler(user_input, state.user_id, state, extra)
        state.history.add_turn('bot', response)
        return response

    def switch_handler(self, session_id: str, handler_label: str):
        state = self._store.get(session_id)
        if state:
            state.active_handler = handler_label

    def set_privacy_level(self, session_id: str, privacy_level: str):
        state = self._store.get(session_id)
        if state:
            state.history.privacy_level = privacy_level

# Example: default handler for demo
def default_handler(user_input, user_id, state: ConversationState, extra):
    return f"Echo: {user_input}"

# Singleton instance for main app usage
manager = ConversationManager()
manager.register_handler("default", default_handler)

"""
EXPLICIT SAVE LOCATION: This file replaces and extends all prior logic in /app/core/ai/conversation.py 
per specs in /docs/development/day14_plan.md: ALL conversational AI entry/manager code must go here.
"""

