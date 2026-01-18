from typing import List


class SequentialSceneSplitter:
    def split(self, sentences: List[str], split_indices: List[int]) -> List[str]:
        if not sentences:
            return []

        scenes = []
        start = 0
        for split_idx in sorted(split_indices):
            scenes.append(' '.join(sentences[start:split_idx + 1]))
            start = split_idx + 1

        if start < len(sentences):
            scenes.append(' '.join(sentences[start:]))

        return scenes
    