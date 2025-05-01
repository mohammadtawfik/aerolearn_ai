# AeroLearn AI — Course Enrollment Workflow

*Location: `/docs/user_guides/enrollment_workflow.md`*

---

## Overview

This document describes the course enrollment workflow in AeroLearn AI for both students and professors. It covers browsing/searching courses, enrollment requests and approvals, access management, notification mechanisms, integration points, and supported API/events. This documentation is intended for both developers and users (students/professors).

---

## 1. Course Browsing and Search

- **Browse Courses:** Students can view all available courses via the Student Dashboard.
- **Search:** The dashboard provides search/filter functionality by course name, category, tags, instructor, etc.
- **Course Metadata:** Each course displays key info: title, description, instructors, status, and enrollment options.

---

## 2. Enrollment Request and Approval Workflow

### Students

1. **Request Enrollment:**  
   - Click the "Enroll" button for a target course.
   - Confirmation dialog is shown.
   - An `EnrollmentRequestEvent` is emitted.

2. **Pending Approval:**  
   - The course moves to the "Pending Approval" state in both the dashboard and course list.
   - Students receive a notification (see Notification Center) about request submission.

### Professors

1. **Review Requests:**  
   - Professors see all pending enrollment requests for their courses in their dashboard.
   - Each request shows student details and requested course.

2. **Approve/Deny:**  
   - Professors approve/deny each request.
   - The system emits an `EnrollmentStatusChangedEvent` for each decision.
   - Students are notified accordingly.

---

## 3. Course Access Management

- **Upon Approval:**  
  - Student status set to "Enrolled".
  - Course content is accessible from the dashboard.
  - Enrollment reflected in backend and shown in the UI.

- **Upon Denial:**  
  - Status updated in UI and backend.
  - Student receives denial notification.

- **Withdraw/Drop:**  
  - Students can cancel their enrollment.
  - A `WithdrawalEvent` is emitted.
  - Professors are notified of withdrawals.

---

## 4. Notification System

- **Enrollment Actions:**  
  - All key actions (request, approval, denial, withdrawal) trigger notifications.
  - Notifications appear both in the Notification Center and (optionally) via email.

- **Routing & Delivery:**  
  - The notification system ensures event-based and role-aware delivery.

---

## 5. Integration – Cross-Component Event Flow

- All actions (request, approve, deny, withdraw) use AeroLearn’s event system.
- Major event types:  
  - `EnrollmentRequestEvent`
  - `EnrollmentStatusChangedEvent`
  - `WithdrawalEvent`
- Event propagation ensures:
  - UI components update in real time.
  - Notification Center receives/filters relevant messages.
  - Audit logs and analytics are supported via `enrollment` events.

---

## 6. API & Developer Notes

- Enrollment workflow is event-driven, built atop the system’s event bus.
- _Major endpoints/events_: see `/app/models/course.py`, `/app/models/content.py`, and `/app/core/auth/authorization.py`.
- Notification APIs: see `/docs/user_guides/notification_center.md`.

---

## 7. Example User Flows

### Student

1. Browse courses → Select course → Enroll → Wait for approval → Get notification → Access course.

### Professor

1. View requests → Approve or deny → System notifies student and updates roster.

---

## 8. Edge Cases & Error Handling

- Duplicate requests prevented and reported.
- Students cannot access course material without approval.
- All actions auditable and recorded via system events.

---

## 9. References

- [Notification Center Documentation](/docs/user_guides/notification_center.md)
- [Core Event Bus System](/integrations/events/event_bus.py)
- [Course Model Schema](/app/models/course.py)