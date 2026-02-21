from typing import Protocol


class TextNormalizer(Protocol):
    def normalize(self, text: str) -> str: ...
    