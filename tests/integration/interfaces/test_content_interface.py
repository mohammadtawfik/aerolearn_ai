"""
Unit tests for the content interface contracts.

This module tests the functionality of the content-related interfaces like
ContentProviderInterface, ContentSearchInterface, and others.
"""
import sys
import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from datetime import datetime

# Add the project root to the Python path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the modules to test
from integrations.interfaces.base_interface import (
    BaseInterface, InterfaceImplementation, InterfaceMethod
)
from integrations.interfaces.content_interface import (
    ContentType, ContentFormat, ContentMetadata, ContentReference, 
    ContentSearchResult, ContentProviderInterface, ContentSearchInterface,
    ContentIndexerInterface, ContentProcessorInterface, ContentAnalyzerInterface
)


class TestContentEnums:
    """Tests for content-related enumerations."""
    
    def test_content_type_values(self):
        """Test that ContentType has expected values."""
        assert ContentType.DOCUMENT.value == "document"
        assert ContentType.PDF.value == "pdf"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.VIDEO.value == "video"
        
    def test_content_format_values(self):
        """Test that ContentFormat has expected values."""
        assert ContentFormat.PDF.value == "pdf"
        assert ContentFormat.DOCX.value == "docx"
        assert ContentFormat.JPG.value == "jpg"
        assert ContentFormat.MP4.value == "mp4"


class TestContentMetadata:
    """Tests for the ContentMetadata class."""
    
    def test_init_with_required_fields(self):
        """Test initialization with required fields."""
        metadata = ContentMetadata(
            content_id="test123",
            title="Test Document",
            content_type=ContentType.DOCUMENT,
            content_format=ContentFormat.DOCX
        )
        
        assert metadata["content_id"] == "test123"
        assert metadata["title"] == "Test Document"
        assert metadata["content_type"] == ContentType.DOCUMENT
        assert metadata["content_format"] == ContentFormat.DOCX
        assert "created_date" in metadata
        assert "modified_date" in metadata
        assert isinstance(metadata["created_date"], datetime)
    
    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        created_date = datetime(2025, 1, 1)
        modified_date = datetime(2025, 2, 1)
        
        metadata = ContentMetadata(
            content_id="test123",
            title="Test Document",
            content_type=ContentType.DOCUMENT,
            content_format=ContentFormat.DOCX,
            author="Test Author",
            created_date=created_date,
            modified_date=modified_date,
            size_bytes=1024,
            tags=["test", "document"],
            description="Test description",
            course_id="course123",
            custom_field="custom value"
        )
        
        assert metadata["content_id"] == "test123"
        assert metadata["author"] == "Test Author"
        assert metadata["created_date"] == created_date
        assert metadata["modified_date"] == modified_date
        assert metadata["size_bytes"] == 1024
        assert metadata["tags"] == ["test", "document"]
        assert metadata["description"] == "Test description"
        assert metadata["course_id"] == "course123"
        assert metadata["custom_field"] == "custom value"
    
    def test_dict_functionality(self):
        """Test that ContentMetadata works like a dict."""
        metadata = ContentMetadata(
            content_id="test123",
            title="Test Document",
            content_type=ContentType.DOCUMENT,
            content_format=ContentFormat.DOCX
        )
        
        # Test item access
        assert metadata["content_id"] == "test123"
        
        # Test item assignment
        metadata["author"] = "New Author"
        assert metadata["author"] == "New Author"
        
        # Test iteration
        keys = list(metadata)
        assert "content_id" in keys
        assert "title" in keys


class TestContentReference:
    """Tests for the ContentReference class."""
    
    def test_init_with_required_fields(self):
        """Test initialization with required fields."""
        ref = ContentReference(
            content_id="test123",
            provider_id="test_provider"
        )
        
        assert ref.content_id == "test123"
        assert ref.provider_id == "test_provider"
        assert ref.content_type is None
        assert ref.metadata == {}
    
    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        metadata = {"key": "value"}
        ref = ContentReference(
            content_id="test123",
            provider_id="test_provider",
            content_type=ContentType.DOCUMENT,
            metadata=metadata
        )
        
        assert ref.content_id == "test123"
        assert ref.provider_id == "test_provider"
        assert ref.content_type == ContentType.DOCUMENT
        assert ref.metadata == metadata


class TestContentSearchResult:
    """Tests for the ContentSearchResult class."""
    
    def test_init_with_required_fields(self):
        """Test initialization with required fields."""
        content_ref = ContentReference("test123", "test_provider")
        metadata = ContentMetadata(
            content_id="test123",
            title="Test Document",
            content_type=ContentType.DOCUMENT,
            content_format=ContentFormat.DOCX
        )
        
        result = ContentSearchResult(
            content_reference=content_ref,
            metadata=metadata
        )
        
        assert result.content_reference == content_ref
        assert result.metadata == metadata
        assert result.relevance_score == 0.0
        assert result.highlight_snippets == []
    
    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        content_ref = ContentReference("test123", "test_provider")
        metadata = ContentMetadata(
            content_id="test123",
            title="Test Document",
            content_type=ContentType.DOCUMENT,
            content_format=ContentFormat.DOCX
        )
        snippets = ["This is a <b>test</b> document", "Another <b>test</b> snippet"]
        
        result = ContentSearchResult(
            content_reference=content_ref,
            metadata=metadata,
            relevance_score=0.95,
            highlight_snippets=snippets
        )
        
        assert result.content_reference == content_ref
        assert result.metadata == metadata
        assert result.relevance_score == 0.95
        assert result.highlight_snippets == snippets


class TestContentProviderInterface:
    """Tests for the ContentProviderInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert ContentProviderInterface.interface_name == "content_provider"
        assert ContentProviderInterface.interface_version == "1.0.0"
        
        # Register the interface
        ContentProviderInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "content_provider" in interfaces
        assert interfaces["content_provider"] == ContentProviderInterface
    
    @pytest.mark.asyncio
    async def test_get_content_method_signature(self):
        """Test the get_content method signature."""
        # Create a class that implements the interface correctly
        @InterfaceImplementation(ContentProviderInterface)
        class TestContentProvider:
            async def get_content(self, content_id: str) -> Tuple[Optional[BinaryIO], Optional[ContentMetadata]]:
                return None, None
            
            async def store_content(self, content_stream: BinaryIO, metadata: ContentMetadata) -> Optional[str]:
                return "test123"
            
            async def delete_content(self, content_id: str) -> bool:
                return True
            
            async def update_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
                return True
            
            async def get_metadata(self, content_id: str) -> Optional[ContentMetadata]:
                return None
            
            async def list_content(self, filter_criteria: Dict[str, Any] = None) -> List[ContentMetadata]:
                return []
        
        # This should pass if the implementation is correct
        provider = TestContentProvider()
        result = await provider.get_content("test123")
        assert result == (None, None)


class TestContentSearchInterface:
    """Tests for the ContentSearchInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert ContentSearchInterface.interface_name == "content_search"
        assert ContentSearchInterface.interface_version == "1.0.0"
        
        # Register the interface
        ContentSearchInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "content_search" in interfaces
        assert interfaces["content_search"] == ContentSearchInterface
    
    @pytest.mark.asyncio
    async def test_search_method_signature(self):
        """Test the search method signature."""
        # Create a class that implements the interface correctly
        @InterfaceImplementation(ContentSearchInterface)
        class TestContentSearch:
            async def search(self, query: str, filters: Dict[str, Any] = None) -> List[ContentSearchResult]:
                return []
            
            async def get_suggestions(self, partial_query: str) -> List[str]:
                return []
        
        # This should pass if the implementation is correct
        search = TestContentSearch()
        result = await search.search("test query")
        assert result == []


class TestContentIndexerInterface:
    """Tests for the ContentIndexerInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert ContentIndexerInterface.interface_name == "content_indexer"
        assert ContentIndexerInterface.interface_version == "1.0.0"
        
        # Register the interface
        ContentIndexerInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "content_indexer" in interfaces
        assert interfaces["content_indexer"] == ContentIndexerInterface


class TestContentProcessorInterface:
    """Tests for the ContentProcessorInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert ContentProcessorInterface.interface_name == "content_processor"
        assert ContentProcessorInterface.interface_version == "1.0.0"
        
        # Register the interface
        ContentProcessorInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "content_processor" in interfaces
        assert interfaces["content_processor"] == ContentProcessorInterface


class TestContentAnalyzerInterface:
    """Tests for the ContentAnalyzerInterface."""
    
    def test_interface_registration(self):
        """Test that the interface is properly registered."""
        assert ContentAnalyzerInterface.interface_name == "content_analyzer"
        assert ContentAnalyzerInterface.interface_version == "1.0.0"
        
        # Register the interface
        ContentAnalyzerInterface.register_interface()
        
        # Check it's in the registry
        interfaces = BaseInterface.get_all_interfaces()
        assert "content_analyzer" in interfaces
        assert interfaces["content_analyzer"] == ContentAnalyzerInterface


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
