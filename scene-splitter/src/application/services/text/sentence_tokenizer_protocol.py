from typing import Protocol, List


class SentenceTokenizer(Protocol):
    def tokenize(self, text: str) -> List[str]: ...
