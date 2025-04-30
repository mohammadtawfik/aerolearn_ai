# File location: /app/core/vector_db/sync_manager.py

"""
Handles synchronization and persistence for AeroLearn AI vector DB.
Features local file backup/restore, and (if extended) remote sync with a production vector DB.
"""

import threading
import time
import os

class VectorDBSyncManager:
    def __init__(self, index_manager, persist_path="vector_index.dat", interval_sec=60):
        self.index_manager = index_manager
        self.persist_path = persist_path
        self.interval_sec = interval_sec
        self._stop_event = threading.Event()
        self._thread = None

    def start_auto_sync(self):
        if self._thread and self._thread.is_alive():
            return  # Already running
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop_auto_sync(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _run(self):
        while not self._stop_event.is_set():
            self.persist()
            time.sleep(self.interval_sec)

    def persist(self):
        try:
            self.index_manager.persist_index(self.persist_path)
            print(f"[VectorDBSyncManager] Index persisted to {self.persist_path}")
        except Exception as e:
            print(f"[VectorDBSyncManager] Persist error: {e}")

    def restore(self):
        if os.path.exists(self.persist_path):
            try:
                self.index_manager.load_index(self.persist_path)
                print(f"[VectorDBSyncManager] Index restored from {self.persist_path}")
            except Exception as e:
                print(f"[VectorDBSyncManager] Restore error: {e}")
        else:
            print(f"[VectorDBSyncManager] No persisted index found at {self.persist_path}")