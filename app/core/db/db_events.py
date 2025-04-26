"""
Database Event Hooks for Event Bus Integration (Task 3.1)
---------------------------------------------------------

This module connects SQLAlchemy ORM events (insert/update/delete) for tracked models 
to the AeroLearn AI event system. 

- Hooks are registered for all mapped models in app.core.db.schema.
- On DB entity changes, a content.event (CREATED, UPDATED, DELETED) is published to the EventBus.
- Each event includes model, PK, and change data in the payload.

Place this file at: `app/core/db/db_events.py`

To activate event publishing, import this module after SQLAlchemy models are loaded (e.g., at app startup):

    from app.core.db import db_events

Requires: event bus to be started (`await EventBus().start()`).

"""

import logging
from sqlalchemy import event
from sqlalchemy.orm import Mapper
from app.core.db import schema
from integrations.events.event_bus import EventBus
from integrations.events.event_types import (
    ContentEvent, ContentEventType, EventPriority
)

logger = logging.getLogger(__name__)


def _get_primary_key(obj):
    """Helper to retrieve primary key(s) as a dict."""
    pk_dict = {}
    for pk_column in obj.__table__.primary_key:
        pk_dict[pk_column.name] = getattr(obj, pk_column.name)
    return pk_dict

async def _publish_db_event(event_type: str, instance, old_data=None):
    bus = EventBus()
    if not bus._is_running:
        logger.warning("Event bus is not running; cannot publish DB events.")
        return

    data = {
        "model": instance.__class__.__name__,
        "primary_key": _get_primary_key(instance),
        "values": {c.name: getattr(instance, c.name) for c in instance.__table__.columns},
    }
    if old_data:
        data["old_values"] = old_data

    event_obj = ContentEvent(
        event_type=event_type,
        source_component="db",
        data=data,
        priority=EventPriority.NORMAL,
        is_persistent=False  # Set to True if you'd like all mutations to persist in event history
    )
    await bus.publish(event_obj)


def register_db_event_hooks():
    """
    Register all hooks for after_insert, after_update, after_delete
    on all ORM models found in schema.Base registry.
    """
    # List of models to monitor. (You can customize/whitelist as needed)
    monitored_models = [
        m.class_ for m in schema.Base.registry.mappers
    ]

    for model in monitored_models:
        # Insert (CREATE)
        @event.listens_for(model, "after_insert")
        def after_insert(mapper, connection, target):
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(_publish_db_event(ContentEventType.CREATED, target))

        # Update
        @event.listens_for(model, "after_update")
        def after_update(mapper, connection, target):
            # Optionally, you may want to include before/after values
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(_publish_db_event(ContentEventType.UPDATED, target))

        # Delete
        @event.listens_for(model, "after_delete")
        def after_delete(mapper, connection, target):
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(_publish_db_event(ContentEventType.DELETED, target))


# Register hooks immediately on import (you can also call register_db_event_hooks() manually)
register_db_event_hooks()

# Usage / Integration Note:
# Simply ensure this file is imported during your application startup (after models are loaded),
# and your event bus is running. Every insert, update, and delete on your database will now auto-publish
# to the event bus for content-related events.