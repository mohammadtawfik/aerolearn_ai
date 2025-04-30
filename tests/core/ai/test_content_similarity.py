"""
File Location: tests/core/ai/test_content_similarity.py

Purpose: Unit tests for content similarity and recommendation logic.
"""

import unittest
import numpy as np

from app.core.ai.content_similarity import (
    SimilarityCalculator, calculate_similarity, 
    cross_content_similarity, get_content_recommendations
)

class TestSimilarityCalculator(unittest.TestCase):
    def test_cosine_similarity_self(self):
        vec = np.random.rand(100)
        normed = vec / np.linalg.norm(vec)
        score = SimilarityCalculator.cosine_similarity(normed, normed)
        self.assertAlmostEqual(score, 1.0, places=6)

    def test_cosine_similarity_orthogonal(self):
        # Use standard basis
        a = np.zeros(100); a[0]=1
        b = np.zeros(100); b[1]=1
        score = SimilarityCalculator.cosine_similarity(a, b)
        self.assertAlmostEqual(score, 0.0, places=6)

    def test_jaccard_similarity(self):
        a = np.array([1,0,1,0,1,0]*16 + [0,0,0,0])
        b = np.array([1,1,0,0,1,0]*16 + [0,0,0,0])
        score = SimilarityCalculator.jaccard_similarity(a, b)
        self.assertTrue(0 <= score <= 1)

class TestSimilarityFunctions(unittest.TestCase):
    def test_calculate_similarity_threshold(self):
        a = "A unique piece of content"
        b = "A totally different thing"
        score, match = calculate_similarity(a, b, 'text', 'cosine', threshold=0.01)
        self.assertIsInstance(score, float)
        self.assertTrue(match)  # With such a low threshold, anything should match

    def test_cross_content_similarity_matrix(self):
        content_list_a = ["Sample A", "Test B"]
        content_list_b = ["Sample A", "Completely different"]
        result = cross_content_similarity(content_list_a, content_list_b, 'text', 'cosine', 0.5)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)
        self.assertIsInstance(result[0][0]['score'], float)
        self.assertIsInstance(result[0][1]['match'], bool)

    def test_recommendations(self):
        target = "Learn Python programming"
        candidates = ["Python basics", "Advanced C++", "Python programming guide", "Cooking tips"]
        recs = get_content_recommendations(target, candidates, 'text', 'cosine', top_k=2, threshold=0.1)
        self.assertLessEqual(len(recs), 2)
        for rec in recs:
            self.assertIn('index', rec)
            self.assertIn('score', rec)
            self.assertIn('content', rec)

if __name__ == '__main__':
    unittest.main()