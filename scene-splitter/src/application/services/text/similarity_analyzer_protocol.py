from typing import Protocol, Tuple, List
import numpy as np


class SimilarityAnalyzer(Protocol):
    def analyze(self, embeddings: np.ndarray) -> Tuple[np.ndarray, List[int]]: ...
