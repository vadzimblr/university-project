from typing import List, Tuple
import numpy as np
import nltk
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.ndimage import gaussian_filter1d


class SceneSplitterService:
    def __init__(self, model_name: str = 'cointegrated/rubert-tiny2'):
        self.model = SentenceTransformer(model_name)
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
    
    def normalize_text(self, text: str) -> str:
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize_sentences(self, text: str) -> List[str]:
        return nltk.sent_tokenize(text, language='russian')
    
    def embed_sentences(self, sentences: List[str]) -> np.ndarray:
        return self.model.encode(sentences)
    
    def compute_smoothed_similarities(self, embeddings: np.ndarray, sigma: float = 2.0) -> np.ndarray:
        similarities = [
            cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            for i in range(len(embeddings) - 1)
        ]
        return gaussian_filter1d(similarities, sigma=sigma)
    
    def find_valleys(self, smoothed: np.ndarray) -> List[int]:
        valleys = []
        for i in range(1, len(smoothed) - 1):
            if smoothed[i] < smoothed[i - 1] and smoothed[i] < smoothed[i + 1]:
                valleys.append(i)
        return valleys
    
    def split_into_chunks(self, sentences: List[str], valleys: List[int]) -> List[str]:
        chunks = []
        start = 0
        for v in valleys:
            chunks.append(' '.join(sentences[start:v+1]))
            start = v + 1
        chunks.append(' '.join(sentences[start:]))
        return chunks
    
    def analyze_scenes(self, text: str) -> Tuple[List[str], List[int], np.ndarray]:
        normalized_text = self.normalize_text(text)
        sentences = self.tokenize_sentences(normalized_text)
        
        if len(sentences) < 3:
            return [text], [], np.array([])
        
        embeddings = self.embed_sentences(sentences)
        smoothed = self.compute_smoothed_similarities(embeddings)
        valleys = self.find_valleys(smoothed)
        scenes = self.split_into_chunks(sentences, valleys)
        
        return scenes, valleys, smoothed
    
    def get_scene_statistics(self, scenes: List[str]) -> List[dict]:
        stats = []
        for i, scene in enumerate(scenes):
            sentences = self.tokenize_sentences(scene)
            stats.append({
                'scene_number': i + 1,
                'sentence_count': len(sentences),
                'word_count': len(scene.split()),
                'char_count': len(scene)
            })
        return stats
