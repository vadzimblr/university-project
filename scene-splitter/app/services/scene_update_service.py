from typing import List, Dict, Any
from sqlalchemy.orm import Session
from enum import Enum
import re
import nltk

from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.models.enums import ProcessingStatus


class SceneUpdateError(Exception):
    """Base class for scene update errors."""


class JobNotEditableError(SceneUpdateError):
    pass


class SceneNotFoundError(SceneUpdateError):
    pass


class SceneUpdateService:
    def __init__(self, session: Session):
        self.session = session
        self.job_repo = ProcessingJobRepository(session)
        self._ensure_tokenizer()

    def update_scenes(self, job_id: str, patches: List[Dict[str, Any]]) -> List[Scene]:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotEditableError(f"Job {job_id} not found")

        status_value = job.status.value if isinstance(job.status, Enum) else str(job.status)
        if status_value in {ProcessingStatus.APPROVED.value, ProcessingStatus.COMPLETED.value, "approved", "completed"}:
            raise JobNotEditableError("Job is finalized and scenes cannot be modified")

        numbers = [p["scene_number"] for p in patches]
        scenes = (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id, Scene.scene_number.in_(numbers))
            .all()
        )

        found_map = {scene.scene_number: scene for scene in scenes}
        if len(found_map) != len(numbers):
            missing = set(numbers) - set(found_map.keys())
            missing_list = ", ".join(str(m) for m in sorted(missing))
            raise SceneNotFoundError(f"Scenes with numbers [{missing_list}] not found for job {job_id}")

        for patch in patches:
            scene = found_map[patch["scene_number"]]

            new_text = patch.get("scene_text")
            if new_text is None:
                raise SceneUpdateError("scene_text is required for each patch item")

            scene.scene_text = new_text
            self._recalculate_metrics(scene)

        self.session.commit()

        return (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id, Scene.scene_number.in_(numbers))
            .order_by(Scene.scene_number)
            .all()
        )

    def _ensure_tokenizer(self):
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            try:
                nltk.download("punkt_tab")
            except Exception:
                pass

    def _recalculate_metrics(self, scene: Scene):
        text = scene.scene_text or ""
        scene.word_count = len(text.split())
        scene.char_count = len(text)
        try:
            sentences = nltk.sent_tokenize(text, language="russian")
            scene.sentence_count = len(sentences)
        except Exception:
            scene.sentence_count = self._fallback_sentence_count(text)

    @staticmethod
    def _fallback_sentence_count(text: str) -> int:
        if not text.strip():
            return 0

        parts = re.split(r"[.!?]+", text)
        return len([p for p in parts if p.strip()])
