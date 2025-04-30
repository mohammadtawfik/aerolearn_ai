"""
File Location: tests/core/ai/test_embedding.py

Purpose: Unit tests for TextEmbedder, DocumentEmbedder, and MultimediaEmbedder.
"""

import unittest
import numpy as np

from app.core.ai.embedding import TextEmbedder, DocumentEmbedder, MultimediaEmbedder

class TestTextEmbedder(unittest.TestCase):
    def test_text_embed_shape(self):
        embedder = TextEmbedder()
        vector = embedder.embed("sample text")
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape, (100,))
    
    def test_text_embed_repeatability(self):
        embedder = TextEmbedder()
        vec1 = embedder.embed("reproducible result")
        vec2 = embedder.embed("reproducible result")
        np.testing.assert_array_equal(vec1, vec2)

    def test_empty_text(self):
        embedder = TextEmbedder()
        vec = embedder.embed("")
        self.assertTrue(np.allclose(vec, 0))

class TestDocumentEmbedder(unittest.TestCase):
    def test_document_embedding(self):
        embedder = DocumentEmbedder()
        doc = "This is a document. It contains several sentences."
        vector = embedder.embed(doc)
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape, (100,))

class TestMultimediaEmbedder(unittest.TestCase):
    def test_multimedia_embedding(self):
        embedder = MultimediaEmbedder()
        metadata = {"duration": 55, "format": "mp4"}
        vector = embedder.embed(metadata)
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape, (100,))

if __name__ == '__main__':
    unittest.main()