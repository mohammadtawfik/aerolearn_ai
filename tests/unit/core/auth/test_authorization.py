import unittest
from app.core.auth.authorization import (
    Permission, Role, UserPermissions, require_permission, PermissionError
)
from app.core.auth.permission_registry import (
    permission_registry, assign_user_role, assign_user_permission, get_user_permissions,
    STUDENT, PROFESSOR, ADMIN, PERM_VIEW_CONTENT, PERM_EDIT_CONTENT, PERM_MANAGE_USERS
)

class TestAuthorizationAndPermissions(unittest.TestCase):
    def setUp(self):
        # Clear existing assignments
        permission_registry._user_roles.clear()
        permission_registry._user_permissions.clear()

    def test_permission_and_role_equality(self):
        p1 = Permission("content.view")
        p2 = Permission("content.view")
        self.assertEqual(p1, p2)
        r1 = Role("student", {p1})
        r2 = Role("student", {p2})
        self.assertEqual(r1.name, r2.name)

    def test_role_permission_inheritance(self):
        base = Role("base", {PERM_VIEW_CONTENT})
        child = Role("child", {PERM_EDIT_CONTENT}, parents={base})
        # child gets both its own and inherited
        perms = child.all_permissions()
        self.assertIn(PERM_VIEW_CONTENT, perms)
        self.assertIn(PERM_EDIT_CONTENT, perms)

    def test_user_role_assignment_and_permission_check(self):
        user_id = "u1"
        assign_user_role(user_id, "student")
        perms = get_user_permissions(user_id)
        self.assertIn(PERM_VIEW_CONTENT, perms)
        self.assertNotIn(PERM_EDIT_CONTENT, perms)
        # Assign professor (should get edit content)
        assign_user_role(user_id, "professor")
        perms = get_user_permissions(user_id)
        self.assertIn(PERM_EDIT_CONTENT, perms)

    def test_dynamic_permission_assignment_and_removal(self):
        user_id = "u2"
        assign_user_role(user_id, "student")
        assign_user_permission(user_id, PERM_MANAGE_USERS)
        perms = get_user_permissions(user_id)
        self.assertIn(PERM_MANAGE_USERS, perms)
        # Remove permission
        permission_registry.remove_permission(user_id, PERM_MANAGE_USERS)
        perms = get_user_permissions(user_id)
        self.assertNotIn(PERM_MANAGE_USERS, perms)

    def test_require_permission_decorator_success_and_failure(self):
        permission_registry.assign_role("u3", STUDENT)
        permission_registry.assign_permission("u3", PERM_EDIT_CONTENT)
        # Decorated function expects user_id as first argument

        @require_permission(PERM_EDIT_CONTENT)
        def edit_content(user_id):
            return True

        @require_permission(PERM_MANAGE_USERS)
        def admin_only(user_id):
            return True

        self.assertTrue(edit_content("u3"))
        # No such permission, should raise PermissionError
        with self.assertRaises(PermissionError):
            admin_only("u3")

    def test_permission_registry_methods(self):
        user_id = "u4"
        # No assignments: empty sets
        self.assertSetEqual(permission_registry.get_roles(user_id), set())
        self.assertSetEqual(permission_registry.get_permissions(user_id), set())

        permission_registry.assign_role(user_id, STUDENT)
        self.assertIn(STUDENT, permission_registry.get_roles(user_id))
        permission_registry.remove_role(user_id, STUDENT)
        self.assertNotIn(STUDENT, permission_registry.get_roles(user_id))

if __name__ == "__main__":
    unittest.main()