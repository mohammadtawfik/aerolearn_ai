"""
Content Type Registry

- Provides taxonomy and categorization for content
- Pluggable for future AI/content analysis
- Used in validation, display, extraction
- Supports multi-level detection strategies (extension, mimetype, plugin, AI)
"""
from typing import Callable, Optional, Dict, List, Any
import inspect


class ContentType:
    """
    Represents a content type with associated metadata.
    
    Attributes:
        name: Identifier for the content type (e.g., 'pdf', 'image')
        extensions: File extensions associated with this type
        mimetypes: MIME types associated with this type
        category: Broader category this type belongs to (e.g., 'document', 'media')
    """
    def __init__(self, name: str, extensions: List[str], mimetypes: List[str], category: str):
        self.name = name
        self.extensions = extensions
        self.mimetypes = mimetypes
        self.category = category


class ContentTypeRegistry:
    """
    Registry for file/content type detection with multiple detection strategies.
    
    Supports:
    1. Extension-based detection
    2. MIME type detection
    3. Plugin/custom detectors
    4. AI-based fallback detection
    """
    _instance = None
    _detectors: List[Callable[[str, Optional[str], Optional[Any]], Optional[str]]] = []
    _type_by_ext: Dict[str, str] = {
        ".pdf": "pdf",
        ".jpg": "image", ".jpeg": "image", ".png": "image", ".bmp": "image", ".gif": "image",
        ".mp4": "video", ".avi": "video", ".mov": "video", ".mkv": "video",
        ".txt": "text", ".md": "text", ".csv": "text",
        ".step": "cad", ".stp": "cad", ".igs": "cad", ".iges": "cad", ".sldprt": "cad", ".sldasm": "cad",
        ".sim": "sim", ".simulation": "sim"
    }
    _type_by_mime: Dict[str, str] = {
        "application/pdf": "pdf",
        "image/jpeg": "image", "image/png": "image", "image/gif": "image",
        "video/mp4": "video", "video/avi": "video", "video/quicktime": "video",
        "text/plain": "text", "text/markdown": "text", "text/csv": "text"
    }
    _content_types: Dict[str, ContentType] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContentTypeRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the registry with default content types."""
        self.register(ContentType('pdf', ['.pdf'], ['application/pdf'], 'document'))
        self.register(ContentType('image', ['.jpg', '.jpeg', '.png', '.bmp', '.gif'], 
                                 ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'], 'media'))
        self.register(ContentType('video', ['.mp4', '.avi', '.mov', '.mkv'], 
                                 ['video/mp4', 'video/avi', 'video/quicktime'], 'media'))
        self.register(ContentType('text', ['.txt', '.md', '.csv'], 
                                 ['text/plain', 'text/markdown', 'text/csv'], 'document'))
        self.register(ContentType('cad', ['.step', '.stp', '.igs', '.iges', '.sldprt', '.sldasm'], 
                                 ['application/step', 'application/iges'], 'engineering'))
        self.register(ContentType('sim', ['.sim', '.simulation'], 
                                 ['application/simulation'], 'engineering'))
    
    def register(self, ct: ContentType):
        """Register a content type with the registry."""
        self._content_types[ct.name] = ct
        
        # Update lookup dictionaries
        for ext in ct.extensions:
            self._type_by_ext[ext] = ct.name
        
        for mime in ct.mimetypes:
            self._type_by_mime[mime] = ct.name
    
    @classmethod
    def register_detector(cls, detector: Callable[[str, Optional[str], Optional[Any]], Optional[str]]) -> None:
        """
        Register a custom detector function.
        
        Args:
            detector: Function that takes filename, mimetype, and optional context and returns content type or None.
                      The detector should return a string content type name or None if it cannot determine the type.
        """
        cls._detectors.append(detector)
    
    @classmethod
    def detect_type(cls, filename: str, mimetype: Optional[str] = None, 
                   ai_detector: Optional[Callable] = None,
                   context: Optional[Any] = None) -> Optional[str]:
        """
        Detect content type using multiple strategies.
        
        Args:
            filename: Name of the file
            mimetype: Optional MIME type if available
            ai_detector: Optional AI-based detector function
            context: Optional context data for detectors
            
        Returns:
            Content type identifier or None if unknown
        """
        # 1. Extension-based detection
        ext = cls._get_extension(filename)
        if ext in cls._type_by_ext:
            return cls._type_by_ext[ext]
        
        # 2. MIME type detection
        if mimetype and mimetype in cls._type_by_mime:
            return cls._type_by_mime[mimetype]
        
        # 3. Plugin/custom detectors
        for detector in cls._detectors:
            result = detector(filename, mimetype, context)
            if result:
                return result
        
        # 4. AI-based fallback (if provided)
        if ai_detector:
            try:
                # Check the signature of the ai_detector function
                sig = inspect.signature(ai_detector)
                params = sig.parameters
                
                # Call with appropriate number of arguments
                if len(params) >= 2:
                    result = ai_detector(filename, mimetype)
                else:
                    result = ai_detector(filename)
                    
                if result:
                    return result
            except Exception:
                # Fallback to simpler approach if signature inspection fails
                try:
                    result = ai_detector(filename)
                    if result:
                        return result
                except Exception:
                    pass
        
        # Unknown
        return None
    
    @staticmethod
    def _get_extension(filename: str) -> str:
        """Extract the file extension from a filename."""
        filename = filename.lower()
        if "." in filename:
            return "." + filename.split(".")[-1]
        return ""
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get a list of all supported content types."""
        return list(set(cls._type_by_ext.values()))
    
    def get_content_type(self, type_name: str) -> Optional[ContentType]:
        """Get ContentType object by name."""
        return self._content_types.get(type_name)
    
    def detect(self, filename: str, mimetype: str = None):
        """
        Legacy method for backward compatibility.
        
        Returns ContentType object instead of just the type name.
        """
        type_name = self.detect_type(filename, mimetype)
        if type_name:
            return self._content_types.get(type_name)
        return None


# Create singleton instance
registry = ContentTypeRegistry()
