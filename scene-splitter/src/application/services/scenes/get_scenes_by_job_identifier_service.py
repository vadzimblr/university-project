from uuid import UUID

from application.dtos.processing_jobs.processing_job_scenes_response_dto import ProcessingJobScenesResponseDto
from application.dtos.scenes.scene_response_dto import SceneResponseDto
from domain.exceptions.processing_jobs.processing_job_not_found_exception import ProcessingJobNotFoundException
from domain.exceptions.processing_jobs.processing_not_completed_exception import ProcessingNotCompletedException
from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from infrastructure.persistence.repositories.scene_repository import SceneRepository


class GetSceneByJobIdentifierService:
    def __init__(
        self,
        processing_job_repository: ProcessingJobRepository,
        scene_repository: SceneRepository
    ):
        self.processing_job_repository = processing_job_repository
        self.scene_repository = scene_repository

    async def get_scenes_by_job_identifier(self, job_identifier: UUID):
        job_identifier_str = str(job_identifier)
        job = self.processing_job_repository.get_by_id(job_identifier_str)

        if not job:
            raise ProcessingJobNotFoundException(search_criteria='identifier', value=job_identifier_str)

        if job.status != "completed":
            raise ProcessingNotCompletedException()

        scenes = self.scene_repository.get_scenes_by_processing_job_identifier(job_identifier)

        return ProcessingJobScenesResponseDto.from_values(
            processing_job=job,
            scenes=SceneResponseDto.from_entities(scenes),
        )
