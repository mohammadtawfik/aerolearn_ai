"""
Content interface contracts for the AeroLearn AI system.

This module defines the interfaces for content management, including content
providers, content retrieval, and content processing components.
"""
import abc
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union, BinaryIO, Tuple

from .base_interface import BaseInterface, InterfaceImplementation, InterfaceMethod


class ContentType(Enum):
    """Enumeration of supported content types."""
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    DATASET = "dataset"
    OTHER = "other"


class ContentFormat(Enum):
    """Enumeration of specific content formats."""
    # Documents
    DOCX = "docx"
    DOC = "doc"
    ODT = "odt"
    RTF = "rtf"
    TXT = "txt"
    MD = "md"
    LATEX = "latex"
    
    # Presentations
    PPTX = "pptx"
    PPT = "ppt"
    ODP = "odp"
    
    # Spreadsheets
    XLSX = "xlsx"
    XLS = "xls"
    ODS = "ods"
    CSV = "csv"
    
    # PDFs
    PDF = "pdf"
    
    # Images
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    GIF = "gif"
    SVG = "svg"
    
    # Videos
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    
    # Audio
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    
    # Code
    PY = "py"
    JS = "js"
    HTML = "html"
    CSS = "css"
    CPP = "cpp"
    JAVA = "java"
    
    # Data
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    
    # Other
    OTHER = "other"


class ContentMetadata(dict):
    """Class for content metadata with standard fields and custom properties."""
    
    def __init__(self, 
                 content_id: str,
                 title: str,
                 content_type: ContentType,
                 content_format: ContentFormat,
                 author: str = None,
                 created_date: datetime = None,
                 modified_date: datetime = None,
                 size_bytes: int = 0,
                 tags: List[str] = None,
                 description: str = None,
                 course_id: str = None,
                 **kwargs):
        """
        Initialize content metadata.
        
        Args:
            content_id: Unique identifier for the content
            title: Title of the content
            content_type: Type of content (document, video, etc.)
            content_format: Specific format (docx, pdf, mp4, etc.)
            author: Author of the content
            created_date: Date the content was created
            modified_date: Date the content was last modified
            size_bytes: Size of the content in bytes
            tags: List of tags associated with the content
            description: Description of the content
            course_id: ID of the course this content belongs to
            **kwargs: Additional custom metadata
        """
        super().__init__()
        self["content_id"] = content_id
        self["title"] = title
        self["content_type"] = content_type
        self["content_format"] = content_format
        self["author"] = author
        self["created_date"] = created_date or datetime.now()
        self["modified_date"] = modified_date or datetime.now()
        self["size_bytes"] = size_bytes
        self["tags"] = tags or []
        self["description"] = description
        self["course_id"] = course_id
        
        # Add any additional metadata
        for key, value in kwargs.items():
            self[key] = value


class ContentReference:
    """Reference to content that can be resolved by content providers."""
    
    def __init__(self, 
                 content_id: str,
                 provider_id: str,
                 content_type: ContentType = None,
                 metadata: Dict[str, Any] = None):
        """
        Initialize a content reference.
        
        Args:
            content_id: Unique identifier for the content
            provider_id: ID of the provider that can resolve this reference
            content_type: Optional type of the content
            metadata: Optional metadata for the content
        """
        self.content_id = content_id
        self.provider_id = provider_id
        self.content_type = content_type
        self.metadata = metadata or {}


class ContentSearchResult:
    """Result from a content search operation."""
    
    def __init__(self,
                 content_reference: ContentReference,
                 metadata: ContentMetadata,
                 relevance_score: float = 0.0,
                 highlight_snippets: List[str] = None):
        """
        Initialize a content search result.
        
        Args:
            content_reference: Reference to the matching content
            metadata: Metadata for the matching content
            relevance_score: Score indicating relevance to the search query
            highlight_snippets: Text snippets with search term highlights
        """
        self.content_reference = content_reference
        self.metadata = metadata
        self.relevance_score = relevance_score
        self.highlight_snippets = highlight_snippets or []


class ContentProviderInterface(BaseInterface):
    """
    Interface for components that provide access to content.
    
    Content providers are responsible for retrieving and storing content,
    but not for processing or transforming it.
    """
    interface_name = "content_provider"
    interface_version = "1.0.0"
    interface_description = "Interface for components that provide access to content"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_content(self, content_id: str) -> Tuple[Optional[BinaryIO], Optional[ContentMetadata]]:
        """
        Retrieve content by ID.
        
        Args:
            content_id: ID of the content to retrieve
            
        Returns:
            Tuple of (content_stream, metadata) or (None, None) if not found
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def store_content(self, content_stream: BinaryIO, metadata: ContentMetadata) -> Optional[str]:
        """
        Store content with the provided metadata.
        
        Args:
            content_stream: Binary stream of the content to store
            metadata: Metadata for the content
            
        Returns:
            Content ID if successful, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def delete_content(self, content_id: str) -> bool:
        """
        Delete content by ID.
        
        Args:
            content_id: ID of the content to delete
            
        Returns:
            True if deleted, False if not found or unable to delete
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def update_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for content.
        
        Args:
            content_id: ID of the content to update
            metadata: New metadata values to apply
            
        Returns:
            True if updated, False if not found or unable to update
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_metadata(self, content_id: str) -> Optional[ContentMetadata]:
        """
        Get metadata for content.
        
        Args:
            content_id: ID of the content
            
        Returns:
            Metadata if found, None otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def list_content(self, filter_criteria: Dict[str, Any] = None) -> List[ContentMetadata]:
        """
        List content matching the filter criteria.
        
        Args:
            filter_criteria: Dictionary of criteria to filter by
            
        Returns:
            List of matching content metadata
        """
        pass


class ContentSearchInterface(BaseInterface):
    """
    Interface for components that provide content search capabilities.
    """
    interface_name = "content_search"
    interface_version = "1.0.0"
    interface_description = "Interface for components that provide content search capabilities"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[ContentSearchResult]:
        """
        Search for content matching the query.
        
        Args:
            query: Search query string
            filters: Dictionary of filters to apply to the search
            
        Returns:
            List of search results
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """
        Get query suggestions based on a partial query.
        
        Args:
            partial_query: Partial search query
            
        Returns:
            List of query suggestions
        """
        pass


class ContentIndexerInterface(BaseInterface):
    """
    Interface for components that index content for search.
    """
    interface_name = "content_indexer"
    interface_version = "1.0.0"
    interface_description = "Interface for components that index content for search"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def index_content(self, content_reference: ContentReference) -> bool:
        """
        Index content for search.
        
        Args:
            content_reference: Reference to the content to index
            
        Returns:
            True if indexed successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def update_index(self, content_reference: ContentReference) -> bool:
        """
        Update index for content that has changed.
        
        Args:
            content_reference: Reference to the updated content
            
        Returns:
            True if index updated successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def remove_from_index(self, content_id: str) -> bool:
        """
        Remove content from the index.
        
        Args:
            content_id: ID of the content to remove
            
        Returns:
            True if removed from index successfully, False otherwise
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def get_index_status(self, content_id: str) -> Dict[str, Any]:
        """
        Get indexing status for content.
        
        Args:
            content_id: ID of the content to check
            
        Returns:
            Dictionary containing index status information
        """
        pass


class ContentProcessorInterface(BaseInterface):
    """
    Interface for components that process and transform content.
    """
    interface_name = "content_processor"
    interface_version = "1.0.0"
    interface_description = "Interface for components that process and transform content"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def process_content(self, content_stream: BinaryIO, metadata: ContentMetadata, 
                              options: Dict[str, Any] = None) -> Tuple[BinaryIO, ContentMetadata]:
        """
        Process content according to specified options.
        
        Args:
            content_stream: Binary stream of the content to process
            metadata: Metadata for the content
            options: Processing options
            
        Returns:
            Tuple of (processed_content_stream, updated_metadata)
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def extract_text(self, content_stream: BinaryIO, metadata: ContentMetadata) -> str:
        """
        Extract plain text from content.
        
        Args:
            content_stream: Binary stream of the content
            metadata: Metadata for the content
            
        Returns:
            Extracted text
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def extract_metadata(self, content_stream: BinaryIO) -> Dict[str, Any]:
        """
        Extract metadata from content.
        
        Args:
            content_stream: Binary stream of the content
            
        Returns:
            Dictionary of extracted metadata
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def convert_format(self, content_stream: BinaryIO, source_format: ContentFormat, 
                             target_format: ContentFormat) -> BinaryIO:
        """
        Convert content from one format to another.
        
        Args:
            content_stream: Binary stream of the content to convert
            source_format: Format of the source content
            target_format: Desired target format
            
        Returns:
            Binary stream of the converted content
        """
        pass


class ContentAnalyzerInterface(BaseInterface):
    """
    Interface for components that analyze content for insights.
    """
    interface_name = "content_analyzer"
    interface_version = "1.0.0"
    interface_description = "Interface for components that analyze content for insights"
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def analyze_complexity(self, content_reference: ContentReference) -> Dict[str, Any]:
        """
        Analyze content complexity.
        
        Args:
            content_reference: Reference to the content to analyze
            
        Returns:
            Dictionary of complexity metrics
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def extract_topics(self, content_reference: ContentReference) -> List[Dict[str, Any]]:
        """
        Extract topics from content.
        
        Args:
            content_reference: Reference to the content to analyze
            
        Returns:
            List of topics with relevance scores
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def analyze_similarity(self, content_reference1: ContentReference, 
                                content_reference2: ContentReference) -> float:
        """
        Calculate similarity between two pieces of content.
        
        Args:
            content_reference1: First content reference
            content_reference2: Second content reference
            
        Returns:
            Similarity score (0-1)
        """
        pass
    
    @BaseInterface.interface_method
    @abc.abstractmethod
    async def generate_summary(self, content_reference: ContentReference, max_length: int = 1000) -> str:
        """
        Generate a summary of the content.
        
        Args:
            content_reference: Reference to the content to summarize
            max_length: Maximum length of the summary in characters
            
        Returns:
            Summary text
        """
        pass
