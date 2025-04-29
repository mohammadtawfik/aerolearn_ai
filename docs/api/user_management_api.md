# User Management API (Admin)

This document describes the available programmatic interface for admin user management.

## Endpoints / Methods

### User CRUD
- `create_user(profile_data)`: Create new user (returns user_id as str).
- `read_user(user_id)`: Fetch user profile as Python dict.
- `update_user(user_id, fields)`: Update user fields (partial update, returns True/False).
- `delete_user(user_id)`: Delete user (returns True/False).
- `list_users(filters=None)`: List/search users, returns List[dict].

### Permissions / Role Assignment
- `assign_role(user_id, role)`: Assign role to user (returns True/False).
- `remove_role(user_id, role)`: Remove role from user (returns True/False).
- `assign_permission(user_id, permission)`: Directly assign permission string (returns True/False).
- `remove_permission(user_id, permission)`: Remove permission from user (returns True/False).

### Activity Logs
- `get_activity_log(user_id=None, filters=None)`: View/filter user activity (admin only).  
  Uses `SessionManager` to retrieve activity logs on current sessions.

### Bulk User Operations
- `bulk_create_users(profiles)`: Batch creation (returns list of user_ids as strings).
- `bulk_update_roles(user_ids, role, action)`: Assign/remove role in bulk (returns count succeeded).
- `bulk_delete_users(user_ids)`: Batch deletion (returns count succeeded).

## Security and Types

All operations require the admin to have the relevant permissions.
User IDs and bulk operations use `str` for keys (consistent with model and tests).
Session-based logs are ephemeral (expand persistence in future).

## Examples

See `/tests/ui/test_user_management.py` for usage patterns.

---

**See also:** `/docs/user_guides/admin_user_mgmt.md` for a workflow guide.
