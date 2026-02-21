import re


class RegexTextNormalizer:
    def normalize(self, text: str) -> str:
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    