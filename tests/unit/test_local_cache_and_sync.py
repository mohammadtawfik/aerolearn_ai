import pytest
import tempfile
import os
import time

from app.core.db.local_cache import LocalCache, LocalCacheInvalidationPolicy
from app.core.db.sync_manager import SyncManager, RemoteSyncProvider

@pytest.fixture(autouse=True)
def reset_cache_singletons():
    LocalCache.reset_singletons()
    yield
    LocalCache.reset_singletons()  # Clean up after test

def test_cache_storage_and_retrieval(tmp_path):
    db_path = tmp_path / "cache.db"
    cache = LocalCache(str(db_path))
    cache.set("foo", {"bar": 1}, priority=1)
    val = cache.get("foo")
    assert isinstance(val, dict)
    assert val['bar'] == 1

def test_cache_expiry(tmp_path):
    db_path = tmp_path / "cache2.db"
    policy = LocalCacheInvalidationPolicy(default_ttl_seconds=1)  # 1s TTL
    cache = LocalCache(str(db_path), invalidation_policy=policy)
    cache.set("baz", 123)
    time.sleep(1.5)
    assert cache.get("baz") is None  # expired

def test_cache_priority(tmp_path):
    db_path = tmp_path / "cache3.db"
    cache = LocalCache(str(db_path))
    cache.set("crit1", "data1", priority=5)
    cache.set("noncrit", "data2", priority=1)
    crit = cache.get_priority_items(3)
    assert "crit1" in crit
    assert "noncrit" not in crit

def test_cache_offline_mode_sync(tmp_path):
    db_path = tmp_path / "cache4.db"
    cache = LocalCache(str(db_path))
    remote = RemoteSyncProvider()
    sync = SyncManager(cache, remote_provider=remote)

    cache.set("alpha", 1)
    sync.go_offline()
    cache.set("beta", 2)  # Added while offline

    assert sync.offline_mode
    sync.go_online()
    assert not sync.offline_mode

def test_sync_conflict_resolution(tmp_path):
    db_path = tmp_path / "cache5.db"
    cache = LocalCache(str(db_path))
    remote = RemoteSyncProvider()
    sync = SyncManager(cache, remote_provider=remote)

    cache.set("k", "local", priority=1)
    ts = time.time()
    remote.push({"k": ("remote", ts - 100)})  # Older remote
    sync.sync()
    assert cache.get("k") == "local"

    cache.set("k2", "local2", priority=1)
    ts = time.time()
    remote.push({"k2": ("remote2", ts + 100)})
    sync.sync()
    assert cache.get("k2") == "remote2"

def test_cache_invalidation(tmp_path):
    db_path = tmp_path / "cache6.db"
    policy = LocalCacheInvalidationPolicy(default_ttl_seconds=1)
    cache = LocalCache(str(db_path), invalidation_policy=policy)
    cache.set("d", 1)
    time.sleep(1.2)
    cache.invalidate_expired()
    assert cache.get("d") is None

def test_cache_persistence(tmp_path):
    db_path = tmp_path / "cache7.db"
    cache = LocalCache(str(db_path))
    cache.set("persist", 42)
    del cache  # simulate app restart
    cache2 = LocalCache(str(db_path))
    assert cache2.get("persist") == 42
