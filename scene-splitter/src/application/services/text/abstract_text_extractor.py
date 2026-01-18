from abc import ABC, abstractmethod

class AbstractFileTextExtractor(ABC):
    @abstractmethod
    def extract(self, file: bytes, start_page: int|None, end_page: int|None) -> str:
        pass
