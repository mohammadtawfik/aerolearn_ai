"""
File: file_operations.py

Implements file upload and download operations with support for local and remote (Google Drive) backends.
Uses events to notify about operations and errors. Metadata updates handled via metadata.py.
"""

import os
from typing import BinaryIO, Optional, Callable

class FileOperationError(Exception):
    """Custom exception type for file operations."""
    pass

class FileOperations:
    def __init__(self, storage_backend, event_callback: Optional[Callable] = None):
        """
        storage_backend: Must implement upload_file, download_file, and delete_file as required by the interface.
        event_callback: Optional function for event notification.
        """
        self.backend = storage_backend
        self.event_callback = event_callback

    def upload(self, src_path: str, dest_path: str, metadata: Optional[dict] = None) -> dict:
        """
        Upload a file from src_path to dest_path on the backend.
        metadata: Optional dictionary to store with file.
        Returns updated metadata.
        """
        if not os.path.exists(src_path):
            raise FileOperationError(f"File not found: {src_path}")
        try:
            result_meta = self.backend.upload_file(src_path, dest_path, metadata)
            if self.event_callback:
                self.event_callback("file_uploaded", {"src": src_path, "dest": dest_path, "metadata": result_meta})
            return result_meta
        except Exception as e:
            if self.event_callback:
                self.event_callback("file_upload_failed", {"src": src_path, "dest": dest_path, "error": str(e)})
            raise FileOperationError(str(e)) from e
        
    def download(self, file_path: str, dest_path: str) -> None:
        """
        Download a file from backend file_path to dest_path.
        """
        try:
            self.backend.download_file(file_path, dest_path)
            if self.event_callback:
                self.event_callback("file_downloaded", {"src": file_path, "dest": dest_path})
        except Exception as e:
            if self.event_callback:
                self.event_callback("file_download_failed", {"src": file_path, "dest": dest_path, "error": str(e)})
            raise FileOperationError(str(e)) from e

    def delete(self, file_path: str) -> None:
        """
        Delete file from backend.
        """
        try:
            self.backend.delete_file(file_path)
            if self.event_callback:
                self.event_callback("file_deleted", {"path": file_path})
        except Exception as e:
            if self.event_callback:
                self.event_callback("file_delete_failed", {"path": file_path, "error": str(e)})
            raise FileOperationError(str(e)) from e

# The storage_backend should be implemented (e.g., LocalFileBackend, GoogleDriveBackend).