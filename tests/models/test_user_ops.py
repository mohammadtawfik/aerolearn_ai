"""
File location: /tests/models/test_user_ops.py

Unit tests for /app/core/auth/user_profile.py
"""

import unittest
from app.core.auth.user_profile import UserProfileManager

class TestUserProfileManager(unittest.TestCase):

    def setUp(self):
        self.mgr = UserProfileManager()

    def test_create_and_get_user(self):
        user_id = self.mgr.create_user({'username': 'dog', 'email': 'dog@pets.com'})
        user = self.mgr.get_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'dog')

    def test_update_user(self):
        user_id = self.mgr.create_user({'username': 'cat', 'email': 'cat@pets.com'})
        updated = self.mgr.update_user(user_id, {'email': 'catz@pets.com'})
        self.assertTrue(updated)
        user = self.mgr.get_user(user_id)
        self.assertEqual(user['email'], 'catz@pets.com')

    def test_delete_user(self):
        user_id = self.mgr.create_user({'username': 'rat', 'email': 'rat@pets.com'})
        deleted = self.mgr.delete_user(user_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.mgr.get_user(user_id))

    def test_list_users(self):
        orig = len(self.mgr.list_users({}))
        self.mgr.create_user({'username': 'bird', 'email': 'bird@pets.com'})
        self.assertEqual(len(self.mgr.list_users({})), orig+1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.mgr.create_user({'username': '', 'email': 'fail@pets.com'})
        with self.assertRaises(ValueError):
            self.mgr.create_user({'username': 'failuser'})
        with self.assertRaises(ValueError):
            self.mgr.create_user({'email': 'fail@pets.com'})

if __name__ == "__main__":
    unittest.main()