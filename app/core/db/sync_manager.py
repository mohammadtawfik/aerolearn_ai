"""
SyncManager for AeroLearn AI
- Handles synchronization between local cache and remote persistence (or server)
- Implements conflict resolution (last-writer-wins for now, pluggable in future)
- Batch synchronization and detection of offline/online state
"""

import threading
import time
import pickle
from typing import Any, Dict, Tuple, Optional

# In a real system, these would be part of an abstraction/interface
class RemoteSyncProvider:
    """Simulated remote store (would be replaced with actual DB/API client)."""

    def __init__(self):
        self.store = {}

    def pull(self) -> Dict[str, Tuple[Any, float]]:
        """Fetch all remote items: {key: (value, timestamp)}."""
        return self.store.copy()

    def push(self, updates: Dict[str, Tuple[Any, float]]):
        """Update remote storage with the given keys."""
        for k, (v, ts) in updates.items():
            # Last-writer-wins
            if (
                k not in self.store 
                or self.store[k][1] < ts
            ):
                self.store[k] = (v, ts)

    def get(self, key: str):
        return self.store.get(key, (None, 0))

class SyncManager:
    """
    Manage synchronization between the local cache and remote (cloud/server).
    Detects and resolves conflicts. Handles offline/online mode.
    """

    def __init__(self, cache, remote_provider=None):
        self.cache = cache
        self.remote = remote_provider or RemoteSyncProvider()
        self.sync_lock = threading.Lock()
        self.offline_mode = False
        self.last_sync_time = None

    def go_offline(self):
        self.offline_mode = True

    def go_online(self):
        self.offline_mode = False

    def sync(self):
        """Synchronize cache with remote storage."""
        with self.sync_lock:
            # Step 1: Pull remote state
            remote_data = self.remote.pull()
            # Step 2: Merge into cache (conflict = last-write-wins)
            merged_keys = set(remote_data.keys())
            local_cursor = self.cache.conn.execute('SELECT key, value, timestamp FROM cache')
            local_data = {row[0]: (row[1], row[2]) for row in local_cursor.fetchall()}
            merged_keys.update(local_data.keys())

            for key in merged_keys:
                remote_val, remote_ts = remote_data.get(key, (None, 0))
                local_blob, local_ts = local_data.get(key, (None, 0))

                if remote_ts >= local_ts:
                    # Prefer remote
                    if remote_val is not None:
                        self.cache.set(key, remote_val, priority=0)
                elif local_blob is not None:
                    # Prefer local
                    local_val = pickle.loads(local_blob)
                    self.remote.push({key: (local_val, local_ts)})

            self.last_sync_time = time.time()

    def resolve_conflict(self, key: str, remote_item: Tuple[Any, float], local_item: Tuple[Any, float]):
        """Custom conflict resolution if needed (default: last-writer-wins)."""
        # For now, just return the latest
        if remote_item[1] >= local_item[1]:
            return remote_item
        return local_item

    def sync_priority(self, min_priority: int):
        """Sync only high-priority data first (for critical offline/online ops)."""
        items = self.cache.get_priority_items(min_priority)
        updates = {}
        now = time.time()
        for key, value in items.items():
            updates[key] = (value, now)
        self.remote.push(updates)

    def schedule_periodic_sync(self, interval=60):
        """Start a thread that periodically runs sync for background operation."""
        def sync_loop():
            while not self.offline_mode:
                self.sync()
                time.sleep(interval)
        threading.Thread(target=sync_loop, daemon=True).start()
