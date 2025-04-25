import unittest
import os
from app.core.auth.credential_manager import CredentialManager

class TestCredentialManager(unittest.TestCase):
    def setUp(self):
        self.password = "securepassword"
        self.manager = CredentialManager(self.password)

    def tearDown(self):
        # Clean up test files
        if os.path.exists("salt.bin"):
            os.remove("salt.bin")
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")

    def test_store_and_retrieve_credential(self):
        """Test storing and retrieving a credential."""
        self.manager.store_credential("api_key", "12345")
        retrieved = self.manager.retrieve_credential("api_key")
        self.assertEqual(retrieved, "12345")

if __name__ == "__main__":
    unittest.main()