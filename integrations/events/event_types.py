"""
Event type definitions for the AeroLearn AI event system.

This module defines the event classes and types used throughout the system for
inter-component communication. It provides a type-safe way to define and handle events.

Event types can be accessed either through the EventType enum (for type checking and IDE support)
or through the category-specific classes (SystemEventType, ContentEventType, etc.) for
organizational clarity.
"""
import uuid
import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List, Type


class EventType(enum.Enum):
    """
    General event type enumeration for core system/event bus usage.
    Provides a centralized enum for all event types across categories.
    
    For organizational clarity, category-specific event type classes
    like SystemEventType, ContentEventType, etc. are also available.
    """
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_COMPONENT_REGISTERED = "system.component.registered"
    SYSTEM_COMPONENT_UNREGISTERED = "system.component.unregistered"
    SYSTEM_COMPONENT_ERROR = "system.component.error"
    SYSTEM_INTEGRATION_ERROR = "system.integration.error"
    
    # Content events
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    CONTENT_INDEXED = "content.indexed"
    CONTENT_ANALYZED = "content.analyzed"
    CONTENT_SIMILARITY_DETECTED = "content.similarity.detected"
    
    # User events
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    USER_PROFILE_UPDATED = "user.profile.updated"
    USER_PERMISSION_CHANGED = "user.permission.changed"
    USER_PROGRESS_UPDATED = "user.progress.updated"
    
    # AI events
    AI_QUERY_PROCESSED = "ai.query.processed"
    AI_CONTENT_ENHANCED = "ai.content.enhanced"
    AI_RECOMMENDATION_GENERATED = "ai.recommendation.generated"
    AI_MODEL_UPDATED = "ai.model.updated"


class EventPriority(enum.IntEnum):
    """Event priority levels for determining handling order."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class EventCategory(enum.Enum):
    """Categories for grouping related events."""
    SYSTEM = "system"
    CONTENT = "content"
    USER = "user"
    AI = "ai"
    UI = "ui"
    STORAGE = "storage"
    AUTH = "auth"
    INTEGRATION = "integration"


@dataclass
class Event:
    """Base class for all events in the system."""
    event_type: str
    category: EventCategory
    source_component: str
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_persistent: bool = False
    
    def serialize(self) -> Dict[str, Any]:
        """Convert the event to a serializable dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "category": self.category.value,
            "source_component": self.source_component,
            "data": self.data,
            "priority": int(self.priority),
            "timestamp": self.timestamp.isoformat(),
            "is_persistent": self.is_persistent
        }
    
    @classmethod
    def deserialize(cls, event_data: Dict[str, Any]) -> 'Event':
        """Recreate an event from a serialized dictionary."""
        return cls(
            event_type=event_data["event_type"],
            category=EventCategory(event_data["category"]),
            source_component=event_data["source_component"],
            data=event_data["data"],
            priority=EventPriority(event_data["priority"]),
            timestamp=datetime.fromisoformat(event_data["timestamp"]),
            event_id=event_data["event_id"],
            is_persistent=event_data.get("is_persistent", False)
        )


# System Events
@dataclass
class SystemEvent(Event):
    """System-level events related to application lifecycle and operations."""
    def __init__(self, event_type: str, source_component: str, data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=event_type,
            category=EventCategory.SYSTEM,
            source_component=source_component,
            data=data,
            **kwargs
        )


# Content Events
@dataclass
class ContentEvent(Event):
    """Events related to educational content operations."""
    def __init__(self, event_type: str, source_component: str, data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=event_type,
            category=EventCategory.CONTENT,
            source_component=source_component,
            data=data,
            **kwargs
        )


# User Events
@dataclass
class UserEvent(Event):
    """Events related to user actions and profile changes."""
    def __init__(self, event_type: str, source_component: str, data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=event_type,
            category=EventCategory.USER,
            source_component=source_component,
            data=data,
            **kwargs
        )


# AI Events
@dataclass
class AIEvent(Event):
    """Events related to AI operations and intelligence."""
    def __init__(self, event_type: str, source_component: str, data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=event_type,
            category=EventCategory.AI,
            source_component=source_component,
            data=data,
            **kwargs
        )


# UI Events
@dataclass
class UIEvent(Event):
    """Events related to user interface interactions."""
    def __init__(self, event_type: str, source_component: str, data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=event_type,
            category=EventCategory.UI,
            source_component=source_component,
            data=data,
            **kwargs
        )


# Common System Events
class SystemEventType:
    """Common system event type constants."""
    STARTUP = "system.startup"
    SHUTDOWN = "system.shutdown"
    COMPONENT_REGISTERED = "system.component.registered"
    COMPONENT_UNREGISTERED = "system.component.unregistered"
    COMPONENT_ERROR = "system.component.error"
    INTEGRATION_ERROR = "system.integration.error"


# Common Content Events
class ContentEventType:
    """Common content event type constants."""
    CREATED = "content.created"
    UPDATED = "content.updated"
    DELETED = "content.deleted"
    INDEXED = "content.indexed"
    ANALYZED = "content.analyzed"
    SIMILARITY_DETECTED = "content.similarity.detected"


# Common User Events
class UserEventType:
    """Common user event type constants."""
    LOGGED_IN = "user.logged_in"
    LOGGED_OUT = "user.logged_out"
    PROFILE_UPDATED = "user.profile.updated"
    PERMISSION_CHANGED = "user.permission.changed"
    PROGRESS_UPDATED = "user.progress.updated"


# Common AI Events
class AIEventType:
    """Common AI event type constants."""
    QUERY_PROCESSED = "ai.query.processed"
    CONTENT_ENHANCED = "ai.content.enhanced"
    RECOMMENDATION_GENERATED = "ai.recommendation.generated"
    MODEL_UPDATED = "ai.model.updated"
