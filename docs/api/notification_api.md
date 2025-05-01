# AeroLearn AI Notification Center – API Guide

**Location:** `/docs/api/notification_api.md`

## Overview

The Notification Center is a centralized hub for routing, storing, and delivering notifications in AeroLearn AI.  
It supports priority, categorization, direct/broadcast delivery, per-user history, subscriptions, and callbacks.

---

## Key Concepts

- **Notification:**  
  Represents an event/message shown to a user or component.  
- **Categories/Priorities:**  
  Structured enums control labeling and delivery filtering.
- **Subscriptions:**  
  Allows users/components to receive broadcast notifications matching their interests or needs.
- **Callback Handling:**  
  Subscribed parties can provide a callback to be called on delivery.
- **History:**  
  Every notification sent to a user (either by direct targeting or subscription) is stored in per-user history.

---

## API Surface

### Notification Creation

```python
from app.core.monitoring.notification_center import Notification, NotificationCategory, NotificationPriority

notif = Notification(
    title="Course Update",
    message="Your enrollment has been approved.",
    category=NotificationCategory.ENROLLMENT,
    priority=NotificationPriority.HIGH,
    recipient_id="user_id_123"
)
```

### Sending/Delivering

```python
from app.core.monitoring.notification_center import notification_center

notification_center.notify(notif)
```

- **Direct Notifications:** (with `recipient_id`)  
  Always delivered and stored in the recipient's history, regardless of their current subscriptions.
- **Broadcast Notifications:** (with `recipient_id=None`)  
  Delivered and stored **only** for those users/components whose subscription matches the category/priority.

### Subscribing

```python
def my_notification_callback(notification):
    print("Received notification:", notification.title)

notification_center.subscribe(
    subscriber_id="my_component_id",
    categories={NotificationCategory.SYSTEM},
    priorities={NotificationPriority.CRITICAL, NotificationPriority.HIGH},
    callback=my_notification_callback
)
```

### Unsubscribing

```python
notification_center.unsubscribe("my_component_id")
```

### Retrieving Notification History

```python
history = notification_center.get_notifications("user_id_123")
unread_history = notification_center.get_notifications("user_id_123", unread_only=True)
```

### Marking as Read / Archiving

```python
notification_center.mark_as_read("user_id_123", notification_id)
notification_center.archive_notification("user_id_123", notification_id)
```

### Searching

```python
progress_notifs = notification_center.search_notifications(
    "user_id_123"
    , category=NotificationCategory.PROGRESS
)
```

---

## Example Integration Patterns

- **UI Widgets:**  
  Use `get_notifications(recipient_id)` to provide the data for notification popups, trays, or dashboards.
- **System Components:**  
  Subscribe with a callback for automation or auditing of cross-cutting events.
- **Automated Cleanup:**  
  Use `archive_notification` or remove old ones via `notification_center.get_notifications` for admin use.

---

## Delivery Guarantees & Semantics

- **Targeted (Direct):**
  - Every notification with `recipient_id` is **ALWAYS** delivered and stored in that user's/component's history.
- **Broadcast:**
  - Delivered/stored **only** to matching subscribers (category & priority).
- **Unsubscribed Recipients:**
  - Will still receive all targeted (direct) notifications, but no broadcasts.

---

## Thread Safety

- All operations are thread safe for concurrency in desktop and backend contexts.

---

## Related Files

- Core Logic: `/app/core/monitoring/notification_center.py`
- Unit Tests: `/tests/unit/core/monitoring/test_notification_center.py`

---

## See Also

- [Student Dashboard Framework](/docs/development/day15_plan.md)
- [Progress Metric API](/docs/api/progress_metrics.md)