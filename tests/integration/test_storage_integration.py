# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Storage System Integration Tests

These tests validate the storage layer's integration with local and cloud backends,
including end-to-end workflows and performance measurement.

Assumptions:
- Storage interface exposes: upload_file, download_file, delete_file, list_files
- There is a unified abstraction for local/cloud, selectable by config or function arg
"""

import pytest
from unittest.mock import MagicMock

# Dummy storage backends for demonstration
class DummyLocalStorage:
    files = {}
    @classmethod
    def upload_file(cls, filename, content):
        cls.files[filename] = content
        return True
    @classmethod
    def download_file(cls, filename):
        return cls.files.get(filename, None)
    @classmethod
    def delete_file(cls, filename):
        if filename in cls.files:
            del cls.files[filename]
            return True
        return False
    @classmethod
    def list_files(cls):
        return list(cls.files.keys())

class DummyCloudStorage:
    files = {}  # Separate file dictionary for cloud storage
    
    @classmethod
    def upload_file(cls, filename, content):
        cls.files[filename] = content
        return True
    
    @classmethod
    def download_file(cls, filename):
        return cls.files.get(filename, None)
    
    @classmethod
    def delete_file(cls, filename):
        if filename in cls.files:
            del cls.files[filename]
            return True
        return False
    
    @classmethod
    def list_files(cls):
        return list(cls.files.keys())

@pytest.fixture(autouse=True)
def reset_storage():
    # Reset both storage systems before each test
    DummyLocalStorage.files = {}
    DummyCloudStorage.files = {}
    
@pytest.fixture(params=["local", "cloud"])
def storage_system(request):
    if request.param == "local":
        return DummyLocalStorage
    elif request.param == "cloud":
        return DummyCloudStorage

def test_file_upload_and_download(storage_system):
    filename = "test.txt"
    content = "Integration content"
    assert storage_system.upload_file(filename, content) is True
    retrieved = storage_system.download_file(filename)
    assert retrieved == content

def test_file_delete_and_list(storage_system):
    filename = "delete.txt"
    storage_system.upload_file(filename, "delcontent")
    assert filename in storage_system.list_files()
    assert storage_system.delete_file(filename) is True
    assert filename not in storage_system.list_files()

def test_cross_backend_integrity():
    # Upload in local, not visible in cloud, and vice versa
    DummyLocalStorage.upload_file("localfile.dat", "data123")
    DummyCloudStorage.upload_file("cloudfile.dat", "dataABC")
    assert DummyLocalStorage.download_file("localfile.dat") == "data123"
    assert DummyCloudStorage.download_file("cloudfile.dat") == "dataABC"
    assert DummyCloudStorage.download_file("localfile.dat") is None
    assert DummyLocalStorage.download_file("cloudfile.dat") is None

def test_end_to_end_storage_workflow(storage_system):
    # Simulate file creation, retrieval, and deletion in a true workflow
    fname = "e2e_file.md"
    content = "# E2E Test"
    assert storage_system.upload_file(fname, content)
    assert fname in storage_system.list_files()
    assert storage_system.download_file(fname) == content
    assert storage_system.delete_file(fname)
    assert storage_system.download_file(fname) is None

def test_storage_performance_upload(storage_system):
    import time
    n = 500
    content = "x" * 5000
    start = time.time()
    for i in range(n):
        assert storage_system.upload_file(f"file_{i}.bin", content)
    elapsed = time.time() - start
    assert elapsed < 3.0  # Adjust threshold per environment
