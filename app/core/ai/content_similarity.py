"""
File Location: app/core/ai/content_similarity.py

Purpose: Implements similarity detection for educational content, including
vector similarity metrics, thresholding, and recommendation heuristics.
"""

import numpy as np
from .embedding import TextEmbedder, DocumentEmbedder, MultimediaEmbedder

# Configurable similarity threshold (can be overridden via constructor or config)
DEFAULT_SIMILARITY_THRESHOLD = 0.75

class SimilarityCalculator:
    """
    Provides static methods for common similarity metrics.
    """
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        if vec1.shape != vec2.shape:
            raise ValueError("Vectors must have the same shape.")
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    @staticmethod
    def jaccard_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        # Simplified for binary vectors; for real-valued use as in embeddings, use intersection over union of presence
        bin1, bin2 = (vec1 > 0).astype(int), (vec2 > 0).astype(int)
        intersection = np.sum(bin1 & bin2)
        union = np.sum(bin1 | bin2)
        return float(intersection / union) if union else 0.0


class ContentSimilarityCalculator:
    """
    Adapter API for project-wide content similarity calculations.
    Usage:
        csc = ContentSimilarityCalculator()
        score = csc.similarity_score(vec_a, vec_b, metric='cosine')
    """
    @staticmethod
    def similarity_score(vec_a, vec_b, metric='cosine'):
        """
        Returns a similarity score (float from 0 to 1) between two embedding vectors.
        """
        if metric == 'cosine':
            return SimilarityCalculator.cosine_similarity(np.array(vec_a), np.array(vec_b))
        elif metric == 'jaccard':
            return SimilarityCalculator.jaccard_similarity(np.array(vec_a), np.array(vec_b))
        else:
            raise ValueError(f"Unknown metric: {metric}")

def calculate_similarity(content_a, content_b, 
                        content_type='text', 
                        metric='cosine',
                        threshold=DEFAULT_SIMILARITY_THRESHOLD):
    """
    Embeds and compares two pieces of content (text, document, multimedia).
    Returns similarity score and match boolean (always Python bool).
    """
    if content_type == 'text':
        embedder = TextEmbedder()
        emb_a = embedder.embed(content_a)
        emb_b = embedder.embed(content_b)
    elif content_type == 'document':
        embedder = DocumentEmbedder()
        emb_a = embedder.embed(content_a)
        emb_b = embedder.embed(content_b)
    elif content_type == 'multimedia':
        embedder = MultimediaEmbedder()
        emb_a = embedder.embed(content_a)
        emb_b = embedder.embed(content_b)
    else:
        raise ValueError(f"Unknown content_type: {content_type}")

    calculator = ContentSimilarityCalculator()
    score = calculator.similarity_score(emb_a, emb_b, metric=metric)

    return score, bool(score >= threshold)

def cross_content_similarity(content_list_a, content_list_b, content_type='text',
                            metric='cosine', threshold=DEFAULT_SIMILARITY_THRESHOLD):
    """
    Given two lists (e.g. lessons from two courses), computes pairwise similarity 
    and returns a score matrix and match flags (Python bool).
    """
    embedder_map = {
        'text': TextEmbedder,
        'document': DocumentEmbedder,
        'multimedia': MultimediaEmbedder
    }
    if content_type not in embedder_map:
        raise ValueError(f"Unknown content_type: {content_type}")
    embedder = embedder_map[content_type]()
    embeddings_a = [embedder.embed(c) for c in content_list_a]
    embeddings_b = [embedder.embed(c) for c in content_list_b]

    results = []
    for i, ea in enumerate(embeddings_a):
        row = []
        for j, eb in enumerate(embeddings_b):
            calculator = ContentSimilarityCalculator()
            score = calculator.similarity_score(ea, eb, metric=metric)
            row.append({'score': score, 'match': bool(score >= threshold)})
        results.append(row)
    return results

def get_content_recommendations(target_content, candidate_contents, 
                               content_type='text', metric='cosine',
                               top_k=3, threshold=DEFAULT_SIMILARITY_THRESHOLD):
    """
    Recommends the top-K most similar items from candidate_contents to target_content.
    Returns strictly Python bool in all flags.
    """
    embedder_map = {
        'text': TextEmbedder,
        'document': DocumentEmbedder,
        'multimedia': MultimediaEmbedder
    }
    if content_type not in embedder_map:
        raise ValueError(f"Unknown content_type: {content_type}")
    embedder = embedder_map[content_type]()
    target_emb = embedder.embed(target_content)
    candidate_embs = [embedder.embed(c) for c in candidate_contents]

    scored = []
    for idx, emb in enumerate(candidate_embs):
        calculator = ContentSimilarityCalculator()
        score = calculator.similarity_score(target_emb, emb, metric=metric)
        scored.append((idx, score))
    # Filter candidates by threshold, then rank by score
    filtered = [(idx, scr) for idx, scr in scored if scr >= threshold]
    filtered.sort(key=lambda x: -x[1])
    top = filtered[:top_k]
    # Return recommended items (indices and scores)
    return [{'index': idx, 'score': scr, 'content': candidate_contents[idx]} for idx, scr in top]
