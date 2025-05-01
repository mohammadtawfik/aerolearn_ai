# Course Enrollment API Documentation

**Location:** `/docs/api/course_enrollment_api.md`  
*(Save in /docs/api/ as per API doc conventions.)*

## Overview

This API enables browsing/searching courses, requesting enrollment, handling approvals/rejections/cancelations, and querying enrollment status.

---

## Endpoints

| Method | Endpoint                                           | Purpose                     |
|--------|----------------------------------------------------|-----------------------------|
| GET    | `/courses`                                         | List all courses            |
| GET    | `/courses/search?query=...`                        | Search for courses          |
| POST   | `/courses/{course_id}/enroll`                      | Request enrollment          |
| POST   | `/courses/{course_id}/enrollment/approve`          | Approve enrollment request  |
| POST   | `/courses/{course_id}/enrollment/reject`           | Reject enrollment request   |
| POST   | `/courses/{course_id}/enrollment/cancel`           | Cancel an enrollment        |
| GET    | `/courses/{course_id}/enrollment/status?user_id=..`| Get enrollment status       |

---

## Enrollment Workflow

1. **Browse/Search**: Student lists or searches courses.
2. **Request Enrollment**: Student requests; status is `pending`.
3. **Approve/Reject**: Professor/admin approves/rejects; student is notified.
4. **Cancel**: Student can cancel their pending request.
5. **Query Status**: Status updates to `approved`, `rejected`, or `cancelled`.

---

## Payloads

### Enrollment Request (POST `/courses/{course_id}/enroll`)
```json
{
  "user_id": "student_id"
}
```
**Response**:  
Enrollment status object

### Approve/Reject (POST `/courses/{course_id}/enrollment/approve`)
```json
{
  "user_id": "student_id",
  "approver_id": "prof_id"
}
```
**Response:**  
Enrollment status object

---

## Status Object

```json
{
  "user_id": "student_id",
  "course_id": "course_id",
  "status": "pending|approved|rejected|cancelled",
  "approved_by": "prof_id/null",
  "status_history": [ { "status": "...", "at": "...", "by": "..."} ]
}
```

---

## Error Response

```json
{
  "detail": "Course not found"
}
```
or
```json
{
  "detail": "Enrollment request/course not found"
}
```

---

## Related Files

- `/app/models/course.py` – Data model, status methods
- `/app/core/enrollment/enrollment_service.py` – Service logic
- `/app/core/api/course_api.py` – API endpoints

---

## Security Notes

- Only approved users can approve/reject requests.
- All mutations should check session/permission.
- Status and request timing should be auditable.

---

**File location:** `/docs/api/course_enrollment_api.md`