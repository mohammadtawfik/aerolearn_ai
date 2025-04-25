"""
Storage interface contracts for the AeroLearn AI system.

This module defines the interfaces for storage systems, including local and cloud
storage providers, synchronization mechanisms, and file operations.
"""
import abc
import os
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union, BinaryIO, Tuple, AsyncIterator

from .base_interface import BaseInterface, InterfaceImplementation, InterfaceMethod


class StorageScope(Enum):
    """Defines the scope/visibility of stored data."""
    USER = "user"         # Visible only to a specific user
    COURSE = "course"     # Visible to all participants in a course
    INSTITUTION = "institution"  # Visible to all users in an institution
    PUBLIC = "public"     # Publicly visible
    SYSTEM = "system"     # System-level storage, not directly user-accessible


class StoragePermission(Enum):
    """Permission levels for stored items."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    FULL = "full"
    NONE = "none"


class SyncStatus(Enum):
    """Synchronization status for stored items."""
    SYNCED = "synced"          # Fully synchronized with remote storage
    LOCAL_ONLY = "local_only"  # Exists only locally
    REMOTE_ONLY = "remote_only"  # Exists only in remote storage
    MODIFIED = "modified"      # Modified locally, not yet synced
    CONFLICT = "conflict"      # Conflicting changes between local and remote
    SYNCING = "syncing"        # Currently being synchronized
    ERROR = "error"            # Error during synchronization


class StorageItem:
    """
    Represents a storage item (file or folder) with metadata.
    """
    
    def __init__(self,
                 item_id: str,
                 name: str,
                 path: str,
                 is_folder: bool,
                 size_bytes: int = 0,
                 created_date: datetime = None,
                 modified_date: datetime = None,
                 storage_provider: str = None,
                 scope: StorageScope = StorageScope.USER,
                 owner_id: str = None,
                 sync_status: SyncStatus = None,
                 mime_type: str = None,
                 permissions: Dict[str, StoragePermission] = None,
                 metadata: Dict[str, Any] = None):
        """
        Initialize a storage item.
        
        Args:
            item_id: Unique identifier for the item
            name: Display name of the item
            path: Path to the item
            is_folder: True if the item is a folder, False if it's a file
            size_bytes: Size of the item in bytes
            created_date: Date the item was created
            modified_date: Date the item was last modified
            storage_provider: ID of the provider storing this item
            scope: Visibility scope of the item
            owner_id: ID of the item's owner
            sync_status: Current synchronization status
            mime_type: MIME type for files
            permissions: Dictionary mapping user/group IDs to permissions
            metadata: Additional metadata for the item
        """
        self.item_id = item_id
        self.name = name
        self.path = path
        self.is_folder = is_folder
        self.size_bytes = size_bytes
        self.created_date = created_date or datetime.now()
        self.modified_date = modified_date or datetime.now()
        self.storage_provider = storage_provider
        self.scope = scope
        self.owner_id = owner_id
        self.sync_status = sync_status
        self.mime_type = mime_type
        self.permissions = permissions or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the storage item to a dictionary."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "path": self.path,
            "is_folder": self.is_folder,
            "size_bytes": self.size_bytes,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "modified_date": self.modified_date.isoformat() if self.modified_date else None,
            "storage_provider": self.storage_provider,
            "scope": self.scope.value if self.scope else None,
            "owner_id": self.owner_id,
            "sync_status": self.sync_status.value if self.sync_status else None,
            "mime_type": self.mime_type,
            "permissions": {k: v.value for k, v in self.permissions.items()},
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageItem':
        """Create a storage item from a dictionary."""
        # Convert string dates to datetime objects
        created_date = datetime.fromisoformat(data["created_date"]) if data.get("created_date") else None
        modified_date = datetime.fromisoformat(data["modified_date"]) if data.get("modified_date") else None
        
        # Convert string enums to enum objects
        scope = StorageScope(data["scope"]) if data.get("scope") else None
        sync_status = SyncStatus(data["sync_status"]) if data.get("sync_status") else None
        permissions = {k: StoragePermission(v) for k, v in data.get("permissions", {}).items()}
        
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            path=data["path"],
            is_folder=data["is_folder"],
            size_bytes=data.get("size_bytes", 0),
            created_date=created_date,
            modified_date=modified_date,
            storage_provider=data.get("storage_provider"),
            scope=scope,
            owner_id=data.get("owner_id"),
            sync_status=sync_status,
            mime_type=data.get("mime_type"),
            permissions=permissions,
            metadata=data.get("metadata", {})
        )


class SyncConflict:
    """
    Represents a synchronization conflict between local and remote versions.
    """
    
    def __init__(self,
                 item_id: str,
                 path: str,
                 local_modified_date: datetime,
                 remote_modified_date: datetime,
                 local_size_bytes: int,
                 remote_size_bytes: int,
                 conflict_detected_date: datetime = None):
        """
        Initialize a sync conflict.
        
        Args:
            item_id: ID of the conflicting item
            path: Path to the conflicting item
            local_modified_date: Modification date of the local version
            remote_modified_date: Modification date of the remote version
            local_size_bytes: Size of the local version
            remote_size_bytes: Size of the remote version
            conflict_detected_date: Date the conflict was detected
        """
        self.item_id = item_id
        self.path = path
        self.local_modified_date = local_modified_date
        self.remote_modified_date = remote_modified_date
        self.local_size_bytes = local_size_bytes
        self.remote_size_bytes = remote_size_bytes
        self.conflict_detected_date = conflict_detected_date or datetime.now()


class SyncProgress:
    """
    Represents the progress of a synchronization operation.
    """
    
    def __init__(self,
                 total_items: int,
                 processed_items: int = 0,
                 bytes_transferred: int = 0,
                 total_bytes: int = 0,
                 current_item: str = None,
                 start_time: datetime = None,
                 estimated_completion_time: datetime = None,
                 status: str = "pending"):
        """
        Initialize sync progress.
        
        Args:
            total_items: Total number of items to sync
            processed_items: Number of items processed so far
            bytes_transferred: Number of bytes transferred so far
            total_bytes: Total number of bytes to transfer
            current_item: Path of the item currently being processed
            start_time: Time the sync operation started
            estimated_completion_time: Estimated completion time
            status: Current status of the sync operation
        """
        self.total_items = total_items
        self.processed_items = processed_items
        self.bytes_transferred = bytes_transferred
        self.total_bytes = total_bytes
        self.current_item = current_item
        self.start_time = start_time or datetime.now()
        self.estimated_completion_time = estimated_completion_time
        self.status = status
    
    @property
    def completion_percentage(self) -> float:
        """Calculate the completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100


class StorageProviderInterface(BaseInterface):
    """
    Interface for components that provide storage capabilities.
    """
    interface_name = "storage_provider"
    interface_version = "1.0.0"
    interface_description = "Interface for components that provide storage capabilities"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_file(self, path: str) -> Tuple[Optional[BinaryIO], Optional[StorageItem]]:
        """
        Retrieve a file by path.
        
        Args:
            path: Path to the file
            
        Returns:
            Tuple of (file_stream, metadata) or (None, None) if not found
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def put_file(self, path: str, file_stream: BinaryIO, metadata: Dict[str, Any] = None) -> Optional[StorageItem]:
        """
        Store a file at the specified path.
        
        Args:
            path: Path where the file should be stored
            file_stream: Binary stream of the file content
            metadata: Optional metadata for the file
            
        Returns:
            StorageItem if successful, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def delete_item(self, path: str) -> bool:
        """
        Delete a file or folder by path.
        
        Args:
            path: Path to the item to delete
            
        Returns:
            True if deleted, False if not found or unable to delete
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def create_folder(self, path: str, metadata: Dict[str, Any] = None) -> Optional[StorageItem]:
        """
        Create a folder at the specified path.
        
        Args:
            path: Path where the folder should be created
            metadata: Optional metadata for the folder
            
        Returns:
            StorageItem if successful, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def list_items(self, path: str) -> List[StorageItem]:
        """
        List items in a folder.
        
        Args:
            path: Path to the folder
            
        Returns:
            List of items in the folder
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def item_exists(self, path: str) -> bool:
        """
        Check if an item exists at the specified path.
        
        Args:
            path: Path to check
            
        Returns:
            True if the item exists, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_item_metadata(self, path: str) -> Optional[StorageItem]:
        """
        Get metadata for an item without retrieving its content.
        
        Args:
            path: Path to the item
            
        Returns:
            StorageItem if found, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def update_item_metadata(self, path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an item.
        
        Args:
            path: Path to the item
            metadata: New metadata values to apply
            
        Returns:
            True if updated, False if not found or unable to update
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def move_item(self, source_path: str, destination_path: str) -> bool:
        """
        Move an item from one path to another.
        
        Args:
            source_path: Current path of the item
            destination_path: New path for the item
            
        Returns:
            True if moved, False if not found or unable to move
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def copy_item(self, source_path: str, destination_path: str) -> Optional[StorageItem]:
        """
        Copy an item from one path to another.
        
        Args:
            source_path: Path of the item to copy
            destination_path: Path where the copy should be created
            
        Returns:
            StorageItem for the copy if successful, None otherwise
        """
        pass


class SynchronizationInterface(BaseInterface):
    """
    Interface for components that synchronize content between storage providers.
    """
    interface_name = "synchronization"
    interface_version = "1.0.0"
    interface_description = "Interface for components that synchronize content between storage providers"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def sync_item(self, path: str, direction: str = "both") -> bool:
        """
        Synchronize a specific item.
        
        Args:
            path: Path to the item to synchronize
            direction: Direction of synchronization ("upload", "download", or "both")
            
        Returns:
            True if synchronized successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def sync_folder(self, path: str, recursive: bool = True, 
                         direction: str = "both") -> Dict[str, Any]:
        """
        Synchronize a folder and optionally its contents.
        
        Args:
            path: Path to the folder to synchronize
            recursive: Whether to synchronize subfolders recursively
            direction: Direction of synchronization ("upload", "download", or "both")
            
        Returns:
            Dictionary with synchronization results
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def start_continuous_sync(self, path: str) -> bool:
        """
        Start continuous synchronization for a path.
        
        Args:
            path: Path to continuously synchronize
            
        Returns:
            True if continuous sync started successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def stop_continuous_sync(self, path: str) -> bool:
        """
        Stop continuous synchronization for a path.
        
        Args:
            path: Path to stop synchronizing
            
        Returns:
            True if continuous sync stopped successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_sync_status(self, path: str) -> Dict[str, Any]:
        """
        Get synchronization status for an item.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with sync status information
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def resolve_conflict(self, path: str, resolution: str) -> bool:
        """
        Resolve a synchronization conflict.
        
        Args:
            path: Path to the item with a conflict
            resolution: Conflict resolution strategy ("use_local", "use_remote", "keep_both")
            
        Returns:
            True if conflict resolved successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def list_conflicts(self) -> List[SyncConflict]:
        """
        List all current synchronization conflicts.
        
        Returns:
            List of sync conflicts
        """
        pass
    

class StorageQuotaInterface(BaseInterface):
    """
    Interface for components that manage storage quotas.
    """
    interface_name = "storage_quota"
    interface_version = "1.0.0"
    interface_description = "Interface for components that manage storage quotas"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_usage(self, scope: StorageScope = StorageScope.USER, owner_id: str = None) -> Dict[str, int]:
        """
        Get storage usage statistics.
        
        Args:
            scope: Scope to check usage for
            owner_id: ID of the owner (required for USER scope)
            
        Returns:
            Dictionary with usage statistics (bytes used, bytes allowed, etc.)
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def set_quota(self, bytes_allowed: int, scope: StorageScope = StorageScope.USER, 
                       owner_id: str = None) -> bool:
        """
        Set storage quota.
        
        Args:
            bytes_allowed: Number of bytes allowed
            scope: Scope to set quota for
            owner_id: ID of the owner (required for USER scope)
            
        Returns:
            True if quota set successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def check_quota(self, bytes_needed: int, scope: StorageScope = StorageScope.USER, 
                         owner_id: str = None) -> bool:
        """
        Check if a quota allows for the specified amount of bytes.
        
        Args:
            bytes_needed: Number of bytes needed
            scope: Scope to check quota for
            owner_id: ID of the owner (required for USER scope)
            
        Returns:
            True if the quota allows for the bytes needed, False otherwise
        """
        pass


class StoragePermissionInterface(BaseInterface):
    """
    Interface for components that manage storage permissions.
    """
    interface_name = "storage_permission"
    interface_version = "1.0.0"
    interface_description = "Interface for components that manage storage permissions"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_permissions(self, path: str) -> Dict[str, StoragePermission]:
        """
        Get permissions for an item.
        
        Args:
            path: Path to the item
            
        Returns:
            Dictionary mapping user/group IDs to permissions
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def set_permission(self, path: str, principal_id: str, permission: StoragePermission) -> bool:
        """
        Set permission for a principal on an item.
        
        Args:
            path: Path to the item
            principal_id: ID of the user or group
            permission: Permission to set
            
        Returns:
            True if permission set successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def check_permission(self, path: str, principal_id: str, required_permission: StoragePermission) -> bool:
        """
        Check if a principal has the required permission on an item.
        
        Args:
            path: Path to the item
            principal_id: ID of the user or group
            required_permission: Permission to check
            
        Returns:
            True if the principal has the required permission, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def inherit_permissions(self, path: str, recursive: bool = False) -> bool:
        """
        Set an item to inherit permissions from its parent.
        
        Args:
            path: Path to the item
            recursive: Whether to apply inheritance recursively to children
            
        Returns:
            True if inheritance set successfully, False otherwise
        """
        pass


class FileStreamingInterface(BaseInterface):
    """
    Interface for components that provide file streaming capabilities.
    """
    interface_name = "file_streaming"
    interface_version = "1.0.0"
    interface_description = "Interface for components that provide file streaming capabilities"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def stream_file(self, path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream a file in chunks.
        
        Args:
            path: Path to the file
            chunk_size: Size of each chunk in bytes
            
        Returns:
            Async iterator yielding file chunks
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def stream_to_file(self, source_stream: AsyncIterator[bytes], destination_path: str) -> int:
        """
        Stream data to a file.
        
        Args:
            source_stream: Async iterator yielding data chunks
            destination_path: Path where the file should be created
            
        Returns:
            Total number of bytes written
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_content_range(self, path: str, start: int, end: int) -> Tuple[bytes, StorageItem]:
        """
        Get a specific byte range from a file.
        
        Args:
            path: Path to the file
            start: Start byte (inclusive)
            end: End byte (inclusive)
            
        Returns:
            Tuple of (content_bytes, metadata)
        """
        pass
