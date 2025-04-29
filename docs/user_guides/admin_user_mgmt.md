# Admin User Management Guide

This guide describes how to perform all user management operations as an AeroLearn AI admin.

---

## Features

- **Create/Edit/Delete Users:** Use the User Management interface (`/app/ui/admin/user_management.py`) to add, update, or remove user accounts. Returns user ID as a string.
- **Assign/Remove Roles and Permissions:** Select a user and assign roles (admin, professor, student, custom) or granular permissions.
- **View Activity Logs:** Filter and inspect activity for specific users or actions. Uses `SessionManager` for per-session audit.
- **Bulk Operations:** Use the bulk actions for onboarding/offboarding users, especially for institutional deployment.

---

## Workflow Example

1. **Creating Users:** Fill in the required profile info (`username`, `email`). Click 'Add'. Bulk creation possible via spreadsheet upload. Each user is identified by a string ID.
2. **Editing Users:** Locate user, click 'Edit', update details as needed.
3. **Deleting Users:** Select user and click 'Remove' (with confirmation).
4. **Assigning Roles/Permissions:** Open user details, select role(s)/permissions, and save.
5. **Viewing Logs:** Use filters to show specific actions (login, updates, permission changes, etc). Logs are available for currently active sessions.
6. **Bulk Actions:** Use the 'Bulk' menu for onboarding/offboarding. Import/export supported.

---

## Notes

- User and admin IDs are consistently treated as strings for robustness.
- Logs are session-based; system-wide audit logs may require future extension.
- Role/permission structure leverages `/app/core/auth/authorization.py`.

---

_For in-depth API details, see `/docs/api/user_management_api.md` and inline code documentation._
