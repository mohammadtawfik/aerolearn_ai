# Course Management API & Admin Guide

_Last updated: 2024-06-09_

## Overview

This document describes the public API and admin UI for course management as implemented in:
- `/app/core/db/course_admin.py`
- `/app/ui/admin/course_management.py`
- Related ORM models in `/app/models/course.py`, `/app/models/user.py`, etc.

Features included:
- Course creation/customization (direct and from templates)
- Bulk enrollment/removal
- Course templates/inheritance
- Course archiving/restoring
- Fully permission-controlled admin operations

---

## Core API

### `CourseAdminService` (`/app/core/db/course_admin.py`)

#### Constructor

```python
CourseAdminService(session: Session)
```
Requires a SQLAlchemy session.

#### Methods

##### `create_course(title, description="", from_template_id=None, is_template=False) -> Course`
- Creates a new course; can optionally instantiate from a template ID.
- If `from_template_id` provided, clones the template (modules, lessons).

##### `archive_course(course_id)`
- Marks a course as archived. Archived courses are hidden from normal listings.

##### `restore_course(course_id)`
- Un-archives a given course.

##### `enroll_users_bulk(course_id, user_ids)`
- Bulk-enrolls an iterable of user IDs in the selected course. Ignores users already enrolled.

##### `list_templates() -> List[Course]`
- Returns all course templates.

##### `list_courses(include_archived=False) -> List[Course]`
- Returns all courses. If `include_archived=True`, includes archived items.

---

## Admin UI Features

Main UI: `/app/ui/admin/course_management.py` (PyQt6)

- Lists all courses (with archived status)
- Allows creation, archiving, restoring, and bulk enrollment
- Template and course creation integrated into UI
- Can be launched via the admin panel or instantiated for tests

---

## Database/ORM Details

- All admin services rely on correct model relationships between Course, Module, Lesson, Enrollment, User, Category, etc.
- Templates are first-class Course ORM objects (`is_template=True`)
- Enrollment relationships are bidirectional for admin/statistics use

---

## API Usage Example

```python
from app.core.db.course_admin import CourseAdminService
from app.core.db.db_client import DBClient
from sqlalchemy.orm import sessionmaker

db = DBClient("sqlite:///app_database.db")
session = sessionmaker(bind=db.engine)()
admin = CourseAdminService(session)
# Create a course
course = admin.create_course(title="Intro to Aerospace")
# Archive
admin.archive_course(course.id)
# Restore
admin.restore_course(course.id)
# Enroll users
admin.enroll_users_bulk(course.id, [123, 456, 789])
```

---

## Testing

- Corresponding tests are implemented at `/tests/ui/test_course_admin.py`.
- Tests cover: course creation, archiving, restoring, template instantiation, and bulk enrollment.
- All tests are currently passing ✅.

---

## Permissions & Security

- The CourseAdminService and UI components utilize role/permission checks as defined for admin operations.
- Unauthorized actions are not permitted from the UI.

---

## Extending

To add additional admin features, see:
- `/app/core/db/course_admin.py` for service logic patterns
- `/app/ui/admin/course_management.py` for UI conventions
- Existing model/relationship patterns in `/app/models/`

---

For further admin user workflows, see `/docs/user_guides/admin_workflows.md`.
