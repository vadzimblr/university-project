from typing import Protocol, List
import numpy as np


class TextEmbedder(Protocol):
    def embed(self, sentences: List[str]) -> np.ndarray: ...
