from typing import Tuple, List

import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.metrics.pairwise import cosine_similarity


class CosineSimilarityAnalyzer:
    def __init__(self, sigma: float = 2.0):
        self.sigma = sigma

    def analyze(self, embeddings: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        similarities = self._compute_pairwise_similarities(embeddings)
        smoothed = self._smooth_similarities(similarities)
        valleys = self._find_valleys(smoothed)
        return smoothed, valleys

    def _compute_pairwise_similarities(self, embeddings: np.ndarray) -> List[float]:
        return [
            cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            for i in range(len(embeddings) - 1)
        ]

    def _smooth_similarities(self, similarities: List[float]) -> np.ndarray:
        return gaussian_filter1d(similarities, sigma=self.sigma)

    def _find_valleys(self, smoothed: np.ndarray) -> List[int]:
        valleys = []
        for i in range(1, len(smoothed) - 1):
            if smoothed[i] < smoothed[i - 1] and smoothed[i] < smoothed[i + 1]:
                valleys.append(i)
        return valleys
    