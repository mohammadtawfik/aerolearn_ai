"""
Local Cache System for AeroLearn AI
- Local cache storage using SQLite (for persistence and offline ops)
- Invalidation logic for expiration or manual/integrity-based removes
- Cache prioritization support for critical data
- Thread-safe design
"""

import threading
import time
import sqlite3
import pickle
from typing import Any, Optional, Dict

class LocalCacheInvalidationPolicy:
    """Handles cache invalidation policies (time-based, manual, integrity)."""

    def __init__(self, default_ttl_seconds=86400):
        # TTL in seconds. Default to 24hrs.
        self.default_ttl = default_ttl_seconds

    def is_expired(self, item_timestamp, current_time=None) -> bool:
        if current_time is None:
            current_time = time.time()
        return (current_time - item_timestamp) > self.default_ttl

class LocalCache:
    """
    Local cache storage supporting offline operation and prioritization.
    
    Singleton is per-db_path for proper test isolation; .get() always rechecks expiration
    and invalidates expired items every time.
    """

    _instances: Dict[str, "LocalCache"] = {}
    _lock = threading.Lock()

    def __new__(cls, db_path=":memory:", *args, **kwargs):
        # Singleton per db_path for correct test isolation and parallel usage
        with cls._lock:
            if db_path not in cls._instances:
                instance = super(LocalCache, cls).__new__(cls)
                cls._instances[db_path] = instance
            return cls._instances[db_path]

    def __init__(self, db_path=":memory:", invalidation_policy=None):
        # Only initialize once per DB path
        if getattr(self, "_initialized", False):
            return
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value BLOB,
                timestamp REAL,
                priority INTEGER
            )
        ''')
        self.invalidation_policy = invalidation_policy or LocalCacheInvalidationPolicy()
        self.cache_lock = threading.RLock()
        self._initialized = True

    def set(self, key: str, value: Any, priority: int = 0):
        """Store a value in the cache with an optional priority."""
        with self.cache_lock:
            blob = pickle.dumps(value)
            now = time.time()
            self.conn.execute('''
                INSERT OR REPLACE INTO cache (key, value, timestamp, priority) VALUES (?, ?, ?, ?)
            ''', (key, blob, now, priority))
            self.conn.commit()

    def get(self, key: str, default: Any = None, allow_expired: bool = False) -> Any:
        """Retrieve cache value; returns default if not found/expired and invalidates if expired."""
        with self.cache_lock:
            cursor = self.conn.execute('SELECT value, timestamp FROM cache WHERE key=?', (key,))
            row = cursor.fetchone()
            if not row:
                return default
            value_blob, ts = row
            if not allow_expired and self.invalidation_policy.is_expired(ts):
                self.delete(key)
                return default
            return pickle.loads(value_blob)

    def delete(self, key: str):
        """Remove a cache entry by key."""
        with self.cache_lock:
            self.conn.execute('DELETE FROM cache WHERE key=?', (key,))
            self.conn.commit()

    def invalidate_expired(self):
        """Remove all expired cache entries efficiently in one commit."""
        with self.cache_lock:
            now = time.time()
            cur = self.conn.execute('SELECT key, timestamp FROM cache')
            keys_to_delete = [row[0] for row in cur if self.invalidation_policy.is_expired(row[1], now)]
            if keys_to_delete:
                self.conn.executemany('DELETE FROM cache WHERE key=?', [(key,) for key in keys_to_delete])
                self.conn.commit()

    def clear(self):
        """Wipe all cache entries."""
        with self.cache_lock:
            self.conn.execute('DELETE FROM cache')
            self.conn.commit()

    def size(self):
        with self.cache_lock:
            cur = self.conn.execute('SELECT COUNT(*) FROM cache')
            return cur.fetchone()[0]

    def get_priority_items(self, min_priority: int) -> Dict[str, Any]:
        """Return all items with at least a minimum priority."""
        with self.cache_lock:
            cur = self.conn.execute('SELECT key, value FROM cache WHERE priority >= ?', (min_priority,))
            result = {row[0]: pickle.loads(row[1]) for row in cur.fetchall()}
            return result
            
    @classmethod
    def reset_singletons(cls):
        """Test utility: clears all singleton cache instances (for test isolation)."""
        with cls._lock:
            for inst in cls._instances.values():
                if hasattr(inst, "conn"):
                    try:
                        inst.conn.close()
                    except Exception:
                        pass
            cls._instances.clear()
