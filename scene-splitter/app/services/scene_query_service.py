from typing import List
from sqlalchemy.orm import Session
import re
import nltk

from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository


class SceneQueryError(Exception):
    """Base class for scene query errors."""


class SceneNotFoundError(SceneQueryError):
    pass


class JobNotFoundError(SceneQueryError):
    pass


class SceneQueryService:
    def __init__(self, session: Session):
        self.session = session
        self.job_repo = ProcessingJobRepository(session)
        self._ensure_tokenizer()

    def get_scene_sentences(self, job_id: str, scene_number: int) -> List[str]:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found")

        scene = (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id, Scene.scene_number == scene_number)
            .first()
        )
        if not scene:
            raise SceneNotFoundError(f"Scene {scene_number} not found for job {job_id}")

        text = scene.scene_text or ""
        try:
            return nltk.sent_tokenize(text, language="russian")
        except Exception:
            return self._fallback_sentences(text)

    def _ensure_tokenizer(self):
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            try:
                nltk.download("punkt_tab")
            except Exception:
                pass

    @staticmethod
    def _fallback_sentences(text: str) -> List[str]:
        if not text.strip():
            return []
        parts = re.split(r"(?<=[.!?])\\s+", text)
        return [p.strip() for p in parts if p.strip()]
