import re
import nltk

from app.models import Scene


class SceneMetricsService:
    def __init__(self) -> None:
        self._ensure_tokenizer()

    def apply(self, scene: Scene) -> None:
        text = scene.scene_text or ""
        scene.word_count = len(text.split())
        scene.char_count = len(text)
        try:
            sentences = nltk.sent_tokenize(text, language="russian")
            scene.sentence_count = len(sentences)
        except Exception:
            scene.sentence_count = self._fallback_sentence_count(text)

    def _ensure_tokenizer(self) -> None:
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            try:
                nltk.download("punkt_tab")
            except Exception:
                pass

    @staticmethod
    def _fallback_sentence_count(text: str) -> int:
        if not text.strip():
            return 0

        parts = re.split(r"[.!?]+", text)
        return len([p for p in parts if p.strip()])
