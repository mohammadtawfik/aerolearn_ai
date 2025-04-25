from app.core.auth.authorization import Role, Permission, UserPermissions

# Define system roles and permissions
permission_registry = UserPermissions()

# Define foundational permissions
PERM_VIEW_CONTENT = Permission("content.view")
PERM_EDIT_CONTENT = Permission("content.edit")
PERM_GRADE_ASSIGNMENTS = Permission("assignments.grade")
PERM_MANAGE_USERS = Permission("user.manage")
PERM_ADMIN_PANEL = Permission("admin.panel")

# Define roles
STUDENT = Role("student", permissions={PERM_VIEW_CONTENT})
PROFESSOR = Role("professor", permissions={PERM_VIEW_CONTENT, PERM_EDIT_CONTENT, PERM_GRADE_ASSIGNMENTS})
ADMIN = Role("admin", permissions={PERM_VIEW_CONTENT, PERM_EDIT_CONTENT, PERM_GRADE_ASSIGNMENTS, PERM_MANAGE_USERS, PERM_ADMIN_PANEL})

# If you want role inheritance:
# PROFESSOR.add_parent(STUDENT)
# ADMIN.add_parent(PROFESSOR)

# Register sample roles
role_map = {
    "student": STUDENT,
    "professor": PROFESSOR,
    "admin": ADMIN,
}

def assign_user_role(user_id: str, role_name: str):
    role = role_map.get(role_name)
    if role:
        permission_registry.assign_role(user_id, role)

def assign_user_permission(user_id: str, permission: Permission):
    permission_registry.assign_permission(user_id, permission)

def get_user_permissions(user_id: str):
    return permission_registry.get_permissions(user_id)