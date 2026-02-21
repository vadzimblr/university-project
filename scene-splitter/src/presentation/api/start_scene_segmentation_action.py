from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends

from application.dtos.processing_jobs.processing_job_created_response_dto import ProcessingJobCreatedResponseDto
from core.di.container import Container
from infrastructure.celery.tasks.scene_segmentation_task import scene_segmentation_task
from infrastructure.persistence.repositories.document_repository import DocumentRepository
from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository

router = APIRouter()


@router.post("/processing-jobs/segment-scenes")
@inject
async def start_scene_segmentation_action(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(999),
    document_repository: Annotated[
        DocumentRepository,
        Depends(Provide[Container.document_repository])
    ],
    processing_job_repository: Annotated[
        ProcessingJobRepository,
        Depends(Provide[Container.processing_job_repository])
    ],
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()

    document = document_repository.create(
        filename=file.filename,
        file_size=len(pdf_bytes),
        mime_type=file.content_type or "application/pdf"
    )

    job = processing_job_repository.create(
        document_id=str(document.id),
        start_page=start_page,
        end_page=end_page
    )

    task = scene_segmentation_task.delay(str(job.id), pdf_bytes, start_page, end_page)
    processing_job_repository.update_celery_task_id(str(job.id), task.id)

    return ProcessingJobCreatedResponseDto.from_values(
        job_identifier=job.id,
        task_identifier=task.id,
        document_identifier=document.id
    )
