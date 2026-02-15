from typing import List, Dict, Any
from sqlalchemy.orm import Session
from enum import Enum

from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.models.enums import ProcessingStatus
from app.services.scene_metrics_service import SceneMetricsService


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
        self.metrics = SceneMetricsService()

    def update_scenes(self, job_id: str, patches: List[Dict[str, Any]]) -> List[Scene]:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotEditableError(f"Job {job_id} not found")

        status_value = self._normalize_status(job.status)
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
            self.metrics.apply(scene)

        self.session.commit()

        return (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id, Scene.scene_number.in_(numbers))
            .order_by(Scene.scene_number)
            .all()
        )

    @staticmethod
    def _normalize_status(raw_status: object) -> str:
        if isinstance(raw_status, Enum):
            return raw_status.value
        if isinstance(raw_status, str) and raw_status.startswith("ProcessingStatus."):
            name = raw_status.split(".", 1)[1]
            if name in ProcessingStatus.__members__:
                return ProcessingStatus[name].value
        return str(raw_status)
