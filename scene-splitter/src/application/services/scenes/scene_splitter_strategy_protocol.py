from typing import Protocol, List


class SceneSplitterStrategy(Protocol):
    def split(self, sentences: List[str], split_indices: List[int]) -> List[str]: ...