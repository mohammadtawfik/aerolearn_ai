"""
Unit tests for the storage interface contracts.

This module tests the functionality of the storage-related interfaces like
StorageProviderInterface, SynchronizationInterface, and others.
"""
import sys
import os
import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Optional, Any, BinaryIO, Tuple, AsyncIterator
from datetime import datetime

# Add the project root to the Python path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the modules to test
from integrations.interfaces.base_interface import (
    BaseInterface, InterfaceImplementation, InterfaceMethod
)
from integrations.interfaces.storage_interface import (
    StorageScope, StoragePermission, SyncStatus, StorageItem, SyncConflict,
    SyncProgress, StorageProviderInterface, SynchronizationInterface,
    StorageQuotaInterface, StoragePermissionInterface, FileStreamingInterface
)


class TestStorageEnums:
    """Tests for storage-related enumerations."""
    
    def test_storage_scope_values(self):
        """Test that StorageScope has expected values."""
        assert StorageScope.USER.value == "user"
        assert StorageScope.COURSE.value == "course"
        assert StorageScope.INSTITUTION.value == "institution"
        assert StorageScope.PUBLIC.value == "public"
        assert StorageScope.SYSTEM.value == "system"
    
    def test_storage_permission_values(self):
        """Test that StoragePermission has expected values."""
        assert StoragePermission.READ.value == "read"
        assert StoragePermission.WRITE.value == "write"
        assert StoragePermission.DELETE.value == "delete"
        assert StoragePermission.FULL.value == "full"
        assert StoragePermission.NONE.value == "none"
    
    def test_sync_status_values(self):
        """Test that SyncStatus has expected values."""
        assert SyncStatus.SYNCED.value == "synced"
        assert SyncStatus.LOCAL_ONLY.value == "local_only"
        assert SyncStatus.REMOTE_ONLY.value == "remote_only"
        assert SyncStatus.MODIFIED.value == "modified"
        assert SyncStatus.CONFLICT.value == "conflict"


class TestStorageItem:
    """Tests for the StorageItem class."""
    
    def test_init_with_required_fields(self):
        """Test initialization with required fields."""
        item = StorageItem(
            item_id="item123",
            name="test.txt",
            path="/user/test.txt",
            is_folder=False
        )
        
        assert item.item_id == "item123"
        assert item.name == "test.txt"
        assert item.path == "/user/test.txt"
        assert item.is_folder is False
        assert item.size_bytes == 0
        assert isinstance(item.created_date, datetime)
        assert isinstance(item.modified_date, datetime)
    
    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        created_date = datetime(2025, 1, 1)
        modified_date = datetime(2025, 2, 1)
        permissions = {"user1": StoragePermission.READ}
        metadata = {"key": "value"}
        
        item = StorageItem(
            item_id="item123",
            name="test.txt",
            path="/user/test.txt",
            is_folder=False,
            size_bytes=1024,
            created_date=created_date,
            modified_date=modified_date,
            storage_provider="local",
            scope=StorageScope.USER,
            owner_id="user1",
            sync_status=SyncStatus.SYNCED,
            mime_type="text/plain",
            permissions=permissions,
            metadata=metadata
        )
        
        assert item.item_id == "item123"
        assert item.name == "test.txt"
        assert item.size_bytes == 1024
        assert item.created_date == created_date
        assert item.modified_date == modified_date
        assert item.storage_provider == "local"
        assert item.scope == StorageScope.USER
        assert item.owner_id == "user1"
        assert item.sync_status == SyncStatus.SYNCED
        assert item.mime_type == "text/plain"
        assert item.permissions == permissions
        assert item.metadata == metadata
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        created_date = datetime(2025, 1, 1)
        modified_date = datetime(2025, 2, 1)
        
        item = StorageItem(
            item_id="item123",
            name="test.txt",
            path="/user/test.txt",
            is_folder=False,
            size_bytes=1024,
            created_date=created_date,
            modified_date=modified_date,
            storage_provider="local",
            scope=StorageScope.USER,
            owner_id="user1",
            sync_status=SyncStatus.SYNCED,
            mime_type="text/plain",
            permissions={"user1": StoragePermission.READ},
            metadata={"key": "value"}
        )
        
        item_dict = item.to_dict()
        
        assert item_dict["item_id"] == "item123"
        assert item_dict["name"] == "test.txt"
        assert item_dict["path"] == "/user/test.txt"
        assert item_dict["is_folder"] is False
        assert item_dict["size_bytes"] == 1024
        assert item_dict["created_date"] == created_date.isoformat()
        assert item_dict["modified_date"] == modified_date.isoformat()
        assert item_dict["storage_provider"] == "local"
        assert item_dict["scope"] == StorageScope.USER.value
        assert item_dict["owner_id"] == "user1"
        assert item_dict["sync_status"] == SyncStatus.SYNCED.value
        assert item_dict["mime_type"] == "text/plain"
        assert item_dict["permissions"]["user1"] == StoragePermission.READ.value
        assert item_dict["metadata"]["key"] == "value"
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        created_date = datetime(2025, 1, 1)
        modified_date = datetime(2025, 2, 1)
        
        item_dict = {
            "item_id": "item123",
            "name": "test.txt",
            "path": "/user/test.txt",
            "is_folder": False,
            "size_bytes": 1024,
            "created_date": created_date.isoformat(),
            "modified_date": modified_date.isoformat(),
            "storage_provider": "local",
            "scope": "user",
            "owner_id": "user1",
            "sync_status": "synced",
            "mime_type": "text/plain",
            "permissions": {"user1": "read"},
            "metadata": {"key": "value"}
        }
        
        item = StorageItem.from_dict(item_dict)
        
        assert item.item_id == "item123"
        assert item.name == "test.txt"
        assert item.path == "/user/test.txt"
        assert item.is_folder is False
        assert item.size_bytes == 1024
        assert item.created_date.isoformat() == created_date.isoformat()
        assert item.modified_date.isoformat() == modified_date.isoformat()
        assert item.storage_provider == "local"
        assert item.scope == StorageScope.USER
        assert item.owner_id == "user1"
        assert item.sync_status == SyncStatus.SYNCED
        assert item.mime_type == "text/plain"
        assert item.permissions["user1"] == StoragePermission.READ
        assert item.metadata["key"] == "value"


class TestSyncConflict:
    """Tests for the SyncConflict class."""
    
    def test_init(self):
        """Test initialization."""
        local_date = datetime(2025, 1, 1)
        remote_date = datetime(2025, 2, 1)
        
        conflict = SyncConflict(
            item_id="item123",
            path="/user/test.txt",
            local_modified_date=local_date,
            remote_modified_date=remote_date,
            local_size_bytes=1024,
            remote_size_bytes=2048
        )
        
        assert conflict.item_id == "item123"
        assert conflict.path == "/user/test.txt"
        assert conflict.local_modified_date == local_date
        assert conflict.remote_modified_date == remote_date
        assert conflict.local_size_bytes == 1024
        assert conflict.remote_size_bytes == 2048
        assert isinstance(conflict.conflict_detected_date, datetime)


class TestSyncProgress:
    """Tests for the SyncProgress class."""
    
    def test_init_with_required_fields(self):
        """Test initialization with required fields."""
        progress = SyncProgress(total_items=10)
        
        assert progress.total_items == 10
        assert progress.processed_items == 0
        assert progress.bytes_transferred == 0
        assert progress.total_bytes == 0
        assert progress.current_item is None
        assert isinstance(progress.start_time, datetime)
        assert progress.estimated_completion_time is None
        assert progress.status == "pending"
    
    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        start_time = datetime(2025, 1, 1)
        estimated_completion_time = datetime(2025, 1, 1, 1, 0, 0)
        
        progress = SyncProgress(
            total_items=10,
            processed_items=5,
            bytes_transferred=512,
            total_bytes=1024,
            current_item="/user/test.txt",
            start_time=start_time,
            estimated_completion_time=estimated_completion_time,
            status="in_progress"
        )
        
        assert progress.total_items == 10
        assert progress.processed_items == 5
        assert progress.bytes_transferred == 512
        assert progress.total_bytes == 1024
        assert progress.current_item == "/user/test.txt"
        assert progress.start_time == start_time
        assert progress.estimated_completion_time == estimated_completion_time
        assert progress.status == "in_progress"
    
    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        progress1 = SyncProgress(total_items=10, processed_items=5)
        assert progress1.completion_percentage == 50.0
        
        progress2 = SyncProgress(total_items=0)
        assert progress2.completion_percentage == 0.0
        
        progress3 = SyncProgress(total_items=10, processed_items=10)
        assert progress3.completion_percentage == 100.0


class TestStorageProviderInterface:
    """Tests for the StorageProviderInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert StorageProviderInterface.interface_name == "storage_provider"
        assert StorageProviderInterface.interface_version == "1.0.0"
        
        # Register the interface
        StorageProviderInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "storage_provider" in interfaces
        assert interfaces["storage_provider"] == StorageProviderInterface


class TestSynchronizationInterface:
    """Tests for the SynchronizationInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert SynchronizationInterface.interface_name == "synchronization"
        assert SynchronizationInterface.interface_version == "1.0.0"
        
        # Register the interface
        SynchronizationInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "synchronization" in interfaces
        assert interfaces["synchronization"] == SynchronizationInterface


class TestStorageQuotaInterface:
    """Tests for the StorageQuotaInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert StorageQuotaInterface.interface_name == "storage_quota"
        assert StorageQuotaInterface.interface_version == "1.0.0"
        
        # Register the interface
        StorageQuotaInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "storage_quota" in interfaces
        assert interfaces["storage_quota"] == StorageQuotaInterface


class TestStoragePermissionInterface:
    """Tests for the StoragePermissionInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert StoragePermissionInterface.interface_name == "storage_permission"
        assert StoragePermissionInterface.interface_version == "1.0.0"
        
        # Register the interface
        StoragePermissionInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "storage_permission" in interfaces
        assert interfaces["storage_permission"] == StoragePermissionInterface


class TestFileStreamingInterface:
    """Tests for the FileStreamingInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert FileStreamingInterface.interface_name == "file_streaming"
        assert FileStreamingInterface.interface_version == "1.0.0"
        
        # Register the interface
        FileStreamingInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "file_streaming" in interfaces
        assert interfaces["file_streaming"] == FileStreamingInterface


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
