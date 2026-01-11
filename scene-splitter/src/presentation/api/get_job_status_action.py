from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends

from application.dtos.processing_jobs.processing_job_response_dto import ProcessingJobStatusResponseDto
from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from core.di.container import Container

router = APIRouter()

@router.get("/processing-jobs/{job_id}/status")
@inject
async def get_job_status_action(
    job_id: str,
        processing_job_repository: Annotated[
            ProcessingJobRepository,
            Depends(Provide[Container.processing_job_repository])
        ],
):
    job = processing_job_repository.get_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return ProcessingJobStatusResponseDto.from_entity(job)
