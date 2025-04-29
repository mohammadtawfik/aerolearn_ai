"""
File location: /app/ui/admin/user_management.py

Admin User Management UI Interface.
Implements user CRUD, role assignment, activity log viewing, and bulk actions for institutional deployment.
Ties into core logic via user_profile and permission system.

This file should be saved at: /app/ui/admin/user_management.py
"""

from app.core.auth.user_profile import UserProfileManager
from app.core.auth.authorization import AuthorizationManagerClass, Permission
from app.core.auth.session import SessionManager
from typing import List, Optional, Dict, Any

class UserManagementUI:
    """
    Admin-facing interface for managing users:
    - CRUD operations (create, read, update, delete)
    - Role and permission assignment
    - Activity logs (with filter/search)
    - Bulk user actions
    """

    def __init__(self, user_profile_mgr: Optional[UserProfileManager] = None, authz_mgr: Optional[AuthorizationManagerClass] = None):
        self.user_profile_mgr = user_profile_mgr or UserProfileManager()
        self.authz_mgr = authz_mgr or AuthorizationManagerClass()
        self.session_mgr = SessionManager()

    # --- CRUD Operations ---

    def create_user(self, profile_data: Dict[str, Any]) -> str:
        """Create a new user account. Returns user ID."""
        return self.user_profile_mgr.create_user(profile_data)

    def read_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user details."""
        return self.user_profile_mgr.get_user(user_id)

    def update_user(self, user_id: str, update_fields: Dict[str, Any]) -> bool:
        """Update user fields."""
        return self.user_profile_mgr.update_user(user_id, update_fields)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user account."""
        return self.user_profile_mgr.delete_user(user_id)

    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List users, optionally filtered."""
        return self.user_profile_mgr.list_users(filters or {})

    # --- Role/Permission Management ---

    def assign_role(self, user_id: str, role: str) -> bool:
        """Assign a role to the user."""
        return self.authz_mgr.assign_role_to_user(user_id, role)

    def remove_role(self, user_id: str, role: str) -> bool:
        """Remove a role from a user."""
        return self.authz_mgr.remove_role_from_user(user_id, role)

    def assign_permission(self, user_id: str, permission: str) -> bool:
        """Assign an individual permission."""
        perm_obj = Permission(permission)
        return self.authz_mgr.assign_permission_to_user(user_id, perm_obj)

    def remove_permission(self, user_id: str, permission: str) -> bool:
        """Remove an individual permission."""
        perm_obj = Permission(permission)
        return self.authz_mgr.remove_permission_from_user(user_id, perm_obj)

    # --- User Activity Monitoring ---

    def get_activity_log(self, user_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Return admin activity log(s), filterable by user, action, date range, etc.
        NOTE: SessionManager does not persist logs across sessions. 
        Requires enhancement for production audit logs.
        """
        result = []
        sessions = self.session_mgr.get_active_sessions(user_id) if user_id is not None else self.session_mgr._sessions.values()
        for session in sessions:
            for entry in session.activity_log:
                match = True
                if filters:
                    # Only perform very simple filtering
                    for k, v in filters.items():
                        if entry.get(k) != v:
                            match = False
                            break
                if match:
                    result.append(entry)
        return result

    # --- Bulk User Operations ---

    def bulk_create_users(self, profiles: List[Dict[str, Any]]) -> List[str]:
        """Bulk create user accounts. Returns list of user IDs."""
        return self.user_profile_mgr.bulk_create_users(profiles)

    def bulk_update_roles(self, user_ids: List[str], role: str, action: str = "assign") -> int:
        """Bulk (assign/remove) role for multiple users. Returns count succeeded."""
        if action == "assign":
            return sum(self.assign_role(uid, role) for uid in user_ids)
        elif action == "remove":
            return sum(self.remove_role(uid, role) for uid in user_ids)
        else:
            raise ValueError("action must be 'assign' or 'remove'")

    def bulk_delete_users(self, user_ids: List[str]) -> int:
        """Bulk delete users. Returns count succeeded."""
        return sum(self.delete_user(uid) for uid in user_ids)

    # Additional UI control logic/states would be implemented as needed for actual GUI/web
