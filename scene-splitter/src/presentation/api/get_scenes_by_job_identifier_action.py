from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends

from application.services.scenes.get_scenes_by_job_identifier_service import GetSceneByJobIdentifierService
from core.di.container import Container
from domain.exceptions.processing_jobs.processing_job_not_found_exception import ProcessingJobNotFoundException
from domain.exceptions.processing_jobs.processing_not_completed_exception import ProcessingNotCompletedException

router = APIRouter()

@router.get("/processing-jobs/{job_id}/scenes")
@inject
async def get_scenes_by_job_identifier_action(
        job_id: UUID,
        service: Annotated[
            GetSceneByJobIdentifierService,
            Depends(Provide[Container.get_scenes_by_job_identifier_service])
        ],
):
    try:
        result = await service.get_scenes_by_job_identifier(job_id)
    except ProcessingJobNotFoundException as process_job_not_found_exception:
        raise HTTPException(status_code=404, detail=str(process_job_not_found_exception))
    except ProcessingNotCompletedException as process_not_completed_exception:
        raise HTTPException(status_code=404, detail=str(process_not_completed_exception))

    return result
