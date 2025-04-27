# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

import unittest
from app.utils.crypto import CryptoUtils

class TestCryptoUtils(unittest.TestCase):
    def setUp(self):
        password = "securepassword"
        self.salt = CryptoUtils.generate_salt()
        key = CryptoUtils.generate_key(password, self.salt)
        self.crypto = CryptoUtils(key)

    def test_encryption_decryption(self):
        """Test if encryption and decryption work properly."""
        plaintext = "Sensitive Data"
        encrypted = self.crypto.encrypt(plaintext)
        decrypted = self.crypto.decrypt(encrypted)
        self.assertEqual(plaintext, decrypted)

if __name__ == "__main__":
    unittest.main()
