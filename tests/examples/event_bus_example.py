"""
Example usage of the event bus system.

This script demonstrates how to set up and use the event bus for
inter-component communication in the AeroLearn AI system.
"""
import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from integrations.events.event_bus import EventBus
from integrations.events.event_types import (
    SystemEvent, ContentEvent, UserEvent, AIEvent, 
    EventCategory, EventPriority,
    SystemEventType, ContentEventType, UserEventType
)
from integrations.events.event_subscribers import EventSubscriber, EventFilter, CallbackEventSubscriber


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemComponent(EventSubscriber):
    """Example system component that publishes and subscribes to events."""
    
    def __init__(self, component_id: str):
        """Initialize the component with a unique ID."""
        super().__init__(f"system-{component_id}")
        self.component_id = component_id
        
        # Subscribe to system events
        self.add_filter(EventFilter(
            categories=[EventCategory.SYSTEM],
            min_priority=EventPriority.NORMAL
        ))
    
    async def handle_event(self, event) -> None:
        """Handle system events."""
        logger.info(f"System component {self.component_id} received event: {event.event_type}")
        
        # Respond to specific events
        if event.event_type == SystemEventType.STARTUP:
            logger.info(f"System component {self.component_id} starting up")
        elif event.event_type == SystemEventType.SHUTDOWN:
            logger.info(f"System component {self.component_id} shutting down")


class ContentManager(EventSubscriber):
    """Example content manager component."""
    
    def __init__(self):
        """Initialize the content manager."""
        super().__init__("content-manager")
        
        # Subscribe to content events
        self.add_filter(EventFilter(
            categories=[EventCategory.CONTENT]
        ))
        
        # Also subscribe to specific system events
        self.add_filter(EventFilter(
            event_types=[SystemEventType.STARTUP, SystemEventType.SHUTDOWN]
        ))
    
    async def handle_event(self, event) -> None:
        """Handle content and system events."""
        logger.info(f"Content manager received event: {event.event_type}")
        
        # Handle specific events
        if event.event_type == ContentEventType.CREATED:
            await self.process_new_content(event.data)
        elif event.event_type == ContentEventType.UPDATED:
            await self.update_content_index(event.data)
    
    async def process_new_content(self, data: Dict[str, Any]) -> None:
        """Process newly created content."""
        content_id = data.get("content_id")
        logger.info(f"Processing new content: {content_id}")
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # After processing, publish an indexed event
        event_bus = EventBus()
        await event_bus.publish(ContentEvent(
            event_type=ContentEventType.INDEXED,
            source_component="content-manager",
            data={"content_id": content_id, "status": "indexed"}
        ))
    
    async def update_content_index(self, data: Dict[str, Any]) -> None:
        """Update content index after content update."""
        content_id = data.get("content_id")
        logger.info(f"Updating index for content: {content_id}")
        # Simulate processing time
        await asyncio.sleep(0.3)


class UserManager(EventSubscriber):
    """Example user manager component."""
    
    def __init__(self):
        """Initialize the user manager."""
        super().__init__("user-manager")
        
        # Subscribe to user events
        self.add_filter(EventFilter(
            categories=[EventCategory.USER]
        ))
    
    async def handle_event(self, event) -> None:
        """Handle user events."""
        logger.info(f"User manager received event: {event.event_type}")
        
        # Handle specific events
        if event.event_type == UserEventType.LOGGED_IN:
            logger.info(f"User logged in: {event.data.get('user_id')}")
        elif event.event_type == UserEventType.PROFILE_UPDATED:
            logger.info(f"User profile updated: {event.data.get('user_id')}")


async def run_example():
    """Run an example event flow."""
    # Create and start the event bus
    event_bus = EventBus()
    await event_bus.start()
    
    try:
        # Create and register components
        system_component = SystemComponent("main")
        content_manager = ContentManager()
        user_manager = UserManager()
        
        event_bus.register_subscriber(system_component)
        event_bus.register_subscriber(content_manager)
        event_bus.register_subscriber(user_manager)
        
        # Also register a simple callback subscriber
        event_bus.register_subscriber(CallbackEventSubscriber(
            "logger",
            lambda event: logger.debug(f"Event logged: {event.event_type}")
        ))
        
        # Start the system
        logger.info("Starting example event flow")
        
        # Publish system startup event
        await event_bus.publish(SystemEvent(
            event_type=SystemEventType.STARTUP,
            source_component="example",
            data={},
            priority=EventPriority.HIGH,
            is_persistent=True
        ))
        
        # Publish a user login event
        await event_bus.publish(UserEvent(
            event_type=UserEventType.LOGGED_IN,
            source_component="example",
            data={"user_id": "user-123", "username": "professor1"}
        ))
        
        # Publish a content creation event
        await event_bus.publish(ContentEvent(
            event_type=ContentEventType.CREATED,
            source_component="example",
            data={"content_id": "content-456", "title": "Introduction to Aerospace Engineering"}
        ))
        
        # Wait for all events to be processed
        await asyncio.sleep(1)
        
        # Get some statistics
        stats = event_bus.get_stats()
        logger.info(f"Event bus statistics: {stats}")
        
        # Publish system shutdown event
        await event_bus.publish(SystemEvent(
            event_type=SystemEventType.SHUTDOWN,
            source_component="example",
            data={},
            priority=EventPriority.HIGH
        ))
        
        # Wait for final events to be processed
        await asyncio.sleep(0.5)
    finally:
        # Always stop the event bus
        await event_bus.stop()


# In Spyder, you can run this example directly with:
# await run_example()
#
# If running as script, we'd do this:
if __name__ == "__main__":
    print("Run this example in Spyder by executing: await run_example()")
