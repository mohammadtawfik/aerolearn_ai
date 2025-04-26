"""
File: metadata.py

Manages metadata for files and directories, including custom tags, versioning, and change detection.
"""

from typing import Dict, Any, Optional
import hashlib
import time
import os

class MetadataManager:
    def __init__(self, backend):
        """
        backend: Should provide storage for metadata (could be local file, DB, or remote service).
        """
        self.backend = backend

    def generate_file_hash(self, file_path: str) -> Optional[str]:
        """
        Calculates and returns a SHA256 hash for file content.
        """
        if not os.path.isfile(file_path):
            return None
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()

    def set_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        Stores or updates metadata for a file.
        """
        self.backend.set_metadata(file_path, metadata)

    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata associated with file_path.
        """
        return self.backend.get_metadata(file_path)
    
    def detect_change(self, file_path: str) -> bool:
        """
        Detects if file has changed (by comparing hash with stored).
        Stores new hash if change is detected.
        Returns True if changed.
        """
        stored = self.get_metadata(file_path) or {}
        current_hash = self.generate_file_hash(file_path)
        if not current_hash:
            return False
        if stored.get("hash") != current_hash:
            new_metadata = dict(stored)
            new_metadata["hash"] = current_hash
            new_metadata["last_modified"] = time.time()
            self.set_metadata(file_path, new_metadata)
            return True
        return False