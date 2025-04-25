from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
import os
import base64

class CryptoUtils:
    def __init__(self, key: bytes):
        self.key = key
        self.backend = default_backend()

    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        """Generate a 256-bit key using PBKDF2 with SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    @staticmethod
    def generate_salt() -> bytes:
        """Generate a random salt."""
        return os.urandom(16)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt the plaintext string."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()

        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext).decode()

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt the encrypted string."""
        encrypted_data = base64.b64decode(encrypted_text)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode()