import unittest
import os
import json
from unittest.mock import patch, MagicMock
from app.core.auth.credential_manager import CredentialManager

class TestCredentialManager(unittest.TestCase):
    def setUp(self):
        self.password = "securepassword"
        self.manager = CredentialManager(self.password)
        # Clean residual files before each test to isolate tests
        self._cleanup_files()

    def tearDown(self):
        self._cleanup_files()

    def _cleanup_files(self):
        """Helper method to clean up test files."""
        if os.path.exists("salt.bin"):
            os.remove("salt.bin")
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")

    def test_store_and_retrieve_credential(self):
        """Test storing and retrieving a credential."""
        value = "12345"
        self.manager.store_credential("api_key", value)
        retrieved = self.manager.retrieve_credential("api_key")
        self.assertEqual(retrieved, value)

    def test_encryption_at_rest(self):
        """Verify that credentials are stored encrypted on disk."""
        value = "verySecretApiKey"
        self.manager.store_credential("api_key", value)
        # Ensure the value at rest is not plaintext
        with open("credentials.json", "r") as f:
            stored = json.load(f)
            stored_value = stored.get("api_key")
            self.assertNotEqual(stored_value, value)
            self.assertIsInstance(stored_value, str)
            self.assertGreater(len(stored_value), 0)
            self.assertNotIn(value, stored_value)

    def test_improper_access_raises(self):
        """Test retrieval of missing credential raises error."""
        with self.assertRaises(ValueError):
            self.manager.retrieve_credential("nonexistent_key")

    def test_credential_rotation(self):
        """Test credential rotation updates value properly."""
        self.manager.store_credential("api_key", "old_value")
        old_retrieved = self.manager.retrieve_credential("api_key")
        self.assertEqual(old_retrieved, "old_value")
        self.manager.store_credential("api_key", "new_value")
        new_retrieved = self.manager.retrieve_credential("api_key")
        self.assertEqual(new_retrieved, "new_value")

    def test_memory_clear_on_del(self):
        """Test credentials are not lingering in manager after deletion (best-effort given Python semantics)."""
        # Store and retrieve something, then delete the manager
        self.manager.store_credential("api_key", "secret")
        ref = self.manager.crypto
        del self.manager
        import gc; gc.collect()
        # At this point, we can't directly assure memory is wiped, but we can check that creating a new manager resets its state
        mgr2 = CredentialManager(self.password)
        self.assertTrue(hasattr(mgr2, "crypto"))

    @patch("app.core.auth.credential_manager.CryptoUtils")
    def test_encryption_library_used(self, MockCryptoUtils):
        """Ensure encryption utility is being called for encryption/decryption."""
        mock_crypto = MockCryptoUtils.return_value
        mock_crypto.encrypt.return_value = "encrypted"
        mock_crypto.decrypt.return_value = "decrypted"
        mgr = CredentialManager(self.password)
        mgr.crypto = mock_crypto
        mgr.store_credential("test_key", "topsecret")
        val = mgr.retrieve_credential("test_key")
        mock_crypto.encrypt.assert_called_once()
        mock_crypto.decrypt.assert_called_once()
        self.assertEqual(val, "decrypted")

    def test_permissions_are_local_to_file(self):
        """Simulate improper access by using a wrong password."""
        value = "supersecret"
        self.manager.store_credential("api_key", value)
        # simulate 'logout'
        del self.manager
        # Try loading with wrong password
        wrong_pass_manager = CredentialManager("wrongpassword")
        # Decryption should fail or give wrong value (depending on CryptoUtils), so catch value error or check mismatch
        with self.assertRaises(Exception):
            wrong_pass_manager.retrieve_credential("api_key")

    def test_resilience_basic_extraction(self):
        """Basic test: encrypted credential should look like ciphertext, not a secret, in file."""
        value = "MySuperSensitiveToken"
        self.manager.store_credential("api_key", value)
        # Try to extract from credentials file
        with open("credentials.json", "r") as f:
            data = f.read()
        self.assertNotIn(value, data)
        # Simulate reading salt file to reconstruct the key: would require the password
        with open("salt.bin", "rb") as sf:
            salt = sf.read()
        self.assertIsInstance(salt, bytes)

    def test_multiple_credentials(self):
        """Test storing and retrieving multiple credentials."""
        creds = {
            "api_key1": "secret1",
            "api_key2": "secret2",
            "api_key3": "secret3"
        }
        for k, v in creds.items():
            self.manager.store_credential(k, v)
        for k, v in creds.items():
            self.assertEqual(self.manager.retrieve_credential(k), v)

if __name__ == "__main__":
    unittest.main()
