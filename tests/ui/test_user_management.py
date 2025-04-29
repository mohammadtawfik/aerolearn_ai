"""
File location: /tests/ui/test_user_management.py

Unit tests for /app/ui/admin/user_management.py (UserManagementUI).
"""

import unittest
from app.ui.admin.user_management import UserManagementUI

class TestUserManagementUI(unittest.TestCase):

    def setUp(self):
        self.ui = UserManagementUI()

    def test_create_and_read_user(self):
        user_id = self.ui.create_user({'username': 'alice', 'email': 'alice@example.com'})
        user = self.ui.read_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'alice')

    def test_update_user(self):
        user_id = self.ui.create_user({'username': 'bob', 'email': 'bob@example.com'})
        success = self.ui.update_user(user_id, {'email': 'bob2@example.com'})
        self.assertTrue(success)
        user = self.ui.read_user(user_id)
        self.assertEqual(user['email'], 'bob2@example.com')

    def test_delete_user(self):
        user_id = self.ui.create_user({'username': 'carol', 'email': 'carol@example.com'})
        success = self.ui.delete_user(user_id)
        self.assertTrue(success)
        self.assertIsNone(self.ui.read_user(user_id))

    def test_list_users(self):
        count_before = len(self.ui.list_users())
        self.ui.create_user({'username': 'x', 'email': 'x@example.com'})
        self.ui.create_user({'username': 'y', 'email': 'y@example.com'})
        count_after = len(self.ui.list_users())
        self.assertEqual(count_after, count_before + 2)

    def test_bulk_create_and_delete(self):
        profiles = [{'username': f'user{i}', 'email': f'u{i}@ex.com'} for i in range(3)]
        ids = self.ui.bulk_create_users(profiles)
        self.assertEqual(len(ids), 3)
        deleted = self.ui.bulk_delete_users(ids)
        self.assertEqual(deleted, 3)

    # More tests would be written for permissions, roles, logs as permissions system matures

if __name__ == "__main__":
    unittest.main()