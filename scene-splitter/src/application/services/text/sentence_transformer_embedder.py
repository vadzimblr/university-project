from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = 'cointegrated/rubert-tiny2'):
        self.model = SentenceTransformer(model_name)

    def embed(self, sentences: List[str]) -> np.ndarray:
        return self.model.encode(sentences)
    