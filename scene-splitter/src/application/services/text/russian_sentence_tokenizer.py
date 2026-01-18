from typing import List
import nltk


class RussianSentenceTokenizer:
    def __init__(self):
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')

    def tokenize(self, text: str) -> List[str]:
        return nltk.sent_tokenize(text, language='russian')
    