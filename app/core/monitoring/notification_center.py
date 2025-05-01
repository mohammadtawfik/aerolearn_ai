"""
Notification Center for AeroLearn AI
Location: app/core/monitoring/notification_center.py

This file implements a centralized notification hub with support for:
- Notification categories and priority levels
- Subscriptions for components/users
- Notification history management
- Event-driven integration points

NOTE: Integrations with events and UI to follow after core logic review.
"""

from enum import Enum, auto
from typing import Callable, List, Dict, Any, Optional, Set
import threading
import time
import uuid

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

# Notification data structure
class Notification:
    def __init__(
        self,
        title: str,
        message: str,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        recipient_id: Optional[str] = None,  # user_id, group_id, or component_id
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,  # What component/system generated this
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

class Subscription:
    def __init__(
        self,
        subscriber_id: str,  # user_id or component_id
        categories: Optional[Set[NotificationCategory]] = None,
        priorities: Optional[Set[NotificationPriority]] = None,
        callback: Optional[NotificationCallback] = None,
    ):
        self.subscriber_id = subscriber_id
        self.categories = categories or set(NotificationCategory)
        self.priorities = priorities or set(NotificationPriority)
        self.callback = callback  # Optional: on notification delivery

    def matches(self, notification: Notification) -> bool:
        return (
            notification.category in self.categories and
            notification.priority in self.priorities
        )

class NotificationHistory:
    """
    Stores and manages notification history per recipient/component.
    Supports retrieval, search, and archival.
    Thread-safe.
    """
    def __init__(self):
        self._history: Dict[str, List[Notification]] = {}
        self._lock = threading.Lock()

    def add(self, recipient_id: str, notification: Notification):
        with self._lock:
            self._history.setdefault(recipient_id, []).append(notification)

    def get(self, recipient_id: str, unread_only: bool = False) -> List[Notification]:
        with self._lock:
            notifs = self._history.get(recipient_id, []).copy()
        if unread_only:
            return [n for n in notifs if n.status == NotificationStatus.UNREAD]
        return notifs

    def search(
        self,
        recipient_id: str,
        category: Optional[NotificationCategory] = None,
        status: Optional[NotificationStatus] = None
    ) -> List[Notification]:
        with self._lock:
            results = []
            for n in self._history.get(recipient_id, []):
                if (category is None or n.category == category) and \
                   (status is None or n.status == status):
                    results.append(n)
            return results

class NotificationCenter:
    """
    Central notification hub:
    - Maintains subscriptions (per category/priority)
    - Delivers notifications
    - Manages notification history and status
    - Thread-safe.
    """
    def __init__(self):
        self._subscriptions: Dict[str, List[Subscription]] = {}
        self._history = NotificationHistory()
        self._lock = threading.Lock()

    def subscribe(
        self,
        subscriber_id: str,
        categories: Optional[Set[NotificationCategory]] = None,
        priorities: Optional[Set[NotificationPriority]] = None,
        callback: Optional[NotificationCallback] = None,
    ):
        sub = Subscription(
            subscriber_id=subscriber_id,
            categories=categories,
            priorities=priorities,
            callback=callback
        )
        with self._lock:
            self._subscriptions.setdefault(subscriber_id, []).append(sub)

    def unsubscribe(self, subscriber_id: str):
        with self._lock:
            self._subscriptions.pop(subscriber_id, None)

    def notify(self, notification: Notification):
        """
        Deliver a notification:
        - For direct notifications (recipient_id): Always stores in recipient's history, and calls callbacks if any matching subscriptions.
        - For broadcast (recipient_id=None): Deliver/store ONLY to subscribers whose subscriptions match.
        """
        delivered = set()
        with self._lock:
            # Case 1: Direct notification to specific recipient
            if notification.recipient_id:
                # Always store direct notifications in recipient's history
                self._history.add(notification.recipient_id, notification)
                # Deliver to any subscribers (callbacks) with matching filters
                subs = self._subscriptions.get(notification.recipient_id, [])
                for sub in subs:
                    if sub.matches(notification) and sub.callback:
                        sub.callback(notification)
                        delivered.add(notification.recipient_id)
            else:
                # Case 2: Broadcast - deliver to anyone with a matching subscription
                for subscriber_id, subs in self._subscriptions.items():
                    for sub in subs:
                        if sub.matches(notification):
                            self._history.add(subscriber_id, notification)
                            if sub.callback:
                                sub.callback(notification)
                            delivered.add(subscriber_id)
                if not delivered:
                    # No subscriber matched: Store as global broadcast for tracking
                    self._history.add("broadcast", notification)

    def get_notifications(self, recipient_id: str, unread_only: bool = False) -> List[Notification]:
        return self._history.get(recipient_id, unread_only)

    def archive_notification(self, recipient_id: str, notification_id: str) -> bool:
        notifs = self._history.get(recipient_id)
        for n in notifs:
            if n.notification_id == notification_id:
                n.archive()
                return True
        return False

    def mark_as_read(self, recipient_id: str, notification_id: str) -> bool:
        notifs = self._history.get(recipient_id)
        for n in notifs:
            if n.notification_id == notification_id:
                n.mark_read()
                return True
        return False

    def search_notifications(
        self,
        recipient_id: str,
        category: Optional[NotificationCategory] = None,
        status: Optional[NotificationStatus] = None
    ) -> List[Notification]:
        return self._history.search(recipient_id, category, status)

# Singleton export
notification_center = NotificationCenter()

"""
To integrate:
- Listen to events from EventBus (see integrations/events/event_bus.py)
- Provide UI widget (see app/ui/student/widgets or app/ui/common)
- Add API for triggering and retrieving notifications
"""
