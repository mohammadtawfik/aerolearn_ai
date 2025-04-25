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