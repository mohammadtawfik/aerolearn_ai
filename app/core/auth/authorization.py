from typing import List, Set, Dict, Optional, Callable
from functools import wraps

class Permission:
    """
    Represents a single permission string, such as 'content.edit' or 'user.manage'.
    """
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Permission) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

class Role:
    """
    Represents a user role (e.g., student, professor, admin), with a set of permissions.
    Supports role hierarchy (inheritance).
    """
    def __init__(self, name: str, permissions: Optional[Set[Permission]] = None, parents: Optional[Set['Role']] = None):
        self.name = name
        self.permissions: Set[Permission] = permissions or set()
        self.parents: Set['Role'] = parents or set()

    def all_permissions(self) -> Set[Permission]:
        perms = set(self.permissions)
        for parent in self.parents:
            perms.update(parent.all_permissions())
        return perms

    def add_permission(self, permission: Permission):
        self.permissions.add(permission)

    def add_parent(self, parent: 'Role'):
        self.parents.add(parent)

class UserPermissions:
    """
    Assigns roles and direct permissions to users (by user_id).
    """
    def __init__(self):
        self._user_roles: Dict[str, Set[Role]] = {}
        self._user_permissions: Dict[str, Set[Permission]] = {}

    def assign_role(self, user_id: str, role: Role):
        self._user_roles.setdefault(user_id, set()).add(role)

    def remove_role(self, user_id: str, role: Role):
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)

    def assign_permission(self, user_id: str, permission: Permission):
        self._user_permissions.setdefault(user_id, set()).add(permission)

    def remove_permission(self, user_id: str, permission: Permission):
        if user_id in self._user_permissions:
            self._user_permissions[user_id].discard(permission)

    def get_roles(self, user_id: str) -> Set[Role]:
        return self._user_roles.get(user_id, set())

    def get_permissions(self, user_id: str) -> Set[Permission]:
        perms = set(self._user_permissions.get(user_id, set()))
        for role in self.get_roles(user_id):
            perms.update(role.all_permissions())
        return perms

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        return permission in self.get_permissions(user_id)

class AuthorizationManagerClass:
    """
    Central registry for roles, permissions, and user/role assignment.
    Provides high-level APIs for assigning and checking permissions/roles.
    """
    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._user_permissions = UserPermissions()
        # For tracking user-role assignments
        self._user_role_map: Dict[str, Set[str]] = {}

    def register_permission(self, perm_name: str) -> Permission:
        """Register a permission by name, or return existing one if already registered"""
        if perm_name not in self._permissions:
            self._permissions[perm_name] = Permission(perm_name)
        return self._permissions[perm_name]

    def register_role(self, role_name: str, perm_names: List[str] = None) -> Role:
        """Register a role with optional permissions"""
        # Create/get Role object
        if role_name not in self._roles:
            self._roles[role_name] = Role(name=role_name)
        role = self._roles[role_name]
        
        # Assign all permissions if provided
        if perm_names:
            for pname in perm_names:
                perm = self.register_permission(pname)
                role.add_permission(perm)
        return role

    def set_role_parent(self, role_name: str, parent_role_name: str):
        """Set a parent role for inheritance"""
        if role_name not in self._roles:
            raise ValueError(f"Role '{role_name}' not registered")
        if parent_role_name not in self._roles:
            raise ValueError(f"Parent role '{parent_role_name}' not registered")
            
        role = self._roles[role_name]
        parent_role = self._roles[parent_role_name]
        role.add_parent(parent_role)

    def assign_role_to_user(self, user_id: str, role_name: str):
        """Assign a role to a user"""
        if role_name not in self._roles:
            raise ValueError(f"Role '{role_name}' not registered")
        self._user_permissions.assign_role(user_id, self._roles[role_name])
        # For quick reference/tracking
        self._user_role_map.setdefault(user_id, set()).add(role_name)

    def remove_role_from_user(self, user_id: str, role_name: str):
        """Remove a role from a user"""
        if role_name not in self._roles:
            return  # No-op if role doesn't exist
        self._user_permissions.remove_role(user_id, self._roles[role_name])
        if user_id in self._user_role_map:
            self._user_role_map[user_id].discard(role_name)

    def assign_permission_to_user(self, user_id: str, perm_name: str):
        """Assign a direct permission to a user"""
        perm = self.register_permission(perm_name)
        self._user_permissions.assign_permission(user_id, perm)

    def remove_permission_from_user(self, user_id: str, perm_name: str):
        """Remove a direct permission from a user"""
        if perm_name in self._permissions:
            self._user_permissions.remove_permission(user_id, self._permissions[perm_name])

    def has_permission(self, user_id: str, perm_name: str) -> bool:
        """Check if a user has a specific permission"""
        if perm_name not in self._permissions:
            return False
        return self._user_permissions.has_permission(user_id, self._permissions[perm_name])

    def get_user_roles(self, user_id: str) -> Set[Role]:
        """Get all roles assigned to a user"""
        return self._user_permissions.get_roles(user_id)
    
    def get_user_role_names(self, user_id: str) -> Set[str]:
        """Get names of all roles assigned to a user"""
        return self._user_role_map.get(user_id, set())

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions a user has (from roles and direct assignments)"""
        return self._user_permissions.get_permissions(user_id)

    def get_role(self, role_name: str) -> Optional[Role]:
        """Get a role by name"""
        return self._roles.get(role_name)

    def get_permission(self, perm_name: str) -> Optional[Permission]:
        """Get a permission by name"""
        return self._permissions.get(perm_name)

# Create the singleton instance
AuthorizationManager = AuthorizationManagerClass()

def require_permission(permission: str):
    """
    Decorator for functions/methods to enforce the required permission.
    Expects the decorated function to accept a 'user_id' kwarg or positional argument.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find user_id
            user_id = kwargs.get('user_id')
            if user_id is None and len(args) > 0:
                user_id = args[0]  # Assume first positional argument is user_id by convention
            
            # Use the AuthorizationManager to check permission
            if not AuthorizationManager.has_permission(user_id, permission):
                raise PermissionError(f"User '{user_id}' lacks permission '{permission}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class PermissionError(Exception):
    pass
