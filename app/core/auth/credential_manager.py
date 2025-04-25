import os
import json
from app.utils.crypto import CryptoUtils

class CredentialManager:
    def __init__(self, password: str):
        self.salt_file = "salt.bin"
        self.credentials_file = "credentials.json"
        self.salt = self._load_or_generate_salt()
        self.crypto = CryptoUtils(CryptoUtils.generate_key(password, self.salt))

    def _load_or_generate_salt(self) -> bytes:
        """Load or generate a random salt for key derivation."""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, "rb") as f:
                return f.read()
        else:
            salt = CryptoUtils.generate_salt()
            with open(self.salt_file, "wb") as f:
                f.write(salt)
            return salt

    def store_credential(self, key: str, value: str) -> None:
        """Store an encrypted credential."""
        credentials = self._load_credentials()
        encrypted_value = self.crypto.encrypt(value)
        credentials[key] = encrypted_value
        self._save_credentials(credentials)

    def retrieve_credential(self, key: str) -> str:
        """Retrieve and decrypt a credential."""
        credentials = self._load_credentials()
        encrypted_value = credentials.get(key)
        if not encrypted_value:
            raise ValueError("Credential not found")
        return self.crypto.decrypt(encrypted_value)

    def _load_credentials(self) -> dict:
        """Load credentials from the file."""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "r") as f:
                return json.load(f)
        return {}

    def _save_credentials(self, credentials: dict) -> None:
        """Save credentials to the file."""
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=4)