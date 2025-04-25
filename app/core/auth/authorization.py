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

def require_permission(permission: Permission):
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
            # Permission registry must be globally accessible or passed in
            from app.core.auth.permission_registry import permission_registry
            if not permission_registry.has_permission(user_id, permission):
                raise PermissionError(f"User '{user_id}' lacks permission '{permission}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class PermissionError(Exception):
    pass