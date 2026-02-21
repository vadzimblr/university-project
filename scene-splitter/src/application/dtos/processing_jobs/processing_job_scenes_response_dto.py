from uuid import UUID

from pydantic import BaseModel

from application.dtos.scenes.scene_response_dto import SceneResponseDto
from domain.entities import ProcessingJob


class ProcessingJobScenesResponseDto(BaseModel):
    job_identifier: UUID
    scenes_count: int
    scenes: list[SceneResponseDto]

    @classmethod
    def from_values(cls, processing_job: ProcessingJob, scenes: list[SceneResponseDto]) -> "ProcessingJobScenesResponseDto":
        return cls(
            job_identifier=processing_job.id,
            scenes_count=len(scenes),
            scenes=scenes,
        )
