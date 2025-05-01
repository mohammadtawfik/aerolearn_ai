"""
Unit tests for Notification Center

Location: /tests/unit/core/monitoring/test_notification_center.py
(Place this file in the tests/unit/core/monitoring/ directory as per project conventions)
"""

import pytest
from app.core.monitoring.notification_center import (
    NotificationCenter, notification_center,
    Notification, NotificationCategory, NotificationPriority, NotificationStatus
)
import threading

def _make_simple_notification(
    title="Test",
    message="Test message",
    category=NotificationCategory.SYSTEM,
    priority=NotificationPriority.NORMAL,
    recipient_id=None,
    data=None,
    source="unit_test",
):
    return Notification(
        title=title,
        message=message,
        category=category,
        priority=priority,
        recipient_id=recipient_id,
        data=data,
        source=source
    )

def setup_function():
    # Reset the notification_center instance before each test for isolation
    notification_center._subscriptions.clear()
    notification_center._history._history.clear()

def test_basic_notification_delivery_and_history():
    recipient_id = "user1"
    notif = _make_simple_notification(recipient_id=recipient_id)
    notification_center.notify(notif)
    # Recipient should see the notification in their history
    notifs = notification_center.get_notifications(recipient_id)
    assert any(n.notification_id == notif.notification_id for n in notifs)

def test_subscription_and_callback(monkeypatch):
    recipient_id = "user-callback"
    received = []
    def callback(n):
        received.append(n)

    notification_center.subscribe(subscriber_id=recipient_id, callback=callback)
    notif = _make_simple_notification(recipient_id=recipient_id)
    notification_center.notify(notif)
    assert received
    assert received[0].notification_id == notif.notification_id

def test_priority_filtering():
    user = "user_priority"
    # Only subscribe to high and critical
    notification_center.subscribe(
        subscriber_id=user,
        priorities={NotificationPriority.HIGH, NotificationPriority.CRITICAL}
    )
    # -- Targeted notifications (should always be stored in history, regardless of filter) --
    high_notif = _make_simple_notification(recipient_id=user, priority=NotificationPriority.HIGH)
    notification_center.notify(high_notif)
    normal_notif = _make_simple_notification(recipient_id=user, priority=NotificationPriority.NORMAL)
    notification_center.notify(normal_notif)
    user_notifs = notification_center.get_notifications(user)
    ids = [n.notification_id for n in user_notifs]
    # Both should appear (targeted notifications always delivered)
    assert high_notif.notification_id in ids
    assert normal_notif.notification_id in ids
    # -- Broadcast notification (should only appear if matching filter) --
    bcast_high = _make_simple_notification(recipient_id=None, priority=NotificationPriority.HIGH)
    bcast_normal = _make_simple_notification(recipient_id=None, priority=NotificationPriority.NORMAL)
    notification_center.notify(bcast_high)
    notification_center.notify(bcast_normal)
    user_bcast_notifs = [
        n.notification_id for n in notification_center.get_notifications(user)
        if n.recipient_id is None  # Broadcasts have no recipient_id
    ]
    assert bcast_high.notification_id in user_bcast_notifs
    assert bcast_normal.notification_id not in user_bcast_notifs

def test_category_filtering():
    user = "user_category"
    notification_center.subscribe(
        subscriber_id=user,
        categories={NotificationCategory.ENROLLMENT}
    )
    # -- Targeted notifications (should always be stored in history, regardless of filter) --
    enrollment_notif = _make_simple_notification(recipient_id=user, category=NotificationCategory.ENROLLMENT)
    system_notif = _make_simple_notification(recipient_id=user, category=NotificationCategory.SYSTEM)
    notification_center.notify(enrollment_notif)
    notification_center.notify(system_notif)
    user_notifs = notification_center.get_notifications(user)
    # Both should appear in history (targeted)
    ids = [n.notification_id for n in user_notifs]
    assert enrollment_notif.notification_id in ids
    assert system_notif.notification_id in ids
    # -- Broadcast notifications (should only appear if matching filter) --
    bcast_enrollment = _make_simple_notification(recipient_id=None, category=NotificationCategory.ENROLLMENT)
    bcast_system = _make_simple_notification(recipient_id=None, category=NotificationCategory.SYSTEM)
    notification_center.notify(bcast_enrollment)
    notification_center.notify(bcast_system)
    user_bcast_notifs = [
        n.notification_id for n in notification_center.get_notifications(user)
        if n.recipient_id is None
    ]
    assert bcast_enrollment.notification_id in user_bcast_notifs
    assert bcast_system.notification_id not in user_bcast_notifs

def test_broadcast_notification_to_all():
    user_a = "broadcastA"
    user_b = "broadcastB"
    notification_center.subscribe(subscriber_id=user_a)
    notification_center.subscribe(subscriber_id=user_b)
    notif = _make_simple_notification(recipient_id=None)
    notification_center.notify(notif)
    notifs_a = notification_center.get_notifications(user_a)
    notifs_b = notification_center.get_notifications(user_b)
    assert any(n.notification_id == notif.notification_id for n in notifs_a)
    assert any(n.notification_id == notif.notification_id for n in notifs_b)

def test_mark_as_read_and_archive():
    user = "user_read_archive"
    notif = _make_simple_notification(recipient_id=user)
    notification_center.notify(notif)
    r = notification_center.mark_as_read(user, notif.notification_id)
    assert r
    notifs = notification_center.get_notifications(user)
    n = [n for n in notifs if n.notification_id == notif.notification_id][0]
    assert n.status == NotificationStatus.READ
    r2 = notification_center.archive_notification(user, notif.notification_id)
    assert r2
    assert n.status == NotificationStatus.ARCHIVED

def test_search_notifications():
    user = "user_search"
    notif1 = _make_simple_notification(recipient_id=user, category=NotificationCategory.PROGRESS)
    notif2 = _make_simple_notification(recipient_id=user, category=NotificationCategory.CONTENT)
    notification_center.notify(notif1)
    notification_center.notify(notif2)
    found = notification_center.search_notifications(user, category=NotificationCategory.PROGRESS)
    assert len(found) == 1
    assert found[0].category == NotificationCategory.PROGRESS

def test_unsubscribe():
    user = "user_unsub"
    notification_center.subscribe(subscriber_id=user)
    notification_center.unsubscribe(user)
    notif = _make_simple_notification(recipient_id=user)
    notification_center.notify(notif)
    # No subscription, so should not receive notification through callback; history still present if direct delivery
    notifs = notification_center.get_notifications(user)
    assert any(n.notification_id == notif.notification_id for n in notifs)

def test_thread_safety():
    # Launch many notifications and subscriptions in parallel to test for race conditions
    user = "user_thread"
    results = []
    def callback(n): results.append(n.notification_id)
    def subscribe_and_notify():
        notification_center.subscribe(subscriber_id=user, callback=callback)
        for _ in range(10):
            notification_center.notify(_make_simple_notification(recipient_id=user))
    threads = [threading.Thread(target=subscribe_and_notify) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    notifs = notification_center.get_notifications(user)
    # Should have at least as many notifications as threads * 10
    assert len(notifs) >= 50
