from typing import List
from enum import Enum
from sqlalchemy.orm import Session

from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.models.enums import ProcessingStatus
from app.services.scene_metrics_service import SceneMetricsService


class SceneMergeError(Exception):
    """Base class for scene merge errors."""


class SceneMergeValidationError(SceneMergeError):
    pass


class JobNotFoundError(SceneMergeError):
    pass


class JobNotEditableError(SceneMergeError):
    pass


class SceneNotFoundError(SceneMergeError):
    pass


class SceneMergeService:
    def __init__(self, session: Session):
        self.session = session
        self.job_repo = ProcessingJobRepository(session)
        self.metrics = SceneMetricsService()

    def merge_scenes(self, job_id: str, scene_numbers: List[int]) -> List[Scene]:
        numbers = self._validate_scene_numbers(scene_numbers)

        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found")

        status_value = self._normalize_status(job.status)
        if status_value in {
            ProcessingStatus.APPROVED.value,
            ProcessingStatus.COMPLETED.value,
            "approved",
            "completed",
        }:
            raise JobNotEditableError("Job is finalized and scenes cannot be modified")

        scenes = (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id, Scene.scene_number.in_(numbers))
            .order_by(Scene.scene_number)
            .all()
        )

        if len(scenes) != len(numbers):
            found_numbers = {scene.scene_number for scene in scenes}
            missing = [num for num in numbers if num not in found_numbers]
            missing_list = ", ".join(str(num) for num in missing)
            raise SceneNotFoundError(f"Scenes with numbers [{missing_list}] not found for job {job_id}")

        merged_scene = scenes[0]
        merged_scene.scene_number = numbers[0]
        merged_scene.scene_text = "\n\n".join(scene.scene_text for scene in scenes)
        merged_scene.start_sentence_idx = None
        merged_scene.end_sentence_idx = None
        merged_scene.boundary_confidence = None
        self.metrics.apply(merged_scene)

        for scene in scenes[1:]:
            self.session.delete(scene)

        shift = len(numbers) - 1
        if shift:
            following_scenes = (
                self.session.query(Scene)
                .filter(Scene.processing_job_id == job.id, Scene.scene_number > numbers[-1])
                .order_by(Scene.scene_number)
                .all()
            )
            for scene in following_scenes:
                scene.scene_number -= shift

        self.session.commit()

        return (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id)
            .order_by(Scene.scene_number)
            .all()
        )

    @staticmethod
    def _validate_scene_numbers(scene_numbers: List[int]) -> List[int]:
        if not scene_numbers or len(scene_numbers) < 2:
            raise SceneMergeValidationError("At least two scene numbers are required to merge")

        if any(num < 1 for num in scene_numbers):
            raise SceneMergeValidationError("Scene numbers must be positive")

        if len(set(scene_numbers)) != len(scene_numbers):
            raise SceneMergeValidationError("Scene numbers must be unique")

        numbers = sorted(scene_numbers)
        for idx in range(1, len(numbers)):
            if numbers[idx] != numbers[idx - 1] + 1:
                raise SceneMergeValidationError("Scene numbers must be consecutive")

        return numbers

    @staticmethod
    def _normalize_status(raw_status: object) -> str:
        if isinstance(raw_status, Enum):
            return raw_status.value
        if isinstance(raw_status, str) and raw_status.startswith("ProcessingStatus."):
            name = raw_status.split(".", 1)[1]
            if name in ProcessingStatus.__members__:
                return ProcessingStatus[name].value
        return str(raw_status)
