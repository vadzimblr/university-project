from application.dtos.scenes.scene_analysis_result_dto import SceneAnalysisResultDto
from application.services.scenes.scene_splitter_strategy_protocol import SceneSplitterStrategy
from application.services.scenes.scene_statistics_calculator import BasicSceneStatisticsCalculator
from application.services.text.sentence_tokenizer_protocol import SentenceTokenizer
from application.services.text.similarity_analyzer_protocol import SimilarityAnalyzer
from application.services.text.text_embedder_protocol import TextEmbedder
from application.services.text.text_normalizer_protocol import TextNormalizer
import numpy as np

class SceneAnalysisService:
    def __init__(
        self,
        normalizer: TextNormalizer,
        tokenizer: SentenceTokenizer,
        embedder: TextEmbedder,
        similarity_analyzer: SimilarityAnalyzer,
        scene_splitter: SceneSplitterStrategy,
        stats_calculator: BasicSceneStatisticsCalculator
    ):
        self.normalizer = normalizer
        self.tokenizer = tokenizer
        self.embedder = embedder
        self.similarity_analyzer = similarity_analyzer
        self.scene_splitter = scene_splitter
        self.stats_calculator = stats_calculator

    def analyze(self, text: str) -> SceneAnalysisResultDto:
        normalized_text = self.normalizer.normalize(text)

        sentences = self.tokenizer.tokenize(normalized_text)

        if len(sentences) < 3:
            scenes = [text]
            valleys = []
            similarities = np.array([])
        else:
            embeddings = self.embedder.embed(sentences)
            similarities, valleys = self.similarity_analyzer.analyze(embeddings)
            scenes = self.scene_splitter.split(sentences, valleys)

        statistics = self.stats_calculator.calculate(scenes)

        return SceneAnalysisResultDto(
            scenes=scenes,
            valleys=valleys,
            similarities=similarities,
            statistics=statistics
        )
