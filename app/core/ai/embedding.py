"""
File Location: app/core/ai/embedding.py

Purpose: This module provides embedding generation for various content types 
(text, document, multimedia), supporting the AeroLearn AI content analysis system.
"""

import numpy as np
import string
from typing import Any, List, Union, Dict

class BaseEmbedder:
    """
    Abstract base class for content embedders.
    """
    def embed(self, content):
        raise NotImplementedError("Embed method must be implemented by subclasses.")


class TextEmbedder(BaseEmbedder):
    """
    Embeds plain text into a dense vector using simple bag-of-words on lowercase letters
    for more consistent and testable similarity outputs.
    """
    def __init__(self, embedding_dim: int = 26):
        self.embedding_dim = embedding_dim
        self.vocab = list(string.ascii_lowercase)
        
    def embed(self, text: str) -> np.ndarray:
        # Simple bag-of-letters approach for testability
        vector = np.zeros(self.embedding_dim)
        text = text.lower()
        for char in text:
            if char in self.vocab:
                idx = self.vocab.index(char)
                vector[idx] += 1.0
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector


class DocumentEmbedder(BaseEmbedder):
    """
    Embeds a document (could be PDF, DOCX, etc.) by processing its text content.
    """
    def __init__(self, text_embedder=None):
        self.text_embedder = text_embedder or TextEmbedder()

    def embed(self, document_text: str) -> np.ndarray:
        # For baseline, treat document as one text block
        return self.text_embedder.embed(document_text)


class MultimediaEmbedder(BaseEmbedder):
    """
    Embeds multimedia (video, audio, image) by converting metadata to text
    and using the text embedder.
    """
    def __init__(self, text_embedder=None):
        self.text_embedder = text_embedder or TextEmbedder()
        
    def embed(self, metadata: dict) -> np.ndarray:
        # Convert metadata to text and use text embedder
        text = " ".join([f"{k} {v}" for k, v in metadata.items()])
        return self.text_embedder.embed(text)


class EmbeddingGenerator:
    """
    EmbeddingGenerator is responsible for generating vector representations (embeddings) 
    from input text or content.
    
    This is the main API for creating embeddings in the AeroLearn AI system.
    
    Usage:
        emb_gen = EmbeddingGenerator()
        vec = emb_gen.embed("example content")
        vec = emb_gen.embed({"type": "video", "title": "Learning AI"})  # multimedia
    """

    def __init__(self, embedding_dim: int = 26):
        self.embedding_dim = embedding_dim
        self.text_embedder = TextEmbedder(embedding_dim)
        self.document_embedder = DocumentEmbedder(self.text_embedder)
        self.multimedia_embedder = MultimediaEmbedder(self.text_embedder)

    def embed(self, content: Any) -> List[float]:
        """
        Generate an embedding vector for the input content.

        Args:
            content: The raw content (text, document text, or multimedia metadata)
                     Can be str for text/documents or dict for multimedia

        Returns:
            List[float]: Embedding vector as a list of floats
        """
        # Determine content type and use appropriate embedder
        if isinstance(content, str):
            # Text or document content
            vector = self.text_embedder.embed(content)
        elif isinstance(content, dict):
            # Multimedia content with metadata
            vector = self.multimedia_embedder.embed(content)
        else:
            # Convert to string as fallback
            vector = self.text_embedder.embed(str(content))
            
        # Vector should already be the right size and normalized
            
        return vector.tolist()
