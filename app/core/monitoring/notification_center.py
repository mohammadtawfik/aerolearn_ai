"""
Notification Center for AeroLearn AI - Stub Implementation
Location: app/core/monitoring/notification_center.py

This is a simplified stub implementation of the NotificationCenter
for compatibility with service dashboard tests.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set, Callable
import uuid
import time

# Notification categories and priorities
class NotificationCategory(Enum):
    SYSTEM = "system"
    COURSE = "course"
    ENROLLMENT = "enrollment"
    CONTENT = "content"
    PROGRESS = "progress"
    AI = "ai"
    MESSAGE = "message"
    OTHER = "other"

class NotificationPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class NotificationStatus(Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification:
    def __init__(
        self,
        title: str,
        message: str,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        recipient_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        notification_id: Optional[str] = None,
    ):
        self.notification_id = notification_id or str(uuid.uuid4())
        self.timestamp = time.time()
        self.title = title
        self.message = message
        self.category = category
        self.priority = priority
        self.status = NotificationStatus.UNREAD
        self.recipient_id = recipient_id
        self.data = data or {}
        self.source = source

    def mark_read(self):
        self.status = NotificationStatus.READ

    def archive(self):
        self.status = NotificationStatus.ARCHIVED

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "timestamp": self.timestamp,
            "title": self.title,
            "message": self.message,
            "category": self.category.value,
            "priority": self.priority.name,
            "status": self.status.value,
            "recipient_id": self.recipient_id,
            "data": self.data,
            "source": self.source,
        }

# Observer/callback type for subscriptions
NotificationCallback = Callable[[Notification], None]

class NotificationCenter:
    """
    Stub implementation of NotificationCenter that maintains the same interface
    but with simplified functionality for testing purposes.
    """
    def __init__(self):
        self._notifications = []
        self._subscriptions = {}

    def subscribe(
        self,
        subscriber_id: str,
        categories: Optional[Set[NotificationCategory]] = None,
        priorities: Optional[Set[NotificationPriority]] = None,
        callback: Optional[NotificationCallback] = None,
    ):
        self._subscriptions[subscriber_id] = {
            'categories': categories or set(NotificationCategory),
            'priorities': priorities or set(NotificationPriority),
            'callback': callback
        }

    def unsubscribe(self, subscriber_id: str):
        if subscriber_id in self._subscriptions:
            del self._subscriptions[subscriber_id]

    def notify(self, notification: Notification):
        self._notifications.append(notification)
        # Call callbacks for matching subscribers
        for subscriber_id, sub in self._subscriptions.items():
            if notification.category in sub['categories'] and notification.priority in sub['priorities']:
                if sub['callback']:
                    sub['callback'](notification)

    def get_notifications(self, recipient_id: str, unread_only: bool = False) -> List[Notification]:
        if unread_only:
            return [n for n in self._notifications if n.recipient_id == recipient_id and n.status == NotificationStatus.UNREAD]
        return [n for n in self._notifications if n.recipient_id == recipient_id]

    def archive_notification(self, recipient_id: str, notification_id: str) -> bool:
        for n in self._notifications:
            if n.notification_id == notification_id and n.recipient_id == recipient_id:
                n.archive()
                return True
        return False

    def mark_as_read(self, recipient_id: str, notification_id: str) -> bool:
        for n in self._notifications:
            if n.notification_id == notification_id and n.recipient_id == recipient_id:
                n.mark_read()
                return True
        return False

    def search_notifications(
        self,
        recipient_id: str,
        category: Optional[NotificationCategory] = None,
        status: Optional[NotificationStatus] = None
    ) -> List[Notification]:
        results = []
        for n in self._notifications:
            if n.recipient_id == recipient_id:
                if (category is None or n.category == category) and \
                   (status is None or n.status == status):
                    results.append(n)
        return results

# Singleton export
notification_center = NotificationCenter()
