from typing import List

from application.dtos.scenes.scene_statistic_dto import SceneStatisticDto
from application.services.text.sentence_tokenizer_protocol import SentenceTokenizer


class BasicSceneStatisticsCalculator:
    def __init__(self, tokenizer: SentenceTokenizer):
        self.tokenizer = tokenizer

    def calculate(self, scenes: List[str]) -> List[SceneStatisticDto]:
        statistics = []

        for i, scene in enumerate(scenes):
            sentences = self.tokenizer.tokenize(scene)
            statistics.append(SceneStatisticDto(
                scene_number=i + 1,
                sentence_count=len(sentences),
                word_count=len(scene.split()),
                char_count=len(scene)
            ))

        return statistics
