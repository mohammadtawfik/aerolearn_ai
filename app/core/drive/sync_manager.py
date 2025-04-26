"""
File: sync_manager.py

Implements file synchronization between local cache and remote backend (e.g., Google Drive).
Handles conflict resolution, batch sync, and uses MetadataManager for change detection.
"""

from typing import List, Dict
import os
import threading

class ConflictType:
    LOCAL_WIN = "local"
    REMOTE_WIN = "remote"
    MANUAL = "manual"

class SyncConflict(Exception):
    def __init__(self, file_path, local_meta, remote_meta):
        super().__init__(f"Sync conflict for {file_path}")
        self.file_path = file_path
        self.local_meta = local_meta
        self.remote_meta = remote_meta

class SyncManager:
    def __init__(self, local_backend, remote_backend, metadata_manager):
        """
        local_backend: implements upload_file, download_file, list_files, delete_file
        remote_backend: same interface as local_backend (can be Google Drive)
        metadata_manager: MetadataManager instance
        """
        self.local = local_backend
        self.remote = remote_backend
        self.meta = metadata_manager

    def sync_file(self, rel_path: str, conflict_policy=ConflictType.MANUAL):
        """
        Synchronize a single file by relative path.
        Returns True if file synchronized, False if skipped, raises SyncConflict if manual intervention needed.
        """
        local_meta = self.meta.get_metadata(self.local.abs_path(rel_path)) or {}
        remote_meta = self.meta.get_metadata(self.remote.abs_path(rel_path)) or {}

        local_hash = local_meta.get("hash")
        remote_hash = remote_meta.get("hash")

        # Detect conflicts
        if local_hash and remote_hash and local_hash != remote_hash:
            if conflict_policy == ConflictType.LOCAL_WIN:
                self.remote.upload_file(self.local.abs_path(rel_path), rel_path)
                self.meta.set_metadata(self.remote.abs_path(rel_path), local_meta)
                return True
            elif conflict_policy == ConflictType.REMOTE_WIN:
                self.local.download_file(rel_path, self.local.abs_path(rel_path))
                self.meta.set_metadata(self.local.abs_path(rel_path), remote_meta)
                return True
            else:
                raise SyncConflict(rel_path, local_meta, remote_meta)
        elif not remote_hash and local_hash:
            self.remote.upload_file(self.local.abs_path(rel_path), rel_path)
            self.meta.set_metadata(self.remote.abs_path(rel_path), local_meta)
            return True
        elif not local_hash and remote_hash:
            self.local.download_file(rel_path, self.local.abs_path(rel_path))
            self.meta.set_metadata(self.local.abs_path(rel_path), remote_meta)
            return True
        return False  # No sync needed

    def sync_all(self, conflict_policy=ConflictType.MANUAL) -> Dict[str, str]:
        """
        Batch synchronizes all files. Returns a dict: file -> status.
        """
        results = {}
        local_files = set(self.local.list_files())
        remote_files = set(self.remote.list_files())
        all_files = local_files.union(remote_files)
        for rel_path in all_files:
            try:
                res = self.sync_file(rel_path, conflict_policy)
                if res:
                    results[rel_path] = "synced"
                else:
                    results[rel_path] = "up-to-date"
            except SyncConflict as sc:
                results[rel_path] = f"conflict: {sc}"
        return results